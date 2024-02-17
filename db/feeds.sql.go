// Code generated by sqlc. DO NOT EDIT.
// versions:
//   sqlc v1.25.0
// source: feeds.sql

package db

import (
	"context"

	"github.com/jackc/pgx/v5/pgtype"
)

const countFeeds = `-- name: CountFeeds :one
SELECT
    COUNT(*)
FROM
    feeds
`

func (q *Queries) CountFeeds(ctx context.Context) (int64, error) {
	row := q.db.QueryRow(ctx, countFeeds)
	var count int64
	err := row.Scan(&count)
	return count, err
}

const countItems = `-- name: CountItems :one
SELECT
    COUNT(*)
FROM
    items
`

func (q *Queries) CountItems(ctx context.Context) (int64, error) {
	row := q.db.QueryRow(ctx, countItems)
	var count int64
	err := row.Scan(&count)
	return count, err
}

const createFeed = `-- name: CreateFeed :one
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
    ) RETURNING id, url, created_at, updated_at, deleted_at, title, description, link, feed_link, links, updated, updated_parsed, published, published_parsed, language, copyright, generator, categories, custom, feed_type, feed_version
`

type CreateFeedParams struct {
	Url             string             `json:"url"`
	CreatedAt       pgtype.Timestamptz `json:"created_at"`
	UpdatedAt       pgtype.Timestamptz `json:"updated_at"`
	DeletedAt       pgtype.Timestamptz `json:"deleted_at"`
	Title           pgtype.Text        `json:"title"`
	Description     pgtype.Text        `json:"description"`
	Link            pgtype.Text        `json:"link"`
	FeedLink        pgtype.Text        `json:"feed_link"`
	Links           []string           `json:"links"`
	Updated         pgtype.Text        `json:"updated"`
	UpdatedParsed   pgtype.Timestamptz `json:"updated_parsed"`
	Published       pgtype.Text        `json:"published"`
	PublishedParsed pgtype.Timestamptz `json:"published_parsed"`
	Language        pgtype.Text        `json:"language"`
	Copyright       pgtype.Text        `json:"copyright"`
	Generator       pgtype.Text        `json:"generator"`
	Categories      []string           `json:"categories"`
	Custom          []byte             `json:"custom"`
	FeedType        pgtype.Text        `json:"feed_type"`
	FeedVersion     pgtype.Text        `json:"feed_version"`
}

func (q *Queries) CreateFeed(ctx context.Context, arg CreateFeedParams) (Feed, error) {
	row := q.db.QueryRow(ctx, createFeed,
		arg.Url,
		arg.CreatedAt,
		arg.UpdatedAt,
		arg.DeletedAt,
		arg.Title,
		arg.Description,
		arg.Link,
		arg.FeedLink,
		arg.Links,
		arg.Updated,
		arg.UpdatedParsed,
		arg.Published,
		arg.PublishedParsed,
		arg.Language,
		arg.Copyright,
		arg.Generator,
		arg.Categories,
		arg.Custom,
		arg.FeedType,
		arg.FeedVersion,
	)
	var i Feed
	err := row.Scan(
		&i.ID,
		&i.Url,
		&i.CreatedAt,
		&i.UpdatedAt,
		&i.DeletedAt,
		&i.Title,
		&i.Description,
		&i.Link,
		&i.FeedLink,
		&i.Links,
		&i.Updated,
		&i.UpdatedParsed,
		&i.Published,
		&i.PublishedParsed,
		&i.Language,
		&i.Copyright,
		&i.Generator,
		&i.Categories,
		&i.Custom,
		&i.FeedType,
		&i.FeedVersion,
	)
	return i, err
}

const createItem = `-- name: CreateItem :one
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
    ) RETURNING id, created_at, updated_at, deleted_at, title, description, content, link, links, updated, updated_parsed, published, published_parsed, guid, categories, custom, feed_id
`

type CreateItemParams struct {
	CreatedAt       pgtype.Timestamptz `json:"created_at"`
	UpdatedAt       pgtype.Timestamptz `json:"updated_at"`
	DeletedAt       pgtype.Timestamptz `json:"deleted_at"`
	Title           pgtype.Text        `json:"title"`
	Description     pgtype.Text        `json:"description"`
	Content         pgtype.Text        `json:"content"`
	Link            pgtype.Text        `json:"link"`
	Links           []string           `json:"links"`
	Updated         pgtype.Text        `json:"updated"`
	UpdatedParsed   pgtype.Timestamp   `json:"updated_parsed"`
	Published       pgtype.Text        `json:"published"`
	PublishedParsed pgtype.Timestamp   `json:"published_parsed"`
	Guid            pgtype.Text        `json:"guid"`
	Categories      []string           `json:"categories"`
	Custom          []byte             `json:"custom"`
	FeedID          int64              `json:"feed_id"`
}

func (q *Queries) CreateItem(ctx context.Context, arg CreateItemParams) (Item, error) {
	row := q.db.QueryRow(ctx, createItem,
		arg.CreatedAt,
		arg.UpdatedAt,
		arg.DeletedAt,
		arg.Title,
		arg.Description,
		arg.Content,
		arg.Link,
		arg.Links,
		arg.Updated,
		arg.UpdatedParsed,
		arg.Published,
		arg.PublishedParsed,
		arg.Guid,
		arg.Categories,
		arg.Custom,
		arg.FeedID,
	)
	var i Item
	err := row.Scan(
		&i.ID,
		&i.CreatedAt,
		&i.UpdatedAt,
		&i.DeletedAt,
		&i.Title,
		&i.Description,
		&i.Content,
		&i.Link,
		&i.Links,
		&i.Updated,
		&i.UpdatedParsed,
		&i.Published,
		&i.PublishedParsed,
		&i.Guid,
		&i.Categories,
		&i.Custom,
		&i.FeedID,
	)
	return i, err
}

const getFeed = `-- name: GetFeed :one
SELECT
    id, url, created_at, updated_at, deleted_at, title, description, link, feed_link, links, updated, updated_parsed, published, published_parsed, language, copyright, generator, categories, custom, feed_type, feed_version
FROM
    feeds
WHERE
    id = $1
`

func (q *Queries) GetFeed(ctx context.Context, id int64) (Feed, error) {
	row := q.db.QueryRow(ctx, getFeed, id)
	var i Feed
	err := row.Scan(
		&i.ID,
		&i.Url,
		&i.CreatedAt,
		&i.UpdatedAt,
		&i.DeletedAt,
		&i.Title,
		&i.Description,
		&i.Link,
		&i.FeedLink,
		&i.Links,
		&i.Updated,
		&i.UpdatedParsed,
		&i.Published,
		&i.PublishedParsed,
		&i.Language,
		&i.Copyright,
		&i.Generator,
		&i.Categories,
		&i.Custom,
		&i.FeedType,
		&i.FeedVersion,
	)
	return i, err
}

const getFeeds = `-- name: GetFeeds :many
SELECT
    id, url, created_at, updated_at, deleted_at, title, description, link, feed_link, links, updated, updated_parsed, published, published_parsed, language, copyright, generator, categories, custom, feed_type, feed_version
FROM
    feeds
ORDER BY
    created_at DESC
LIMIT $1
OFFSET $2
`

type GetFeedsParams struct {
	Limit  int32 `json:"limit"`
	Offset int32 `json:"offset"`
}

func (q *Queries) GetFeeds(ctx context.Context, arg GetFeedsParams) ([]Feed, error) {
	rows, err := q.db.Query(ctx, getFeeds, arg.Limit, arg.Offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	items := []Feed{}
	for rows.Next() {
		var i Feed
		if err := rows.Scan(
			&i.ID,
			&i.Url,
			&i.CreatedAt,
			&i.UpdatedAt,
			&i.DeletedAt,
			&i.Title,
			&i.Description,
			&i.Link,
			&i.FeedLink,
			&i.Links,
			&i.Updated,
			&i.UpdatedParsed,
			&i.Published,
			&i.PublishedParsed,
			&i.Language,
			&i.Copyright,
			&i.Generator,
			&i.Categories,
			&i.Custom,
			&i.FeedType,
			&i.FeedVersion,
		); err != nil {
			return nil, err
		}
		items = append(items, i)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return items, nil
}

const getItem = `-- name: GetItem :one
SELECT
    id, created_at, updated_at, deleted_at, title, description, content, link, links, updated, updated_parsed, published, published_parsed, guid, categories, custom, feed_id
FROM
    items
WHERE
    id = $1
`

func (q *Queries) GetItem(ctx context.Context, id int64) (Item, error) {
	row := q.db.QueryRow(ctx, getItem, id)
	var i Item
	err := row.Scan(
		&i.ID,
		&i.CreatedAt,
		&i.UpdatedAt,
		&i.DeletedAt,
		&i.Title,
		&i.Description,
		&i.Content,
		&i.Link,
		&i.Links,
		&i.Updated,
		&i.UpdatedParsed,
		&i.Published,
		&i.PublishedParsed,
		&i.Guid,
		&i.Categories,
		&i.Custom,
		&i.FeedID,
	)
	return i, err
}

const getItems = `-- name: GetItems :many
SELECT
    id, created_at, updated_at, deleted_at, title, description, content, link, links, updated, updated_parsed, published, published_parsed, guid, categories, custom, feed_id
FROM
    items
WHERE
    feed_id = $1
ORDER BY
    created_at DESC
LIMIT $2
OFFSET $3
`

type GetItemsParams struct {
	FeedID int64 `json:"feed_id"`
	Limit  int32 `json:"limit"`
	Offset int32 `json:"offset"`
}

func (q *Queries) GetItems(ctx context.Context, arg GetItemsParams) ([]Item, error) {
	rows, err := q.db.Query(ctx, getItems, arg.FeedID, arg.Limit, arg.Offset)
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	items := []Item{}
	for rows.Next() {
		var i Item
		if err := rows.Scan(
			&i.ID,
			&i.CreatedAt,
			&i.UpdatedAt,
			&i.DeletedAt,
			&i.Title,
			&i.Description,
			&i.Content,
			&i.Link,
			&i.Links,
			&i.Updated,
			&i.UpdatedParsed,
			&i.Published,
			&i.PublishedParsed,
			&i.Guid,
			&i.Categories,
			&i.Custom,
			&i.FeedID,
		); err != nil {
			return nil, err
		}
		items = append(items, i)
	}
	if err := rows.Err(); err != nil {
		return nil, err
	}
	return items, nil
}
