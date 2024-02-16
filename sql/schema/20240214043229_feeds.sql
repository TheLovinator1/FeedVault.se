-- +goose Up
-- +goose StatementBegin
-- Create table feeds if not exists
CREATE TABLE IF NOT EXISTS feeds (
    id SERIAL PRIMARY KEY,
    "url" TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed: https://github.com/mmcdole/gofeed/blob/master/feed.go
    title TEXT,
    "description" TEXT,
    link TEXT,
    feed_link TEXT,
    links TEXT [],
    updated TEXT,
    updated_parsed TIMESTAMP,
    published TEXT,
    published_parsed TIMESTAMP,
    -- Authors - See feed_authors
    "language" TEXT,
    -- Image - See feed_images
    copyright TEXT,
    generator TEXT,
    categories TEXT [],
    -- Dublin Core - See feed_dublin_cores
    -- Itunes - See feed_itunes
    -- Extensions - See feed_extensions
    custom JSONB,
    -- Items - See items
    feed_type TEXT,
    feed_version TEXT
);

-- Feed item
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L49
CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    title TEXT,
    "description" TEXT,
    content TEXT,
    link TEXT,
    links TEXT [],
    updated TEXT,
    updated_parsed TIMESTAMP,
    published TEXT,
    published_parsed TIMESTAMP,
    -- Authors - See item_authors
    "guid" TEXT,
    -- Image - See item_images
    categories TEXT [],
    -- Enclosures - See enclosures
    -- Dublin Core - See item_dublin_cores
    -- Itunes - See item_itunes
    -- Extensions - See item_extensions
    custom JSONB,
    -- Link to feed
    feed_id INTEGER NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feeds;

DROP TABLE IF EXISTS items;

-- +goose StatementEnd
