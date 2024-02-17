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

func addFeedExtensionToDB(ctx context.Context, feed *gofeed.Feed, newFeed db.Feed) {
	// Add extensions to the database
	// TODO: Check if this is correct and works
	for _, ext := range feed.Extensions {
		for _, exts := range ext {
			for _, e := range exts {
				attrsCustom := []byte("{}")
				if e.Attrs != nil {
					var err error
					attrsCustom, err = json.Marshal(e.Attrs)
					if err != nil {
						fmt.Println("Error marshalling extension attributes:", err)
						attrsCustom = []byte("{}")
					}
				}

				childrenCustom := []byte("{}")
				if e.Children != nil {
					var err error
					childrenCustom, err = json.Marshal(e.Children)
					if err != nil {
						fmt.Println("Error marshalling extension children:", err)
						childrenCustom = []byte("{}")
					}
				}

				_, err := DB.CreateFeedExtension(ctx, db.CreateFeedExtensionParams{
					CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
					UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
					DeletedAt: pgtype.Timestamptz{Valid: false},
					Name:      pgtype.Text{String: e.Name, Valid: e.Name != ""},
					Value:     pgtype.Text{String: e.Value, Valid: e.Value != ""},
					Attrs:     attrsCustom,
					Children:  childrenCustom,
					FeedID:    newFeed.ID,
				})

				if err != nil {
					log.Printf("Error adding extension to database: %s", err)
				}
			}
		}
	}
}

func addFeedAuthors(ctx context.Context, feed *gofeed.Feed, newFeed db.Feed) {
	if feed.Authors == nil {
		log.Printf("No authors to add to database")
		return
	}

	// Add authors to the database
	for _, author := range feed.Authors {
		_, err := DB.CreateFeedAuthor(ctx, db.CreateFeedAuthorParams{
			CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
			UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
			DeletedAt: pgtype.Timestamptz{Valid: false},
			Name:      pgtype.Text{String: author.Name, Valid: author.Name != ""},
			FeedID:    newFeed.ID,
		})
		if err != nil {
			log.Printf("Error adding author %s (%s) to database: %s", author.Name, author.Email, err)
			continue
		}
		log.Printf("Author %s (%s) added to database", author.Name, author.Email)
	}
}

func addFeedImages(ctx context.Context, feed *gofeed.Feed, newFeed db.Feed) {
	if feed.Image == nil {
		log.Printf("No image to add to database")
		return
	}

	// TODO: Download the image and store it on the server
	_, err := DB.CreateFeedImage(ctx, db.CreateFeedImageParams{
		CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt: pgtype.Timestamptz{Valid: false},
		Url:       pgtype.Text{String: feed.Image.URL, Valid: feed.Image.URL != ""},
		Title:     pgtype.Text{String: feed.Image.Title, Valid: feed.Image.Title != ""},
		FeedID:    newFeed.ID,
	})
	if err != nil {
		log.Printf("Error adding image to database: %s", err)
		return
	}
	log.Printf("Image added to database: %s", feed.Image.URL)
}
