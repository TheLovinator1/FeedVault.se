# Docker Compose

You can run the project using Docker Compose. You can use the following commands to build, run, and stop the project:

```bash
docker compose build
docker compose up
docker compose down
```

## Accessing the database

```bash
docker-compose exec db psql -U feedvault -d feedvault
```

## Environment variables

You can use the following environment variables to configure the project:

- `PORT`: The port to listen on (default: `8000`)
- `DATABASE_URL`: The URL of the database (default: `postgres://feedvault:feedvault@db/feedvault?sslmode=disable`)
  - FeedVault only supports PostgreSQL at the moment
- `ADMIN_EMAIL`: The email where we should email errors to.
- `EMAIL_HOST_USER`: The email address to send emails from.
- `EMAIL_HOST_PASSWORD`: The password for the email address to send emails from.
- `EMAIL_HOST`: The SMTP server to send emails through. (default: `smtp.gmail.com`)
- `EMAIL_PORT`: The port to send emails through. (default: `587`)
- `DISCORD_WEBHOOK_URL`: The Discord webhook URL to send messages to.
- `APP_ENV`: The environment the app is running in. Development or Production. (default: `development`)
- `USER_AGENT`: The user agent to use for making requests. (default: `None`)
