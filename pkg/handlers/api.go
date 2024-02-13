package handlers

import (
	"net/http"

	"github.com/TheLovinator1/FeedVault/pkg/html"
)

func ApiHandler(w http.ResponseWriter, _ *http.Request) {
	htmlData := html.HTMLData{
		Title:        "FeedVault API",
		Description:  "FeedVault API - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive, API",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/api",
		Content:      "<p>Here be dragons.</p>",
	}
	html := html.FullHTML(htmlData)
	w.Write([]byte(html))
}
