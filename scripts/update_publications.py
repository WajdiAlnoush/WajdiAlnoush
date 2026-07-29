import requests
from urllib.parse import quote

ORCID = "0000-0002-6089-032X"

HEADERS = {
    "Accept": "application/json"
}


def highlight_me(name):
    """
    Underline my name regardless of formatting.
    """

    normalized = (
        name.lower()
            .replace(".", "")
            .replace(",", "")
            .strip()
    )

    if "alnoush" in normalized:
        #return f"<u>{name}</u>"
        return f"<ins>{name}</ins>"

    return name


# -----------------------------
# Retrieve publications from ORCID
# -----------------------------

works = requests.get(f"https://pub.orcid.org/v3.0/{ORCID}/works", headers=HEADERS).json()["group"]

papers = []

for work in works:
    summary = work["work-summary"][0]
    put_code = summary["put-code"]
    paper = requests.get(f"https://pub.orcid.org/v3.0/{ORCID}/work/{put_code}",headers=HEADERS).json()
    title = (paper.get("title", {}).get("title", {}).get("value", "Untitled"))
    journal = (paper.get("journal-title", {}).get("value", ""))
    year = (paper.get("publication-date", {}).get("year", {}).get("value", ""))
    doi = ""

    for ext in paper.get("external-ids", {}).get("external-id", []):
        if ext.get("external-id-type", "").lower() == "doi":
            doi = ext.get("external-id-value", "")
            break

    authors = []

    for contributor in paper.get("contributors", {}).get("contributor", []):
        credit_name = contributor.get("credit-name")
        if credit_name and "value" in credit_name:
            authors.append(credit_name["value"])

    papers.append({
        "title": title,
        "journal": journal,
        "year": int(year) if year.isdigit() else 0,
        "doi": doi,
        "authors": authors
    })


# -----------------------------
# Sort newest first
# -----------------------------

papers.sort(key=lambda p: p["year"], reverse=True)
latest = papers[:3]


# -----------------------------
# Build README content
# -----------------------------

content = ""

for paper in latest:

    scholar = (
        "https://scholar.google.com/scholar?q="
        + quote(paper["title"])
    )

    publisher = (
        f"https://doi.org/{paper['doi']}"
        if paper["doi"] else ""
    )

    content += f"### {paper['title']}\n\n"

    # Authors
    if paper["authors"]:

        display_authors = [
            highlight_me(a)
            for a in paper["authors"]
        ]

        if len(display_authors) > 12:

            display_authors = display_authors[:12]
            display_authors.append("*et al.*")

        content += ", ".join(display_authors)
        content += "\n\n"

    # Journal + Year
    if paper["journal"]:
        content += f"*{paper['journal']}*, {paper['year']}\n\n"
    # Links
    links = []

    if paper["doi"]:
        links.append(f"[📄 DOI](https://doi.org/{paper['doi']})")

    links.append(f"[🎓 Google Scholar]({scholar})")

    if publisher:
        links.append(f"[🌐 Publisher]({publisher})")

    content += " • ".join(links)
    content += "\n\n---\n\n"


# -----------------------------
# Update README
# -----------------------------

with open("README.md", "r", encoding="utf-8") as f:

    readme = f.read()

START = "<!-- PUBLICATIONS:START -->"
END = "<!-- PUBLICATIONS:END -->"

before = readme.split(START)[0]
after = readme.split(END)[1]

new_readme = before + START + "\n\n" + content + END + after

with open("README.md", "w", encoding="utf-8") as f:

    f.write(new_readme)
