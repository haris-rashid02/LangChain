import json
import time
import os
import re
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

# ------------------------------
# Load environment variables
# ------------------------------
load_dotenv()

# ------------------------------
# Initialize OpenRouter / DeepSeek R1
# ------------------------------
llm = ChatOpenAI(
    model="deepseek/deepseek-r1:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.3,
    max_retries=2,
    timeout=None,
)

# ------------------------------
# Load raw scraped data
# ------------------------------
with open("raw_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ------------------------------
# Prompt Template
# ------------------------------
ai_prompt_template = PromptTemplate(
    input_variables=["company_name", "scraped_data"],
    template="""
You are a professional AI agent specialized in company data enrichment.

Your job:
1. Extract ALL real data from scraped text.
2. Any missing values must be filled with realistic dummy data.
3. Every dummy value MUST end with " (Not Verified)".
4. Never overwrite real scraped data.
5. Dummy data must appear business-realistic.
6. budget_range must be one of: "$", "$$", "$$$", "$$$$".
7. Reviews must follow this structure:
   {{
     "reviewer": "",
     "rating": 4.5,
     "review_text": ""
   }}
8. Extract email and phone_number if present; dummy must end with " (Not Verified)".

Scraped text for {company_name}:
{scraped_data}

Return ONLY valid JSON matching this EXACT structure:

[
  {{"company": {{
      "name": "",
      "rating": null,
      "reviews_count": null,
      "verified_hires": null,
      "tagline": "",
      "featured_review": {{
        "reviewer": "",
        "review_text": ""
      }},
      "details": {{
        "address": "",
        "verified_business": false,
        "description": "",
        "years_in_business": null,
        "license_number": "",
        "certifications": [],
        "awards": [],
        "services_offered": [],
        "specialties": [],
        "service_areas": [{{"city": "", "zip_code": ""}}],
        "responds_quickly": false,
        "hired_on_platform": false,
        "provides_3d_visualization": false,
        "eco_friendly": false,
        "family_owned": false,
        "locally_owned": false,
        "offers_custom_work": false,
        "languages": [],
        "budget_range": "",
        "professional_category": "",
        "email": "",
        "phone_number": ""
      }},
      "client_reviews": {{
        "average_rating": null,
        "total_reviews": null,
        "highlights": "",
        "reviews": [{{"reviewer": "", "rating": null, "review_text": ""}}]
      }}
  }}]
"""
)

# ------------------------------
# JSON Cleaner for R1 output
# ------------------------------
def extract_json_r1(text):
    """
    Extract valid JSON array from R1 reasoning output.
    Tries all bracketed sections until it parses successfully.
    """
    matches = re.findall(r"\[.*?\]", text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except:
            continue
    raise ValueError("No valid JSON found in R1 output")

# ------------------------------
# Fallback dummy entry
# ------------------------------
def fallback_entry(name):
    return {
        "company": {
            "name": name + " (Not Verified)",
            "rating": None,
            "reviews_count": None,
            "verified_hires": None,
            "tagline": " (Not Verified)",
            "featured_review": {"reviewer": " (Not Verified)", "review_text": " (Not Verified)"},
            "details": {
                "address": " (Not Verified)",
                "verified_business": False,
                "description": " (Not Verified)",
                "years_in_business": None,
                "license_number": " (Not Verified)",
                "certifications": [" (Not Verified)"],
                "awards": [" (Not Verified)"],
                "services_offered": [" (Not Verified)"],
                "specialties": [" (Not Verified)"],
                "service_areas": [{"city": " (Not Verified)", "zip_code": " (Not Verified)"}],
                "responds_quickly": False,
                "hired_on_platform": False,
                "provides_3d_visualization": False,
                "eco_friendly": False,
                "family_owned": False,
                "locally_owned": False,
                "offers_custom_work": False,
                "languages": [" (Not Verified)"],
                "budget_range": " (Not Verified)",
                "professional_category": " (Not Verified)",
                "email": "example@example.com (Not Verified)",
                "phone_number": "000-000-0000 (Not Verified)"
            },
            "client_reviews": {
                "average_rating": None,
                "total_reviews": None,
                "highlights": " (Not Verified)",
                "reviews": [{"reviewer": " (Not Verified)", "rating": None, "review_text": " (Not Verified)"}]
            }
        }
    }

# ------------------------------
# Main Loop
# ------------------------------
final_data = []

for company in data:
    name = company.get("company_name")
    if not name:
        print("⚠️ Skipping entry without company name")
        continue

    scraped_text = ""
    for website in company.get("websites", []):
        for entry in website.get("scraped_data", []):
            scraped_text += entry.get("content", "").strip() + "\n"

    if not scraped_text.strip():
        print(f"⚠️ Skipping {name}: no scraped content found")
        continue

    print(f"🧠 Processing: {name}")

    try:
        prompt = ai_prompt_template.format(company_name=name, scraped_data=scraped_text)

        response = llm.invoke({"company_name": name, "scraped_data": scraped_text})
        # R1 may return reasoning + JSON
        cleaned_json = extract_json_r1(response)
        final_data.append(cleaned_json[0])
        print(f"✅ Completed: {name}")

    except Exception as e:
        print(f"❌ Error for {name}: {e}")
        final_data.append(fallback_entry(name))

    # Save checkpoint after each company
    with open("final_companies_structured.json", "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4)

    time.sleep(1)  # rate limit protection

print("🎉 All companies processed successfully!")
