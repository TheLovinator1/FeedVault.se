-- +goose Up
-- +goose StatementBegin
-- Person for feeds
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L73
CREATE TABLE IF NOT EXISTS feed_authors (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    -- From gofeed:
    "name" TEXT,
    email TEXT,
    -- Link to feed
    feed_id BIGINT NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Person for items
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L73
CREATE TABLE IF NOT EXISTS item_authors (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    -- From gofeed:
    "name" TEXT,
    email TEXT,
    -- Link to feed item (Also called feed entry)
    item_id BIGINT NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_authors;

DROP TABLE IF EXISTS item_authors;

-- +goose StatementEnd
