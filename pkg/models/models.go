package models

import (
	"net/http"

	"github.com/TheLovinator1/FeedVault/pkg/stats"
)

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
	// TODO: Get the feed count from the database
	// TODO: Add amount of entries
	// TODO: Add amount of users
	d.DatabaseSize = stats.GetDBSize()
}
