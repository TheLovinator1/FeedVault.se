package main

import (
	"context"
	"log"
	"time"

	"github.com/TheLovinator1/FeedVault/db"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/mmcdole/gofeed"
)

func createFeedItunes(ctx context.Context, feed *gofeed.Feed, newFeed db.Feed) (db.FeedItune, error) {
	if feed.ITunesExt == nil {
		log.Printf("No iTunes extensions to add to database")
		return db.FeedItune{}, nil
	}

	// Add iTunes extensions to the database
	itunesID, err := DB.CreateFeedItunes(ctx, db.CreateFeedItunesParams{
		CreatedAt:  pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt:  pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt:  pgtype.Timestamptz{Valid: false},
		Author:     pgtype.Text{String: feed.ITunesExt.Author, Valid: feed.ITunesExt.Author != ""},
		Block:      pgtype.Text{String: feed.ITunesExt.Block, Valid: feed.ITunesExt.Block != ""},
		Explicit:   pgtype.Text{String: feed.ITunesExt.Explicit, Valid: feed.ITunesExt.Explicit != ""},
		Keywords:   pgtype.Text{String: feed.ITunesExt.Keywords, Valid: feed.ITunesExt.Keywords != ""},
		Subtitle:   pgtype.Text{String: feed.ITunesExt.Subtitle, Valid: feed.ITunesExt.Subtitle != ""},
		Summary:    pgtype.Text{String: feed.ITunesExt.Summary, Valid: feed.ITunesExt.Summary != ""},
		Image:      pgtype.Text{String: feed.ITunesExt.Image, Valid: feed.ITunesExt.Image != ""},
		Complete:   pgtype.Text{String: feed.ITunesExt.Complete, Valid: feed.ITunesExt.Complete != ""},
		NewFeedUrl: pgtype.Text{String: feed.ITunesExt.NewFeedURL, Valid: feed.ITunesExt.NewFeedURL != ""},
		Type:       pgtype.Text{String: feed.ITunesExt.Type, Valid: feed.ITunesExt.Type != ""},
		FeedID:     newFeed.ID,
	})
	if err != nil {
		log.Printf("Error adding iTunes extensions to database: %s", err)
		return db.FeedItune{}, err
	}
	log.Printf("iTunes extensions added to database")
	return itunesID, nil
}

func createItemItunes(ctx context.Context, item *gofeed.Item, newItem db.Item) (db.ItemItune, error) {
	if item.ITunesExt == nil {
		log.Printf("No iTunes extensions to add to database")
		return db.ItemItune{}, nil
	}

	// Add iTunes extensions to the database
	itunesID, err := DB.CreateItemItunes(ctx, db.CreateItemItunesParams{
		CreatedAt:         pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt:         pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt:         pgtype.Timestamptz{Valid: false},
		Author:            pgtype.Text{String: item.ITunesExt.Author, Valid: item.ITunesExt.Author != ""},
		Block:             pgtype.Text{String: item.ITunesExt.Block, Valid: item.ITunesExt.Block != ""},
		Explicit:          pgtype.Text{String: item.ITunesExt.Explicit, Valid: item.ITunesExt.Explicit != ""},
		Keywords:          pgtype.Text{String: item.ITunesExt.Keywords, Valid: item.ITunesExt.Keywords != ""},
		Subtitle:          pgtype.Text{String: item.ITunesExt.Subtitle, Valid: item.ITunesExt.Subtitle != ""},
		Summary:           pgtype.Text{String: item.ITunesExt.Summary, Valid: item.ITunesExt.Summary != ""},
		Image:             pgtype.Text{String: item.ITunesExt.Image, Valid: item.ITunesExt.Image != ""},
		IsClosedCaptioned: pgtype.Text{String: item.ITunesExt.IsClosedCaptioned, Valid: item.ITunesExt.IsClosedCaptioned != ""},
		Episode:           pgtype.Text{String: item.ITunesExt.Episode, Valid: item.ITunesExt.Episode != ""},
		Season:            pgtype.Text{String: item.ITunesExt.Season, Valid: item.ITunesExt.Season != ""},
		Order:             pgtype.Text{String: item.ITunesExt.Order, Valid: item.ITunesExt.Order != ""},
		EpisodeType:       pgtype.Text{String: item.ITunesExt.EpisodeType, Valid: item.ITunesExt.EpisodeType != ""},
		ItemID:            newItem.ID,
	})
	if err != nil {
		log.Printf("Error adding iTunes extensions to database: %s", err)
		return db.ItemItune{}, err
	}
	log.Printf("iTunes extensions added to database")
	return itunesID, nil
}

func createFeedItunesCategories(ctx context.Context, feed *gofeed.Feed, itunes db.FeedItune) {
	if feed.ITunesExt == nil {
		log.Printf("No iTunes categories to add to database")
		return
	}
	for _, cat := range feed.ITunesExt.Categories {
		newCat, err := DB.CreateFeedItunesCategory(ctx, db.CreateFeedItunesCategoryParams{
			CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
			UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
			DeletedAt: pgtype.Timestamptz{Valid: false},
			Text:      pgtype.Text{String: cat.Text, Valid: cat.Text != ""}, // 🐈 meow
			ItunesID:  itunes.ID,
		})
		if err != nil {
			log.Printf("Error adding iTunes category to database: %s", err)
			continue
		}
		log.Printf("iTunes category added to database: %s", cat.Text)

		// Add subcategories to the database
		if cat.Subcategory != nil {
			_, err = DB.CreateFeedItunesCategory(ctx, db.CreateFeedItunesCategoryParams{
				CreatedAt:   pgtype.Timestamptz{Time: time.Now(), Valid: true},
				UpdatedAt:   pgtype.Timestamptz{Time: time.Now(), Valid: true},
				DeletedAt:   pgtype.Timestamptz{Valid: false},
				Text:        pgtype.Text{String: cat.Subcategory.Text, Valid: cat.Subcategory.Text != ""}, // 🐈 meow
				ItunesID:    itunes.ID,
				Subcategory: pgtype.Int8{Int64: newCat.ID, Valid: true},
			})
			if err != nil {
				log.Printf("Error adding iTunes subcategory to database: %s", err)
				continue
			}
			log.Printf("iTunes subcategory added to database: %s", cat.Text)
		}
	}
}

func createFeedItunesOwners(ctx context.Context, feed *gofeed.Feed, itunes db.FeedItune) {
	if feed.ITunesExt == nil {
		log.Printf("No iTunes owners to add to database")
		return
	}
	if feed.ITunesExt.Owner == nil {
		log.Printf("No iTunes owner to add to database")
		return
	}

	_, err := DB.CreateFeedItunesOwner(ctx, db.CreateFeedItunesOwnerParams{
		CreatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		UpdatedAt: pgtype.Timestamptz{Time: time.Now(), Valid: true},
		DeletedAt: pgtype.Timestamptz{Valid: false},
		Name:      pgtype.Text{String: feed.ITunesExt.Owner.Name, Valid: feed.ITunesExt.Owner.Name != ""},
		Email:     pgtype.Text{String: feed.ITunesExt.Owner.Email, Valid: feed.ITunesExt.Owner.Email != ""},
		ItunesID:  itunes.ID,
	})
	if err != nil {
		log.Printf("Error adding iTunes owner to database: %s", err)
		return
	}
	log.Printf("iTunes owner added to database: %s", feed.ITunesExt.Owner.Name)
}
