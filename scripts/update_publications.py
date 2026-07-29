import requests
from urllib.parse import quote

ORCID = "0000-0002-6089-032X"

headers = {
    "Accept": "application/json"
}

url = f"https://pub.orcid.org/v3.0/{ORCID}/works"

works = requests.get(url, headers=headers).json()["group"]

papers = []

for work in works:

    summary = work["work-summary"][0]

    put_code = summary["put-code"]

    paper = requests.get(
        f"https://pub.orcid.org/v3.0/{ORCID}/work/{put_code}",
        headers=headers,
    ).json()

    title = (
        paper.get("title", {})
             .get("title", {})
             .get("value", "Untitled")
    )

    year = (
        paper.get("publication-date", {})
             .get("year", {})
             .get("value", "")
    )

    journal = (
        paper.get("journal-title", {})
             .get("value", "")
    )

    doi = ""

    for ext in paper.get("external-ids", {}).get("external-id", []):
        if ext.get("external-id-type", "").lower() == "doi":
            doi = ext.get("external-id-value", "")
            break

    papers.append({
        "title": title,
        "journal": journal,
        "year": int(year) if year.isdigit() else 0,
        "doi": doi,
    })

papers.sort(key=lambda p: p["year"], reverse=True)

latest = papers[:3]

content = ""

for paper in latest:

    scholar = (
        "https://scholar.google.com/scholar?q="
        + quote(paper["title"])
    )

    content += f"### {paper['year']}\n"
    content += f"**{paper['title']}**\n\n"

    if paper["journal"]:
        content += f"*{paper['journal']}*\n\n"

    links = []

    if paper["doi"]:
        links.append(f"[📄 DOI](https://doi.org/{paper['doi']})")

    links.append(f"[🎓 Google Scholar]({scholar})")

    content += " • ".join(links)

    content += "\n\n---\n\n"

with open("README.md", encoding="utf-8") as f:
    readme = f.read()

start = "<!-- PUBLICATIONS:START -->"
end = "<!-- PUBLICATIONS:END -->"

before = readme.split(start)[0]
after = readme.split(end)[1]

new_readme = before + start + "\n\n" + content + end + after

with open("README.md", "w", encoding="utf-8") as f:
    f.write(new_readme)
