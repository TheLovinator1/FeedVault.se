package main

import (
	"net/http"
	"time"

	"gorm.io/gorm"
)

type Feed struct {
	gorm.Model
	Title           string               `json:"title,omitempty"`
	Description     string               `json:"description,omitempty"`
	Link            string               `json:"link,omitempty"`
	FeedLink        string               `json:"feedLink,omitempty"`
	Links           []string             `gorm:"type:text[]" json:"links,omitempty"`
	Updated         string               `json:"updated,omitempty"`
	UpdatedParsed   *time.Time           `json:"updatedParsed,omitempty"`
	Published       string               `json:"published,omitempty"`
	PublishedParsed *time.Time           `json:"publishedParsed,omitempty"`
	Authors         []*Person            `gorm:"many2many:feed_authors;" json:"authors,omitempty"`
	Language        string               `json:"language,omitempty"`
	Image           *Image               `gorm:"foreignKey:ID" json:"image,omitempty"`
	Copyright       string               `json:"copyright,omitempty"`
	Generator       string               `json:"generator,omitempty"`
	Categories      []string             `gorm:"type:text[]" json:"categories,omitempty"`
	DublinCoreExt   *DublinCoreExtension `gorm:"foreignKey:ID" json:"dcExt,omitempty"`
	ITunesExt       *ITunesFeedExtension `gorm:"foreignKey:ID" json:"itunesExt,omitempty"`
	Extensions      Extensions           `gorm:"type:json" json:"extensions,omitempty"`
	Custom          map[string]string    `gorm:"type:json" json:"custom,omitempty"`
	Items           []*Item              `gorm:"foreignKey:ID" json:"items,omitempty"`
	FeedType        string               `json:"feedType"`
	FeedVersion     string               `json:"feedVersion"`
}

type Item struct {
	gorm.Model
	Title           string               `json:"title,omitempty"`
	Description     string               `json:"description,omitempty"`
	Content         string               `json:"content,omitempty"`
	Link            string               `json:"link,omitempty"`
	Links           []string             `gorm:"type:text[]" json:"links,omitempty"`
	Updated         string               `json:"updated,omitempty"`
	UpdatedParsed   *time.Time           `json:"updatedParsed,omitempty"`
	Published       string               `json:"published,omitempty"`
	PublishedParsed *time.Time           `json:"publishedParsed,omitempty"`
	Authors         []*Person            `gorm:"many2many:item_authors;" json:"authors,omitempty"`
	GUID            string               `json:"guid,omitempty"`
	Image           *Image               `gorm:"foreignKey:ID" json:"image,omitempty"`
	Categories      []string             `gorm:"type:text[]" json:"categories,omitempty"`
	Enclosures      []*Enclosure         `gorm:"foreignKey:ID" json:"enclosures,omitempty"`
	DublinCoreExt   *DublinCoreExtension `gorm:"foreignKey:ID" json:"dcExt,omitempty"`
	ITunesExt       *ITunesFeedExtension `gorm:"foreignKey:ID" json:"itunesExt,omitempty"`
	Extensions      Extensions           `gorm:"type:json" json:"extensions,omitempty"`
	Custom          map[string]string    `gorm:"type:json" json:"custom,omitempty"`
}

type Person struct {
	gorm.Model
	Name  string `json:"name,omitempty"`
	Email string `json:"email,omitempty"`
}

func (Person) TableName() string {
	return "feed_authors"
}

type Image struct {
	gorm.Model
	URL   string `json:"url,omitempty"`
	Title string `json:"title,omitempty"`
}

type Enclosure struct {
	gorm.Model
	URL    string `json:"url,omitempty"`
	Length string `json:"length,omitempty"`
	Type   string `json:"type,omitempty"`
}

type DublinCoreExtension struct {
	gorm.Model
	Title       []string `gorm:"type:text[]" json:"title,omitempty"`
	Creator     []string `gorm:"type:text[]" json:"creator,omitempty"`
	Author      []string `gorm:"type:text[]" json:"author,omitempty"`
	Subject     []string `gorm:"type:text[]" json:"subject,omitempty"`
	Description []string `gorm:"type:text[]" json:"description,omitempty"`
	Publisher   []string `gorm:"type:text[]" json:"publisher,omitempty"`
	Contributor []string `gorm:"type:text[]" json:"contributor,omitempty"`
	Date        []string `gorm:"type:text[]" json:"date,omitempty"`
	Type        []string `gorm:"type:text[]" json:"type,omitempty"`
	Format      []string `gorm:"type:text[]" json:"format,omitempty"`
	Identifier  []string `gorm:"type:text[]" json:"identifier,omitempty"`
	Source      []string `gorm:"type:text[]" json:"source,omitempty"`
	Language    []string `gorm:"type:text[]" json:"language,omitempty"`
	Relation    []string `gorm:"type:text[]" json:"relation,omitempty"`
	Coverage    []string `gorm:"type:text[]" json:"coverage,omitempty"`
	Rights      []string `gorm:"type:text[]" json:"rights,omitempty"`
}

type ITunesFeedExtension struct {
	gorm.Model
	Author     string            `json:"author,omitempty"`
	Block      string            `json:"block,omitempty"`
	Categories []*ITunesCategory `gorm:"many2many:feed_itunes_categories;" json:"categories,omitempty"`
	Explicit   string            `json:"explicit,omitempty"`
	Keywords   string            `json:"keywords,omitempty"`
	Owner      *ITunesOwner      `gorm:"foreignKey:ID" json:"owner,omitempty"`
	Subtitle   string            `json:"subtitle,omitempty"`
	Summary    string            `json:"summary,omitempty"`
	Image      string            `json:"image,omitempty"`
	Complete   string            `json:"complete,omitempty"`
	NewFeedURL string            `json:"newFeedUrl,omitempty"`
	Type       string            `json:"type,omitempty"`
}

type ITunesItemExtension struct {
	gorm.Model
	Author            string `json:"author,omitempty"`
	Block             string `json:"block,omitempty"`
	Duration          string `json:"duration,omitempty"`
	Explicit          string `json:"explicit,omitempty"`
	Keywords          string `json:"keywords,omitempty"`
	Subtitle          string `json:"subtitle,omitempty"`
	Summary           string `json:"summary,omitempty"`
	Image             string `json:"image,omitempty"`
	IsClosedCaptioned string `json:"isClosedCaptioned,omitempty"`
	Episode           string `json:"episode,omitempty"`
	Season            string `json:"season,omitempty"`
	Order             string `json:"order,omitempty"`
	EpisodeType       string `json:"episodeType,omitempty"`
}

type ITunesCategory struct {
	gorm.Model
	Text        string          `json:"text,omitempty"`
	Subcategory *ITunesCategory `gorm:"many2many:feed_itunes_categories;" json:"subcategory,omitempty"`
}

func (ITunesCategory) TableName() string {
	return "feed_itunes_categories"
}

type ITunesOwner struct {
	gorm.Model
	Email string `json:"email,omitempty"`
	Name  string `json:"name,omitempty"`
}

type Extensions map[string]map[string][]Extension

type Extension struct {
	gorm.Model
	Name     string                 `json:"name"`
	Value    string                 `json:"value"`
	Attrs    map[string]string      `gorm:"type:json" json:"attrs"`
	Children map[string][]Extension `gorm:"type:json" json:"children"`
}

type TemplateData struct {
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

func (d *TemplateData) GetDatabaseSizeAndFeedCount() {
	d.DatabaseSize = GetDBSize()
}

type BadURLs struct {
	gorm.Model
	URL    string `json:"url"`
	Active bool   `json:"active"`
}

type BadURLsMeta struct {
	gorm.Model
	URL         string    `json:"url"`
	LastScraped time.Time `json:"lastScraped"`
}
