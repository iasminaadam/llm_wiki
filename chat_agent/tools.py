#tools.py
import requests
import trafilatura
from bs4 import BeautifulSoup
from urllib.parse import quote    
import re
from config import *
import os
from datetime import datetime

def read_wiki_pages(files):
    """
    Citește una sau mai multe pagini wiki.
    Limitat la primele 3 pagini.
    """

    # Limit to first 3 files
    files = files[:3]
    
    result = []

    for file_name in files:

        file_name = file_name.strip(
            " '\"`"
        )

        if not file_name.endswith(".md"):
            file_name += ".md"

        path = os.path.join(
            WIKI_DIR,
            file_name
        )

        if not os.path.exists(path):

            result.append(
                f"\n--- {file_name} ---\n"
                f"❌ Fișier inexistent"
            )
            continue

        try:

            with open(
                path,
                "r",
                encoding="utf-8"
            ) as f:

                content = f.read()

            result.append(
                f"\n--- {file_name} ---\n"
                f"{content}"
            )

        except Exception as e:

            result.append(
                f"\n--- {file_name} ---\n"
                f"❌ {str(e)}"
            )

    return "\n".join(result)

def search_site(
    faculty: str,
    query: str,
    max_results: int = 10
):

    faculty = faculty.lower().strip()

    if faculty not in FACULTY_DOMAINS:
        return (
            f"❌ Facultate necunoscută: "
            f"{faculty}"
        )

    url = (
        FACULTY_DOMAINS[faculty]
        + "/?s="
        + quote(query)
    )

    try:

        html = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                "Mozilla/5.0"
            }
        ).text

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        results = []

        for a in soup.find_all(
            "a",
            href=True
        ):

            href = a["href"]

            if faculty not in href:
                continue

            if href not in results:
                results.append(href)

        if not results:
            return (
                "ℹ️ Niciun rezultat."
            )

        return "\n".join(
            results[:max_results]
        )

    except Exception as e:

        return (
            f"❌ SEARCH_SITE error: "
            f"{str(e)}"
        )


def read_url(url: str):

    try:

        downloaded = trafilatura.fetch_url(
            url
        )

        if not downloaded:
            return (
                "❌ Nu am putut descărca pagina."
            )

        text = trafilatura.extract(
            downloaded,
            output_format="markdown",
            include_links=True,
            include_formatting=True
        )

        if not text:
            return (
                "❌ Nu am putut extrage conținut."
            )

        return text[:15000]

    except Exception as e:

        return (
            f"❌ READ_URL error: "
            f"{str(e)}"
        )

TOOL_PATTERN = re.compile(
    r"<tool>\s*(.*?)\s*</tool>",
    re.DOTALL
)

def execute_tool(tool_text):

    lines = [
        x.strip()
        for x in tool_text.splitlines()
        if x.strip()
    ]

    if not lines:
        return "❌ Tool gol."

    tool_name = lines[0]

    # ---------------------------------
    # READ_WIKI
    # ---------------------------------

    if tool_name == "READ_WIKI":

        files = lines[1:]

        if not files:
            return (
                "❌ READ_WIKI necesită "
                "cel puțin un fișier."
            )

        return read_wiki_pages(files)

    # ---------------------------------
    # SEARCH_WEB
    # ---------------------------------

    elif tool_name == "SEARCH_WEB":

        if len(lines) < 3:
            return (
                "❌ SEARCH_WEB necesită:\n"
                "facultate\n"
                "query"
            )

        faculty = lines[1]

        query = " ".join(
            lines[2:]
        )

        return search_site(
            faculty,
            query
        )

    # ---------------------------------
    # READ_WEB_PAGE
    # ---------------------------------

    elif tool_name == "READ_WEB_PAGE":

        if len(lines) < 2:
            return (
                "❌ READ_WEB_PAGE "
                "necesită URL."
            )

        url = lines[1]

        return read_url(url)

    # ---------------------------------

    elif tool_name == "GET_DATE":

        now = datetime.now()
        return (
            "📅 Data curentă este:\n"
            f"{now.strftime('%Y-%m-%d')}\n\n"
            f"⏰ Ora curentă este:\n{now.strftime('%H:%M:%S')}"
        )

    return (
        f"❌ Tool necunoscut: "
        f"{tool_name}"
    )