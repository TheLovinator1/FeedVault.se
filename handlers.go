package main

import (
	"context"
	"io"
	"log"
	"net/http"
	"strconv"

	"strings"

	"github.com/TheLovinator1/FeedVault/db"
)

func ApiHandler(w http.ResponseWriter, _ *http.Request) {
	htmlData := HTMLData{
		Title:        "FeedVault API",
		Description:  "FeedVault API - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive, API",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/api",
		Content:      "<p>Here be dragons.</p>",
	}
	html := FullHTML(htmlData)
	_, err := w.Write([]byte(html))
	if err != nil {
		log.Println("Error writing response:", err)
	}
}

func FeedsHandler(w http.ResponseWriter, _ *http.Request) {
	feeds, err := DB.GetFeeds(context.Background(), db.GetFeedsParams{
		Limit: 100,
	})
	if err != nil {
		log.Println("Error getting feeds:", err)
	}

	fb := strings.Builder{}
	for _, feed := range feeds {
		authors, err := DB.GetFeedAuthors(context.Background(), db.GetFeedAuthorsParams{
			FeedID: feed.ID,
			Limit:  100,
		})
		if err != nil {
			http.Error(w, "Error getting authors", http.StatusInternalServerError)
		}

		extensions, err := DB.GetFeedExtensions(context.Background(), db.GetFeedExtensionsParams{
			FeedID: feed.ID,
			Limit:  100,
		})
		if err != nil {
			log.Println("Error getting extensions:", err)
		}

		// Get the itunes extensions
		itunes, err := DB.GetFeedItunes(context.Background(), feed.ID)
		if err != nil {
			log.Println("Error getting itunes extensions:", err)
		}

		fb.WriteString("<li>")
		fb.WriteString(feed.Title.String)
		fb.WriteString("<ul>")
		for _, author := range authors {
			if author.Name.Valid {
				fb.WriteString("<li>Author: " + author.Name.String + "</li>")
			}
			if author.Email.Valid {
				fb.WriteString("<li>Email: " + author.Email.String + "</li>")
			}
		}

		for _, ext := range extensions {
			if ext.Attrs != nil {
				fb.WriteString("<li>Attrs: " + string(ext.Attrs) + "</li>")
			}
			if ext.Children != nil {
				fb.WriteString("<li>Children: " + string(ext.Children) + "</li>")
			}
			if ext.Name.Valid {
				fb.WriteString("<li>Name: " + ext.Name.String + "</li>")
			}
			if ext.Value.Valid {
				fb.WriteString("<li>Value: " + ext.Value.String + "</li>")
			}
		}

		// Itunes extensions

		fb.WriteString("<ul>")
		if itunes.Author.Valid {
			fb.WriteString("<li>Itunes Author: " + itunes.Author.String + "</li>")
		}
		if itunes.Block.Valid {
			fb.WriteString("<li>Itunes Block: " + itunes.Block.String + "</li>")
		}
		if itunes.Explicit.Valid {
			fb.WriteString("<li>Itunes Explicit: " + itunes.Explicit.String + "</li>")
		}
		if itunes.Image.Valid {
			fb.WriteString("<li>Itunes Image: " + itunes.Image.String + "</li>")
		}
		if itunes.Keywords.Valid {
			fb.WriteString("<li>Itunes Keywords: " + itunes.Keywords.String + "</li>")
		}
		if itunes.Subtitle.Valid {
			fb.WriteString("<li>Itunes Subtitle: " + itunes.Subtitle.String + "</li>")
		}
		if itunes.Summary.Valid {
			fb.WriteString("<li>Itunes Summary: " + itunes.Summary.String + "</li>")
		}
		if itunes.Type.Valid {
			fb.WriteString("<li>Itunes Type: " + itunes.Type.String + "</li>")
		}
		fb.WriteString("</ul>")

		images, err := DB.GetFeedImages(context.Background(), db.GetFeedImagesParams{
			FeedID: feed.ID,
			Limit:  100,
		})
		if err != nil {
			log.Println("Error getting images:", err)
			continue
		}
		for _, image := range images {
			fb.WriteString("<li><img src=\"" + image.Url.String + "\" alt=\"Feed Image\" width=\"256\"></li>")
		}

		fb.WriteString("</ul>")
		fb.WriteString("<a href=\"/feed/" + strconv.FormatInt(feed.ID, 10) + "\">" + feed.Url + "</a>")
		fb.WriteString("</li>")
	}

	htmlData := HTMLData{
		Title:        "FeedVault Feeds",
		Description:  "FeedVault Feeds - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/feeds",
		Content:      "<ul>" + fb.String() + "</ul>",
	}
	html := FullHTML(htmlData)
	_, err = w.Write([]byte(html))
	if err != nil {
		log.Println("Error writing response:", err)
	}
}

func AddFeedHandler(w http.ResponseWriter, r *http.Request) {
	var parseErrors []ParseResult

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
		err := ValidateFeedURL(feed_url)
		if err != nil {
			parseErrors = append(parseErrors, ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
			continue
		}

		err = AddFeedToDB(feed_url)
		if err != nil {
			parseErrors = append(parseErrors, ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
			continue
		}

		// Feed was added successfully
		parseErrors = append(parseErrors, ParseResult{FeedURL: feed_url, Msg: "Added", IsError: false})

	}
	htmlData := HTMLData{
		Title:        "FeedVault",
		Description:  "FeedVault - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/",
		Content:      "<p>Feeds added.</p>",
		ParseResult:  parseErrors,
	}

	html := FullHTML(htmlData)
	_, err = w.Write([]byte(html))
	if err != nil {
		log.Println("Error writing response:", err)
	}

}

func IndexHandler(w http.ResponseWriter, _ *http.Request) {

	content := `<h2>Feeds to archive</h2>
    <p>
        Input the URLs of the feeds you wish to archive below. You can add as many as needed, and access them through the website or API. Alternatively, include links to .opml files, and the feeds within will be archived.
    </p>
    <form action="/add" method="post">
        <textarea id="urls" name="urls" rows="5" cols="50" required></textarea>
        <button type="submit">Add feeds</button>
    </form>
    <br>
    <p>You can also upload .opml files containing the feeds you wish to archive:</p>
    <form enctype="multipart/form-data" method="post" action="/upload_opml">
        <input type="file" name="file" id="file" accept=".opml" required>
        <button type="submit">Upload OPML</button>
    </form>
	`

	FAQ := `

    <h2>FAQ</h2>
    <details>
        <summary>What are web feeds?</summary>
        <p>
            Web feeds are a way to distribute content on the web. They allow users to access updates from websites without having to visit them directly. Feeds are typically used for news websites, blogs, and other sites that frequently update content.
            <br>
            You can read more about web feeds on <a href="https://en.wikipedia.org/wiki/Web_feed">Wikipedia</a>.
        </p>
        <hr>
    </details>
    <details>
        <summary>What is FeedVault?</summary>
        <p>
            FeedVault is a service that archives web  It allows users to access and search for historical content from various websites. The service is designed to preserve the history of the web and provide a reliable source for accessing content that may no longer be available on the original websites.
        </p>
        <hr>
    </details>
    <details>
        <summary>Why archive feeds?</summary>
        <p>
            Web feeds are a valuable source of information, and archiving them ensures that the content is preserved for future reference. By archiving feeds, we can ensure that historical content is available for research, analysis, and other purposes. Additionally, archiving feeds can help prevent the loss of valuable information due to website changes, outages, or other issues.
        </p>
        <hr>
    </details>
    <details>
        <summary>How does it work?</summary>
        <p>
            FeedVault is written in Go and uses the <a href="https://github.com/mmcdole/gofeed">gofeed</a> library to parse  The service periodically checks for new content in the feeds and stores it in a database. Users can access the archived feeds through the website or API.
        <hr>
    </details>
    <details>
        <summary>How can I access the archived feeds?</summary>
        <p>
            You can access the archived feeds through the website or API. The website provides a user interface for searching and browsing the feeds, while the API allows you to access the feeds programmatically. You can also download the feeds in various formats, such as JSON, XML, or RSS.
        </p>
    </details>
	`

	content += FAQ

	htmlData := HTMLData{
		Title:        "FeedVault",
		Description:  "FeedVault - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/",
		Content:      content,
	}
	html := FullHTML(htmlData)
	_, err := w.Write([]byte(html))
	if err != nil {
		log.Println("Error writing response:", err)
	}
}

func UploadOpmlHandler(w http.ResponseWriter, r *http.Request) {
	// Parse the form and get the file
	err := r.ParseMultipartForm(10 << 20) // 10 MB
	if err != nil {
		http.Error(w, "Error parsing form", http.StatusInternalServerError)
		return
	}
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
	parseResult := []ParseResult{}
	links, err := ParseOpml(string(all))
	if err != nil {
		parseResult = append(parseResult, ParseResult{FeedURL: "/upload_opml", Msg: err.Error(), IsError: true})
	} else {
		// Add the feeds to the database
		for _, feed_url := range links.XMLLinks {
			log.Println("Adding feed:", feed_url)

			// Validate the URL
			err := ValidateFeedURL(feed_url)
			if err != nil {
				parseResult = append(parseResult, ParseResult{FeedURL: feed_url, Msg: err.Error(), IsError: true})
				continue
			}

			parseResult = append(parseResult, ParseResult{FeedURL: feed_url, Msg: "Added", IsError: false})
		}
	}

	// Return the results
	htmlData := HTMLData{
		Title:        "FeedVault",
		Description:  "FeedVault - A feed archive",
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/",
		Content:      "<p>Feeds added.</p>",
		ParseResult:  parseResult,
	}
	html := FullHTML(htmlData)
	_, err = w.Write([]byte(html))
	if err != nil {
		log.Println("Error writing response:", err)
	}
}

func FeedHandler(w http.ResponseWriter, r *http.Request) {
	// Get the feed ID from the URL
	parts := strings.Split(r.URL.Path, "/")
	if len(parts) < 3 {
		http.Error(w, "No feed ID provided", http.StatusBadRequest)
		return
	}
	feedID, err := strconv.ParseInt(parts[2], 10, 64)
	if err != nil {
		http.Error(w, "Invalid feed ID", http.StatusBadRequest)
		return
	}

	// Get the feed from the database
	feed, err := DB.GetFeed(context.Background(), feedID)
	if err != nil {
		http.Error(w, "Error getting feed", http.StatusInternalServerError)
		return
	}

	// Get the items for the feed
	items, err := DB.GetItems(context.Background(), db.GetItemsParams{
		FeedID: feedID,
		Limit:  100,
	})
	if err != nil {
		log.Println("Error getting items:", err)
	}

	// Build the HTML
	fb := strings.Builder{}
	for _, item := range items {
		// Get authors for the item
		authors, err := DB.GetItemAuthors(context.Background(), db.GetItemAuthorsParams{
			ItemID: item.ID,
			Limit:  100,
		})
		if err != nil {
			http.Error(w, "Error getting authors", http.StatusInternalServerError)
			return
		}

		// Get extensions for the item
		extensions, err := DB.GetItemExtensions(context.Background(), db.GetItemExtensionsParams{
			ItemID: item.ID,
			Limit:  100,
		})
		if err != nil {
			http.Error(w, "Error getting extensions", http.StatusInternalServerError)
			return
		}

		fb.WriteString("<li>")
		fb.WriteString("<a href=\"" + item.Link.String + "\">" + item.Title.String + "</a>")
		fb.WriteString("<ul>")
		for _, author := range authors {
			fb.WriteString("<li>Author: " + author.Name.String + "</li>")
		}

		for _, ext := range extensions {
			fb.WriteString("<ul>")
			fb.WriteString("<li>Extension: " + ext.Name.String + "</li>")
			if ext.Value.Valid {
				fb.WriteString("<li>Name: " + ext.Value.String + "</li>")
			}
			if ext.Attrs != nil {
				fb.WriteString("<li>Attrs: " + string(ext.Attrs) + "</li>")
			}
			if ext.Children != nil {
				fb.WriteString("<li>Children: " + string(ext.Children) + "</li>")
			}
			fb.WriteString("</ul>")
		}

		// Get images for the item
		images, err := DB.GetItemImages(context.Background(), db.GetItemImagesParams{
			ItemID: item.ID,
			Limit:  100,
		})
		if err != nil {
			http.Error(w, "Error getting images", http.StatusInternalServerError)
			return
		}
		for _, image := range images {
			fb.WriteString("<li><img src=\"" + image.Url.String + "\" alt=\"Feed Image\" width=\"256\"></li>")
		}

		fb.WriteString("</ul>")
		fb.WriteString("<ul>")
		if item.Published.Valid {
			fb.WriteString("<li>Published: " + item.Published.String + "</li>")
		}
		if item.Updated.Valid {
			fb.WriteString("<li>Updated: " + item.Updated.String + "</li>")
		}
		if item.Description.Valid {
			fb.WriteString("<li>" + item.Description.String + "</li>")
		}
		if item.Content.Valid {
			fb.WriteString("<li>" + item.Content.String + "</li>")
		}
		fb.WriteString("</ul>")
		fb.WriteString("<hr>")
		fb.WriteString("</li>")

		// Itunes extensions
		itunes, err := DB.GetItemItunes(context.Background(), item.ID)
		if err != nil {
			log.Println("Error getting itunes extensions:", err)
		}
		fb.WriteString("<ul>")
		if itunes.Author.Valid {
			fb.WriteString("<li>Itunes Author: " + itunes.Author.String + "</li>")
		}
		if itunes.Block.Valid {
			fb.WriteString("<li>Itunes Block: " + itunes.Block.String + "</li>")
		}
		if itunes.Duration.Valid {
			fb.WriteString("<li>Itunes Duration: " + itunes.Duration.String + "</li>")
		}
		if itunes.Explicit.Valid {
			fb.WriteString("<li>Itunes Explicit: " + itunes.Explicit.String + "</li>")
		}
		if itunes.Image.Valid {
			fb.WriteString("<li>Itunes Image: " + itunes.Image.String + "</li>")
		}
		if itunes.Keywords.Valid {
			fb.WriteString("<li>Itunes Keywords: " + itunes.Keywords.String + "</li>")
		}
		if itunes.Subtitle.Valid {
			fb.WriteString("<li>Itunes Subtitle: " + itunes.Subtitle.String + "</li>")
		}
		if itunes.Summary.Valid {
			fb.WriteString("<li>Itunes Summary: " + itunes.Summary.String + "</li>")
		}
		fb.WriteString("</ul>")

	}

	htmlData := HTMLData{
		Title:        feed.Title.String,
		Description:  feed.Description.String,
		Keywords:     "RSS, Atom, Feed, Archive",
		Author:       "TheLovinator",
		CanonicalURL: "http://localhost:8000/feed/" + strconv.FormatInt(feed.ID, 10),
		Content:      "<ul>" + fb.String() + "</ul>",
	}
	html := FullHTML(htmlData)
	_, err = w.Write([]byte(html))
	if err != nil {
		log.Println("Error writing response:", err)
	}
}
