# FeedVault

_A seed vault for your feeds._

[FeedVault](https://feedvault.se/) is an free and open-source archive of RSS/Atom feeds.

## Contributing

Feel free to contribute with anything. If you have any questions, please open an issue or reach out to me directly.

I can be reached at [tlovinator@gmail.com](mailto:tlovinator@gmail.com) or on Discord: `TheLovinator#9276`

## Deployment

```bash
sudo pacman -S postgresql
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl enable --now postgresql
```

Create a local role and database:

```bash
sudo -u postgres createuser -P feedvault
sudo -u postgres createdb -O feedvault feedvault
```

Point Django at the unix socket used by Arch (`/run/postgresql`):

```bash
POSTGRES_USER=feedvault
POSTGRES_PASSWORD=your_password
POSTGRES_DB=feedvault
POSTGRES_HOST=/run/postgresql
POSTGRES_PORT=5432
```

### Linux (Systemd)

```bash
sudo useradd --create-home --home-dir /home/feedvault --shell /bin/fish feedvault
sudo passwd feedvault
# sudo usermod -aG wheel feedvault
su - feedvault
git clone https://git.lovinator.space/TheLovinator/feedvault.se.git feedvault
cd feedvault
uv sync --no-dev

# Modify .env with the correct database credentials and other settings, then run migrations:
uv run python manage.py migrate
```

Install the systemd service from the repo:

```bash
sudo install -m 0644 tools/systemd/feedvault.socket /etc/systemd/system/feedvault.socket
sudo install -m 0644 tools/systemd/feedvault.service /etc/systemd/system/feedvault.service
```

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now feedvault.socket
sudo systemctl enable --now feedvault.service

# Add to Nginx config and test with:
curl --unix-socket /run/feedvault/feedvault.sock https://feedvault.se
```
