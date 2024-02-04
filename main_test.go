package main

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/stretchr/testify/assert"
)

// URL starts with http://
func TestURLStartsWithHTTP(t *testing.T) {
	url := "http://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// URL starts with https://
func TestURLStartsWithHTTPS(t *testing.T) {
	url := "https://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// URL contains a valid domain
func TestURLContainsValidDomain(t *testing.T) {
	url := "http://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// URL is empty
func TestURLEmpty(t *testing.T) {
	url := ""
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// URL does not contain a domain
func TestURLNotNumbers(t *testing.T) {
	url := "12345"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// URL is not a valid URL
func TestURLNotValidURL(t *testing.T) {
	url := "example.com"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// Domain is resolvable
func TestDomainIsResolvable(t *testing.T) {
	url := "http://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// Domain does not end with .local
func TestDomainDoesNotEndWithLocal(t *testing.T) {
	url := "http://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// Domain is not localhost
func TestDomainIsNotLocalhost(t *testing.T) {
	url := "http://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// Domain is not an IP address
func TestDomainIsNotIPAddress(t *testing.T) {
	url := "http://example.com"
	err := validateURL(url)
	assert.Nil(t, err)
}

// URL is a file path
func TestURLIsFilePath(t *testing.T) {
	url := "/path/to/file"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// URL is a relative path
func TestURLIsRelativePath(t *testing.T) {
	url := "/path/to/resource"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// URL is a non-existent domain
func TestNonExistentDomainURL(t *testing.T) {
	url := "http://jfsalksajlkfsajklfsajklfllfjffffkfsklslsksassflfskjlfjlfsjkalfsaf.com"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "failed to resolve domain", err.Error())
}

// URL is a malformed URL
func TestMalformedURL(t *testing.T) {
	url := "malformedurl"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// URL is a domain that does not support HTTP/HTTPS
func TestURLDomainNotSupportHTTP(t *testing.T) {
	url := "ftp://example.com"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URL must start with http:// or https://", err.Error())
}

// URL is an unreachable domain
func TestUnreachableDomain(t *testing.T) {
	url := "http://fafsffsfsfsfsafsasafassfs.com"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "failed to resolve domain", err.Error())
}

// URL is an IP address
func TestURLIsIPAddress(t *testing.T) {
	url := "http://84.55.107.42"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "IP address URLs are not allowed", err.Error())
}

// URL ends with .local
func TestURLEndsWithLocal(t *testing.T) {
	url := "http://example.local"
	err := validateURL(url)
	assert.NotNil(t, err)
	assert.Equal(t, "URLs ending with .local are not allowed", err.Error())
}

func TestLocalURLs(t *testing.T) {
	localURLs := []string{
		"https://localhost",
		"https://home.arpa",
		"https://airbox.home",
		"https://airport",
		"https://arcor.easybox",
		"https://aterm.me",
		"https://bthub.home",
		"https://bthomehub.home",
		"https://congstar.box",
		"https://connect.box",
		"https://console.gl-inet.com",
		"https://easy.box",
		"https://etxr",
		"https://fire.walla",
		"https://fritz.box",
		"https://fritz.nas",
		"https://fritz.repeater",
		"https://giga.cube",
		"https://hi.link",
		"https://hitronhub.home",
		"https://homerouter.cpe",
		"https://huaweimobilewifi.com",
		"https://localbattle.net",
		"https://myfritz.box",
		"https://mobile.hotspot",
		"https://ntt.setup",
		"https://pi.hole",
		"https://plex.direct",
		"https://repeater.asus.com",
		"https://router.asus.com",
		"https://routerlogin.com",
		"https://routerlogin.net",
		"https://samsung.router",
		"https://speedport.ip",
		"https://steamloopback.host",
		"https://tplinkap.net",
		"https://tplinkeap.net",
		"https://tplinkmodem.net",
		"https://tplinkplclogin.net",
		"https://tplinkrepeater.net",
		"https://tplinkwifi.net",
		"https://web.setup",
		"https://web.setup.home",
	}

	for _, localURL := range localURLs {
		err := validateURL(localURL)
		if err == nil {
			t.Errorf("Expected an error for local URL %s, got nil", localURL)
		}
		assert.Equal(t, "local URLs are not allowed", err.Error())
	}
}

func TestIndexHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(IndexHandler)

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
	if !assert.Contains(t, body, shouldContain) {
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
	handler := http.HandlerFunc(ApiHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check the response contains the expected string.
	shouldContain := "<p>Here be dragons.</p>"
	body := rr.Body.String()
	if !assert.Contains(t, body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}

func TestTermsHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/terms", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(TermsHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check the response contains the expected string.
	shouldContain := "Terms of Service"
	body := rr.Body.String()
	if !assert.Contains(t, body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}

func TestPrivacyHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/privacy", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(PrivacyHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check the response contains the expected string.
	shouldContain := "Privacy Policy"
	body := rr.Body.String()
	if !assert.Contains(t, body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}

func TestNotFoundHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/notfound", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(NotFoundHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusNotFound {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusNotFound)
	}

	// Check the response contains the expected string.
	shouldContain := "<h2>404 - Page not found</h2>"
	body := rr.Body.String()
	if !assert.Contains(t, body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}

func TestMethodNotAllowedHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/api", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(MethodNotAllowedHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusMethodNotAllowed {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusMethodNotAllowed)
	}

	// Check the response contains the expected string.
	shouldContain := "<h2>405 - Method Not Allowed</h2>"
	body := rr.Body.String()
	if !assert.Contains(t, body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}

func TestDonateHandler(t *testing.T) {
	// Create a request to pass to our handler.
	req, err := http.NewRequest("GET", "/donate", nil)
	if err != nil {
		t.Fatal(err)
	}

	// We create a ResponseRecorder (which satisfies http.ResponseWriter) to record the response.
	rr := httptest.NewRecorder()
	handler := http.HandlerFunc(DonateHandler)

	// Our handlers satisfy http.Handler, so we can call their ServeHTTP method
	// directly and pass in our Request and ResponseRecorder.
	handler.ServeHTTP(rr, req)

	// Check the status code is what we expect.
	if status := rr.Code; status != http.StatusOK {
		t.Errorf("handler returned wrong status code: got %v want %v",
			status, http.StatusOK)
	}

	// Check the response contains the expected string.
	shouldContain := "tl;dr: <a href=\"https://github.com/sponsors/TheLovinator1\">GitHub Sponsors</a>"
	body := rr.Body.String()
	if !assert.Contains(t, body, shouldContain) {
		t.Errorf("handler returned unexpected body: got %v want %v",
			body, shouldContain)
	}
}
