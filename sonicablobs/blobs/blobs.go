package blobs

import (
	"appengine"
	"appengine/blobstore"
	"appengine/urlfetch"
	"fmt"
	"io"
	"net/http"
	"net/url"
)

const (
	MAIN_APPLICATION = "http://talkexperience.com"
	//MAIN_APPLICATION = "http://localhost:8080"
)

func serveError(c appengine.Context, w http.ResponseWriter, err error) {
	w.WriteHeader(http.StatusInternalServerError)
	w.Header().Set("Content-Type", "text/plain")
	io.WriteString(w, "Internal Server Error")
	c.Errorf("%v", err)
}

func handleUrl(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	uploadURL, err := blobstore.UploadURL(c, "/upload", nil)
	if err != nil {
		serveError(c, w, err)
		return
	}
	w.Header().Set("Content-Type", "text/plain")
	fmt.Fprint(w, uploadURL)
}

func handleServe(w http.ResponseWriter, r *http.Request) {
	blobstore.Send(w, appengine.BlobKey(r.FormValue("blobKey")))
}

func handleDelete(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	err := blobstore.Delete(c, appengine.BlobKey(r.FormValue("blobKey")))
	if err != nil {
		serveError(c, w, err)
		return
	}
}

func handleUpload(w http.ResponseWriter, r *http.Request) {
	c := appengine.NewContext(r)
	client := urlfetch.Client(c)
	blobs, other, err := blobstore.ParseUpload(r)
	if err != nil {
		serveError(c, w, err)
		return
	}
	uuid := other["uuid"][0]
	file := blobs["upload"]
	if len(file) == 0 {
		c.Errorf("no file uploaded")
		http.Redirect(w, r, "/", http.StatusFound)
		return
	}
	c.Infof("Uploading: %s - %s", file[0].Filename, uuid)
	w.Header().Set("Content-Type", "text/plain")
	// setting download info
	_, err = client.PostForm(MAIN_APPLICATION+"/set_download_info",
		url.Values{"uuid": {uuid}, "host": {r.Host}, "key": {string(file[0].BlobKey)}, "filename": {file[0].Filename}})
	if err != nil {
	     c.Errorf("Error uploading blob information: %v", err)
	}
}

func init() {
	http.HandleFunc("/geturl", handleUrl)
	http.HandleFunc("/serve/", handleServe)
	http.HandleFunc("/upload", handleUpload)
	http.HandleFunc("/delete/", handleDelete)
}
