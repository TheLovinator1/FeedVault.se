-- +goose Up
-- +goose StatementBegin
-- Itunes for feeds
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L5
CREATE TABLE IF NOT EXISTS feed_itunes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    -- From gofeed:
    author TEXT,
    "block" TEXT,
    -- Categories - See feed_itunes_categories
    "explicit" TEXT,
    keywords TEXT,
    -- Owner - See feed_itunes_owners
    subtitle TEXT,
    summary TEXT,
    "image" TEXT,
    complete TEXT,
    new_feed_url TEXT,
    "type" TEXT,
    -- Link to feed
    feed_id BIGINT NOT NULL,
    CONSTRAINT fk_feed_id FOREIGN KEY (feed_id) REFERENCES feeds (id) ON DELETE CASCADE
);

-- Itunes for items
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L22
CREATE TABLE IF NOT EXISTS item_itunes (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
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
    item_id BIGINT NOT NULL,
    CONSTRAINT fk_item_id FOREIGN KEY (item_id) REFERENCES items (id) ON DELETE CASCADE
);

-- Itunes categories for feeds
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L39
CREATE TABLE IF NOT EXISTS feed_itunes_categories (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    -- From gofeed:
    "text" TEXT,
    subcategory BIGINT,
    -- Link to itunes
    itunes_id BIGINT NOT NULL,
    CONSTRAINT fk_itunes_id FOREIGN KEY (itunes_id) REFERENCES feed_itunes (id) ON DELETE CASCADE,
    CONSTRAINT fk_subcategory_id FOREIGN KEY (subcategory) REFERENCES feed_itunes_categories (id) ON DELETE SET NULL
);

-- Itunes owners
-- https://github.com/mmcdole/gofeed/blob/master/extensions/itunes.go#L45
CREATE TABLE IF NOT EXISTS feed_itunes_owners (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMPTZ DEFAULT NULL,
    -- From gofeed:
    email TEXT,
    "name" TEXT,
    -- Link to itunes
    itunes_id BIGINT NOT NULL,
    CONSTRAINT fk_itunes_id FOREIGN KEY (itunes_id) REFERENCES feed_itunes (id) ON DELETE CASCADE
);

-- +goose StatementEnd
-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS feed_itunes CASCADE;

DROP TABLE IF EXISTS item_itunes CASCADE;

DROP TABLE IF EXISTS feed_itunes_categories CASCADE;

DROP TABLE IF EXISTS feed_itunes_owners CASCADE;

-- +goose StatementEnd
