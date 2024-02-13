package main

import (
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/TheLovinator1/FeedVault/pkg/handlers"
)

func TestIndexHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handlers.IndexHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check the response contains the expected string.
	shouldContain := "Input the URLs of the feeds you wish to archive below. You can add as many as needed, and access them through the website or API. Alternatively, include links to .opml files, and the feeds within will be archived."
	body := rr.Body.String()
	if !strings.Contains(body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}

func TestApiHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/api", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(handlers.ApiHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check the response contains the expected string.
	shouldContain := "Here be dragons."
	body := rr.Body.String()
	if !strings.Contains(body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}
