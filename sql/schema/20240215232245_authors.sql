-- +goose Up
-- +goose StatementBegin
-- Person for feeds
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L73
CREATE TABLE IF NOT EXISTS feed_authors (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "name" TEXT,
    email TEXT,
    uri TEXT,
    -- Link to feed
    feed_id INTEGER NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Person for items
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L73
CREATE TABLE IF NOT EXISTS item_authors (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "name" TEXT,
    email TEXT,
    uri TEXT,
    -- Link to feed item (Also called feed entry)
    item_id INTEGER NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_authors;

DROP TABLE IF EXISTS item_authors;

-- +goose StatementEnd
