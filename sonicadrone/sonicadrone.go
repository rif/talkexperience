package main

import (
	"bytes"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"mime/multipart"
	"net/http"
	"os"
	"os/exec"
	"path"
	"strings"
)

var (
	ACCEPTED_ORIGINS = []string{"http://sonicalabs.appspot.com", "http://www.talkexperience.com", "http://localhost:8080", "::1"}
)

const (
	MAIN_APPLICATION = "http://www.talkexperience.com"
	//MAIN_APPLICATION = "http://localhost:8080"
	BLOBS_APPLICATION = "http://sonicablobs.appspot.com"
	//BLOBS_APPLICATION = "http://localhost:8081"
	TRANSFORMER = "ffmpeg"
)

func checkOrigin(orig []string, ref string) (right bool) {
	if (orig == nil) || (len(orig) != 1) {
		return
	}
	for _, accO := range ACCEPTED_ORIGINS {
		if strings.Contains(orig[0], accO) {
			right = true
			break
		}
	}
	if !right {
		return
	}
	right = false
	for _, accO := range ACCEPTED_ORIGINS {
		if strings.Contains(ref, accO) {
			right = true
			break
		}
	}
	return
}

func handleProcess(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Access-Control-Allow-Origin", MAIN_APPLICATION)
	w.Header().Set("Access-Control-Allow-Headers", "X-Requested-With,X-File-Name,Content-Type")
	if r.Method != "POST" {
		return
	}
	if !checkOrigin(r.Header["Origin"], r.Referer()) {
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
	path := "./upload/" + uuid + "_" + fileName
	f, _ := os.Create(path)

	if r.Header["X-Requested-With"] != nil && r.Header["X-Requested-With"][0] != "XMLHttpRequest" {
		fn, _, err := r.FormFile("qqfile")
		defer fn.Close()
		if err != nil {
			log.Print("Could not get upload from main app!", err)
			fmt.Fprint(w, "{error: 'Could not get upload from main app!'}")
			return
		}
		io.Copy(f, fn)
	} else {
		io.Copy(f, r.Body)
		defer r.Body.Close()
	}
	f.Close()
	log.Print("Start processing ", fileName, " - ", uuid)
	go process(path, fileName, uuid)
	fmt.Fprint(w, "{success:true}")
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
	newFileName := transcode(path, removeExt(fileName))
	// Open the file to upload	
	fd, err := os.Open(newFileName)
	if err != nil {
		log.Print("Could not open transcoded file for reading!")
		return
	}
	_, err = io.Copy(part, fd)
	if err != nil {
		log.Print("Could not write upload to local file!")
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

func removeExt(oldfn string) (basefn string) {
	ext := path.Ext(oldfn)
	basefn = strings.TrimRight(oldfn, ext)
	return
}

func transcode(oldfn, basefn string) (newfn string) {
	_, err := exec.LookPath(TRANSFORMER)
	if err != nil {
		log.Fatal(TRANSFORMER + " not installed!")
	}
	newfn = "ready/" + basefn + ".mp3"
	log.Printf("Transcoding %s to %s", oldfn, newfn)
	//err = exec.Command(TRANSFORMER, "-i", oldfn, "-vn", "-c:a", "libmp3lame", "-b:a", "96k", "-q:a", "9", "-y", newfn).Run()
	err = exec.Command(TRANSFORMER, "-i", oldfn, "-vn", "-acodec", "libmp3lame", "-ab", "96k", "-aq", "9", "-y", newfn).Run()
	if err != nil {
		log.Print(err)
	}
	err = os.Remove(oldfn)
	if err != nil {
		log.Print("Could not delete: ", oldfn)
	}
	return
}

func main() {
	http.HandleFunc("/process", handleProcess)
	log.Print("Serving...")
	err := http.ListenAndServe(":6060", nil)
	if err != nil {
		log.Print("Could not start server!")
		return
	}
}
