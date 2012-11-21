package main

import (
	"bytes"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path"
	"strconv"
	"strings"
	"time"
        "runtime"
)

var (
	ACCEPTED_ORIGINS = []string{"http://talk-experience.appspot.com", "http://www.talkexperience.com", "http://localhost:8000", "::1"}
        REPO_PATH = os.Getenv("OPENSHIFT_REPO_DIR")
        DATA_DIR = os.Getenv("OPENSHIFT_DATA_DIR")
)

const (
	MAIN_APPLICATION = "http://www.talkexperience.com"
	//MAIN_APPLICATION = "http://localhost:8000"
	BLOBS_APPLICATION = "http://talkexperienceblobs.appspot.com"
	//BLOBS_APPLICATION    = "http://localhost:8081"	
	TRANSFORMER          = "ffmpeg"
	BITRATE              = "96k"
	FOLDER_UPLOAD        = "upload"
	FOLDER_READY         = "ready"
	CROSSDOMAIN_WAMI_XML = `<cross-domain-policy>
<site-control permitted-cross-domain-policies="master-only"/>
<allow-access-from domain="*.talkexperience.com" secure="false"/>
<allow-http-request-headers-from domain="*.talkexperience.com" headers="*"/>
</cross-domain-policy>
`
)

func checkOrigin(orig []string) bool {
	if (orig == nil) || (len(orig) != 1) {
		return false
	}
	for _, accO := range ACCEPTED_ORIGINS {
		if strings.Contains(orig[0], accO) {
			return true
			break
		}
	}
	return false
}

func checkReferer(ref string) bool {
	for _, accO := range ACCEPTED_ORIGINS {
		if strings.Contains(ref, accO) {
			return true
			break
		}
	}
	return false
}

func handleProcess(w http.ResponseWriter, r *http.Request) {
	log.Printf("record request: %+v", r)
	w.Header().Set("Access-Control-Allow-Origin", MAIN_APPLICATION)
	//w.Header().Set("Access-Control-Allow-Headers", "X-Requested-With,X-File-Name,Content-Type")
	w.Header().Set("Access-Control-Allow-Headers", "origin, x-mime-type, x-requested-with, x-file-name, content-type, cache-control")
	if r.Method == "OPTIONS" {
		return
	}

	if r.Method != "POST" {
		log.Print("Not a POST request, returning!")
		return
	}

	if !checkOrigin(r.Header["Origin"]) || !checkReferer(r.Referer()) {
		log.Printf("Hacker request: origin: %v, referer: %v", r.Header["Origin"], r.Referer())
		return
	}
	uuid := r.FormValue("uuid")
	fileName := r.FormValue("qqfile")
	if uuid == "" || fileName == "" {
		log.Print("Invalid form values!")
		fmt.Fprint(w, "{error: 'Invalid form values!'}")
		return
	}
	path := path.Join(DATA_DIR, FOLDER_UPLOAD, uuid+"_"+fileName)
	f, err := os.Create(path)
	if err != nil {
		log.Print("Could not create ", path)
	}

	if r.Header["X-Requested-With"] != nil && r.Header["X-Requested-With"][0] != "XMLHttpRequest" {
		fn, _, err := r.FormFile("qqfile")

		if err != nil {
			log.Print("Could not get upload from main app!", err)
			fmt.Fprint(w, "{error: 'Could not get upload from main app!'}")
			return
		}
		io.Copy(f, fn)
		fn.Close()
	} else {
		io.Copy(f, r.Body)
		defer r.Body.Close()
	}
	if f != nil {
	    f.Close()
	}

	log.Print("Start processing ", fileName, " - ", uuid)
	go process(path, fileName, uuid)
	fmt.Fprint(w, `{"success":true}`)
}

func handleRecord(w http.ResponseWriter, r *http.Request) {
	log.Printf("record request: %+v", r)
	if r.Method != "POST" {
		return
	}
	if !checkReferer(r.Referer()) {
		log.Printf("Hacker request: origin: %v, referer: %v", r.Header["Origin"], r.Referer())
		return
	}
	r.ParseForm()
	uuid := ""
	if uuidFormValue, ok := r.Form["uuid"]; ok {
		uuid = uuidFormValue[0]
	} else {
		log.Print("UUID missing, aborting")
		return
	}

	data, err := ioutil.ReadAll(r.Body)
	defer r.Body.Close()
	if err != nil {
		fmt.Println(err)
	}
	fileName := fmt.Sprintf("record_%s.wav", genUUID())
	path := path.Join(DATA_DIR, FOLDER_UPLOAD, uuid+"_"+fileName)
	err = ioutil.WriteFile(path, data, 0660)
	if err != nil {
		fmt.Println(err)
	}
	log.Print("Start processing ", fileName, " - ", uuid)
	go process(path, fileName, uuid)
	fmt.Fprint(w, `{"success":true}`)
}

func handleCrossdomainWamiXML(w http.ResponseWriter, r *http.Request) {
	fmt.Fprint(w, CROSSDOMAIN_WAMI_XML)
}

func process(path, fileName, uuid string) {
	resp, err := http.Get(BLOBS_APPLICATION + "/geturl")
	if err != nil {
		log.Print("No response from get upload url!")
		return
	}
	defer resp.Body.Close()
	postUrl, err := ioutil.ReadAll(resp.Body)

	// create the form
	buf := new(bytes.Buffer)
	writer := multipart.NewWriter(buf)
	// Create a uuid field
	err = writer.WriteField("uuid", uuid)
	if err != nil {
		log.Print("Could not add uuid form part!")
		return
	}
	// Create a upload field
	part, err := writer.CreateFormFile("upload", fileName)
	if err != nil {
		log.Print("Could not add upload form part!")
		return
	}
	//transcode the file
	newFileName := transcode(path, prepareNewFileName(fileName, uuid))
	// Open the file to upload	
	fd, err := os.Open(newFileName)
	if err != nil {
		log.Print("Could not open transcoded file for reading!")
		return
	}
	log.Print("Loading to part: ", newFileName)
	_, err = io.Copy(part, fd)
	if err != nil {
		log.Print("Could not write upload to part!")
		return
	}
	err = writer.Close()
	if err != nil {
		log.Print("Could not close multipart form!")
		return
	}
	err = fd.Close()
	if err != nil {
		log.Print("Could not close transcoded file!")
		return
	}

	// Create the POST request to the URL with all fields mounted
	req, err := http.NewRequest("POST", string(postUrl), buf)
	if err != nil {
		log.Print("Could not create upload post request!")
		return
	}
	// Set the header of the request to send 
	req.Header.Set("Content-Type", writer.FormDataContentType())
	// Declare our HTTP client to execute the request 
	client := new(http.Client)
	// Finally send our POST HTTP request 
	_, err = client.Do(req)
	if err != nil {
		log.Print("Could not execute upload post request!")
		return
	}
	err = os.Remove(newFileName)
	if err != nil {
		log.Print("Could not delete transcoded file: ", path)
	}
}

func prepareNewFileName(oldfn, uuid string) (basefn string) {
	ext := path.Ext(oldfn)
	basefn = uuid + "_" + strings.TrimRight(oldfn, ext)
	return
}

func transcode(oldfn, basefn string) (newfn string) {
        if REPO_PATH == ""{
            _, err := exec.LookPath(TRANSFORMER)
            if err != nil {
                log.Fatal(TRANSFORMER + " not installed!")
            }
        }
	newfn = path.Join(DATA_DIR, FOLDER_READY, basefn+".mp3")
	log.Printf("Transcoding %s to %s", oldfn, newfn)
	//err = exec.Command(TRANSFORMER, "-i", oldfn, "-vn", "-c:a", "libmp3lame", "-b:a", "96k", "-q:a", "9", "-y", newfn).Run()
	err := exec.Command(path.Join(REPO_PATH, "misc", TRANSFORMER), "-i", oldfn, "-vn", "-acodec", "libmp3lame", "-ab", BITRATE, "-aq", "9", "-y", newfn).Run()
	if err != nil {
		log.Print(err)
	}
	err = os.Remove(oldfn)
	if err != nil {
		log.Print("Could not delete: ", oldfn)
	}
	log.Print("Done ", newfn)
	return
}

// helper function for uuid generation
func genUUID() string {
	uuid := make([]byte, 16)
	n, err := rand.Read(uuid)
	if n != len(uuid) || err != nil {
		return strconv.FormatInt(time.Now().UnixNano(), 10)
	}
	// TODO: verify the two lines implement RFC 4122 correctly
	uuid[8] = 0x80 // variant bits see page 5
	uuid[4] = 0x40 // version 4 Pseudo Random, see page 7

	return hex.EncodeToString(uuid)
}

func main() {
    runtime.GOMAXPROCS(runtime.NumCPU())
    ip := os.Getenv("OPENSHIFT_INTERNAL_IP") // empty is localhost
    os.Mkdir(path.Join(DATA_DIR, FOLDER_UPLOAD), os.ModeDir | os.ModePerm)
    os.Mkdir(path.Join(DATA_DIR, FOLDER_READY), os.ModeDir | os.ModePerm)
	http.HandleFunc("/process", handleProcess)
	http.HandleFunc("/record", handleRecord)
	http.HandleFunc("/crossdomain.xml", handleCrossdomainWamiXML)
	log.Print("Serving...")
	err := http.ListenAndServe(fmt.Sprintf("%s:8080", ip), nil)
	if err != nil {
            log.Print("Could not start server: ", err)
            return
	}
}
