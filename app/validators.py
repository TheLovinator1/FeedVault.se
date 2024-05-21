from urllib.parse import ParseResult, urlparse


def uri_validator(url: str) -> bool:
    """Validate a URI.

    Args:
        url: The URI to validate.

    Returns:
        True if the URI is valid, False otherwise.
    """
    try:
        result: ParseResult = urlparse(url)
        return all([result.scheme, result.netloc])
    except AttributeError:
        return False
