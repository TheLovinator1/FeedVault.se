package main

import (
	"log"

	"net/http"
)

func init() { log.SetFlags(log.LstdFlags | log.Lshortfile) }

func main() {
	log.Print("Starting server")

	// Create a new ServeMux
	mux := http.NewServeMux()

	// Routes
	mux.HandleFunc("/", IndexHandler)
	mux.HandleFunc("/api", ApiHandler)
	mux.HandleFunc("/feeds", FeedsHandler)
	mux.HandleFunc("/add", AddFeedHandler)
	mux.HandleFunc("/upload_opml", UploadOpmlHandler)

	// Create server
	server := &http.Server{
		Addr:    "127.0.0.1:8000",
		Handler: mux,
	}

	log.Print("Server started on http://localhost:8000/ <Ctrl-C> to stop")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("ListenAndServe(): %v", err)
	}
}
