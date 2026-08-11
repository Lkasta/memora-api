"""Keeps ``memory_images`` - and UploadThing storage - in step with the
images a memory actually references.

The flow every caller follows is the same:

1. mutate the memory (title/content/cover) as usual;
2. call :func:`sync_memory_images`, which rewrites the image rows and hands
   back the file keys nothing references any more;
3. ``db.session.commit()``;
4. pass those keys to :func:`services.uploadthing.delete_files`.

Step 4 comes *after* the commit on purpose: if the transaction rolls back, no
file has been destroyed for a save that never happened.
"""

import logging
from html.parser import HTMLParser
from typing import Iterable, List, Optional, Set

from models import MemoryImage, db
from services.uploadthing import extract_file_key

logger = logging.getLogger(__name__)


class _ImageSrcParser(HTMLParser):
    """Collects the ``src`` of every ``<img>`` in a fragment of HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: List[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag != "img":
            return
        src = dict(attrs).get("src")
        if src:
            self.sources.append(src)


def extract_content_image_urls(content: Optional[str]) -> List[str]:
    """Every ``<img src>`` in a memory body, in document order, deduplicated.

    The editor stores its document as HTML, so this is the only place that has
    to know that. Malformed markup is tolerated: a parse failure means "no
    images found", never a failed save.
    """
    if not content:
        return []

    parser = _ImageSrcParser()
    try:
        parser.feed(content)
        parser.close()
    except Exception:  # pylint: disable=broad-except
        logger.warning("Could not parse memory content for images", exc_info=True)

    seen: Set[str] = set()
    urls: List[str] = []
    for src in parser.sources:
        url = src.strip()
        if url and url not in seen:
            seen.add(url)
            urls.append(url)
    return urls


def orphaned_file_keys(candidate_keys: Iterable[str]) -> Set[str]:
    """Of the given file keys, the ones no memory references any more.

    The check matters because the same uploaded file can legitimately be
    referenced twice (a cover that is also embedded in the body, or an image
    copy-pasted into a second memory). Deleting the file the moment one
    reference goes away would break the others.
    """
    keys = {key for key in candidate_keys if key}
    if not keys:
        return set()

    still_referenced = {
        row.file_key
        for row in MemoryImage.query.filter(MemoryImage.file_key.in_(keys)).all()
    }
    return keys - still_referenced


def sync_memory_images(memory) -> Set[str]:
    """Rewrite ``memory``'s image rows to match what it currently references.

    Returns the UploadThing file keys that are now unreferenced everywhere and
    should be deleted from storage once the surrounding transaction commits.
    """
    desired = []
    if memory.image_url:
        desired.append((MemoryImage.SOURCE_COVER, memory.image_url))
    for url in extract_content_image_urls(memory.content):
        desired.append((MemoryImage.SOURCE_CONTENT, url))

    desired_keys = set(desired)
    existing = {(row.source, row.url): row for row in memory.images}

    dropped = existing.keys() - desired_keys
    removed_file_keys = {existing[key].file_key for key in dropped}
    for key in dropped:
        memory.images.remove(existing[key])

    for source, url in desired:
        if (source, url) not in existing:
            memory.images.append(
                MemoryImage(url=url, source=source, file_key=extract_file_key(url))
            )

    # Flush so the pending inserts/deletes are visible to the query below -
    # otherwise a key that just moved from one memory to another would look
    # unreferenced and get deleted out from under its new owner.
    db.session.flush()
    return orphaned_file_keys(removed_file_keys)


def memory_file_keys(memory) -> Set[str]:
    """Every UploadThing file key attached to a memory.

    Read this *before* deleting the memory; the rows go away with it.
    """
    return {row.file_key for row in memory.images if row.file_key}
