import os
import re
import pytest

from tools import (
    patch_index,
    patch_wiki_page,
    find_pages,
    search_links,
    execute_tool
)


@pytest.fixture
def wiki_env():

    import tools

    with pytest.MonkeyPatch.context() as mp:

        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:

            mp.setattr(tools, "WIKI_DIR", tmp)

            index_path = os.path.join(
                tmp,
                "index.md"
            )

            with open(
                index_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write("""
# Index

## Facultatea de Mecanică

## Facultatea de Automatică și Calculatoare
""")

            yield {
                "tmp": tmp,
                "index": index_path
            }


def test_add_link_under_existing_section(wiki_env):

    result = patch_index(
        "Facultatea de Mecanică",
        "* [[mec_taxe]] - taxe"
    )

    assert "Succes" in result

    content = open(
        wiki_env["index"],
        encoding="utf-8"
    ).read()

    assert "[[mec_taxe]]" in content


def test_duplicate_link_not_added(wiki_env):

    patch_index(
        "Facultatea de Mecanică",
        "* [[mec_taxe]] - taxe"
    )

    patch_index(
        "Facultatea de Mecanică",
        "* [[mec_taxe]] - taxe"
    )

    content = open(
        wiki_env["index"],
        encoding="utf-8"
    ).read()

    assert content.count(
        "[[mec_taxe]]"
    ) == 1


def test_missing_section_rejected(wiki_env):

    result = patch_index(
        "Sectiune Inventata",
        "* [[pagina]]"
    )

    assert "nu a fost găsită" in result


def test_create_missing_page(wiki_env):

    result = patch_wiki_page(
        "mec_taxe",
        "Taxe",
        "Taxa este 100 lei"
    )

    assert "nu exista" in result

    assert os.path.exists(
        os.path.join(
            wiki_env["tmp"],
            "mec_taxe.md"
        )
    )


def test_duplicate_content_not_added(wiki_env):

    patch_wiki_page(
        "mec_taxe",
        "Taxe",
        "Taxa este 100 lei"
    )

    patch_wiki_page(
        "mec_taxe",
        "Taxe",
        "Taxa este 100 lei"
    )

    page = os.path.join(
        wiki_env["tmp"],
        "mec_taxe.md"
    )

    content = open(
        page,
        encoding="utf-8"
    ).read()

    assert content.count(
        "Taxa este 100 lei"
    ) == 1


def test_find_pages(wiki_env):

    open(
        os.path.join(
            wiki_env["tmp"],
            "mec_taxe.md"
        ),
        "w"
    ).close()

    open(
        os.path.join(
            wiki_env["tmp"],
            "mec_calendar.md"
        ),
        "w"
    ).close()

    result = find_pages("mec")

    assert "mec_taxe.md" in result
    assert "mec_calendar.md" in result


def test_search_links(wiki_env):

    page = os.path.join(
        wiki_env["tmp"],
        "pagina.md"
    )

    with open(
        page,
        "w",
        encoding="utf-8"
    ) as f:

        f.write("""
[[calendar]]
[[taxe]]
[[calendar]]
""")

    result = search_links("pagina")

    assert "calendar" in result
    assert "taxe" in result

    assert result.count("calendar") == 1


def test_execute_read_page(wiki_env):

    page = os.path.join(
        wiki_env["tmp"],
        "test.md"
    )

    with open(
        page,
        "w",
        encoding="utf-8"
    ) as f:
        f.write("test")

    result = execute_tool("""
READ_PAGE
test.md
""")

    assert isinstance(
        result,
        str
    )

    assert "test" in result


def test_index_has_no_duplicate_sections(wiki_env):

    content = open(
        wiki_env["index"],
        encoding="utf-8"
    ).read()

    sections = re.findall(
        r"^### .*",
        content,
        re.MULTILINE
    )

    assert len(sections) == len(set(sections))
