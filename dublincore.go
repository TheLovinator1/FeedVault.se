package main

import (
	"context"
	"log"
	"time"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/mmcdole/gofeed"
)

func createFeedDublinCore(ctx context.Context, feed *gofeed.Feed, newFeed db.Feed) {
	// TODO: Check if this is correct and works. I can't find a feed that has Dublin Core to test with :-)
	if feed.DublinCoreExt == nil {
		log.Printf("No Dublin Core to add to database")
		return
	}

	// Add Dublin Core to the database
	_, err := DB.CreateFeedDublinCore(ctx, db.CreateFeedDublinCoreParams{
		CreatedAt:   pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt:   pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt:   pgtype.Timestamptz{Valid: false},
		Title:       feed.DublinCoreExt.Title,
		Creator:     feed.DublinCoreExt.Creator,
		Subject:     feed.DublinCoreExt.Subject,
		Source:      feed.DublinCoreExt.Source,
		Publisher:   feed.DublinCoreExt.Publisher,
		Contributor: feed.DublinCoreExt.Contributor,
		Description: feed.DublinCoreExt.Description,
		Date:        feed.DublinCoreExt.Date,
		Type:        feed.DublinCoreExt.Type,
		Format:      feed.DublinCoreExt.Format,
		Identifier:  feed.DublinCoreExt.Identifier,
		Language:    feed.DublinCoreExt.Language,
		Relation:    feed.DublinCoreExt.Relation,
		Coverage:    feed.DublinCoreExt.Coverage,
		Rights:      feed.DublinCoreExt.Rights,
		FeedID:      newFeed.ID,
	})

	if err != nil {
		log.Printf("Error adding Dublin Core to database: %s", err)
		return
	}
	log.Printf("Dublin Core added to database")
}

func createItemDublinCore(ctx context.Context, item *gofeed.Item, newItem db.Item) {
	if item.DublinCoreExt == nil {
		log.Printf("No Dublin Core to add to database")
		return
	}

	// Add Dublin Core to the database
	_, err := DB.CreateItemDublinCore(ctx, db.CreateItemDublinCoreParams{
		CreatedAt:   pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt:   pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt:   pgtype.Timestamptz{Valid: false},
		Title:       item.DublinCoreExt.Title,
		Creator:     item.DublinCoreExt.Creator,
		Subject:     item.DublinCoreExt.Subject,
		Source:      item.DublinCoreExt.Source,
		Publisher:   item.DublinCoreExt.Publisher,
		Contributor: item.DublinCoreExt.Contributor,
		Description: item.DublinCoreExt.Description,
		Date:        item.DublinCoreExt.Date,
		Type:        item.DublinCoreExt.Type,
		Format:      item.DublinCoreExt.Format,
		Identifier:  item.DublinCoreExt.Identifier,
		Language:    item.DublinCoreExt.Language,
		Relation:    item.DublinCoreExt.Relation,
		Coverage:    item.DublinCoreExt.Coverage,
		Rights:      item.DublinCoreExt.Rights,
		ItemID:      newItem.ID,
	})

	if err != nil {
		log.Printf("Error adding Dublin Core to database: %s", err)
		return
	}
	log.Printf("Dublin Core added to database")
}
