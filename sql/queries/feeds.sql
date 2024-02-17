-- name: CreateFeed :one
INSERT INTO
    feeds (
        "url",
        created_at,
        updated_at,
        deleted_at,
        title,
        "description",
        link,
        feed_link,
        links,
        updated,
        updated_parsed,
        published,
        published_parsed,
        "language",
        copyright,
        generator,
        categories,
        custom,
        feed_type,
        feed_version
    )
VALUES
    (
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        $10,
        $11,
        $12,
        $13,
        $14,
        $15,
        $16,
        $17,
        $18,
        $19,
        $20
    )
RETURNING
    *;

-- name: CountFeeds :one
SELECT
    COUNT(*)
FROM
    feeds;

-- name: CreateItem :one
INSERT INTO
    items (
        created_at,
        updated_at,
        deleted_at,
        title,
        "description",
        content,
        link,
        links,
        updated,
        updated_parsed,
        published,
        published_parsed,
        "guid",
        categories,
        custom,
        feed_id
    )
VALUES
    (
        $1,
        $2,
        $3,
        $4,
        $5,
        $6,
        $7,
        $8,
        $9,
        $10,
        $11,
        $12,
        $13,
        $14,
        $15,
        $16
    )
RETURNING
    *;

-- name: CountItems :one
SELECT
    COUNT(*)
FROM
    items;

-- name: GetFeed :one
SELECT
    *
FROM
    feeds
WHERE
    id = $1;

-- name: GetFeeds :many
SELECT
    *
FROM
    feeds
ORDER BY
    created_at DESC
LIMIT
    $1
OFFSET
    $2;

-- name: GetItem :one
SELECT
    *
FROM
    items
WHERE
    id = $1;

-- name: GetItems :many
SELECT
    *
FROM
    items
WHERE
    feed_id = $1
ORDER BY
    created_at DESC
LIMIT
    $2
OFFSET
    $3;

-- name: CreateFeedExtension :one
INSERT INTO
    feed_extensions (
        created_at,
        updated_at,
        deleted_at,
        "name",
        "value",
        attrs,
        children,
        feed_id
    )
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING
    *;

-- name: CreateItemExtension :one
INSERT INTO
    item_extensions (
        created_at,
        updated_at,
        deleted_at,
        "name",
        "value",
        attrs,
        children,
        item_id
    )
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8)
RETURNING
    *;

-- name: GetFeedExtensions :many
SELECT
    *
FROM
    feed_extensions
WHERE
    feed_id = $1
ORDER BY
    created_at DESC
LIMIT
    $2
OFFSET
    $3;

-- name: GetItemExtensions :many
SELECT
    *
FROM
    item_extensions
WHERE
    item_id = $1
ORDER BY
    created_at DESC
LIMIT
    $2
OFFSET
    $3;

-- name: CreateFeedAuthor :one
INSERT INTO
    feed_authors (
        created_at,
        updated_at,
        deleted_at,
        "name",
        email,
        feed_id
    )
VALUES
    ($1, $2, $3, $4, $5, $6)
RETURNING
    *;

-- name: CreateItemAuthor :one
INSERT INTO
    item_authors (
        created_at,
        updated_at,
        deleted_at,
        "name",
        email,
        item_id
    )
VALUES
    ($1, $2, $3, $4, $5, $6)
RETURNING
    *;

-- name: GetFeedAuthors :many
SELECT
    *
FROM
    feed_authors
WHERE
    feed_id = $1
ORDER BY
    created_at DESC
LIMIT
    $2
OFFSET
    $3;

-- name: GetItemAuthors :many
SELECT
    *
FROM
    item_authors
WHERE
    item_id = $1
ORDER BY
    created_at DESC
LIMIT
    $2
OFFSET
    $3;
