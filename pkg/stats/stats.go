package stats

import (
	"fmt"
	"os"
	"time"
)

type Cache struct {
	timestamp time.Time
	data      string
}

var cache Cache

func GetDBSize() (string, error) {
	// If cache is less than 10 minutes old, return cached data
	if time.Since(cache.timestamp).Minutes() < 10 {
		return cache.data, nil
	}

	// TODO: This should be read from the environment
	fileInfo, err := os.Stat("feedvault.db")
	if err != nil {
		return "", err
	}

	// Get the file size in bytes
	fileSize := fileInfo.Size()

	// Convert to human readable size and append the unit (KiB, MiB, GiB, TiB)
	var size float64

	if fileSize < 1024*1024 {
		// If the file size is less than 1 KiB, return the size in bytes
		size = float64(fileSize) / 1024
		cache.data = fmt.Sprintf("%.2f KiB", size)

	} else if fileSize < 1024*1024*1024 {
		// If the file size is less than 1 MiB, return the size in KiB
		size = float64(fileSize) / (1024 * 1024)
		cache.data = fmt.Sprintf("%.2f MiB", size)

	} else if fileSize < 1024*1024*1024*1024 {
		// If the file size is less than 1 GiB, return the size in MiB
		size = float64(fileSize) / (1024 * 1024 * 1024)
		cache.data = fmt.Sprintf("%.2f GiB", size)
	} else {
		// If the file size is 1 GiB or more, return the size in TiB
		size = float64(fileSize) / (1024 * 1024 * 1024 * 1024)
		cache.data = fmt.Sprintf("%.2f TiB", size)
	}

	// Update cache timestamp
	cache.timestamp = time.Now()

	// Return the human readable size
	return cache.data, nil
}
