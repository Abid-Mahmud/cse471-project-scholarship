import requests
import random
from app import create_app
from app.models.scholarship import Scholarship

app = create_app()

def generate_scholarship(uni_name, country):
    degrees = ["Masters", "PhD", "Both"]
    majors = [
        "Bachelor of Architecture (ARC)",
        "Bachelor of Arts in Applied English Language Studies (BA in AELS)",
        "Bachelor of Arts in English (BA in English)",
        "Bachelor of Business Administration (BBA)",
        "Bachelor of Disaster Management (BDM)",
        "Bachelor of Laws (LL.B. Hons.) (LLB)",
        "Bachelor of Pharmacy (Hons.) (PHR)",
        "Bachelor of Science in Applied Physics and Electronics (APE)",
        "Bachelor of Science in Biotechnology (BIO)",
        "Bachelor of Science in Computer Science (CS)",
        "Bachelor of Science in Computer Science & Engineering (CSE)",
        "Bachelor of Science in Electrical and Electronic Engineering (EEE)",
        "Bachelor of Science in Electronic And Communication Engineering (ECE)",
        "Bachelor of Science in Mathematics (MAT)",
        "Bachelor of Science in Microbiology (MIC)",
        "Bachelor of Science in Physics (PHY)",
        "Bachelor of Social Science in Economics (ECO)",
        "Bachelor of Social Sciences in Anthropology (ANT)"
    ]    
    req_gpa = round(random.uniform(2.8, 4.0), 1)
    
    # Special logic for elite universities to require higher GPAs!
    elite_keywords = ["harvard", "mit", "stanford", "oxford", "cambridge", "macquarie"]
    if any(keyword in uni_name.lower() for keyword in elite_keywords):
        req_gpa = round(random.uniform(3.7, 4.0), 1)
        
    deg = random.choice(degrees)
    target_major = random.choice(majors)
    
    return Scholarship(
        title=f"{uni_name} Excellence Award in {target_major}",
        university=uni_name,
        country=country,
        degree_level=deg,
        minimum_gpa=req_gpa,
        funding_amount="Fully Funded + Monthly Stipend",
        tags=["Worldwide", country, target_major]
    )

with app.app_context():
    print("Clearing old database...")
    Scholarship.objects.delete()

    print("Adding Elite Universities manually...")
    top_unis = [
        {"name": "Massachusetts Institute of Technology (MIT)", "country": "United States"},
        {"name": "Harvard University", "country": "United States"},
        {"name": "Stanford University", "country": "United States"},
        {"name": "University of Oxford", "country": "United Kingdom"},
        {"name": "University of Cambridge", "country": "United Kingdom"},
        {"name": "Macquarie University", "country": "Australia"},
        {"name": "University of Melbourne", "country": "Australia"},
        {"name": "ETH Zurich", "country": "Switzerland"},
        {"name": "National University of Singapore (NUS)", "country": "Singapore"},
        {"name": "Tsinghua University", "country": "China"}
    ]
    
    count = 0
    for uni in top_unis:
        s = generate_scholarship(uni["name"], uni["country"])
        s.save()
        count += 1

    print("Scraping remaining universities from global API...")
    try:
        response = requests.get("http://universities.hipolabs.com/search")
        all_universities = response.json()
        
        # Grab enough to reach exactly 200!
        remaining_needed = 200 - len(top_unis)
        target_universities = all_universities[:remaining_needed]
        
        print(f"Successfully scraped {len(target_universities)} more universities! Generating scholarships...")
        
        for uni in target_universities:
            s = generate_scholarship(uni['name'], uni.get('country', 'Unknown'))
            s.save()
            count += 1
            
            # Changed to print every 50 instead of 100 so you can see it working faster
            if count % 50 == 0:
                print(f"Successfully saved {count} scholarships to database...")
                
    except Exception as e:
        print(f"Error fetching from API: {e}")

    print(f"\n✅ DONE! {count} real universities are now in your MongoDB database.")