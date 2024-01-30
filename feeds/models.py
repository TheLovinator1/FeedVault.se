"""Django models for the feeds app."""

from __future__ import annotations

import typing

from django.contrib.auth.models import User
from django.db import models

FEED_VERSION_CHOICES: tuple = (
    ("atom", "Atom (unknown or unrecognized version)"),
    ("atom01", "Atom 0.1"),
    ("atom02", "Atom 0.2"),
    ("atom03", "Atom 0.3"),
    ("atom10", "Atom 1.0"),
    ("cdf", "CDF"),
    ("rss", "RSS (unknown or unrecognized version)"),
    ("rss090", "RSS 0.90"),
    ("rss091n", "Netscape RSS 0.91"),
    ("rss091u", "Userland RSS 0.91"),
    ("rss092", "RSS 0.92"),
    ("rss093", "RSS 0.93"),
    ("rss094", "RSS 0.94 (no accurate specification is known to exist)"),
    ("rss10", "RSS 1.0"),
    ("rss20", "RSS 2.0"),
)


class Author(models.Model):
    """Details about the author of a feed.

    Comes from the following elements:
    - /atom03:feed/atom03:author
    - /atom10:feed/atom10:author
    - /rdf:RDF/rdf:channel/dc:author
    - /rdf:RDF/rdf:channel/dc:creator
    - /rss/channel/dc:author
    - /rss/channel/dc:creator
    - /rss/channel/itunes:author
    - /rss/channel/managingEditor
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.TextField(blank=True, help_text="The name of the feed author.")
    email = models.EmailField(blank=True, help_text="The email address of the feed author.")

    # If this is a relative URI, it is resolved according to a set of rules:
    # https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    href = models.URLField(
        blank=True,
        help_text="The URL of the feed author. This can be the author's home page, or a contact page with a webmail form.",  # noqa: E501
    )

    class Meta:
        """Author meta."""

        verbose_name: typing.ClassVar[str] = "Feed author"
        verbose_name_plural: typing.ClassVar[str] = "Feed authors"
        db_table_comment: typing.ClassVar[str] = "Details about the author of a feed."

    def __str__(self: Author) -> str:
        """Author."""
        return f"{self.name} {self.email} {self.href}"


class Contributor(models.Model):
    """Details about the contributor to a feed.

    Comes from the following elements:
    - /atom03:feed/atom03:contributor
    - /atom10:feed/atom10:contributor
    - /rss/channel/dc:contributor
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.TextField(blank=True, help_text="The name of this contributor.")
    email = models.EmailField(blank=True, help_text="The email address of this contributor.")

    # If this is a relative URI, it is resolved according to a set of rules:
    # https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    href = models.URLField(
        blank=True,
        help_text="The URL of this contributor. This can be the contributor's home page, or a contact page with a webmail form.",  # noqa: E501
    )

    class Meta:
        """Contributor meta."""

        verbose_name: typing.ClassVar[str] = "Feed contributor"
        verbose_name_plural: typing.ClassVar[str] = "Feed contributors"
        db_table_comment: typing.ClassVar[str] = "Details about the contributor to a feed."

    def __str__(self: Contributor) -> str:
        """Contributor."""
        return f"{self.name} {self.email} {self.href}"


class Cloud(models.Model):
    """No one really knows what a cloud is.

    Comes from the following elements:
    - /rss/channel/cloud
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    domain = models.CharField(
        max_length=255,
        blank=True,
        help_text="The domain of the cloud. Should be just the domain name, not including the http:// protocol. All clouds are presumed to operate over HTTP. The cloud specification does not support secure clouds over HTTPS, nor can clouds operate over other protocols.",  # noqa: E501
    )
    port = models.CharField(
        max_length=255,
        blank=True,
        help_text="The port of the cloud. Should be an integer, but Universal Feed Parser currently returns it as a string.",  # noqa: E501
    )
    path = models.CharField(
        max_length=255,
        blank=True,
        help_text="The URL path of the cloud.",
    )
    register_procedure = models.CharField(
        max_length=255,
        blank=True,
        help_text="The name of the procedure to call on the cloud.",
    )
    protocol = models.CharField(
        max_length=255,
        blank=True,
        help_text="The protocol of the cloud. Documentation differs on what the acceptable values are. Acceptable values definitely include xml-rpc and soap, although only in lowercase, despite both being acronyms. There is no way for a publisher to specify the version number of the protocol to use. soap refers to SOAP 1.1; the cloud interface does not support SOAP 1.0 or 1.2. post or http-post might also be acceptable values; nobody really knows for sure.",  # noqa: E501
    )

    class Meta:
        """Cloud meta."""

        verbose_name: typing.ClassVar[str] = "Feed cloud"
        verbose_name_plural: typing.ClassVar[str] = "Feed clouds"
        db_table_comment: typing.ClassVar[str] = "No one really knows what a cloud is."

    def __str__(self: Cloud) -> str:
        """Cloud domain."""
        return f"{self.register_procedure} {self.protocol}://{self.domain}{self.path}:{self.port}"


class Generator(models.Model):
    """Details about the software used to generate the feed.

    Comes from the following elements:
    - /atom03:feed/atom03:generator
    - /atom10:feed/atom10:generator
    - /rdf:RDF/rdf:channel/admin:generatorAgent/@rdf:resource
    - /rss/channel/generator
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.TextField(blank=True, help_text="Human-readable name of the application used to generate the feed.")

    # If this is a relative URI, it is resolved according to a set of rules:
    # https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    href = models.URLField(
        blank=True,
        help_text="The URL of the application used to generate the feed.",
    )

    version = models.CharField(
        max_length=255,
        blank=True,
        help_text="The version number of the application used to generate the feed. There is no required format for this, but most applications use a MAJOR.MINOR version number.",  # noqa: E501
    )

    class Meta:
        """Generator meta."""

        verbose_name: typing.ClassVar[str] = "Feed generator"
        verbose_name_plural: typing.ClassVar[str] = "Feed generators"
        db_table_comment: typing.ClassVar[str] = "Details about the software used to generate the feed."

    def __str__(self: Generator) -> str:
        """Generator name."""
        return f"{self.name} {self.version} {self.href}"


class Image(models.Model):
    """A feed image can be a logo, banner, or a picture of the author.

    Comes from the following elements:
    - /rdf:RDF/rdf:image
    - /rss/channel/image

    Example:
    ```xml
        <image>
        <title>Feed logo</title>
        <url>http://example.org/logo.png</url>
        <link>http://example.org/</link>
        <width>80</width>
        <height>15</height>
        <description>Visit my home page</description>
        </image>
    ```

    This feed image could be rendered in HTML as this:
    ```html
    <a href="http://example.org/">
        <img src="http://example.org/logo.png"
        width="80"
        height="15"
        alt="Feed logo"
        title="Visit my home page">
    </a>
    ```
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    title = models.TextField(
        blank=True,
        help_text="The alternate text of the feed image, which would go in the alt attribute if you rendered the feed image as an HTML img element.",  # noqa: E501
    )

    # If this is a relative URI, it is resolved according to a set of rules:
    # https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    href = models.URLField(
        blank=True,
        help_text="The URL of the feed image itself, which would go in the src attribute if you rendered the feed image as an HTML img element.",  # noqa: E501
    )

    # If this is a relative URI, it is resolved according to a set of rules:
    # https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    link = models.URLField(
        blank=True,
        help_text="The URL which the feed image would point to. If you rendered the feed image as an HTML img element, you would wrap it in an a element and put this in the href attribute.",  # noqa: E501
    )

    width = models.IntegerField(
        default=0,
        help_text="The width of the feed image, which would go in the width attribute if you rendered the feed image as an HTML img element.",  # noqa: E501
    )

    height = models.IntegerField(
        default=0,
        help_text="The height of the feed image, which would go in the height attribute if you rendered the feed image as an HTML img element.",  # noqa: E501
    )

    description = models.TextField(
        blank=True,
        help_text="A short description of the feed image, which would go in the title attribute if you rendered the feed image as an HTML img element. This element is rare; it was available in Netscape RSS 0.91 but was dropped from Userland RSS 0.91.",  # noqa: E501
    )

    class Meta:
        """Image meta."""

        verbose_name: typing.ClassVar[str] = "Feed image"
        verbose_name_plural: typing.ClassVar[str] = "Feed images"
        db_table_comment: typing.ClassVar[str] = "A feed image can be a logo, banner, or a picture of the author."

    def __str__(self: Image) -> str:
        """Image title."""
        return f"{self.title} {self.href} {self.link} {self.width}x{self.height} {self.description}"


class Info(models.Model):
    """Details about the feed.

    Comes from the following elements:
        - /atom03:feed/atom03:info
        - /rss/channel/feedburner:browserFriendly
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # This element is generally ignored by feed readers.
    # If this contains HTML or XHTML, it is sanitized by default.
    # If this contains HTML or XHTML, certain (X)HTML elements within this value may
    # contain relative URI (Uniform Resource Identifier)'s. These relative URI's are
    # resolved according to a set of rules: https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    value = models.TextField(
        blank=True,
        help_text="Free-form human-readable description of the feed format itself. Intended for people who view the feed in a browser, to explain what they just clicked on.",  # noqa: E501
    )

    # For Atom feeds, the content type is taken from the type attribute, which defaults to text/plain if not specified.
    # For RSS feeds, the content type is auto-determined by inspecting the content, and defaults to text/html.
    # Note that this may cause silent data loss if the value contains plain text with angle brackets.
    # Future enhancement: some versions of RSS clearly specify that certain values default to text/plain,
    # and Universal Feed Parser should respect this, but it doesn't yet.
    info_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="The content type of the feed info. Most likely text/plain, text/html, or application/xhtml+xml.",
    )

    # Supposed to be a language code, but publishers have been known to publish random values like “English” or “German”. # noqa: E501
    # May come from the element's xml:lang attribute, or it may inherit from a parent element's xml:lang, or the Content-Language HTTP header # noqa: E501
    language = models.CharField(
        max_length=255,
        blank=True,
        help_text="The language of the feed info.",
    )

    # is only useful in rare situations and can usually be ignored. It is the original base URI for this value, as
    # specified by the element's xml:base attribute, or a parent element's xml:base, or the appropriate HTTP header,
    # or the URI of the feed. By the time you see it, Universal Feed Parser has already resolved relative links in all
    # values where it makes sense to do so. Clients should never need to manually resolve relative links.
    base = models.URLField(
        blank=True,
        help_text="The original base URI for links within the feed copyright.",
    )

    class Meta:
        """Info meta."""

        verbose_name: typing.ClassVar[str] = "Feed information"
        verbose_name_plural: typing.ClassVar[str] = "Feed information"
        db_table_comment: typing.ClassVar[str] = "Details about the feed."

    def __str__(self: Info) -> str:
        """Info value."""
        return f"{self.value} {self.info_type} {self.language} {self.base}"


class Link(models.Model):
    """A list of dictionaries with details on the links associated with the feed.

    Each link has a rel (relationship), type (content type), and href (the URL that the link points to).
    Some links may also have a title.

    Comes from
        /atom03:feed/atom03:link
        /atom10:feed/atom10:link
        /rdf:RDF/rdf:channel/rdf:link
        /rss/channel/link
    """

    # Atom 1.0 defines five standard link relationships and describes the process for registering others.
    # Here are the five standard rel values:
    #  alternate
    #  enclosure
    #  related
    #  self
    #  via
    rel = models.CharField(
        max_length=255,
        blank=True,
        help_text="The relationship of this feed link.",
    )

    link_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="The content type of the page that this feed link points to.",
    )

    href = models.URLField(
        blank=True,
        help_text="The URL of the page that this feed link points to.",
    )

    title = models.TextField(
        blank=True,
        help_text="The title of this feed link.",
    )

    class Meta:
        """Link meta."""

        verbose_name: typing.ClassVar[str] = "Feed link"
        verbose_name_plural: typing.ClassVar[str] = "Feed links"
        db_table_comment: typing.ClassVar[str] = (
            "A list of dictionaries with details on the links associated with the feed."
        )

    def __str__(self: Link) -> str:
        """Link href."""
        return f"{self.href}"


class Publisher(models.Model):
    """The publisher of the feed.

    Comes from the following elements:
        /rdf:RDF/rdf:channel/dc:publisher
        /rss/channel/dc:publisher
        /rss/channel/itunes:owner
        /rss/channel/webMaster
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    name = models.TextField(blank=True, help_text="The name of this feed's publisher.")
    email = models.EmailField(blank=True, help_text="The email address of this feed's publisher.")

    # If this is a relative URI, it is resolved according to a set of rules:
    # https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    href = models.URLField(
        blank=True,
        help_text="The URL of this feed's publisher. This can be the publisher's home page, or a contact page with a webmail form.",  # noqa: E501
    )

    class Meta:
        """Publisher meta."""

        verbose_name: typing.ClassVar[str] = "Feed publisher"
        verbose_name_plural: typing.ClassVar[str] = "Feed publishers"
        db_table_comment: typing.ClassVar[str] = "Details about the publisher of a feed."

    def __str__(self: Publisher) -> str:
        """Publisher."""
        return f"{self.name} {self.email} {self.href}"


class Rights(models.Model):
    """Details about the rights of a feed.

    For machine-readable copyright information, see feed.license.

    Comes from the following elements:
        /atom03:feed/atom03:copyright
        /atom10:feed/atom10:rights
        /rdf:RDF/rdf:channel/dc:rights
        /rss/channel/copyright
        /rss/channel/dc:rights
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # If this contains HTML or XHTML, it is sanitized by default.
    # If this contains HTML or XHTML, certain (X)HTML elements within this value may
    # contain relative URI (Uniform Resource Identifier)'s. These relative URI's are
    # resolved according to a set of rules: https://feedparser.readthedocs.io/en/latest/resolving-relative-links.html#advanced-base
    value = models.TextField(
        blank=True,
        help_text="A human-readable copyright statement for the feed.",
    )

    # For Atom feeds, the content type is taken from the type attribute, which defaults to text/plain if not specified.
    # For RSS feeds, the content type is auto-determined by inspecting the content, and defaults to text/html.
    # Note that this may cause silent data loss if the value contains plain text with angle brackets.
    # Future enhancement: some versions of RSS clearly specify that certain values default to text/plain,
    # and Universal Feed Parser should respect this, but it doesn't yet.
    rights_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="The content type of the feed copyright. Most likely text/plain, text/html, or application/xhtml+xml.",  # noqa: E501
    )

    # Supposed to be a language code, but publishers have been known to publish random values like “English” or “German”. # noqa: E501
    # May come from the element's xml:lang attribute, or it may inherit from a parent element's xml:lang, or the Content-Language HTTP header # noqa: E501
    language = models.CharField(
        max_length=255,
        blank=True,
        help_text="The language of the feed rights.",
    )

    base = models.URLField(
        blank=True,
        help_text="The original base URI for links within the feed copyright.",
    )

    class Meta:
        """Rights meta."""

        verbose_name: typing.ClassVar[str] = "Feed rights"
        verbose_name_plural: typing.ClassVar[str] = "Feed rights"
        db_table_comment: typing.ClassVar[str] = "Details about the rights of a feed."

    def __str__(self: Rights) -> str:
        """Rights value."""
        return f"{self.value} {self.rights_type} {self.language} {self.base}"


class Subtitle(models.Model):
    """A subtitle, tagline, slogan, or other short description of the feed.

    Comes from
        /atom03:feed/atom03:tagline
        /atom10:feed/atom10:subtitle
        /rdf:RDF/rdf:channel/dc:description
        /rdf:RDF/rdf:channel/rdf:description
        /rss/channel/dc:description
        /rss/channel/description
        /rss/channel/itunes:subtitle
    """

    value = models.TextField(
        blank=True,
        help_text="A subtitle, tagline, slogan, or other short description of the feed.",
    )

    subtitle_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="The content type of the feed subtitle. Most likely text/plain, text/html, or application/xhtml+xml.",
    )

    language = models.CharField(
        max_length=255,
        blank=True,
        help_text="The language of the feed subtitle.",
    )

    base = models.URLField(
        blank=True,
        help_text="The original base URI for links within the feed subtitle.",
    )

    class Meta:
        """Subtitle meta."""

        verbose_name: typing.ClassVar[str] = "Feed subtitle"
        verbose_name_plural: typing.ClassVar[str] = "Feed subtitles"
        db_table_comment: typing.ClassVar[str] = "A subtitle, tagline, slogan, or other short description of the feed."

    def __str__(self: Subtitle) -> str:
        """Subtitle value."""
        return f"{self.value} {self.subtitle_type} {self.language} {self.base}"


class Tags(models.Model):
    """A list of tags associated with the feed.

    Comes from
        /atom03:feed/dc:subject
        /atom10:feed/category
        /rdf:RDF/rdf:channel/dc:subject
        /rss/channel/category
        /rss/channel/dc:subject
        /rss/channel/itunes:category
        /rss/channel/itunes:keywords
    """

    term = models.TextField(
        blank=True,
        help_text="The category term (keyword).",
    )

    scheme = models.CharField(
        blank=True,
        max_length=255,
        help_text="The category scheme (domain).",
    )

    label = models.TextField(
        blank=True,
        help_text="A human-readable label for the category.",
    )

    class Meta:
        """Tags meta."""

        verbose_name: typing.ClassVar[str] = "Feed tag"
        verbose_name_plural: typing.ClassVar[str] = "Feed tags"
        db_table_comment: typing.ClassVar[str] = "A list of tags associated with the feed."

    def __str__(self: Tags) -> str:
        """Tag term."""
        return f"{self.term} {self.scheme} {self.label}"


class TextInput(models.Model):
    """A text input form. No one actually uses this. Why are you?

    Comes from the following elements:
        /rdf:RDF/rdf:textinput
        /rss/channel/textInput
        /rss/channel/textinput

    Example:
    This is a text input in a feed:
    ```xml
    <textInput>
    <title>Go!</title>
    <link>http://example.org/search</link>
    <name>keyword</name>
    <description>Search this site:</description>
    </textInput>
    ```

    This is how it could be rendered in HTML:
    ```html
    <form method="get" action="http://example.org/search">
    <label for="keyword">Search this site:</label>
    <input type="text" id="keyword" name="keyword" value="">
    <input type="submit" value="Go!">
    </form>
    ```
    """

    title = models.TextField(
        blank=True,
        help_text="The title of the text input form, which would go in the value attribute of the form's submit button.",  # noqa: E501
    )

    link = models.URLField(
        blank=True,
        help_text="The link of the script which processes the text input form, which would go in the action attribute of the form.",  # noqa: E501
    )

    name = models.TextField(
        blank=True,
        help_text="The name of the text input box in the form, which would go in the name attribute of the form's input box.",  # noqa: E501
    )

    description = models.TextField(
        blank=True,
        help_text="A short description of the text input form, which would go in the label element of the form.",
    )

    class Meta:
        """TextInput meta."""

        verbose_name: typing.ClassVar[str] = "Feed text input"
        verbose_name_plural: typing.ClassVar[str] = "Feed text inputs"
        db_table_comment: typing.ClassVar[str] = "A text input form. No one actually uses this. Why are you?"

    def __str__(self: TextInput) -> str:
        """TextInput title."""
        return f"{self.title} {self.link} {self.name} {self.description}"


class Title(models.Model):
    """Details about the title of a feed.

    Comes from the following elements:
        /atom03:feed/atom03:title
        /atom10:feed/atom10:title
        /rdf:RDF/rdf:channel/dc:title
        /rdf:RDF/rdf:channel/rdf:title
        /rss/channel/dc:title
        /rss/channel/title
    """

    value = models.TextField(
        blank=True,
        help_text="The title of the feed.",
    )

    title_type = models.CharField(
        max_length=255,
        blank=True,
        help_text="The content type of the feed title. Most likely text/plain, text/html, or application/xhtml+xml.",
    )

    language = models.CharField(
        max_length=255,
        blank=True,
        help_text="The language of the feed title.",
    )

    base = models.URLField(
        blank=True,
        help_text="The original base URI for links within the feed title.",
    )

    class Meta:
        """Title meta."""

        verbose_name: typing.ClassVar[str] = "Feed title"
        verbose_name_plural: typing.ClassVar[str] = "Feed titles"
        db_table_comment: typing.ClassVar[str] = "Details about the title of a feed."

    def __str__(self: Title) -> str:
        """Title value."""
        return f"{self.value} {self.title_type} {self.language} {self.base}"


class Feed(models.Model):
    """A feed."""

    url = models.URLField(
        unique=True,
        help_text="The feed URL.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    # Error tracking
    error = models.BooleanField(default=False)
    error_message = models.TextField(default="")
    error_at = models.DateTimeField(null=True)

    # bozo may not be present. Some platforms, such as Mac OS X 10.2 and some versions of FreeBSD, do not include an XML
    # parser in their Python distributions. Universal Feed Parser will still work on these platforms, but it will not be
    # able to detect whether a feed is well-formed. However, it can detect whether a feed's character encoding is
    # incorrectly declared. (This is done in Python, not by the XML parser.)
    # See: https://feedparser.readthedocs.io/en/latest/bozo.html#advanced-bozo
    bozo = models.BooleanField(default=False, help_text="Is the feed well-formed XML?")
    # bozo_exception will only be present if bozo is True.
    bozo_exception = models.TextField(
        default="",
        help_text="The exception raised when attempting to parse a non-well-formed feed.",
    )

    # The process by which Universal Feed Parser determines the character encoding of the feed is explained can be found here:  # noqa: E501
    # https://feedparser.readthedocs.io/en/latest/character-encoding.html#advanced-encoding
    # This element always exists, although it may be an empty string if the character encoding cannot be determined.
    encoding = models.CharField(
        max_length=255,
        default="",
        help_text="The character encoding that was used to parse the feed.",
    )

    # The purpose of etag is explained here: https://feedparser.readthedocs.io/en/latest/http-etag.html#http-etag
    etag = models.CharField(
        max_length=255,
        default="",
        help_text="The ETag of the feed, as specified in the HTTP headers.",
    )

    # Headers will only be present if the feed was retrieved from a web server. If the feed was parsed from a local file
    # or from a string in memory, headers will not be present.
    headers = models.TextField(
        default="",
        help_text="HTTP headers received from the web server when retrieving the feed.",
    )

    # href will only be present if the feed was retrieved from a web server. If the feed was parsed from a local file or
    # from a string in memory, href will not be present.
    href = models.URLField(
        default="",
        help_text="The final URL of the feed that was parsed. If the feed was redirected from the original requested address, href will contain the final (redirected) address.",  # noqa: E501
    )

    # last_modified will only be present if the feed was retrieved from a web server, and only if the web server
    # provided a Last-Modified HTTP header for the feed. If the feed was parsed from a local file or from a string
    # in memory, last_modified will not be present.
    last_modified = models.DateTimeField(
        null=True,
        help_text="The last-modified date of the feed, as specified in the HTTP headers.",
    )

    # The prefixes listed in the namespaces dictionary may not match the prefixes defined in the original feed.
    # See: https://feedparser.readthedocs.io/en/latest/namespace-handling.html#advanced-namespaces
    # This element always exists, although it may be an empty dictionary if the feed does not define any namespaces (such as an RSS 2.0 feed with no extensions).  # noqa: E501
    namespaces = models.TextField(
        default="",
        help_text="A dictionary of all XML namespaces defined in the feed, as {prefix: namespaceURI}.",
    )

    # If the feed was redirected from its original URL, status will contain the redirect status code, not the
    # final status code.
    # If status is 301, the feed was permanently redirected to a new URL. Clients should update
    # their address book to request the new URL from now on.
    # If status is 410, the feed is gone. Clients should stop polling the feed.
    # status will only be present if the feed was retrieved from a web server. If the feed was parsed from a local file
    # or from a string in memory, status will not be present.
    # TODO(TheLovinator): #1 We should change feed URL if we get a HTTP 301.
    # https://github.com/TheLovinator1/FeedVault/issues/1
    # TODO(TheLovinator): #2 We should stop polling a feed if we get a HTTP 410.
    # https://github.com/TheLovinator1/FeedVault/issues/2
    http_status_code = models.IntegerField(
        default=0,
        help_text="The HTTP status code that was returned by the web server when the feed was fetched.",
    )

    # The format and version of the feed.  the feed type is completely unknown, version will be an empty string.
    version = models.CharField(
        max_length=255,
        choices=FEED_VERSION_CHOICES,
        default="",
        help_text="The version of the feed, as determined by Universal Feed Parser.",
    )

    # /atom03:feed, /atom10:feed, /rdf:RDF/rdf:channel, /rss/channel
    feed_data = models.TextField(
        default="",
        help_text="A dictionary of data about the feed.",
    )

    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        null=True,
        help_text="The author of the feed.",
    )

    cloud = models.ForeignKey(
        Cloud,
        on_delete=models.CASCADE,
        null=True,
        help_text="Cloud enables realtime push notifications or distributed publish/subscribe communication for feeds.",
    )

    contributors = models.ManyToManyField(
        Contributor,
        help_text="A list of contributors (secondary authors) to this feed.",
    )

    # This element is rare. The reasoning was that in 25 years, someone will stumble on
    # an RSS feed and not know what it is, so we should waste everyone's bandwidth with
    # useless links until then. Most publishers skip it, and all clients ignore it. If
    # this is a relative URI, it is resolved according to a set of rules.
    # Comes from /rss/channel/docs
    docs = models.URLField(
        blank=True,
        help_text="A URL pointing to the specification which this feed conforms to.",
    )

    # Comes from /rdf:RDF/admin:errorReportsTo/@rdf:resource
    error_reports_to = models.EmailField(
        blank=True,
        help_text="An email address for reporting errors in the feed itself.",
    )

    # Comes from /atom10:feed/atom10:icon
    generator = models.ForeignKey(
        Generator,
        on_delete=models.CASCADE,
        null=True,
        help_text="Details about the software used to generate the feed.",
    )

    # If this is a relative URI, it is resolved according to a set of rules.
    # Comes from/atom03:feed/atom03:id or /atom10:feed/atom10:id
    feed_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="A globally unique identifier for this feed.",
    )

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        null=True,
        help_text="A feed image can be a logo, banner, or a picture of the author.",
    )

    info = models.ForeignKey(
        Info,
        on_delete=models.CASCADE,
        null=True,
        help_text="Details about the feed.",
    )

    # Comes from:
    #  /atom03:feed/@xml:lang
    #  /atom10:feed/@xml:lang
    #  /rdf:RDF/rdf:channel/dc:language
    #  /rss/channel/dc:language
    #  /rss/channel/language
    language = models.CharField(
        max_length=255,
        blank=True,
        help_text="The primary language of the feed.",
    )

    # Comes from /atom10:feed/atom10:link[@rel=”license”]/@href, /rdf:RDF/cc:license/@rdf:resource or /rss/channel/creativeCommons:license # noqa: E501
    license = models.URLField(
        blank=True,
        help_text="A URL pointing to the license of the feed.",
    )

    link = models.ForeignKey(
        Link,
        on_delete=models.CASCADE,
        null=True,
        help_text="A list of dictionaries with details on the links associated with the feed.",
    )

    # Comes from /atom10:feed/atom10:logo
    logo = models.URLField(
        blank=True,
        help_text="A URL to a graphic representing a logo for the feed.",
    )

    # Comes from /rss/channel/pubDate
    # See feed.published_parsed for a more useful version of this value.
    published = models.CharField(
        max_length=255,
        blank=True,
        help_text="The date the feed was published, as a string in the same format as it was published in the original feed.",  # noqa: E501
    )

    # Parsed version of feed.published. Feedparser gives us a standard Python 9-tuple.
    published_parsed = models.DateTimeField(
        null=True,
        help_text="The date the feed was published.",
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        null=True,
        help_text="The publisher of the feed.",
    )

    rights = models.ForeignKey(
        Rights,
        on_delete=models.CASCADE,
        null=True,
        help_text="Details about the rights of a feed.",
    )

    subtitle = models.ForeignKey(
        Subtitle,
        on_delete=models.CASCADE,
        null=True,
        help_text="A subtitle, tagline, slogan, or other short description of the feed.",
    )

    tags = models.ManyToManyField(
        Tags,
        help_text="A list of tags associated with the feed.",
    )

    text_input = models.ForeignKey(
        TextInput,
        on_delete=models.CASCADE,
        null=True,
        help_text="A text input form. No one actually uses this. Why are you?",
    )

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        null=True,
        help_text="Details about the title of a feed.",
    )

    # No one is quite sure what this means, and no one publishes feeds via file-sharing networks.
    # Some clients have interpreted this element to be some sort of inline caching mechanism, albeit one
    # that completely ignores the underlying HTTP protocol, its robust caching mechanisms, and the huge
    # amount of HTTP-savvy network infrastructure that understands them. Given the vague documentation,
    # it is impossible to say that this interpretation is any more ridiculous than the element itself.
    # Comes from /rss/channel/ttl
    ttl = models.CharField(
        max_length=255,
        blank=True,
        help_text='According to the RSS specification, “None"',
    )

    # if this key doesn't exist but feed.published does, the value of feed.published will be returned.
    updated = models.CharField(
        max_length=255,
        blank=True,
        help_text="The date the feed was last updated, as a string in the same format as it was published in the original feed.",  # noqa: E501
    )

    updated_parsed = models.DateTimeField(
        null=True,
        help_text="The date the feed was last updated.",
    )

    class Meta:
        """Feed meta."""

        verbose_name: typing.ClassVar[str] = "Feed"
        verbose_name_plural: typing.ClassVar[str] = "Feeds"
        db_table_comment: typing.ClassVar[str] = "A feed. This is the main model of the app."

    def __str__(self: Feed) -> str:
        """Feed URL."""
        return f"{self.url}"
