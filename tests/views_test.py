from typing import TYPE_CHECKING

from fastapi.testclient import TestClient

from app.main import app

if TYPE_CHECKING:
    from httpx import Response

client = TestClient(app)


def test_read_main() -> None:
    """Test the main page."""
    # Send a GET request to the app
    response: Response = client.get("/")

    # Check if the response status code is 200 OK
    assert response.status_code == 200

    # Check if the response contains the expected text
    html_text = '<a href="https://en.wikipedia.org/wiki/Web_feed">web feeds</a>.'
    assert html_text in response.text
