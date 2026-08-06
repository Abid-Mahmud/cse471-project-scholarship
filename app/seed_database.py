import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file BEFORE importing app routes
load_dotenv()

from google import genai
from app import create_app
from app.models.scholarship import Scholarship

gemini_api_key = os.environ.get('GEMINI_API_KEY')
if not gemini_api_key:
    print("⚠️ Warning: GEMINI_API_KEY environment variable is missing.")

client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None

app = create_app()

def generate_embedding(text):
    if not client:
        return []
    for model_id in ["embedding-001", "text-embedding-004"]:
        try:
            response = client.models.embed_content(
                model=model_id,
                contents=text
            )
            if response and response.embeddings:
                return response.embeddings[0].values
        except Exception:
            continue
    return []

def seed_real_scholarships():
    possible_files = ["real_scholarships_3.json", "real_scholarships_unique.json", "real_scholarships.json"]
    json_filepath = next((f for f in possible_files if os.path.exists(f)), None)

    if not json_filepath:
        print("❌ Error: Could not find any scholarship JSON file in the root directory.")
        return

    with app.app_context():
        print("🗑️ Clearing database collection...")
        Scholarship.objects.delete()

        with open(json_filepath, "r", encoding="utf-8") as f:
            scholarships_data = json.load(f)

        print(f"🔄 Processing {len(scholarships_data)} real scholarship entries from '{json_filepath}'...")
        saved_count = 0

        for item in scholarships_data:
            title = item.get("title", "").strip()
            university = item.get("university", "").strip()
            country = item.get("country", "").strip()
            degree_level = item.get("degree_level", "Masters").strip()
            minimum_gpa = float(item.get("minimum_gpa", 3.0))
            funding_amount = item.get("funding_amount", "Fully Funded").strip()
            official_url = item.get("official_url", "#").strip()
            major = item.get("major", "All Majors").strip()
            institution_type = item.get("institution_type", "Public").strip()

            search_text = f"{title} at {university} in {country}. Degree: {degree_level}. Major: {major}. Funding: {funding_amount}."
            embedding_vector = generate_embedding(search_text)

            scholarship_doc = Scholarship(
                title=title,
                university=university,
                country=country,
                degree_level=degree_level,
                minimum_gpa=minimum_gpa,
                funding_amount=funding_amount,
                official_url=official_url,
                major=major,
                institution_type=institution_type,
                embedding=embedding_vector,
                tags=[country, degree_level, major]
            )

            scholarship_doc.save()
            saved_count += 1

            if saved_count % 10 == 0 or saved_count == len(scholarships_data):
                print(f"✅ Saved [{saved_count}/{len(scholarships_data)}] entries to MongoDB...")

        print(f"\n🎉 STEP 2 COMPLETE! Successfully seeded {saved_count} real scholarships into MongoDB.")

if __name__ == "__main__":
    seed_real_scholarships()