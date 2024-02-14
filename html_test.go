package main

import (
	"strings"
	"testing"
)

// Displays error messages if there are any parse errors
func TestErrorMessages(t *testing.T) {
	// Initialize test data
	parseResult := []ParseResult{
		{IsError: true, Msg: "Error 1"},
		{IsError: true, Msg: "Error 2"},
	}

	h := HTMLData{
		ParseResult: parseResult,
	}

	// Invoke function under test
	result := FullHTML(h)

	// Assert that the result contains the error messages
	if !strings.Contains(result, "Error 1") || !strings.Contains(result, "Error 2") {
		t.Errorf("Expected error messages, but got: %s", result)
	}
}
