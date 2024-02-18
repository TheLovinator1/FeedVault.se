-- +goose Up
-- +goose StatementBegin
-- Dublin Core for feeds
-- https://github.com/mmcdole/gofeed/blob/master/extensions/dublincore.go#L5
CREATE TABLE IF NOT EXISTS feed_dublin_cores (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
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
    feed_id BIGINT NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Dublin Core for items
-- https://github.com/mmcdole/gofeed/blob/master/extensions/dublincore.go#L5
CREATE TABLE IF NOT EXISTS item_dublin_cores (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
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
    item_id BIGINT NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_dublin_cores CASCADE;

DROP TABLE IF EXISTS item_dublin_cores CASCADE;

-- +goose StatementEnd
