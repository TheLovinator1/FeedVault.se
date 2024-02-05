package main

import "testing"

var opmlExample = `<?xml version="1.0" encoding="utf-8"?>
<opml version="1.0">
	<head>
		<title>My Feeds</title>
	</head>
	<body>
		<outline text="24 ways" htmlUrl="http://24ways.org/" type="rss" xmlUrl="http://feeds.feedburner.com/24ways"/>
		<outline text="Writing — by Jan" htmlUrl="http://writing.jan.io/" type="rss" xmlUrl="http://writing.jan.io/feed.xml"/>
	</body>
</opml> 
`

var secondOpmlExample = `<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
  <head>
    <title>Engineering Blogs</title>
  </head>
  <body>
    <outline text="Engineering Blogs" title="Engineering Blogs">
      <outline type="rss" text="8th Light" title="8th Light" xmlUrl="https://8thlight.com/blog/feed/atom.xml" htmlUrl="https://8thlight.com/blog/"/>
      <outline type="rss" text="A" title="A" xmlUrl="http://www.vertabelo.com/_rss/blog.xml" htmlUrl="http://www.vertabelo.com/blog"/>
    </outline>
  </body>
</opml>
`

// Test the opml parser
func TestParseOpml(t *testing.T) {
	links, err := ParseOpml(opmlExample)
	if err != nil {
		t.Error(err)
	}
	if len(links.XMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.XMLLinks))
	}
	if len(links.HTMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.HTMLLinks))
	}

	// Test that the links are unique
	links.XMLLinks = removeDuplicates(links.XMLLinks)
	links.HTMLLinks = removeDuplicates(links.HTMLLinks)
	if len(links.XMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.XMLLinks))
	}
	if len(links.HTMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.HTMLLinks))
	}

	// Test that the links are correct
	if links.XMLLinks[0] != "http://feeds.feedburner.com/24ways" {
		t.Errorf("Expected http://feeds.feedburner.com/24ways, got %s", links.XMLLinks[0])
	}
	if links.XMLLinks[1] != "http://writing.jan.io/feed.xml" {
		t.Errorf("Expected http://writing.jan.io/feed.xml, got %s", links.XMLLinks[1])
	}
	if links.HTMLLinks[0] != "http://24ways.org/" {
		t.Errorf("Expected http://24ways.org/, got %s", links.HTMLLinks[0])
	}
	if links.HTMLLinks[1] != "http://writing.jan.io/" {
		t.Errorf("Expected http://writing.jan.io/, got %s", links.HTMLLinks[1])
	}

}

// Test the opml parser with nested outlines
func TestParseOpmlNested(t *testing.T) {
	links, err := ParseOpml(secondOpmlExample)
	if err != nil {
		t.Error(err)
	}
	if len(links.XMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.XMLLinks))
	}
	if len(links.HTMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.HTMLLinks))
	}

	// Test that the links are unique
	links.XMLLinks = removeDuplicates(links.XMLLinks)
	links.HTMLLinks = removeDuplicates(links.HTMLLinks)
	if len(links.XMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.XMLLinks))
	}
	if len(links.HTMLLinks) != 2 {
		t.Errorf("Expected 2 links, got %d", len(links.HTMLLinks))
	}

	// Test that the links are correct
	if links.XMLLinks[0] != "https://8thlight.com/blog/feed/atom.xml" {
		t.Errorf("Expected https://8thlight.com/blog/feed/atom.xml, got %s", links.XMLLinks[0])
	}
	if links.XMLLinks[1] != "http://www.vertabelo.com/_rss/blog.xml" {
		t.Errorf("Expected http://www.vertabelo.com/_rss/blog.xml, got %s", links.XMLLinks[1])
	}
	if links.HTMLLinks[0] != "https://8thlight.com/blog/" {
		t.Errorf("Expected https://8thlight.com/blog/, got %s", links.HTMLLinks[0])
	}
	if links.HTMLLinks[1] != "http://www.vertabelo.com/blog" {
		t.Errorf("Expected http://www.vertabelo.com/blog, got %s", links.HTMLLinks[1])
	}

}
