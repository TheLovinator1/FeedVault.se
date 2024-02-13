package handlers

import (
	"io"
	"log"
	"net/http"

	"github.com/TheLovinator1/FeedVault/pkg/html"
	"github.com/TheLovinator1/FeedVault/pkg/models"
	"github.com/TheLovinator1/FeedVault/pkg/opml"
	"github.com/TheLovinator1/FeedVault/pkg/validate"
)

func UploadOpmlHandler(w http.ResponseWriter, r *http.Request) {
	// Parse the form and get the file
	r.ParseMultipartForm(10 << 20) // 10 MB
	file, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "No file provided", http.StatusBadRequest)
		return
	}
	defer file.Close()

	// Read the file
	all, err := io.ReadAll(file)
	if err != nil {
		http.Error(w, "Failed to read file", http.StatusInternalServerError)
		return
	}
	// Parse the OPML file
	parseResult := []models.ParseResult{}
	links, err := opml.ParseOpml(string(all))
	if err != nil {
		parseResult = append(parseResult, models.ParseResult{FeedURL: "/upload_opml", Msg: err.Error(), IsError: true})
	} else {
		// Add the feeds to the database
		for _, feed_url := range links.XMLLinks {
			log.Println("Adding feed:", feed_url)

			// Validate the URL
			err := validate.ValidateFeedURL(feed_url)
			if err != nil {
				parseResult = append(parseResult, models.ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
				continue
			}

			parseResult = append(parseResult, models.ParseResult{FeedURL: feed_url, Msg: "Added", IsError: false})
		}
	}

	// Return the results
	htmlData := html.HTMLData{
		Title:        "FeedVault",
		Description:  "FeedVault - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/",
		Content:      "<p>Feeds added.</p>",
		ParseResult:  parseResult,
	}
	html := html.FullHTML(htmlData)
	w.Write([]byte(html))
}
