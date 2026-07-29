import requests

ORCID = "0000-0002-6089-032X"

url = f"https://pub.orcid.org/v3.0/{ORCID}/works"

headers = {
    "Accept": "application/json"
}

works = requests.get(url, headers=headers).json()["group"]

papers = []

for work in works:

    summary = work["work-summary"][0]

    title = summary["title"]["title"]["value"]

    year = summary.get("publication-date", {}).get("year", {}).get("value", "")

    put_code = summary["put-code"]

    paper = requests.get(
        f"https://pub.orcid.org/v3.0/{ORCID}/work/{put_code}",
        headers=headers
    ).json()

    doi = ""

    if "external-ids" in paper:

        for ext in paper["external-ids"]["external-id"]:

            if ext["external-id-type"].lower() == "doi":

                doi = ext["external-id-value"]

    papers.append((year, title, doi))

papers.sort(reverse=True)

latest = papers[:3]

with open("README.md") as f:
    readme = f.read()

start = "<!-- PUBLICATIONS:START -->"
end = "<!-- PUBLICATIONS:END -->"

content = ""

for year, title, doi in latest:

    if doi:
        content += f"- **{title}** ({year})  \n"
        content += f"  https://doi.org/{doi}\n\n"
    else:
        content += f"- **{title}** ({year})\n\n"

before = readme.split(start)[0]
after = readme.split(end)[1]

new_readme = before + start + "\n" + content + end + after

with open("README.md","w") as f:
    f.write(new_readme)
