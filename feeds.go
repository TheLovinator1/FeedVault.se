package main

import (
	"context"
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

func makeCreateItemParams(item *gofeed.Item, feedID int64) db.CreateItemParams {
	itemCustom := []byte("{}")
	if item.Custom != nil {
		var err error
		itemCustom, err = json.Marshal(item.Custom)
		if err != nil {
			fmt.Println("Error marshalling item custom data:", err)
			itemCustom = []byte("{}")
		}
	}

	params := db.CreateItemParams{
		CreatedAt:       pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt:       pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt:       pgtype.Timestamptz{Valid: false},
		Title:           pgtype.Text{String: item.Title, Valid: item.Title != ""},
		Description:     pgtype.Text{String: item.Description, Valid: item.Description != ""},
		Content:         pgtype.Text{String: item.Content, Valid: item.Content != ""},
		Link:            pgtype.Text{String: item.Link, Valid: item.Link != ""},
		Links:           item.Links,
		Updated:         pgtype.Text{String: item.Updated, Valid: item.Updated != ""},
		UpdatedParsed:   pgtype.Timestamp{Time: *item.UpdatedParsed, Valid: item.UpdatedParsed != nil},
		Published:       pgtype.Text{String: item.Published, Valid: item.Published != ""},
		PublishedParsed: pgtype.Timestamp{Time: *item.PublishedParsed, Valid: item.PublishedParsed != nil},
		Guid:            pgtype.Text{String: item.GUID, Valid: item.GUID != ""},
		Categories:      item.Categories,
		Custom:          itemCustom,
		FeedID:          feedID,
	}

	log.Printf("Created item params: %+v", params)

	return params
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
	newFeed, err := DB.CreateFeed(ctx, makeCreateFeedParams(feedURL, feed))
	if err != nil {
		return fmt.Errorf("Error adding feed to database: %s", err)
	}
	log.Printf("Added feed to database: %+v", newFeed)

	// Add the items to the database
	for _, item := range feed.Items {
		_, err := DB.CreateItem(ctx, makeCreateItemParams(item, newFeed.ID))
		if err != nil {
			log.Printf("Error adding item to database: %s", err)
		}
	}

	fmt.Println(feed.Title)
	return nil
}
