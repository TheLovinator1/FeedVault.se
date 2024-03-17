# FeedVault

_A seed vault for your feeds._

[FeedVault](https://feedvault.se/) is an open-source web application that allows users to archive and search their favorite RSS, Atom, and JSON feeds. With FeedVault, users can effortlessly add their favorite feeds, ensuring they have a centralized location for accessing and preserving valuable content.

## Features

_Note: Some features are currently in development._

- **Unified Feed Archiving**: Archive RSS (0.90 to 2.0), Atom (0.3, 1.0), JSON (1.0, 1.1), Dublin Core, and ITunes feeds seamlessly in one centralized location.
- **Content Search**: Easily search your archive for specific content.
- **Export Options**: Export your archive to various formats, including JSON, CSV, HTML, ODS, RST, TSV, XLS, XLSX, or YAML.
- **API**: Access your archive programmatically through a API.
- **Self-Hosting**: Host FeedVault on your own server for complete control over your data.
- **Privacy-Focused**: FeedVault respects user privacy by not tracking or collecting any personal data. It is an ad-free platform that prioritizes user security.

## Usage

- [Visit the FeedVault website](https://feedvault.se/).
- Sign up for an account or log in if you already have one.
- Add your favorite feeds to start archiving content.
- Explore, manage, and enjoy your centralized feed archive.

## Contributing

Feel free to contribute to the project. If you have any questions, please open an issue.

## Dependencies

- [Python](https://www.python.org/)
- [Poetry](https://python-poetry.org/)
- [PostgreSQL 16](https://www.postgresql.org/)

## tl;dr

```bash
poetry install
poetry shell
python manage.py test
python manage.py collectstatic
python manage.py makemigrations
python manage.py migrate
python manage.py runserver

# Optional
pre-commit install
pre-commit run --all-files

# Update feeds
python manage.py update_feeds
```

## Contact

If you have any questions, please open an issue.

I can also be reached at [hello@panso.se](mailto:hello@panso.se) or on Discord: `TheLovinator#9276`
