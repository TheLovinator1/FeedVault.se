package main

import (
	"encoding/json"
	"fmt"
	"log"
	"time"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/mmcdole/gofeed"
)

func makeCreateFeedParams(feedURL string, feed *gofeed.Feed) db.CreateFeedParams {
	var updatedTime time.Time
	if feed.UpdatedParsed != nil {
		updatedTime = *feed.UpdatedParsed
	}
	var publishedTime time.Time
	if feed.PublishedParsed != nil {
		publishedTime = *feed.PublishedParsed
	}

	feedCustom, err := json.Marshal(feed.Custom)
	if err != nil {
		fmt.Println("Error marshalling feed custom data:", err)
		feedCustom = []byte("{}")
	}

	params := db.CreateFeedParams{
		Url:             feedURL,
		CreatedAt:       pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt:       pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt:       pgtype.Timestamptz{Valid: false},
		Title:           pgtype.Text{String: feed.Title, Valid: feed.Title != ""},
		Description:     pgtype.Text{String: feed.Description, Valid: feed.Description != ""},
		Link:            pgtype.Text{String: feed.Link, Valid: feed.Link != ""},
		FeedLink:        pgtype.Text{String: feed.FeedLink, Valid: feed.FeedLink != ""},
		Links:           feed.Links,
		Updated:         pgtype.Text{String: feed.Updated, Valid: feed.Updated != ""},
		UpdatedParsed:   pgtype.Timestamptz{Time: updatedTime, Valid: !updatedTime.IsZero()},
		Published:       pgtype.Text{String: feed.Published, Valid: feed.Published != ""},
		PublishedParsed: pgtype.Timestamptz{Time: publishedTime, Valid: !publishedTime.IsZero()},
		Language:        pgtype.Text{String: feed.Language, Valid: feed.Language != ""},
		Copyright:       pgtype.Text{String: feed.Copyright, Valid: feed.Copyright != ""},
		Generator:       pgtype.Text{String: feed.Generator, Valid: feed.Generator != ""},
		Categories:      feed.Categories,
		Custom:          feedCustom,
		FeedType:        pgtype.Text{String: feed.FeedType, Valid: feed.FeedType != ""},
		FeedVersion:     pgtype.Text{String: feed.FeedVersion, Valid: feed.FeedVersion != ""},
	}

	log.Printf("Created feed params: %+v", params)

	return params
}
