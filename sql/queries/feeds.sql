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
    ) RETURNING *;

-- name: CountFeeds :one
SELECT
    COUNT(*)
FROM
    feeds;
