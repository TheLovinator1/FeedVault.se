package main

import (
	"errors"
	"fmt"
	"html/template"
	"log"
	"net"
	"net/http"
	"net/url"
	"strings"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"gorm.io/driver/sqlite"
	"gorm.io/gorm"
)

// Database connection
var db *gorm.DB

func main() {
	log.Println("Starting FeedVault...")
	db, err := gorm.Open(sqlite.Open("feedvault.db"), &gorm.Config{})
	if err != nil {
		panic("Failed to connect to database")
	}

	// Migrate the schema
	err = db.AutoMigrate(&Feed{}, &Item{}, &Person{}, &Image{}, &Enclosure{}, &DublinCoreExtension{}, &ITunesFeedExtension{}, &ITunesItemExtension{}, &ITunesCategory{}, &ITunesOwner{}, &Extension{})
	if err != nil {
		panic("Failed to migrate the database")
	}

	// Create a new router
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
	r.Post("/add", AddFeedHandler)

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
	DatabaseSize string
	Request      *http.Request
	ParseErrors  []ParseResult
}

type ParseResult struct {
	FeedURL string
	Msg     string
	IsError bool
}

func (d *Data) GetDatabaseSizeAndFeedCount() {
	d.DatabaseSize = GetDBSize()
}

func renderPage(w http.ResponseWriter, title, description, keywords, author, url, templateName string) {
	data := Data{
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

func validateURL(feed_url string) error {
	// Check if URL starts with http or https
	if !strings.HasPrefix(feed_url, "http://") && !strings.HasPrefix(feed_url, "https://") {
		return errors.New("URL must start with http:// or https://")
	}

	// Parse a url into a URL structure
	u, err := url.Parse(feed_url)
	if err != nil {
		return errors.New("failed to parse URL")
	}

	// Get the domain from the URL
	domain := u.Hostname()
	domain = strings.TrimSpace(domain)
	if domain == "" {
		return errors.New("URL does not contain a domain")
	}

	// Don't allow IP address URLs
	ip := net.ParseIP(domain)
	if ip != nil {
		return errors.New("IP address URLs are not allowed")
	}

	// Don't allow localhost URLs
	if strings.Contains(domain, "localhost") {
		return errors.New("localhost are not allowed")
	}

	// Don't allow URLs that end with .local
	if strings.HasSuffix(domain, ".local") {
		return errors.New("URLs ending with .local are not allowed")
	}

	// Check if the domain is resolvable
	_, err = net.LookupIP(domain)
	if err != nil {
		return errors.New("failed to resolve domain")
	}

	// Check if the URL is reachable
	_, err = http.Get(feed_url)
	if err != nil {
		return errors.New("failed to reach URL")
	}

	return nil
}

func AddFeedHandler(w http.ResponseWriter, r *http.Request) {
	r.ParseForm()
	urls := r.Form.Get("urls")
	if urls == "" {
		http.Error(w, "No feed URLs provided", http.StatusBadRequest)
		return
	}

	var parseErrors []ParseResult

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
	data := Data{
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
