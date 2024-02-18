package main

import (
	"context"
	"log"
	"time"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/mmcdole/gofeed"
)

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

func addItemAuthors(ctx context.Context, item *gofeed.Item, newItem db.Item) {
	for _, author := range item.Authors {
		_, err := DB.CreateItemAuthor(ctx, db.CreateItemAuthorParams{
			CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
			UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
			DeletedAt: pgtype.Timestamptz{Valid: false},
			Name:      pgtype.Text{String: author.Name, Valid: author.Name != ""},
			Email:     pgtype.Text{String: author.Email, Valid: author.Email != ""},
			ItemID:    newItem.ID,
		})

		if err != nil {
			log.Printf("Error adding author %s (%s) to database: %s", author.Name, author.Email, err)
			continue
		}
		log.Printf("Author %s (%s) added to database", author.Name, author.Email)
	}
}
