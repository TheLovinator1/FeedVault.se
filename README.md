# FeedVault

_A seed vault for your feeds._

FeedVault is an open-source web application written in Python that allows users to easily archive RSS, Atom, and JSON feeds.

With FeedVault, users can effortlessly add their favorite feeds, ensuring they have a centralized location for accessing and preserving valuable content.

## Features

_Note: Some features are currently in development._

- **Unified Feed Archiving**: Archive RSS, Atom, and JSON feeds seamlessly in one centralized location.
- **Content Search**: Easily search your archive for specific content.
- **Export Options**: Export your archive to various formats, including JSON, CSV, HTML, ODS, RST, TSV, XLS, XLSX, or YAML.
- **API**: Access your archive programmatically through a API.
- **Self-Hosting**: Host FeedVault on your own server for complete control over your data.
- **User-Friendly Design**: FeedVault is designed to be simple, intuitive, and responsive, working seamlessly on both desktop and mobile devices.
- **Privacy-Focused**: FeedVault respects user privacy by not tracking or collecting any personal data. It is an ad-free platform that prioritizes user security.

## Getting Started

### Prerequisites

#### Development

Ensure you have the following installed on your machine if you plan to run FeedVault locally for development purposes:

- [Python 3.12](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/master/#installation)
- [PostgreSQL](https://www.postgresql.org/download/)

#### Production

Ensure you have the following installed on your machine if you plan to run FeedVault locally for production purposes:

- [Docker](https://docs.docker.com/get-docker/)
- [PostgreSQL](https://www.postgresql.org/download/)

### Installation

Clone the repository:

```bash
git clone https://github.com/TheLovinator1/FeedVault.git
```

Navigate to the project directory:

```bash
cd FeedVault
```

Install the project dependencies:

```bash
poetry install
```

Run the project:

```bash
poetry run site
```

Access FeedVault in your browser at http://localhost:8080.

## Usage

- Visit the FeedVault website.
- Sign up for an account or log in if you already have one.
- Add your favorite feeds to start archiving content.
- Explore, manage, and enjoy your centralized feed archive.

## Contributing

We welcome contributions from the community! If you have ideas for new features, improvements, or bug fixes, feel free to open an issue or submit a pull request.

## Contact

For any inquiries or support, please create an issue on GitHub.

Thank you for using FeedVault! Happy archiving!
