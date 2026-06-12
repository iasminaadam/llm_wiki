import os

from config import (
    START_URLS,
    MAX_DEPTH,
    URLS_FILE
)

from tools import (
    get_links,
    extract_markdown,
    save_markdown
)

def discover_urls():

    visited = set()

    queue = [
        (url, 0)
        for url in START_URLS
    ]

    while queue:

        current_url, depth = queue.pop(0)

        if current_url in visited:
            continue

        visited.add(current_url)

        print(
            f"[{depth}] Discovering: "
            f"{current_url}"
        )

        if depth < MAX_DEPTH:

            links = get_links(
                current_url
            )

            for link in links:

                if link not in visited:

                    queue.append(
                        (link, depth + 1)
                    )

    with open(
        URLS_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        for url in sorted(visited):
            f.write(url + "\n")

    print(
        f"\nSaved {len(visited)} URLs "
        f"to {URLS_FILE}"
    )

def extract_all_urls():

    if not os.path.exists(URLS_FILE):

        print(
            f"{URLS_FILE} not found."
        )

        return

    with open(
        URLS_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        urls = [
            line.strip()
            for line in f
            if line.strip()
        ]

    total = len(urls)

    print(
        f"Processing {total} URLs..."
    )

    for i, url in enumerate(urls, start=1):

        print(
            f"[{i}/{total}] "
            f"Extracting: {url}"
        )

        markdown = extract_markdown(url)

        if not markdown:

            print(
                "Skipped: extraction failed"
            )
            continue

        if len(markdown) < 100:

            print(
                "Skipped: content too short"
            )
            continue

        save_markdown(
            url,
            markdown
        )

    print("\nExtraction complete.")

if __name__ == "__main__":
    discover_urls()
    extract_all_urls()