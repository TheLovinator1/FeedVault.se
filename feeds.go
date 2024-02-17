package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/mmcdole/gofeed"
)

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
	log.Printf("Feed added to database")

	// Add the items to the database
	for _, item := range feed.Items {
		addItemToDB(item, ctx, newFeed)
	}

	// Add extensions to the database
	log.Printf("Adding extensions to the database")
	addFeedExtensionToDB(ctx, feed, newFeed)

	// Add authors to the database
	log.Printf("Adding authors to the database")
	addFeedAuthors(ctx, feed, newFeed)

	// TODO: Add categories to the database

	// Add images to the database
	log.Printf("Adding images to the database")
	addFeedImages(ctx, feed, newFeed)

	log.Printf("Feed added to database")
	return nil
}
