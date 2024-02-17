package main

import (
	"context"
	"fmt"
	"log"
	"math/rand"
	"strings"
)

// Used for success/error message at the top of the page after adding a feed.
type ParseResult struct {
	FeedURL string
	Msg     string
	IsError bool
}

// HTMLData is the data passed to the HTML template.
type HTMLData struct {
	Title        string
	Description  string
	Keywords     string
	Author       string
	CanonicalURL string
	Content      string
	ParseResult  []ParseResult
}

// Our CSS that is included in the HTML.
var style = `
html {
	max-width: 70ch;
	padding: calc(1vmin + 0.5rem);
	margin-inline: auto;
	font-size: clamp(1em, 0.909em + 0.45vmin, 1.25em);
	font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
	color-scheme: light dark;
}

h1 {
	font-size: 2.5rem;
	font-weight: 600;
	margin: 0;
}

.title {
	text-align: center;
}

.search {
	display: flex;
	justify-content: center;
	margin-top: 1rem;
	margin-inline: auto;
}

.leftright {
	display: flex;
	justify-content: center;
}

.left {
	margin-right: auto;
}

.right {
	margin-left: auto;
}

textarea {
	width: 100%;
	height: 10rem;
	resize: vertical;
}

.messages {
	list-style-type: none;
}

.error {
	color: red;
}

.success {
	color: green;
}
`

const (
	// errorListItem is shown after adding a feed. It shows if error or success.
	errorListItem = `<li class="%s"><a href="%s">%s</a> - %s</li>`

	// htmlTemplate is the HTML template for the entire page.
	htmlTemplate = `<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="%s">
        <meta name="keywords" content="%s">
        <meta name="author" content="%s">
        <link rel="canonical" href="%s">
        <title>%s</title>
        <style>%s</style>
    </head>
    <body>
    %s
    <span class="title"><h1><a href="/">FeedVault</a></h1></span>
    <div class="leftright">
        <div class="left">
            <small>Archive of <a href="https://en.wikipedia.org/wiki/Web_feed">web feeds</a>. %d feeds. ~%s.</small>
        </div>
        <div class="right">
            <form action="#" method="get">
                <input type="text" name="q" placeholder="Search">
                <button type="submit">Search</button>
            </form>
        </div>
    </div>
    <nav>
        <small>
            <div class="leftright">
                <div class="left">
                    <a href="/">Home</a> | <a href="/feeds">Feeds</a> | <a href="/api">API</a> 
                </div>
                <div class="right">
                    <a href="https://github.com/TheLovinator1/FeedVault">GitHub</a> | <a href="https://github.com/sponsors/TheLovinator1">Donate</a>
                </div>
            </div>
        </small>
    </nav>
    <hr>
    <main>
    %s
    </main>
    <hr>
    <footer>
        <small>
            <div class="leftright">
                <div class="left">
                    Made by <a href="">Joakim Hellsén</a>.
                </div>
                <div class="right">No rights reserved.</div>
            </div>
            <div class="leftright">
                <div class="left">
                    <a href="mailto:hello@feedvault.se">hello@feedvault.se</a>
                </div>
                <div class="right">
                    %s
                </div>
            </div>
        </small>
    </footer>
    </body>
    </html>`
)

func buildErrorList(parseResults []ParseResult) string {
	var errorBuilder strings.Builder
	if len(parseResults) > 0 {
		errorBuilder.WriteString("<ul>")
		for _, result := range parseResults {
			// CSS class for the list item. Green for success, red for error.
			listItemClass := "success"
			if result.IsError {
				listItemClass = "error"
			}
			errorBuilder.WriteString(fmt.Sprintf(errorListItem, listItemClass, result.FeedURL, result.FeedURL, result.Msg))
		}
		errorBuilder.WriteString("</ul>")
	}
	return errorBuilder.String()
}

func FullHTML(h HTMLData) string {
	statusMsg := buildErrorList(h.ParseResult)

	feedCount, err := DB.CountFeeds(context.Background())
	if err != nil {
		log.Fatalf("DB.CountFeeds(): %v", err)
		feedCount = 0
	}

	databaseSize, err := GetDBSize()
	if err != nil {
		databaseSize = "0 KiB"
		log.Println("Error getting database size:", err)
	}

	funMsg := FunMsg[rand.Intn(len(FunMsg))]
	return fmt.Sprintf(htmlTemplate, h.Description, h.Keywords, h.Author, h.CanonicalURL, h.Title, style, statusMsg, feedCount, databaseSize, h.Content, funMsg)
}
