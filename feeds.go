package main

import (
	"context"
	"encoding/json"
	"fmt"
	"time"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/mmcdole/gofeed"
)

func makeCreateFeedParams(feedURL string, feed *gofeed.Feed) db.CreateFeedParams {
	links := make([]string, len(feed.Items))
	for i, item := range feed.Items {
		links[i] = item.Link
	}

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

	return db.CreateFeedParams{
		Url:             feedURL,
		CreatedAt:       pgtype.Timestamp{Time: time.Now(), Valid: true},
		UpdatedAt:       pgtype.Timestamp{Time: time.Now(), Valid: true},
		DeletedAt:       pgtype.Timestamp{Valid: false},
		Title:           pgtype.Text{String: feed.Title, Valid: feed.Title != ""},
		Description:     pgtype.Text{String: feed.Description, Valid: feed.Description != ""},
		Link:            pgtype.Text{String: feed.Link, Valid: feed.Link != ""},
		FeedLink:        pgtype.Text{String: feed.FeedLink, Valid: feed.FeedLink != ""},
		Links:           links,
		Updated:         pgtype.Text{String: feed.Updated, Valid: feed.Updated != ""},
		UpdatedParsed:   pgtype.Timestamp{Time: updatedTime, Valid: !updatedTime.IsZero()},
		Published:       pgtype.Text{String: feed.Published, Valid: feed.Published != ""},
		PublishedParsed: pgtype.Timestamp{Time: publishedTime, Valid: !publishedTime.IsZero()},
		Language:        pgtype.Text{String: feed.Language, Valid: feed.Language != ""},
		Copyright:       pgtype.Text{String: feed.Copyright, Valid: feed.Copyright != ""},
		Generator:       pgtype.Text{String: feed.Generator, Valid: feed.Generator != ""},
		Categories:      feed.Categories,
		Custom:          feedCustom,
		FeedType:        pgtype.Text{String: feed.FeedType, Valid: feed.FeedType != ""},
		FeedVersion:     pgtype.Text{String: feed.FeedVersion, Valid: feed.FeedVersion != ""},
	}
}

func AddFeedToDB(feedURL string) error {
	// Cancel the request after 60 seconds if it hasn't finished
	ctx, cancel := context.WithTimeout(context.Background(), 60*time.Second)
	defer cancel()

	// Parse the feed
	fp := gofeed.NewParser()
	fp.UserAgent = "FeedVault/1.0 (RSS feed archive; https://feedvault.se; bot@feedvault.se; TheLovinator#9276)"

	feed, err := fp.ParseURLWithContext(feedURL, ctx)
	if err != nil {
		return fmt.Errorf("Error parsing feed: %s", err)
	}

	// Add the feed to the database
	_, err = DB.CreateFeed(ctx, makeCreateFeedParams(feedURL, feed))
	if err != nil {
		return fmt.Errorf("Error adding feed to database: %s", err)
	}

	fmt.Println(feed.Title)
	return nil
}
