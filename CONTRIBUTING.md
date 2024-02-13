# Contributing to FeedVault

Feel free to create a pull request for things like bug fixes, new features, and improvements. Your pull request doesn't have to be perfect, it just needs to work (or show what you're thinking). I can help you with the rest if needed. If you're not sure about something, feel free to open an issue first to discuss it.

Please don't add any dependencies unless it's absolutely necessary. I want to try to keep the project using the standard library as much as possible.

We use GitHub issues for tracking requests and bugs, so feel free to open an issue if you have any questions or need help.

Thank you for your contributions!

## Running the project

You can run the project using the following command:

```bash
go run cmd/feedvault/main.go
```

You can also run the tests using:

```bash
go test ./...
```

## Using Docker

We have a [Docker.md](Docker.md) file with instructions on how to run the project using Docker.

## Using sqlc and goose

I use [sqlc](https://docs.sqlc.dev/en/latest/index.html) for generating type safe Go from SQL. Make sure to regenerate the code after changing any SQL queries:

```bash
sqlc generate
```

[goose](https://pressly.github.io/goose/) is used for managing database migrations. To create a new migration, run:

```bash
goose create add_some_column sql
goose status
goose up
```
