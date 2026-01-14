import re
import json
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# ------------------------------
# Load environment and initialize LLM
# ------------------------------
load_dotenv()
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

# ------------------------------
# Load scraped data
# ------------------------------
with open("raw_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# ------------------------------
# Regex patterns
# ------------------------------
phone_pattern = re.compile(r"\(\d{3}\)\s?\d{3}-\d{4}")
email_pattern = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
license_pattern = re.compile(r"License\s*#[:\s]*([A-Za-z0-9-]+)")
address_pattern = re.compile(r"\d{1,5}\s+\w.+,\s+[A-Z]{2}\s+\d{5}")

# ------------------------------
# AI Prompt Template
# ------------------------------
ai_prompt_template = """
You are a professional data extraction assistant.
Extract all possible information about the company from the scraped content below.
Do not invent data; if something is missing, leave it empty ("") or [].

Scraped content:
{scraped_data}

Return JSON only in this exact format:

{{
  "description": "",
  "portfolio": [],
  "services": [],
  "specialties": [],
  "awards": [],
  "credentials": {{
    "isVerified": false,
    "licenseNumber": "",
    "certifications": []
  }},
  "yearsInBusiness": null,
  "serviceAreas": [],
  "contact": {{
    "email": "",
    "phone": "",
    "website": ""
  }},
  "address": {{
    "full": ""
  }}
}}
"""

ai_prompt = PromptTemplate(input_variables=["scraped_data"], template=ai_prompt_template)
ai_chain = LLMChain(llm=llm, prompt=ai_prompt)

# ------------------------------
# Helper function: regex extraction
# ------------------------------
def extract_with_regex(company):
    result = {
        "id": company.get("id", ""),
        "name": company.get("name", ""),
        "description": "",
        "portfolio": [],
        "services": [],
        "specialties": [],
        "awards": [],
        "credentials": {
            "isVerified": False,
            "licenseNumber": "",
            "certifications": []
        },
        "yearsInBusiness": None,
        "serviceAreas": [],
        "contact": {
            "email": "",
            "phone": "",
            "website": ""
        },
        "address": {
            "full": ""
        }
    }

    for website in company.get("websites", []):
        if "website" in website:
            result["contact"]["website"] = website["website"]

        for entry in website.get("scraped_data", []):
            content = entry.get("content", "")

            if not result["contact"]["phone"]:
                m = phone_pattern.search(content)
                if m:
                    result["contact"]["phone"] = m.group(0)

            if not result["contact"]["email"]:
                m = email_pattern.search(content)
                if m:
                    result["contact"]["email"] = m.group(0)

            if not result["credentials"]["licenseNumber"]:
                m = license_pattern.search(content)
                if m:
                    result["credentials"]["licenseNumber"] = m.group(1)

            if not result["address"]["full"]:
                m = address_pattern.search(content)
                if m:
                    result["address"]["full"] = m.group(0)

    return result

# ------------------------------
# Helper function: generate ID
# ------------------------------
def generate_id(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower().strip()) if name else ""

# ------------------------------
# Main Processing Loop
# ------------------------------
final_data = []

for company in data:
    base_result = extract_with_regex(company)

    # Combine all scraped text for AI extraction
    scraped_text = ""
    for website in company.get("websites", []):
        for entry in website.get("scraped_data", []):
            scraped_text += entry.get("content", "") + "\n"

    if scraped_text.strip():
        print(f"🧠 Enriching {company.get('name')} using AI...")
        ai_response = ai_chain.invoke({"scraped_data": scraped_text})
        try:
            ai_result = json.loads(ai_response["text"])

            # Merge AI fields without overwriting regex-extracted data
            for key in ["description", "portfolio", "services", "specialties", "awards", "yearsInBusiness", "serviceAreas"]:
                if ai_result.get(key):
                    base_result[key] = ai_result[key]

            # Merge credentials
            creds = ai_result.get("credentials", {})
            if creds.get("licenseNumber"):
                base_result["credentials"]["licenseNumber"] = creds.get("licenseNumber")
            if creds.get("certifications"):
                base_result["credentials"]["certifications"] = creds.get("certifications")

            # Merge contact info
            contact = ai_result.get("contact", {})
            base_result["contact"]["email"] = base_result["contact"]["email"] or contact.get("email", "")
            base_result["contact"]["phone"] = base_result["contact"]["phone"] or contact.get("phone", "")
            base_result["contact"]["website"] = base_result["contact"]["website"] or contact.get("website", "")

            # Merge address
            addr = ai_result.get("address", {})
            base_result["address"]["full"] = base_result["address"]["full"] or addr.get("full", "")

        except Exception as e:
            print(f"⚠️ AI parsing error for {company.get('name')}: {e}")

    # Generate ID if missing
    if not base_result["id"]:
        base_result["id"] = generate_id(base_result.get("name", ""))

    final_data.append(base_result)
    time.sleep(2)

# ------------------------------
# Save final enriched data
# ------------------------------
with open("final_enhanced_companies.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=4)

print("✅ Data enrichment complete! File saved as final_enhanced_companies.json")
