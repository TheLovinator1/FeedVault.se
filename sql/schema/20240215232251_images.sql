-- +goose Up
-- +goose StatementBegin
-- Image for feeds
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L80
CREATE TABLE IF NOT EXISTS feed_images (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "url" TEXT,
    title TEXT,
    -- Link to feed
    feed_id INTEGER NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Image for items
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L80
CREATE TABLE IF NOT EXISTS item_images (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "url" TEXT,
    title TEXT,
    -- Link to feed item (Also called feed entry)
    item_id INTEGER NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_images;

DROP TABLE IF EXISTS item_images;

-- +goose StatementEnd
