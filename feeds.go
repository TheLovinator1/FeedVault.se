package main

import (
	"context"
	"fmt"
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

	fmt.Println(feed.Title)
	return nil
}
