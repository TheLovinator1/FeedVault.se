package main

import (
	"bufio"
	"errors"
	"fmt"
	"html/template"
	"log"
	"net"
	"net/http"
	"net/url"
	"strings"
	"time"

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
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Compress(5))
	r.Use(middleware.Heartbeat("/ping"))

	r.Get("/", IndexHandler)
	r.Get("/api", ApiHandler)
	r.Get("/donate", DonateHandler)
	r.Get("/feeds", FeedsHandler)
	r.Get("/privacy", PrivacyHandler)
	r.Post("/add", AddFeedHandler)

	r.Handle("/static/*", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	r.NotFound(NotFoundHandler)
	r.MethodNotAllowed(MethodNotAllowedHandler)

	log.Println("Listening on http://localhost:8000/ <Ctrl-C> to stop")
	http.ListenAndServe("127.0.0.1:8000", r)
}

func scrapeBadURLs() {
	// TODO: We should only scrape the bad URLs if the file has been updated
	// TODO: Use brotli compression https://gitlab.com/malware-filter/urlhaus-filter#compressed-version
	filterListURLs := []string{
		"https://malware-filter.gitlab.io/malware-filter/phishing-filter-dnscrypt-blocked-names.txt",
		"https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-dnscrypt-blocked-names-online.txt",
	}

	// Scrape the bad URLs
	badURLs := []BadURLs{}
	for _, url := range filterListURLs {
		// Check if we have scraped the bad URLs in the last 24 hours
		var meta BadURLsMeta
		db.Where("url = ?", url).First(&meta)
		if time.Since(meta.LastScraped).Hours() < 24 {
			log.Printf("%s was last scraped %.1f hours ago\n", url, time.Since(meta.LastScraped).Hours())
			continue
		}

		// Create the meta if it doesn't exist
		if meta.ID == 0 {
			meta = BadURLsMeta{URL: url}
			db.Create(&meta)
		}

		// Update the last scraped time
		db.Model(&meta).Update("last_scraped", time.Now())

		// Get the filter list
		resp, err := http.Get(url)
		if err != nil {
			log.Println("Failed to get filter list:", err)
			continue
		}
		defer resp.Body.Close()

		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			line := scanner.Text()
			if strings.HasPrefix(line, "#") {
				log.Println("Comment:", line)
				continue
			}

			// Skip the URL if it already exists in the database
			var count int64
			db.Model(&BadURLs{}).Where("url = ?", line).Count(&count)
			if count > 0 {
				log.Println("URL already exists:", line)
				continue
			}

			// Add the bad URL to the list
			badURLs = append(badURLs, BadURLs{URL: line, Active: true})
		}

		if err := scanner.Err(); err != nil {
			log.Println("Failed to scan filter list:", err)
		}
	}

	if len(badURLs) == 0 {
		log.Println("No new URLs found in", len(filterListURLs), "filter lists")
		return
	}

	// Log how many bad URLs we found
	log.Println("Found", len(badURLs), "bad URLs")

	// Mark all the bad URLs as inactive if we have any in the database
	var count int64
	db.Model(&BadURLs{}).Count(&count)
	if count > 0 {
		db.Model(&BadURLs{}).Update("active", false)
	}

	// Save the bad URLs to the database
	db.Create(&badURLs)
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

// Run some simple validation on the URL
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

	// Don't allow local URLs (e.g. router URLs)
	// Taken from https://github.com/uBlockOrigin/uAssets/blob/master/filters/lan-block.txt
	// https://github.com/gwarser/filter-lists
	localURLs := []string{
		"[::]",
		"[::1]",
		"airbox.home",
		"airport",
		"arcor.easybox",
		"aterm.me",
		"bthomehub.home",
		"bthub.home",
		"congstar.box",
		"connect.box",
		"console.gl-inet.com",
		"easy.box",
		"etxr",
		"fire.walla",
		"fritz.box",
		"fritz.nas",
		"fritz.repeater",
		"giga.cube",
		"hi.link",
		"hitronhub.home",
		"home.arpa",
		"homerouter.cpe",
		"host.docker.internal",
		"huaweimobilewifi.com",
		"localbattle.net",
		"localhost",
		"mobile.hotspot",
		"myfritz.box",
		"ntt.setup",
		"pi.hole",
		"plex.direct",
		"repeater.asus.com",
		"router.asus.com",
		"routerlogin.com",
		"routerlogin.net",
		"samsung.router",
		"speedport.ip",
		"steamloopback.host",
		"tplinkap.net",
		"tplinkeap.net",
		"tplinkmodem.net",
		"tplinkplclogin.net",
		"tplinkrepeater.net",
		"tplinkwifi.net",
		"web.setup.home",
		"web.setup",
	}
	for _, localURL := range localURLs {
		if strings.Contains(domain, localURL) {
			return errors.New("local URLs are not allowed")
		}
	}

	// Check if the domain is in BadURLs
	var count int64
	db.Model(&BadURLs{}).Where("url = ?", domain).Count(&count)
	if count > 0 {
		return errors.New("URL is in the bad URLs list")
	}

	// Don't allow URLs that end with .local
	if strings.HasSuffix(domain, ".local") {
		return errors.New("URLs ending with .local are not allowed")
	}

	// Don't allow URLs that end with .onion
	if strings.HasSuffix(domain, ".onion") {
		return errors.New("URLs ending with .onion are not allowed")
	}

	// Don't allow URLs that end with .home.arpa
	if strings.HasSuffix(domain, ".home.arpa") {
		return errors.New("URLs ending with .home.arpa are not allowed")
	}

	// Don't allow URLs that end with .internal
	// Docker uses host.docker.internal
	if strings.HasSuffix(domain, ".internal") {
		return errors.New("URLs ending with .internal are not allowed")
	}

	// Don't allow URLs that end with .localdomain
	if strings.HasSuffix(domain, ".localdomain") {
		return errors.New("URLs ending with .localdomain are not allowed")
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
