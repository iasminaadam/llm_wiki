import os

START_URLS = [
    "https://www.tuiasi.ro/admitere",
    "https://ac.tuiasi.ro/admitere",
    "https://arh.tuiasi.ro/admitere-2025/",
    "https://etti.tuiasi.ro/admitere",
    "https://icpm.tuiasi.ro/admitere/",
    "https://ci.tuiasi.ro/admitere/",
    "https://cmmi.tuiasi.ro/admitere/",
    "https://hgim.tuiasi.ro/admitere/",
    "https://ieeia.tuiasi.ro/admitere/",
    "https://mec.tuiasi.ro/admitere/",
    "https://sim.tuiasi.ro/admitere/",
    "https://dima.tuiasi.ro/admitere/"
]

MAX_DEPTH = 5

OUTPUT_DIR = "../wiki/raw"

KEYWORDS = [
    "licenta",
    "master",
    "doctorat",
    "calendar",
    "taxe",
    "acte",
    "admitere",
    "candidati"
]

BAD_KEYWORDS = [
    "anunt",
    "finalizare",
    "anunturi",
    "xls",
    "teze",
    "docx",
    "plan",
    "pdf",
    "uploads",
    "download",
    "postuniversitare",
    "2000",
    "2001",
    "2002",
    "2003",
    "2004",
    "2005",
    "2006",
    "2007",
    "2008",
    "2009",
    "2010",
    "2011",
    "2012",
    "2013",
    "2014",
    "2015",
    "2016",
    "2017",
    "2018",
    "2019",
    "2020",
    "2021",
    "2022",
    "2023",
    "2024",
    "2025"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

URLS_FILE = "urls.txt"