package main

import (
	"bufio"
	"errors"
	"log"
	"net"
	"net/http"
	"net/url"
	"strings"
	"time"
)

func scrapeBadURLs() {
	// TODO: We should only scrape the bad URLs if the file has been updated
	// TODO: Use brotli compression https://gitlab.com/malware-filter/urlhaus-filter#compressed-version
	filterListURLs := []string{
		"https://malware-filter.gitlab.io/malware-filter/phishing-filter-dnscrypt-blocked-names.txt",
		"https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-dnscrypt-blocked-names-online.txt",
	}

	// Scrape the bad URLs
	badURLs := []BadURLs{}
	for _, url := range filterListURLs {
		// Check if we have scraped the bad URLs in the last 24 hours
		var meta BadURLsMeta
		db.Where("url = ?", url).First(&meta)
		if time.Since(meta.LastScraped).Hours() < 24 {
			log.Printf("%s was last scraped %.1f hours ago\n", url, time.Since(meta.LastScraped).Hours())
			continue
		}

		// Create the meta if it doesn't exist
		if meta.ID == 0 {
			meta = BadURLsMeta{URL: url}
			db.Create(&meta)
		}

		// Update the last scraped time
		db.Model(&meta).Update("last_scraped", time.Now())

		// Get the filter list
		resp, err := http.Get(url)
		if err != nil {
			log.Println("Failed to get filter list:", err)
			continue
		}
		defer resp.Body.Close()

		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			line := scanner.Text()
			if strings.HasPrefix(line, "#") {
				log.Println("Comment:", line)
				continue
			}

			// Skip the URL if it already exists in the database
			var count int64
			db.Model(&BadURLs{}).Where("url = ?", line).Count(&count)
			if count > 0 {
				log.Println("URL already exists:", line)
				continue
			}

			// Add the bad URL to the list
			badURLs = append(badURLs, BadURLs{URL: line, Active: true})
		}

		if err := scanner.Err(); err != nil {
			log.Println("Failed to scan filter list:", err)
		}
	}

	if len(badURLs) == 0 {
		log.Println("No new URLs found in", len(filterListURLs), "filter lists")
		return
	}

	// Log how many bad URLs we found
	log.Println("Found", len(badURLs), "bad URLs")

	// Mark all the bad URLs as inactive if we have any in the database
	var count int64
	db.Model(&BadURLs{}).Count(&count)
	if count > 0 {
		db.Model(&BadURLs{}).Update("active", false)
	}

	// Save the bad URLs to the database
	db.Create(&badURLs)
}

// Run some simple validation on the URL
func validateURL(feed_url string) error {
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

	// Check if the domain is in BadURLs
	var count int64
	db.Model(&BadURLs{}).Where("url = ?", domain).Count(&count)
	if count > 0 {
		return errors.New("URL is in the bad URLs list")
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
