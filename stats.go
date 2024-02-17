package main

import (
	"context"
	"time"
)

type Cache struct {
	timestamp time.Time
	data      string
}

var cache Cache

func GetDBSize() (string, error) {
	// If the cache is older than 5 minutes, get the database size from the database
	if time.Since(cache.timestamp) > 5*time.Minute {
		dbSize, err := getDBSizeFromDB()
		if err != nil {
			return "", err
		}
		cache = Cache{timestamp: time.Now(), data: dbSize}
	}
	return cache.data, nil
}

func getDBSizeFromDB() (string, error) {
	// Get database size from the PostgreSQL database
	dbSize, err := DB.DBSize(context.Background())
	if err != nil {
		return "", err
	}
	return dbSize, nil
}
