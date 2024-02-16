-- +goose Up
-- +goose StatementBegin
-- Itunes for feeds
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L5
CREATE TABLE IF NOT EXISTS feed_itunes (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    author TEXT,
    "block" TEXT,
    "explicit" TEXT,
    keywords TEXT,
    -- Owner
    subtitle TEXT,
    summary TEXT,
    "image" TEXT,
    complete TEXT,
    new_feed_url TEXT,
    "type" TEXT,
    -- Link to feed
    feed_id INTEGER NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Itunes for items
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L22
CREATE TABLE IF NOT EXISTS item_itunes (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    author TEXT,
    "block" TEXT,
    duration TEXT,
    "explicit" TEXT,
    keywords TEXT,
    subtitle TEXT,
    summary TEXT,
    "image" TEXT,
    is_closed_captioned TEXT,
    episode TEXT,
    season TEXT,
    "order" TEXT,
    episode_type TEXT,
    -- Link to feed item (Also called feed entry)
    item_id INTEGER NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- Itunes categories
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L39
CREATE TABLE IF NOT EXISTS itunes_categories (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    "text" TEXT,
    subcategory TEXT,
    -- Link to itunes
    itunes_id INTEGER NOT NULL,
    CONSTRAINT fk_itunes_id FOREIGN KEY (itunes_id) REFERENCES feed_itunes (id) ON DELETE CASCADE
);

-- Itunes owners
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L45
CREATE TABLE IF NOT EXISTS itunes_owners (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP DEFAULT NULL,
    -- From gofeed:
    email TEXT,
    "name" TEXT,
    -- Link to itunes
    itunes_id INTEGER NOT NULL,
    CONSTRAINT fk_itunes_id FOREIGN KEY (itunes_id) REFERENCES feed_itunes (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_itunes;

DROP TABLE IF EXISTS item_itunes;

DROP TABLE IF EXISTS itunes_categories;

DROP TABLE IF EXISTS itunes_owners;

-- +goose StatementEnd
