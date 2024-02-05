package main

import (
	"fmt"
	"log"
	"os"
	"time"
)

type Cache struct {
	timestamp time.Time
	data      string
}

var cache Cache

// Get the size of the database and return as nearest human readable size.
//
//	e.g. 1.23 KiB, 4.56 MiB, 7.89 GiB, 0.12 TiB
//	The size is cached for 10 minutes
func GetDBSize() string {
	// If cache is less than 10 minutes old, return cached data
	if time.Since(cache.timestamp).Minutes() < 10 {
		return cache.data
	}

	fileInfo, err := os.Stat("feedvault.db")
	if err != nil {
		log.Println("Error getting file info:", err)
		return "0 B"
	}

	// Get the file size in bytes
	fileSize := fileInfo.Size()

	// Convert to human readable size and append the unit (KiB, MiB, GiB, TiB)
	var size float64
	if fileSize < 1024*1024 {
		size = float64(fileSize) / 1024
		cache.data = fmt.Sprintf("%.2f KiB", size)
	} else if fileSize < 1024*1024*1024 {
		size = float64(fileSize) / (1024 * 1024)
		cache.data = fmt.Sprintf("%.2f MiB", size)
	} else if fileSize < 1024*1024*1024*1024 {
		size = float64(fileSize) / (1024 * 1024 * 1024)
		cache.data = fmt.Sprintf("%.2f GiB", size)
	} else {
		size = float64(fileSize) / (1024 * 1024 * 1024 * 1024)
		cache.data = fmt.Sprintf("%.2f TiB", size)
	}

	// Update cache timestamp
	cache.timestamp = time.Now()

	log.Println("Returning database size, it is", cache.data)

	return cache.data
}
