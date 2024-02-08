package main

import (
	"log"
	"net/http"

	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

var db *gorm.DB

// Initialize the database
func init() {
	var err error
	db, err = gorm.Open(sqlite.Open("feedvault.db"), &gorm.Config{})
	if err != nil {
		panic("Failed to connect to database")
	}
	if db == nil {
		panic("db nil")
	}
	log.Println("Connected to database")

	// Migrate the schema
	err = db.AutoMigrate(&Feed{}, &Item{}, &Person{}, &Image{}, &Enclosure{}, &DublinCoreExtension{}, &ITunesFeedExtension{}, &ITunesItemExtension{}, &ITunesCategory{}, &ITunesOwner{}, &Extension{})
	if err != nil {
		panic("Failed to migrate the database")
	}
}

func main() {
	log.Println("Starting FeedVault...")

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

	log.Println("Listening on http://localhost:8000/ <Ctrl-C> to stop")
	if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
		log.Fatalf("Server error: %v", err)
	}
}
