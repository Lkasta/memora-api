"""Small helpers shared across route modules."""

from typing import Optional


def clean_image_url(url: Optional[str]) -> Optional[str]:
    """Strip a stray ``data:image/...;base64,`` prefix off an otherwise
    normal HTTP(S) URL.

    A handful of memories/profiles have ``image_url`` values shaped like
    ``data:image/png;base64,https://...`` from an old client-side upload bug
    that glued a data-URI prefix onto the real URL instead of replacing it.
    This recovers the real URL so the API never hands back a broken value.
    Anything else (a clean URL, a real base64 payload, or ``None``) passes
    through untouched.
    """
    if url and url.startswith("data:image/") and "base64,http" in url:
        return url.split("base64,", 1)[1]
    return url
