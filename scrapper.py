import requests
from bs4 import BeautifulSoup
import re

url = "https://www.bidnetdirect.com/private/solicitations/7949459703/abstract"
html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
soup = BeautifulSoup(html, "html.parser")

results = []

# Loop through sections/cards/rows where company details appear
for block in soup.select("div, tr"):
    text = block.get_text(" ", strip=True)

    # Email extraction
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if not email_match:
        continue
    email = email_match.group(0)

    # Contact name extraction (simple heuristic)
    name_match = re.search(r"[A-Z][a-z]+ [A-Z][a-z]+", text)
    person_name = name_match.group(0) if name_match else None

    # Closing date formats (Nov 25, 2025) or (2025-11-25)
    date_match = re.search(
        r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.? \d{1,2}, \d{4}\b|\b\d{4}-\d{2}-\d{2}\b)",
        text
    )
    closing_date = date_match.group(0) if date_match else None

    # Company name — often the bold/title text
    company = None
    company_tag = block.find(["h2", "h3", "strong"])
    if company_tag:
        company = company_tag.get_text(strip=True)

    # Location filter — ONLY Munich
    if "Munich" in text or "München" in text:
        results.append({
            "company_name": company,
            "contact_person": person_name,
            "email": email,
            "closing_date": closing_date,
        })

print(results)
