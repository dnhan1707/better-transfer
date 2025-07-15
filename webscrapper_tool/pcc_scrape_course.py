"""
scrape_all_courses.py
Python ≥3.9   pip install beautifulsoup4 requests tqdm
"""

import json, re, time, pathlib, requests
from bs4 import BeautifulSoup
from tqdm import tqdm               # simple progress bar

BASE = "https://curriculum.pasadena.edu/course-descriptions"
COURSE_CODE = re.compile(r"[A-Z]{2,4}\s?\d{3}[A-Z]?")

# ------------------------------------------------------------
def parse_course(block: BeautifulSoup, dept: str) -> dict | None:
    code_tag  = block.select_one("span.detail-code strong")
    name_tag  = block.select_one("span.detail-title strong")
    units_tag = block.select_one("span.detail-hours_html strong")

    if not code_tag:
        return None
    code = code_tag.text.strip().replace("\xa0", " ")
    if code.endswith("H") or "HONORS" in name_tag.text:
        return None

    units = 0.0
    if units_tag and (m := re.search(r"\d+\.?\d*", units_tag.text)):
        units = float(m.group())

    prereq_span = block.find("strong", string=re.compile("Prerequisite", re.I))
    prereq_text = prereq_span.find_next("em").get_text(" ", strip=True) if prereq_span else ""

    assessment_allow = bool(re.search(r"(placement|assessment)", prereq_text, re.I))

    groups = re.split(r"\bor\b", prereq_text, flags=re.I)
    prereqs = []
    for g in groups:
        codes = COURSE_CODE.findall(g)
        if codes:
            prereqs.append(tuple(c.replace("\xa0", " ") for c in codes))

    return {
        code: {
            "name": name_tag.text.strip().title(),
            "units": units,
            "difficulty": 3,
            "assessment_allow": assessment_allow,
            "prerequisites": prereqs,
            "department": dept,
        }
    }

# ------------------------------------------------------------
def scrape_department(slug: str) -> dict:
    url = f"{BASE}/{slug}/"
    soup = BeautifulSoup(requests.get(url, timeout=30).text, "html.parser")
    catalog = {}
    for block in soup.select("div.courseblock"):
        item = parse_course(block, slug)
        if item:
            catalog.update(item)
    return catalog

# ------------------------------------------------------------
def discover_slugs() -> list[str]:
    """Grab the list of slugs directly from the site so you never hard-code it."""
    soup = BeautifulSoup(requests.get(BASE, timeout=30).text, "html.parser")
    links = soup.select("main a[href^='/course-descriptions/']")
    slugs = sorted({a["href"].split("/")[-2] for a in links})
    return slugs

# ------------------------------------------------------------
if __name__ == "__main__":
    out_dir = pathlib.Path("pcc_courses")
    out_dir.mkdir(exist_ok=True)

    slugs = discover_slugs()
    print(f"Found {len(slugs)} departments: {' '.join(slugs)}")

    all_courses = {}
    for slug in tqdm(slugs, desc="Scraping"):
        data = scrape_department(slug)
        if data:
            all_courses.update(data)
            (out_dir / f"{slug}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        time.sleep(0.5)          # polite pause

    pathlib.Path("all_courses.json").write_text(
        json.dumps(all_courses, indent=2), encoding="utf-8"
    )
    print(f"\nSaved {len(all_courses)} total courses.")
