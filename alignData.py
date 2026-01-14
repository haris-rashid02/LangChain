import csv
import json
import random

# ------------------------------
# CSV Input
# ------------------------------
csv_file = "data.csv"  # your CSV file
start_row = 1000  # you can adjust to skip rows if needed

# ------------------------------
# Dummy data pools
# ------------------------------
us_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
             "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]
us_zips = ["10001", "90001", "60601", "77001", "85001", "19101", "78201", "92101", "75201", "95101"]

services_pool = ["Consulting", "Delivery", "Design", "Construction", "Maintenance", "Logistics"]
specialties_pool = ["Project Management", "Quality Control", "Customer Service", "Safety Compliance"]
certifications_pool = ["ISO 9001", "LEED", "OSHA", "EPA Registered"]
awards_pool = ["Best in Industry", "Top Rated Contractor", "Excellence Award"]

professional_categories = ["General Services", "Logistics", "Construction", "Design", "Delivery"]
budget_ranges = ["$", "$$", "$$$", "$$$$"]

# ------------------------------
# Helper functions
# ------------------------------
def generate_dummy_company_data(company_name, phone, email):
    cities = random.sample(us_cities, 2)
    zips = random.sample(us_zips, 2)
    return {
        "company_name": company_name,
        "tagline": f"{company_name} services",
        "description": f"{company_name} provides professional services in {cities[0]}, {cities[1]}.",
        "rating": round(random.uniform(4.0, 5.0), 1),
        "reviews_count": 0,
        "verified_hires": 0,
        "phone": phone,
        "email": email,
        "address": f"123 {cities[0]} St, {cities[1]}, {zips[0]}",
        "website": f"https://www.{company_name.replace(' ','').lower()}.com",
        "image_url": "",
        "image_url_2": "",
        "image_url_3": "",
        "license_number": f"LIC{random.randint(10000,99999)}",
        "verified_business": False,
        "responds_quickly": False,
        "hired_on_platform": False,
        "family_owned": False,
        "eco_friendly": False,
        "locally_owned": False,
        "offers_custom_work": False,
        "provides_3d_visualization": False,
        "professional_category": random.choice(professional_categories),
        "budget_range": random.choice(budget_ranges),
        "years_in_business": random.randint(5, 50),
        "employees_count": f"{random.randint(10, 100)}",
        "languages": ["English"],
        "services_offered": random.sample(services_pool, 3),
        "specialties": random.sample(specialties_pool, 2),
        "service_areas": f"{cities[0]}, {cities[1]}",
        "service_cities": cities,
        "service_zip_codes": zips,
        "awards": random.sample(awards_pool, 2),
        "certifications": random.sample(certifications_pool, 2),
        "featured_reviewer_name": "John Doe",
        "featured_review_text": "Excellent service!",
        "featured_review_rating": round(random.uniform(4.5, 5.0), 1)
    }

# ------------------------------
# Read CSV and build JSON
# ------------------------------
final_output = []

with open(csv_file, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

    for row in rows[start_row:]:
        company_name = row["customer_name"].strip() if row["customer_name"].strip() else "Unknown Company"
        phone = row["phone_number"].strip() if row["phone_number"].strip() else "000-000-0000"
        email = row["email"].strip() if row["email"].strip() else "unknown@example.com"

        company_data = generate_dummy_company_data(company_name, phone, email)
        final_output.append(company_data)

# ------------------------------
# Save JSON
# ------------------------------
with open("structured_companies_final.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=4)

print(f"🎉 JSON file generated with {len(final_output)} companies!")
