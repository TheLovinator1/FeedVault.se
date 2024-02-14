package main

import (
	"testing"
)

// URL starts with http://
func TestURLStartsWithHTTP(t *testing.T) {
	url := "http://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// URL starts with https://
func TestURLStartsWithHTTPS(t *testing.T) {
	url := "https://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// URL contains a valid domain
func TestURLContainsValidDomain(t *testing.T) {
	url := "http://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// URL is empty
func TestURLEmpty(t *testing.T) {
	url := ""
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// URL does not contain a domain
func TestURLNotNumbers(t *testing.T) {
	url := "12345"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// URL is not a valid URL
func TestURLNotValidURL(t *testing.T) {
	url := "example.com"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// Domain is resolvable
func TestDomainIsResolvable(t *testing.T) {
	url := "http://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// Domain does not end with .local
func TestDomainDoesNotEndWithLocal(t *testing.T) {
	url := "http://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// Domain is not localhost
func TestDomainIsNotLocalhost(t *testing.T) {
	url := "http://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// Domain is not an IP address
func TestDomainIsNotIPAddress(t *testing.T) {
	url := "http://example.com"
	err := ValidateFeedURL(url)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

// URL is a file path
func TestURLIsFilePath(t *testing.T) {
	url := "/path/to/file"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// URL is a relative path
func TestURLIsRelativePath(t *testing.T) {
	url := "/path/to/resource"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// URL is a non-existent domain
func TestNonExistentDomainURL(t *testing.T) {
	url := "http://jfsalksajlkfsajklfsajklfllfjffffkfsklslsksassflfskjlfjlfsjkalfsaf.com"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "failed to resolve domain" {
		t.Errorf("Expected error message 'failed to resolve domain', got '%v'", err.Error())
	}
}

// URL is a malformed URL
func TestMalformedURL(t *testing.T) {
	url := "malformedurl"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// URL is a domain that does not support HTTP/HTTPS
func TestURLDomainNotSupportHTTP(t *testing.T) {
	url := "ftp://example.com"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URL must start with http:// or https://" {
		t.Errorf("Expected error message 'URL must start with http:// or https://', got '%v'", err.Error())
	}
}

// URL is an unreachable domain
func TestUnreachableDomain(t *testing.T) {
	url := "http://fafsffsfsfsfsafsasafassfs.com"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "failed to resolve domain" {
		t.Errorf("Expected error message 'failed to resolve domain', got '%v'", err.Error())
	}
}

// URL is an IP address
func TestURLIsIPAddress(t *testing.T) {
	url := "http://84.55.107.42"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "IP address URLs are not allowed" {
		t.Errorf("Expected error message 'IP address URLs are not allowed', got '%v'", err.Error())
	}
}

// URL ends with .local
func TestURLEndsWithLocal(t *testing.T) {
	url := "http://example.local"
	err := ValidateFeedURL(url)
	if err == nil {
		t.Error("Expected an error, got nil")
	} else if err.Error() != "URLs ending with .local are not allowed" {
		t.Errorf("Expected error message 'URLs ending with .local are not allowed', got '%v'", err.Error())
	}
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
		err := ValidateFeedURL(localURL)
		if err == nil {
			t.Errorf("Expected an error for local URL %s, got nil", localURL)
		} else if err.Error() != "local URLs are not allowed" {
			t.Errorf("Expected error message 'local URLs are not allowed', got '%v'", err.Error())
		}
	}
}
