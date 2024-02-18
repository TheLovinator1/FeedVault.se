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

	// Add images to the database
	if item.Image != nil {
		addItemImages(ctx, item, newItem)
	}

	// Add Dublin Core to the database
	createItemDublinCore(ctx, item, newItem)

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
