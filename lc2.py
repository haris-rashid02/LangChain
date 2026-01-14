import json
import time
import re
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ------------------------------
# Load ENV + Initialize LLM
# ------------------------------
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# ------------------------------
# Load scraped raw data
# ------------------------------
with open("raw_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ------------------------------
# Helper: clean text to reduce tokens
# ------------------------------
def clean_text(text: str) -> str:
    text = re.sub(r"<script.*?>.*?</script>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<style.*?>.*?</style>", " ", text, flags=re.DOTALL)
    drop_patterns = [
        r"(?i)privacy policy.*",
        r"(?i)terms of service.*",
        r"(?i)cookie policy.*",
        r"(?i)all rights reserved.*",
        r"(?i)navigation",
        r"(?i)menu",
        r"(?i)copyright.*"
    ]
    for p in drop_patterns:
        text = re.sub(p, " ", text)
    text = re.sub(r"\s+", " ", text)
    return text[:8000].strip()  # keep under token limit

# ------------------------------
# Helper: generate realistic US ZIP code
# ------------------------------
def generate_zip_code():
    return f"{random.randint(10000, 99999)} (Not Verified)"

# ------------------------------
# LLM Prompt
# ------------------------------
schema_prompt = """
Extract and infer the contractor details using the scraped data.

Rules:
- Extract REAL data from scraped content.
- If missing, generate realistic dummy value and append " (Not Verified)".
- Do NOT overwrite real data extracted from scraped content.
- All boolean fields must be false.
- reviews_count and verified_hires must be 0.
- budget_range MUST be one of: "$", "$$", "$$$", "$$$$".
- Return ONLY valid JSON in the following format:

{{
  "company_name": "",
  "tagline": "",
  "description": "",
  "rating": 0,
  "reviews_count": 0,
  "verified_hires": 0,
  "phone": "",
  "email": "",
  "address": "",
  "website": "",
  "image_url": "",
  "image_url_2": "",
  "image_url_3": "",
  "license_number": "",
  "verified_business": false,
  "responds_quickly": false,
  "hired_on_platform": false,
  "family_owned": false,
  "eco_friendly": false,
  "locally_owned": false,
  "offers_custom_work": false,
  "provides_3d_visualization": false,
  "professional_category": "",
  "budget_range": "",
  "years_in_business": null,
  "employees_count": "",
  "languages": [],
  "services_offered": [],
  "specialties": [],
  "service_areas": "",
  "service_cities": [],
  "service_zip_codes": [],
  "awards": [],
  "certifications": [],
  "featured_reviewer_name": "",
  "featured_review_text": "",
  "featured_review_rating": 0
}}

Scraped Content:
{scraped}
"""

prompt = PromptTemplate(
    input_variables=["scraped"],
    template=schema_prompt
)

chain = prompt | llm | StrOutputParser()

# ------------------------------
# Dummy record template
# ------------------------------
def dummy_record(company_name, website=""):
    return {
        "company_name": company_name + " (Not Verified)",
        "tagline": "Professional services (Not Verified)",
        "description": "High-quality services provided with expertise (Not Verified)",
        "rating": 4.0,
        "reviews_count": 0,
        "verified_hires": 0,
        "phone": "000-000-0000 (Not Verified)",
        "email": "unknown@example.com (Not Verified)",
        "address": "123 Main St, City, State ZIP (Not Verified)",
        "website": website if website else "https://example.com (Not Verified)",
        "image_url": "https://dummyimage.com/400x400 (Not Verified)",
        "image_url_2": "https://dummyimage.com/400x400 (Not Verified)",
        "image_url_3": "https://dummyimage.com/400x400 (Not Verified)",
        "license_number": "ABC12345 (Not Verified)",
        "verified_business": False,
        "responds_quickly": False,
        "hired_on_platform": False,
        "family_owned": False,
        "eco_friendly": False,
        "locally_owned": False,
        "offers_custom_work": False,
        "provides_3d_visualization": False,
        "professional_category": "General Contractors (Not Verified)",
        "budget_range": "$$",
        "years_in_business": 10,
        "employees_count": "10-50 (Not Verified)",
        "languages": ["English (Not Verified)"],
        "services_offered": ["Service 1 (Not Verified)"],
        "specialties": ["Specialty 1 (Not Verified)"],
        "service_areas": "City (ZIP) (Not Verified)",
        "service_cities": ["City (Not Verified)"],
        "service_zip_codes": [generate_zip_code()],
        "awards": ["Award 1 (Not Verified)"],
        "certifications": ["Cert 1 (Not Verified)"],
        "featured_reviewer_name": "John Doe (Not Verified)",
        "featured_review_text": "Excellent service! (Not Verified)",
        "featured_review_rating": 4.5
    }

# ------------------------------
# MAIN LOOP
# ------------------------------
final_output = []

for company in data:
    name = company.get("company_name", "(Unknown Company)")
    print(f"🧠 Extracting: {name}")  # log start

    # Preserve main website
    main_website = ""
    if company.get("websites"):
        main_website = company.get("websites")[0].get("website", "").strip()

    # Initialize dummy record (phone/email empty for LLM extraction)
    structured = dummy_record(name, main_website)
    structured["phone"] = ""
    structured["email"] = ""

    # Gather and clean scraped content
    raw_scraped = ""
    for website in company.get("websites", []):
        for item in website.get("scraped_data", []):
            raw_scraped += item.get("content", "") + " "
    cleaned = clean_text(raw_scraped)

    # LLM extraction
    if cleaned.strip():
        try:
            response = chain.invoke({"scraped": cleaned}).strip()
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                llm_data = json.loads(json_match.group())
                for key, value in llm_data.items():
                    if value not in [None, "", [], {}]:
                        if key == "website" and structured[key]:
                            continue  # preserve website
                        structured[key] = value
            print(f"✅ Completed: {name}")
        except Exception as e:
            print(f"❌ LLM error for {name}: {e}")
    else:
        print(f"⚠️ No scraped content for {name}")

    final_output.append(structured)

    # Save continuously
    with open("structured_companies_final.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)

    time.sleep(1)  # rate-limit safe

print("🎉 Extraction complete! File saved as structured_companies_final.json")
