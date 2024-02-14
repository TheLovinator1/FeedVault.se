package main

import "encoding/xml"

type opml struct {
	Head struct {
		Title string `xml:"title"`
	} `xml:"head"`
	Body Body `xml:"body"`
}

type Body struct {
	Outlines []Outline `xml:"outline"`
}

type Outline struct {
	Outlines []Outline `xml:"outline"`
	XmlUrl   string    `xml:"xmlUrl,attr,omitempty"`
	HtmlUrl  string    `xml:"htmlUrl,attr,omitempty"`
}

func (o *opml) ParseString(s string) error {
	return xml.Unmarshal([]byte(s), o)
}

func (o *opml) String() (string, error) {
	b, err := xml.Marshal(o)
	if err != nil {
		return "", err
	}
	return xml.Header + string(b), nil
}

type linksFromOpml struct {
	XMLLinks  []string `json:"xmlLinks"`
	HTMLLinks []string `json:"htmlLinks"`
}

func RemoveDuplicates(s []string) []string {
	seen := make(map[string]struct{}, len(s))
	j := 0
	for _, v := range s {
		if _, ok := seen[v]; ok {
			continue
		}
		seen[v] = struct{}{}
		s[j] = v
		j++
	}
	return s[:j]
}

func ParseOpml(s string) (linksFromOpml, error) {
	// Get all the feeds from the OPML and return them as linksFromOpml
	opml := &opml{}
	err := opml.ParseString(s)
	if err != nil {
		return linksFromOpml{}, err
	}

	links := linksFromOpml{}
	for _, outline := range opml.Body.Outlines {
		links.XMLLinks = append(links.XMLLinks, outline.XmlUrl)
		links.HTMLLinks = append(links.HTMLLinks, outline.HtmlUrl)
	}

	// Also check outlines for nested outlines
	for _, outline := range opml.Body.Outlines {
		for _, nestedOutline := range outline.Outlines {
			links.XMLLinks = append(links.XMLLinks, nestedOutline.XmlUrl)
			links.HTMLLinks = append(links.HTMLLinks, nestedOutline.HtmlUrl)
		}
	}

	// Remove any empty strings
	for i := 0; i < len(links.XMLLinks); i++ {
		if links.XMLLinks[i] == "" {
			links.XMLLinks = append(links.XMLLinks[:i], links.XMLLinks[i+1:]...)
			i--
		}
	}
	for i := 0; i < len(links.HTMLLinks); i++ {
		if links.HTMLLinks[i] == "" {
			links.HTMLLinks = append(links.HTMLLinks[:i], links.HTMLLinks[i+1:]...)
			i--
		}
	}

	// Remove any duplicates
	links.XMLLinks = RemoveDuplicates(links.XMLLinks)
	links.HTMLLinks = RemoveDuplicates(links.HTMLLinks)

	return links, nil
}
