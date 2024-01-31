"""https://docs.djangoproject.com/en/5.0/topics/forms/."""

from __future__ import annotations

from django import forms


class UploadOPMLForm(forms.Form):
    """Upload OPML.

    Args:
        forms: A collection of Fields, plus their associated data.
    """

    file = forms.FileField(
        label="Select an OPML file",
        help_text="max. 100 megabytes",
        widget=forms.FileInput(attrs={"accept": ".opml"}),
    )
