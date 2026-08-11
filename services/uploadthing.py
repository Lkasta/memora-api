"""Thin client for the one UploadThing API call this backend needs: removing
files that no memory references any more.

Deliberately built on ``urllib`` rather than ``requests`` so tracking images
doesn't add a dependency to a backend that otherwise has none for HTTP.
"""

import base64
import binascii
import json
import logging
import urllib.error
import urllib.request
from typing import Iterable, Optional, Set
from urllib.parse import urlparse

from config import Config

logger = logging.getLogger(__name__)

_TIMEOUT_SECONDS = 10


def extract_file_key(url: Optional[str]) -> Optional[str]:
    """Pull the UploadThing file key out of a file URL.

    Both URL shapes the app has produced end in ``/f/<key>``:
    ``https://utfs.io/f/<key>`` (legacy) and ``https://<appId>.ufs.sh/f/<key>``
    (current). Anything else - a data URI, an image hotlinked from another
    site - has no key here and returns None.
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
    except ValueError:
        return None

    if parsed.scheme not in ("http", "https"):
        return None

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) >= 2 and parts[-2] == "f":
        return parts[-1]
    return None


def _api_key() -> Optional[str]:
    """Resolve the ``sk_...`` key used to authenticate against UploadThing.

    ``UPLOADTHING_TOKEN`` is base64-encoded JSON that wraps the real key - the
    same variable the Next.js frontend already sets, so a deployment only has
    to copy the value across. ``UPLOADTHING_API_KEY`` (the raw key) is
    accepted as an alternative.
    """
    if Config.UPLOADTHING_API_KEY:
        return Config.UPLOADTHING_API_KEY

    token = Config.UPLOADTHING_TOKEN
    if not token:
        return None

    try:
        # Tokens in the wild are often unpadded base64.
        padded = token + "=" * (-len(token) % 4)
        decoded = json.loads(base64.b64decode(padded))
    except (binascii.Error, ValueError, TypeError):
        logger.warning(
            "UPLOADTHING_TOKEN is not valid base64-encoded JSON; files cannot be deleted"
        )
        return None

    api_key = decoded.get("apiKey") if isinstance(decoded, dict) else None
    if not api_key:
        logger.warning("UPLOADTHING_TOKEN has no 'apiKey' field; files cannot be deleted")
    return api_key


def delete_files(file_keys: Iterable[str]) -> bool:
    """Delete the given files from UploadThing storage.

    Best-effort on purpose: the database rows are already gone by the time
    this runs, so a storage hiccup should never turn the user's save or delete
    into an error. The worst case is a file left orphaned in the bucket, which
    is logged loudly enough to be cleaned up later.
    """
    keys: Set[str] = {key for key in file_keys if key}
    if not keys:
        return True

    api_key = _api_key()
    if not api_key:
        logger.warning(
            "UploadThing credentials are not configured; %d file(s) stay in storage: %s",
            len(keys),
            ", ".join(sorted(keys)),
        )
        return False

    request = urllib.request.Request(
        f"{Config.UPLOADTHING_API_URL}/v6/deleteFiles",
        data=json.dumps({"fileKeys": sorted(keys)}).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-uploadthing-api-key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
            body = json.loads(response.read() or b"{}")
    except (urllib.error.URLError, OSError, ValueError) as exc:
        logger.warning(
            "UploadThing delete failed for %s: %s", ", ".join(sorted(keys)), exc
        )
        return False

    logger.info(
        "Deleted %s file(s) from UploadThing: %s",
        body.get("deletedCount", "?"),
        ", ".join(sorted(keys)),
    )
    return True
