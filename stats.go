package main

import (
	"fmt"
	"log"
	"os"
)

// Get the size of the database and return as nearest human readable size
func GetDBSize() string {
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
		return fmt.Sprintf("%.2f KiB", size)
	}

	if fileSize < 1024*1024*1024 {
		size = float64(fileSize) / (1024 * 1024)
		return fmt.Sprintf("%.2f MiB", size)
	}

	if fileSize < 1024*1024*1024*1024 {
		size = float64(fileSize) / (1024 * 1024 * 1024)
		return fmt.Sprintf("%.2f GiB", size)
	}

	size = float64(fileSize) / (1024 * 1024 * 1024 * 1024)
	return fmt.Sprintf("%.2f TiB", size)
}
