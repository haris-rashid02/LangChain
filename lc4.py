import json
import time
import re
import random
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ------------------------------
# Load environment and initialize LLM
# ------------------------------
load_dotenv()
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

# ------------------------------
# Load raw scraped data
# ------------------------------
with open("raw_dataNew.json", "r", encoding="utf-8") as f:
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
    return text[:8000].strip()

# ------------------------------
# Helper: generate realistic dummy ZIP codes
# ------------------------------
us_zips = ["10001", "30301", "60601", "80202", "90001", "94102", "33101", "20001", "70112", "37201"]
us_cities = ["New York", "Atlanta", "Chicago", "Denver", "Los Angeles", "San Francisco", "Miami", "Washington", "New Orleans", "Nashville"]

def generate_dummy_city_zip(n=2):
    selected = random.sample(list(zip(us_cities, us_zips)), k=n)
    cities = [c for c, z in selected]
    zips = [z for c, z in selected]
    return cities, zips

# ------------------------------
# Dummy data generators
# ------------------------------
def dummy_services():
    options = ["Consulting", "Delivery", "Design", "Construction", "Maintenance", "Logistics"]
    return random.sample(options, k=3)

def dummy_specialties():
    options = ["Project Management", "Quality Control", "Customer Service", "Safety Compliance"]
    return random.sample(options, k=2)

def dummy_certifications():
    options = ["ISO 9001", "LEED", "OSHA", "EPA Registered"]
    return random.sample(options, k=2)

def dummy_awards():
    options = ["Best in Industry", "Top Rated Contractor", "Excellence Award"]
    return random.sample(options, k=2)

# ------------------------------
# LLM prompt
# ------------------------------
schema_prompt = """
You are an AI that extracts company information from scraped text. 
Fill the following JSON exactly in this format. Do NOT add extra fields. 
If a field cannot be inferred from the text, generate realistic dummy values. 
All boolean fields must be false, reviews_count and verified_hires must be 0. 
Budget range must be one of: "$", "$$", "$$$", "$$$$". 
Use realistic US cities and ZIP codes if needed.

JSON Format:
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
# Dummy record in case LLM fails
# ------------------------------
def dummy_record(company_name, website="", phone="", email=""):
    cities, zips = generate_dummy_city_zip()
    return {
        "company_name": company_name + " (Not Verified)",
        "tagline": "Professional services (Not Verified)",
        "description": f"{company_name} provides high-quality services in {', '.join(cities)}. (Not Verified)",
        "rating": 0,
        "reviews_count": 0,
        "verified_hires": 0,
        "phone": phone if phone else "000-000-0000 (Not Verified)",
        "email": email if email else f"contact@{company_name.replace(' ','').lower()}.com (Not Verified)",
        "address": f"123 {cities[0]} St, {cities[1]}, {zips[0]}",
        "website": website if website else f"https://www.{company_name.replace(' ','').lower()}.com",
        "image_url": "https://dummyimage.com/400x400 (Not Verified)",
        "image_url_2": "https://dummyimage.com/400x400 (Not Verified)",
        "image_url_3": "https://dummyimage.com/400x400 (Not Verified)",
        "license_number": f"LIC{random.randint(10000,99999)}",
        "verified_business": False,
        "responds_quickly": False,
        "hired_on_platform": False,
        "family_owned": False,
        "eco_friendly": False,
        "locally_owned": False,
        "offers_custom_work": False,
        "provides_3d_visualization": False,
        "professional_category": "General Services (Not Verified)",
        "budget_range": random.choice(["$", "$$", "$$$", "$$$$"]),
        "years_in_business": random.randint(5, 30),
        "employees_count": f"{random.randint(10,100)} (Not Verified)",
        "languages": ["English (Not Verified)"],
        "services_offered": dummy_services(),
        "specialties": dummy_specialties(),
        "service_areas": ", ".join(cities),
        "service_cities": cities,
        "service_zip_codes": zips,
        "awards": dummy_awards(),
        "certifications": dummy_certifications(),
        "featured_reviewer_name": "John Doe (Not Verified)",
        "featured_review_text": "Excellent service! (Not Verified)",
        "featured_review_rating": 0
    }

# ------------------------------
# Main processing loop
# ------------------------------
final_output = []

for company in data:
    name = company.get("company_name", "(Unknown Company)")
    phone = company.get("phone", "")
    email = company.get("email", "")
    website = ""
    if company.get("websites"):
        website = company["websites"][0].get("website", "").strip()
    
    print(f"🧠 Extracting: {name}")
    
    # Gather scraped content
    raw_scraped = ""
    for w in company.get("websites", []):
        for entry in w.get("scraped_data", []):
            raw_scraped += entry.get("content", "") + " "
    cleaned = clean_text(raw_scraped)

    # LLM extraction
    if cleaned.strip():
        try:
            response = chain.invoke({"scraped": cleaned}).strip()
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                llm_data = json.loads(json_match.group())
                # Preserve phone, email, website from raw JSON if present
                if phone:
                    llm_data["phone"] = phone
                if email:
                    llm_data["email"] = email
                if website:
                    llm_data["website"] = website
                final_output.append(llm_data)
                print(f"✅ Completed: {name}")
            else:
                final_output.append(dummy_record(name, website, phone, email))
                print(f"⚠️ LLM returned invalid JSON for {name}, used dummy.")
        except Exception as e:
            final_output.append(dummy_record(name, website, phone, email))
            print(f"❌ LLM error for {name}: {e}, used dummy record")
    else:
        final_output.append(dummy_record(name, website, phone, email))
        print(f"⚠️ No scraped content for {name}, used dummy.")

    # Save continuously
    with open("structured_companies_finalNew.json", "w", encoding="utf-8") as f:
        json.dump(final_output, f, indent=4)
    
    time.sleep(1)

print("🎉 Extraction complete! File saved as structured_companies_final.json")
