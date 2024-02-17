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

func addItemToDB(item *gofeed.Item, ctx context.Context, newFeed db.Feed) {
	newItem, err := DB.CreateItem(ctx, makeCreateItemParams(item, newFeed.ID))
	if err != nil {
		log.Printf("Error adding item to database: %s", err)
	}

	// Add extensions to the database
	addItemExtensionToDB(ctx, item, newItem)

	// Add authors to the database
	addItemAuthors(ctx, item, newItem)

	log.Printf("Item added to database")
}

func makeCreateItemParams(item *gofeed.Item, feedID int64) db.CreateItemParams {
	var updatedTime time.Time
	if item.UpdatedParsed != nil {
		updatedTime = *item.UpdatedParsed
	}
	var publishedTime time.Time
	if item.PublishedParsed != nil {
		publishedTime = *item.PublishedParsed
	}

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
		UpdatedParsed:   pgtype.Timestamptz{Time: updatedTime, Valid: !updatedTime.IsZero()},
		Published:       pgtype.Text{String: item.Published, Valid: item.Published != ""},
		PublishedParsed: pgtype.Timestamptz{Time: publishedTime, Valid: !publishedTime.IsZero()},
		Guid:            pgtype.Text{String: item.GUID, Valid: item.GUID != ""},
		Categories:      item.Categories,
		Custom:          itemCustom,
		FeedID:          feedID,
	}

	log.Printf("Created item params: %+v", params)

	return params
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
					log.Printf("Extension attributes: %s", attrsCustom)
				}

				childrenCustom := []byte("{}")
				if e.Children != nil {
					var err error
					childrenCustom, err = json.Marshal(e.Children)
					if err != nil {
						fmt.Println("Error marshalling extension children:", err)
						childrenCustom = []byte("{}")
					}
					log.Printf("Extension children: %s", childrenCustom)
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
				}

				log.Printf("Extension added to database")
			}
		}
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
		}
		log.Printf("Author %s (%s) added to database", author.Name, author.Email)
	}
}
