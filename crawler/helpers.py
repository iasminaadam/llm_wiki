import re
import hashlib

from urllib.parse import urlparse

from config import (
    KEYWORDS,
    BAD_KEYWORDS
)

def clean_filename(url: str) -> str:

    parsed = urlparse(url)

    path = parsed.path.strip("/")

    if not path:
        path = "index"

    raw_name = f"{parsed.netloc}_{path}"

    raw_name = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        raw_name
    )

    short_hash = hashlib.md5(
        url.encode()
    ).hexdigest()[:8]

    return f"{raw_name}_{short_hash}.md"


def is_valid_link(
    base_domain: str,
    link: str
) -> bool:

    parsed = urlparse(link)

    if parsed.scheme not in ["http", "https"]:
        return False

    if base_domain not in parsed.netloc:
        return False

    lower = link.lower()

    if any(
        bad in lower
        for bad in BAD_KEYWORDS
    ):
        return False

    if KEYWORDS:
        if not any(
            k in lower
            for k in KEYWORDS
        ):
            return False

    return True