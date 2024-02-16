-- +goose Up
-- +goose StatementBegin
-- Enclosures 
-- https://github.com/mmcdole/gofeed/blob/master/feed.go#L86
CREATE TABLE IF NOT EXISTS enclosures (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "url" TEXT,
    "length" TEXT,
    "type" TEXT,
    -- Link to feed item (Also called feed entry)
    item_id INTEGER NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS enclosures;

-- +goose StatementEnd
