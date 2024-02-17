-- +goose Up
-- +goose StatementBegin
-- Enclosures 
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L86
CREATE TABLE IF NOT EXISTS enclosures (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    -- From gofeed:
    "url" TEXT,
    "length" TEXT,
    "type" TEXT,
    -- Link to feed item (Also called feed entry)
    item_id BIGINT NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS enclosures;

-- +goose StatementEnd
