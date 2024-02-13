package main

import (
	"strings"
	"testing"

	"github.com/TheLovinator1/FeedVault/pkg/html"
	"github.com/TheLovinator1/FeedVault/pkg/models"
)

// Displays error messages if there are any parse errors
func TestErrorMessages(t *testing.T) {
	// Initialize test data
	parseResult := []models.ParseResult{
		{IsError: true, Msg: "Error 1"},
		{IsError: true, Msg: "Error 2"},
	}

	h := html.HTMLData{
		ParseResult: parseResult,
	}

	// Invoke function under test
	result := html.FullHTML(h)

	// Assert that the result contains the error messages
	if !strings.Contains(result, "Error 1") || !strings.Contains(result, "Error 2") {
		t.Errorf("Expected error messages, but got: %s", result)
	}
}
