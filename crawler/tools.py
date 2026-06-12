import os
import trafilatura
from bs4 import BeautifulSoup

from urllib.parse import (
    urljoin,
    urlparse
)

from config import OUTPUT_DIR
from helpers import (
    clean_filename,
    is_valid_link
)

def get_links(url: str):

    try:

        html = trafilatura.fetch_url(url)

        if not html:
            return []

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        base_domain = urlparse(
            url
        ).netloc

        links = set()

        for a in soup.find_all(
            "a",
            href=True
        ):

            href = a["href"]

            full_url = urljoin(
                url,
                href
            )

            clean = (
                full_url
                .split("#")[0]
                .rstrip("/")
            )

            if is_valid_link(
                base_domain,
                clean
            ):
                links.add(clean)

        return list(links)

    except Exception as e:

        print(
            f"Error reading links from {url}: {e}"
        )

        return []
    
def extract_markdown(url: str):

    try:

        downloaded = trafilatura.fetch_url(url)

        if not downloaded:
            return None

        soup = BeautifulSoup(
            downloaded,
            "html.parser"
        )

        for tag in soup([
            "nav",
            "header",
            "footer",
            "aside",
            "script",
            "style"
        ]):
            tag.decompose()

        markdown = trafilatura.extract(
            str(soup),
            output_format="markdown",
            include_links=True,
            include_formatting=True,
            favor_precision=True
        )

        if not markdown:
            return None

        return markdown.strip()

    except Exception as e:

        print(
            f"Error extracting {url}: {e}"
        )

        return None
    
def save_markdown(
    url: str,
    content: str
):

    filename = clean_filename(url)

    path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    with open(
        path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            f"# Source\n\n{url}\n\n---\n\n"
        )

        f.write(content)

    print(f"Saved: {path}")

