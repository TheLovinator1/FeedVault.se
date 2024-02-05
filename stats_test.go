package main

import (
	"testing"
	"time"
)

// If the cache is less than 10 minutes old, return the cached data.
func TestCacheLessThan10MinutesOld(t *testing.T) {
	result := GetDBSize()

	// Assert that the size of the database is returned
	if result != cache.data {
		t.Errorf("Expected database size, but got %s", result)
	}
}

// If the cache is more than 10 minutes old, return the size of the database.
func TestCacheMoreThan10MinutesOld(t *testing.T) {
	// Set the cache timestamp to 11 minutes ago
	cache.timestamp = time.Now().Add(-11 * time.Minute)
	result := GetDBSize()

	// Assert that the size of the database is returned
	if result != cache.data {
		t.Errorf("Expected database size, but got %s", result)
	}
}
