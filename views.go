package main

import (
	"fmt"
	"html/template"
	"log"
	"net/http"
	"strings"
)

func NotFoundHandler(w http.ResponseWriter, r *http.Request) {
	data := TemplateData{
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
	data := TemplateData{
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

func PrivacyHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "Privacy", "Privacy Page", "privacy, page", "TheLovinator", "http://localhost:8000/privacy", "privacy")
}

func TermsHandler(w http.ResponseWriter, _ *http.Request) {
	renderPage(w, "Terms", "Terms and Conditions Page", "terms, page", "TheLovinator", "http://localhost:8000/terms", "terms")
}

func AddFeedHandler(w http.ResponseWriter, r *http.Request) {
	var parseErrors []ParseResult

	// Parse the form and get the URLs
	r.ParseForm()
	urls := r.Form.Get("urls")
	if urls == "" {
		http.Error(w, "No URLs provided", http.StatusBadRequest)
		return
	}

	for _, feed_url := range strings.Split(urls, "\n") {
		// TODO: Try to upgrade to https if http is provided

		// Validate the URL
		err := validateURL(feed_url)
		if err != nil {
			parseErrors = append(parseErrors, ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
			continue
		}

		// "Add" the feed to the database
		log.Println("Adding feed:", feed_url)
	}

	// Render the index page with the parse errors
	data := TemplateData{
		Title:       "FeedVault",
		Description: "FeedVault - A feed archive",
		Keywords:    "RSS, Atom, Feed, Archive",
		ParseErrors: parseErrors,
	}
	data.GetDatabaseSizeAndFeedCount()

	t, err := template.ParseFiles("templates/base.tmpl", "templates/index.tmpl")
	if err != nil {
		http.Error(w, fmt.Sprintf("Internal Server Error: %v", err), http.StatusInternalServerError)
		return
	}
	t.ExecuteTemplate(w, "base", data)

}
