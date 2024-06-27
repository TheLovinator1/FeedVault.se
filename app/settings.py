from __future__ import annotations

from pathlib import Path

from platformdirs import user_data_dir

DATA_DIR: str = user_data_dir(
    appname="FeedVault",
    appauthor="TheLovinator",
    roaming=True,
)
DB_PATH: Path = Path(DATA_DIR) / "reader.sqlite"
MEDIA_ROOT: Path = Path(DATA_DIR) / "uploads"
