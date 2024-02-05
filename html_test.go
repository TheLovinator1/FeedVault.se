package main

import (
	"strings"
	"testing"
)

// returns a minified version of the input HTML string
func TestMinifyHTML(t *testing.T) {
	input := "<html><head><title>Test</title></head><body><h1>Hello, World!</h1></body></html>"
	expected := "<title>Test</title><h1>Hello, World!</h1>"

	result := minifyHTML(input)

	if result != expected {
		t.Errorf("Expected minified HTML: %s, but got: %s", expected, result)
	}
}

func TestMinifyCSS(t *testing.T) {
	cssString := `
    body {
        background-color: red;
        color: blue;
    }
    `
	expected := "body{background-color:red;color:blue}"
	result := minifyCSS(cssString)
	if result != expected {
		t.Errorf("Expected minified CSS string to be %s, but got %s", expected, result)
	}
}

// Displays error messages if there are any parse errors
func TestErrorMessages(t *testing.T) {
	// Initialize test data
	h := HTMLData{}
	parseResult := []ParseResult{
		{IsError: true, Msg: "Error 1"},
		{IsError: true, Msg: "Error 2"},
	}

	// Invoke function under test
	result := fullHTML(h, parseResult)

	// Assert that the result contains the error messages
	if !strings.Contains(result, "Error 1") || !strings.Contains(result, "Error 2") {
		t.Errorf("Expected error messages, but got: %s", result)
	}
}
