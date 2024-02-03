package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
)

func main() {
	r := chi.NewRouter()
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Compress(5))
	r.Use(middleware.Heartbeat("/ping"))

	r.Get("/", IndexHandler)
	r.Get("/api", ApiHandler)
	r.Get("/about", AboutHandler)
	r.Get("/donate", DonateHandler)
	r.Get("/feeds", FeedsHandler)

	r.Handle("/static/*", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	r.NotFound(NotFoundHandler)
	r.MethodNotAllowed(MethodNotAllowedHandler)

	log.Println("Listening on http://localhost:8000/ <Ctrl-C> to stop")
	http.ListenAndServe("127.0.0.1:8000", r)
}

type Data struct {
	Title        string
	Description  string
	Keywords     string
	Author       string
	CanonicalURL string
	FeedCount    int
	DatabaseSize int
	Request      *http.Request
}

func (d *Data) GetDatabaseSizeAndFeedCount() {
	// Set the database size to 0
	d.DatabaseSize = 0

	// Set the feed count to 0
	d.FeedCount = 0
}

func renderPage(w http.ResponseWriter, title, description, keywords, author, url, templateName string) {
	data := Data{
		Title:        title,
		Description:  description,
		Keywords:     keywords,
		Author:       author,
		CanonicalURL: url,
		FeedCount:    0,
		DatabaseSize: 0,
	}
	data.GetDatabaseSizeAndFeedCount()

	t, err := template.ParseFiles("templates/base.tmpl", fmt.Sprintf("templates/%s.tmpl", templateName))
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Server Error: %v", err), http.StatusInternalServerError)
		return
	}
	t.ExecuteTemplate(w, "base", data)
}

func NotFoundHandler(w http.ResponseWriter, r *http.Request) {
	data := Data{
		Request: r,
	}
	data.GetDatabaseSizeAndFeedCount()
	t, err := template.ParseFiles("templates/base.tmpl", "templates/404.tmpl")
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Server Error: %v", err), http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusNotFound)
	t.ExecuteTemplate(w, "base", data)
}

func MethodNotAllowedHandler(w http.ResponseWriter, r *http.Request) {
	data := Data{
		Request: r,
	}
	data.GetDatabaseSizeAndFeedCount()
	t, err := template.ParseFiles("templates/base.tmpl", "templates/405.tmpl")
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Server Error: %v", err), http.StatusInternalServerError)
		return
	}
	w.WriteHeader(http.StatusMethodNotAllowed)
	t.ExecuteTemplate(w, "base", data)
}

func IndexHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "FeedVault", "FeedVault - A feed archive", "RSS, Atom, Feed, Archive", "TheLovinator", "http://localhost:8000/", "index")
}

func ApiHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "API", "API Page", "api, page", "TheLovinator", "http://localhost:8000/api", "api")
}
func AboutHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "About", "About Page", "about, page", "TheLovinator", "http://localhost:8000/about", "about")
}

func DonateHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "Donate", "Donate Page", "donate, page", "TheLovinator", "http://localhost:8000/donate", "donate")
}

func FeedsHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "Feeds", "Feeds Page", "feeds, page", "TheLovinator", "http://localhost:8000/feeds", "feeds")
}
