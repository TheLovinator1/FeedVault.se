package main

import (
	"fmt"
	"strings"

	"github.com/tdewolff/minify/v2"
	"github.com/tdewolff/minify/v2/css"
	"github.com/tdewolff/minify/v2/html"
)

type HTMLData struct {
	Title        string
	Description  string
	Keywords     string
	Author       string
	CanonicalURL string
	Content      string
}

func minifyHTML(h string) string {
	m := minify.New()
	m.AddFunc("text/html", html.Minify)
	minified, err := m.String("text/html", h)
	if err != nil {
		return h
	}
	return minified
}

func minifyCSS(h string) string {
	m := minify.New()
	m.AddFunc("text/css", css.Minify)
	minified, err := m.String("text/css", h)
	if err != nil {
		return h
	}
	return minified
}

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

func fullHTML(h HTMLData, ParseResult []ParseResult) string {
	var sb strings.Builder
	var errorBuilder strings.Builder

	FeedCount := 0
	DatabaseSize := GetDBSize()

	// This is the error message that will be displayed if there are any errors
	if len(ParseResult) > 0 {
		errorBuilder.WriteString("<h2>Results</h2><ul>")
		for _, result := range ParseResult {
			var listItemClass, statusMsg string
			if result.IsError {
				listItemClass = "error"
				statusMsg = result.Msg
			} else {
				listItemClass = "success"
				statusMsg = result.Msg
			}
			errorBuilder.WriteString(fmt.Sprintf(`<li class="%s"><a href="%s">%s</a> - %s</li>`, listItemClass, result.FeedURL, result.FeedURL, statusMsg))
		}
		errorBuilder.WriteString("</ul>")
	}
	StatusMsg := errorBuilder.String()

	sb.WriteString(`
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
	`)

	if h.Description != "" {
		sb.WriteString(`<meta name="description" content="` + h.Description + `">`)
	}

	if h.Keywords != "" {
		sb.WriteString(`<meta name="keywords" content="` + h.Keywords + `">`)
	}

	if h.Author != "" {
		sb.WriteString(`<meta name="author" content="` + h.Author + `">`)
	}

	if h.CanonicalURL != "" {
		sb.WriteString(`<link rel="canonical" href="` + h.CanonicalURL + `">`)
	}

	sb.WriteString(`
		<title>` + h.Title + `</title>
		<style>` + minifyCSS(style) + `</style>
	</head>
	<body>
	` + StatusMsg + `
    <span class="title"><h1><a href="/">FeedVault</a></h1></span>
    <div class="leftright">
        <div class="left">
            <small>Archive of <a href="https://en.wikipedia.org/wiki/Web_feed">web feeds</a>. ` + fmt.Sprintf("%d", FeedCount) + ` feeds. ~` + DatabaseSize + `.</small>
        </div>
        <div class="right">
            <!-- Search -->
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
                    <a href="/feeds">Feeds</a> | <a href="/api">API</a> | <a href="/export">Export</a> | <a href="/stats">Stats</a>
                </div>
                <div class="right">
                    <a href="https://github.com/TheLovinator1/FeedVault">GitHub</a> | <a href="https://github.com/sponsors/TheLovinator1">Donate</a>
                </div>
            </div>
        </small>
    </nav>
    <hr>
	<main>
	` + h.Content + `
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
                    Web scraping is not a crime.
                </div>
            </div>
        </small>
    </footer>
	</body>
	</html>`)

	return minifyHTML(sb.String())

}
