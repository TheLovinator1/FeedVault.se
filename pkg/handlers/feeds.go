package handlers

import (
	"net/http"
	"strings"

	"github.com/TheLovinator1/FeedVault/pkg/feeds"
	"github.com/TheLovinator1/FeedVault/pkg/html"
	"github.com/TheLovinator1/FeedVault/pkg/models"
	"github.com/TheLovinator1/FeedVault/pkg/validate"
)

func FeedsHandler(w http.ResponseWriter, _ *http.Request) {
	htmlData := html.HTMLData{
		Title:        "FeedVault Feeds",
		Description:  "FeedVault Feeds - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/feeds",
		Content:      "<p>Here be feeds.</p>",
	}
	html := html.FullHTML(htmlData)
	w.Write([]byte(html))
}

func AddFeedHandler(w http.ResponseWriter, r *http.Request) {
	var parseErrors []models.ParseResult

	// Parse the form and get the URLs
	err := r.ParseForm()
	if err != nil {
		http.Error(w, "Error parsing form", http.StatusInternalServerError)
		return
	}

	urls := r.Form.Get("urls")
	if urls == "" {
		http.Error(w, "No URLs provided", http.StatusBadRequest)
		return
	}

	for _, feed_url := range strings.Split(urls, "\n") {
		// TODO: Try to upgrade to https if http is provided

		// Validate the URL
		err := validate.ValidateFeedURL(feed_url)
		if err != nil {
			parseErrors = append(parseErrors, models.ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
			continue
		}

		err = feeds.AddFeedToDB(feed_url)
		if err != nil {
			parseErrors = append(parseErrors, models.ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
			continue
		}

		// Feed was added successfully
		parseErrors = append(parseErrors, models.ParseResult{FeedURL: feed_url, Msg: "Added", IsError: false})

	}
	htmlData := html.HTMLData{
		Title:        "FeedVault",
		Description:  "FeedVault - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/",
		Content:      "<p>Feeds added.</p>",
		ParseResult:  parseErrors,
	}

	html := html.FullHTML(htmlData)
	w.Write([]byte(html))
}
