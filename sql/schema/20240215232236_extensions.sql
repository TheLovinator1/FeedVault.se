-- +goose Up
-- +goose StatementBegin
-- Extensions for feeds
-- https://github.com/mmcdole/gofeed/blob/master/extensions/extensions.go#L3
CREATE TABLE IF NOT EXISTS feed_extensions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "name" TEXT,
    "value" TEXT,
    attrs JSONB,
    children JSONB,
    -- Link to feed
    feed_id INTEGER NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Extensions for items
-- https://github.com/mmcdole/gofeed/blob/master/extensions/extensions.go#L3
CREATE TABLE IF NOT EXISTS item_extensions (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "name" TEXT,
    "value" TEXT,
    attrs JSONB,
    children JSONB,
    -- Link to feed item (Also called feed entry)
    item_id INTEGER NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_extensions;

DROP TABLE IF EXISTS item_extensions;

-- +goose StatementEnd
