package main

import (
	"errors"
	"net"
	"net/http"
	"net/url"
	"strings"
)

// Run some simple validation on the URL
func ValidateFeedURL(feed_url string) error {
	// Check if URL starts with http or https
	if !strings.HasPrefix(feed_url, "http://") && !strings.HasPrefix(feed_url, "https://") {
		return errors.New("URL must start with http:// or https://")
	}

	// Parse a url into a URL structure
	u, err := url.Parse(feed_url)
	if err != nil {
		return errors.New("failed to parse URL")
	}

	// Get the domain from the URL
	domain := u.Hostname()
	domain = strings.TrimSpace(domain)
	if domain == "" {
		return errors.New("URL does not contain a domain")
	}

	// Don't allow IP address URLs
	ip := net.ParseIP(domain)
	if ip != nil {
		return errors.New("IP address URLs are not allowed")
	}

	// Don't allow local URLs (e.g. router URLs)
	// Taken from https://github.com/uBlockOrigin/uAssets/blob/master/filters/lan-block.txt
	// https://github.com/gwarser/filter-lists
	localURLs := []string{
		"[::]",
		"[::1]",
		"airbox.home",
		"airport",
		"arcor.easybox",
		"aterm.me",
		"bthomehub.home",
		"bthub.home",
		"congstar.box",
		"connect.box",
		"console.gl-inet.com",
		"easy.box",
		"etxr",
		"fire.walla",
		"fritz.box",
		"fritz.nas",
		"fritz.repeater",
		"giga.cube",
		"hi.link",
		"hitronhub.home",
		"home.arpa",
		"homerouter.cpe",
		"host.docker.internal",
		"huaweimobilewifi.com",
		"localbattle.net",
		"localhost",
		"mobile.hotspot",
		"myfritz.box",
		"ntt.setup",
		"pi.hole",
		"plex.direct",
		"repeater.asus.com",
		"router.asus.com",
		"routerlogin.com",
		"routerlogin.net",
		"samsung.router",
		"speedport.ip",
		"steamloopback.host",
		"tplinkap.net",
		"tplinkeap.net",
		"tplinkmodem.net",
		"tplinkplclogin.net",
		"tplinkrepeater.net",
		"tplinkwifi.net",
		"web.setup.home",
		"web.setup",
	}
	for _, localURL := range localURLs {
		if strings.Contains(domain, localURL) {
			return errors.New("local URLs are not allowed")
		}
	}

	// Don't allow URLs that end with .local
	if strings.HasSuffix(domain, ".local") {
		return errors.New("URLs ending with .local are not allowed")
	}

	// Don't allow URLs that end with .onion
	if strings.HasSuffix(domain, ".onion") {
		return errors.New("URLs ending with .onion are not allowed")
	}

	// Don't allow URLs that end with .home.arpa
	if strings.HasSuffix(domain, ".home.arpa") {
		return errors.New("URLs ending with .home.arpa are not allowed")
	}

	// Don't allow URLs that end with .internal
	// Docker uses host.docker.internal
	if strings.HasSuffix(domain, ".internal") {
		return errors.New("URLs ending with .internal are not allowed")
	}

	// Don't allow URLs that end with .localdomain
	if strings.HasSuffix(domain, ".localdomain") {
		return errors.New("URLs ending with .localdomain are not allowed")
	}

	// Check if the domain is resolvable
	_, err = net.LookupIP(domain)
	if err != nil {
		return errors.New("failed to resolve domain")
	}

	// Check if the URL is reachable
	_, err = http.Get(feed_url)
	if err != nil {
		return errors.New("failed to reach URL")
	}

	return nil
}
