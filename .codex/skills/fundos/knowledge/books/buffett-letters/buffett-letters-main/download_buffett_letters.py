#!/usr/bin/env python3
"""
Download all Warren Buffett Berkshire Hathaway shareholder letters
and save them as markdown files in knowledge_base/mentors/warren_buffett/shareholder_letters/
"""

import os
import re
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

BASE_URL = "https://www.berkshirehathaway.com/letters"
INDEX_URL = f"{BASE_URL}/letters.html"
OUTPUT_DIR = Path(__file__).parent.parent / "knowledge_base" / "mentors" / "warren_buffett" / "shareholder_letters"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Encoding": "br, gzip, deflate",  # Required — server uses brotli compression
}


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def fetch_index():
    print(f"Fetching index: {INDEX_URL}")
    resp = requests.get(INDEX_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_letter_links(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)
        # Only process links that look like letter links (year-based)
        if not text:
            continue
        year_match = re.search(r"(19\d\d|20\d\d)", text)
        if not year_match:
            continue
        year = year_match.group(1)
        # Build full URL
        if href.startswith("http"):
            full_url = href
        elif href.startswith("/"):
            full_url = f"https://www.berkshirehathaway.com{href}"
        else:
            full_url = f"{BASE_URL}/{href}"
        is_pdf = href.lower().endswith(".pdf")
        links.append({"year": year, "url": full_url, "is_pdf": is_pdf, "text": text})
    # Deduplicate by year, keeping first occurrence
    seen = set()
    unique = []
    for link in links:
        if link["year"] not in seen:
            seen.add(link["year"])
            unique.append(link)
    return sorted(unique, key=lambda x: x["year"])


def html_to_markdown(html: str, year: str) -> str:
    """Convert raw HTML letter content to clean markdown."""
    soup = BeautifulSoup(html, "html.parser")
    # Remove script/style tags
    for tag in soup(["script", "style", "head"]):
        tag.decompose()
    # Try to find the main letter body
    body = soup.find("body") or soup
    # Get text with some structure
    lines = []
    for elem in body.descendants:
        if elem.name in ("h1", "h2", "h3"):
            lines.append(f"\n## {elem.get_text(strip=True)}\n")
        elif elem.name == "p":
            text = elem.get_text(separator=" ", strip=True)
            if text:
                lines.append(text + "\n")
        elif elem.name in ("li",):
            text = elem.get_text(separator=" ", strip=True)
            if text:
                lines.append(f"- {text}")
        elif elem.name == "br":
            lines.append("")
    # If the structured approach yields too little, fall back to full text
    content = "\n".join(lines).strip()
    if len(content) < 500:
        content = body.get_text(separator="\n", strip=True)
    # Clean up excessive blank lines
    content = re.sub(r"\n{3,}", "\n\n", content)
    return f"# Berkshire Hathaway Shareholder Letter {year}\n\n{content}\n"


def download_html_letter(url: str, year: str) -> str | None:
    print(f"  Fetching HTML: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        return html_to_markdown(resp.text, year)
    except Exception as e:
        print(f"  ERROR fetching {url}: {e}")
        return None


def download_pdf_letter(url: str, year: str) -> str | None:
    """Download PDF and extract text."""
    print(f"  Fetching PDF: {url}")
    try:
        import pdfplumber
    except ImportError:
        print("  pdfplumber not installed. Trying pypdf...")
        try:
            import pypdf
        except ImportError:
            print("  pypdf not installed either. Installing pdfplumber...")
            os.system("pip install pdfplumber -q")
            import pdfplumber

    pdf_path = OUTPUT_DIR / f"{year}_temp.pdf"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
        resp.raise_for_status()
        with open(pdf_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        # Extract text
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append(text)
            content = "\n\n".join(pages)
        except Exception:
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(pdf_path))
                pages = [page.extract_text() for page in reader.pages if page.extract_text()]
                content = "\n\n".join(pages)
            except Exception as e2:
                print(f"  ERROR extracting PDF text: {e2}")
                return None
        pdf_path.unlink(missing_ok=True)
        if not content.strip():
            return None
        content = re.sub(r"\n{3,}", "\n\n", content)
        return f"# Berkshire Hathaway Shareholder Letter {year}\n\n{content}\n"
    except Exception as e:
        print(f"  ERROR downloading PDF {url}: {e}")
        if pdf_path.exists():
            pdf_path.unlink(missing_ok=True)
        return None


def letter_already_saved(year: str) -> bool:
    return (OUTPUT_DIR / f"{year}.md").exists()


def save_letter(year: str, content: str):
    path = OUTPUT_DIR / f"{year}.md"
    path.write_text(content, encoding="utf-8")
    print(f"  Saved: {path.name}")


def create_index(letters: list[dict], saved_years: list[str]):
    """Create a README index file in the output directory."""
    lines = [
        "# Warren Buffett Shareholder Letters\n",
        "Annual letters from Warren Buffett to Berkshire Hathaway shareholders (1977 to present).\n",
        f"Total letters downloaded: {len(saved_years)}\n",
        "\n## Index\n",
    ]
    for letter in letters:
        year = letter["year"]
        if year in saved_years:
            lines.append(f"- [{year}]({year}.md)")
        else:
            lines.append(f"- {year} (not downloaded)")
    index_path = OUTPUT_DIR / "README.md"
    index_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nIndex written to {index_path}")


def main():
    ensure_output_dir()

    # Fetch and parse index
    index_html = fetch_index()
    letters = parse_letter_links(index_html)
    print(f"\nFound {len(letters)} letters to download\n")

    saved_years = []
    for letter in letters:
        year = letter["year"]
        if letter_already_saved(year):
            print(f"  [{year}] already exists, skipping")
            saved_years.append(year)
            continue
        print(f"[{year}] {letter['url']}")
        if letter["is_pdf"]:
            content = download_pdf_letter(letter["url"], year)
        else:
            content = download_html_letter(letter["url"], year)
        if content:
            save_letter(year, content)
            saved_years.append(year)
        else:
            print(f"  SKIPPED {year} — could not retrieve content")
        # Polite delay between requests
        time.sleep(1.5)

    create_index(letters, saved_years)
    print(f"\nDone. {len(saved_years)}/{len(letters)} letters saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
