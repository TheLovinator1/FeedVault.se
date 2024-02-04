package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
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
	err = db.AutoMigrate(&BadURLsMeta{}, &BadURLs{}, &Feed{}, &Item{}, &Person{}, &Image{}, &Enclosure{}, &DublinCoreExtension{}, &ITunesFeedExtension{}, &ITunesItemExtension{}, &ITunesCategory{}, &ITunesOwner{}, &Extension{})
	if err != nil {
		panic("Failed to migrate the database")
	}
}

func main() {
	log.Println("Starting FeedVault...")

	// Scrape the bad URLs in the background
	// TODO: Run this in a goroutine
	scrapeBadURLs()

	// Create a new router
	r := chi.NewRouter()

	// Middleware
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Compress(5))
	r.Use(middleware.Heartbeat("/ping"))

	// Routes
	r.Get("/", IndexHandler)
	r.Get("/api", ApiHandler)
	r.Get("/donate", DonateHandler)
	r.Get("/feeds", FeedsHandler)
	r.Get("/privacy", PrivacyHandler)
	r.Get("/terms", TermsHandler)
	r.Post("/add", AddFeedHandler)

	// Static files
	r.Handle("/static/*", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	// 404 and 405 handlers
	r.NotFound(NotFoundHandler)
	r.MethodNotAllowed(MethodNotAllowedHandler)

	log.Println("Listening on http://localhost:8000/ <Ctrl-C> to stop")
	http.ListenAndServe("127.0.0.1:8000", r)
}

func renderPage(w http.ResponseWriter, title, description, keywords, author, url, templateName string) {
	data := TemplateData{
		Title:        title,
		Description:  description,
		Keywords:     keywords,
		Author:       author,
		CanonicalURL: url,
		FeedCount:    0,
	}
	data.GetDatabaseSizeAndFeedCount()

	t, err := template.ParseFiles("templates/base.tmpl", fmt.Sprintf("templates/%s.tmpl", templateName))
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Server Error: %v", err), http.StatusInternalServerError)
		return
	}
	t.ExecuteTemplate(w, "base", data)
}
