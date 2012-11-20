package main

import (
    "fmt"
    "log"
    "net/http"
)

type Greeting string

func (g Greeting) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Access-Control-Allow-Origin", "http://localhost:8000")	
	w.Header().Set("Access-Control-Allow-Headers", "origin, x-mime-type, x-requested-with, x-file-name, content-type, cache-control")
    log.Printf("received: %+v", r)
    fmt.Fprint(w, g)
}

func main() {
    log.Print("Listening on 6060...")
    err := http.ListenAndServe("localhost:6060", Greeting(`{"success": true}`))
    if err != nil {
        log.Fatal(err)
    }
}
