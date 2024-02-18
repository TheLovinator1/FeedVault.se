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

func addItemExtensionToDB(ctx context.Context, item *gofeed.Item, newItem db.Item) {
	// Add extensions to the database
	for _, ext := range item.Extensions {
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

				_, err := DB.CreateItemExtension(ctx, db.CreateItemExtensionParams{
					CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
					UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
					DeletedAt: pgtype.Timestamptz{Valid: false},
					Name:      pgtype.Text{String: e.Name, Valid: e.Name != ""},
					Value:     pgtype.Text{String: e.Value, Valid: e.Value != ""},
					Attrs:     attrsCustom,
					Children:  childrenCustom,
					ItemID:    newItem.ID,
				})

				if err != nil {
					log.Printf("Error adding extension to database: %s", err)
					continue
				}

				log.Printf("Extension added to database")
			}
		}
	}
}
