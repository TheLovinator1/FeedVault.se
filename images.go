package main

import (
	"context"
	"log"
	"time"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/mmcdole/gofeed"
)

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

func addItemImages(ctx context.Context, item *gofeed.Item, newItem db.Item) {
	_, err := DB.CreateItemImage(ctx, db.CreateItemImageParams{
		CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt: pgtype.Timestamptz{Valid: false},
		Url:       pgtype.Text{String: item.Image.URL, Valid: item.Image.URL != ""},
		Title:     pgtype.Text{String: item.Image.Title, Valid: item.Image.Title != ""},
		ItemID:    newItem.ID,
	})
	if err != nil {
		log.Printf("Error adding image to database: %s", err)
		return
	}
	log.Printf("Image added to database: %s", item.Image.URL)
}
