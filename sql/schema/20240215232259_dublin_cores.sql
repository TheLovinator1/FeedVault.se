-- +goose Up
-- +goose StatementBegin
-- Dublin Core for feeds
-- https://github.com/mmcdole/gofeed/blob/master/extensions/dublincore.go#L5
CREATE TABLE IF NOT EXISTS feed_dublin_cores (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    title TEXT [],
    creator TEXT [],
    author TEXT [],
    "subject" TEXT [],
    "description" TEXT [],
    publisher TEXT [],
    contributor TEXT [],
    "date" TEXT [],
    "type" TEXT [],
    format TEXT [],
    identifier TEXT [],
    source TEXT [],
    "language" TEXT [],
    relation TEXT [],
    coverage TEXT [],
    rights TEXT [],
    -- Link to feed
    feed_id INTEGER NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Dublin Core for items
-- https://github.com/mmcdole/gofeed/blob/master/extensions/dublincore.go#L5
CREATE TABLE IF NOT EXISTS item_dublin_cores (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    title TEXT [],
    creator TEXT [],
    author TEXT [],
    "subject" TEXT [],
    "description" TEXT [],
    publisher TEXT [],
    contributor TEXT [],
    "date" TEXT [],
    "type" TEXT [],
    format TEXT [],
    identifier TEXT [],
    source TEXT [],
    "language" TEXT [],
    relation TEXT [],
    coverage TEXT [],
    rights TEXT [],
    -- Link to feed item (Also called feed entry)
    item_id INTEGER NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_dublin_cores;

DROP TABLE IF EXISTS item_dublin_cores;

-- +goose StatementEnd
