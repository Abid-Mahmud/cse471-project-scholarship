import os
import google.generativeai as genai
from app import create_app
from app.models.scholarship import Scholarship
from dotenv import load_dotenv

# Load your Gemini API key from the .env file
load_dotenv()
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

app = create_app()

with app.app_context():
    scholarships = Scholarship.objects(embedding__size=0)
    print(f"Found {scholarships.count()} scholarships that the AI needs to read...")
    
    count = 0
    for s in scholarships:
        # Create a sentence describing the scholarship
        text_to_embed = f"Title: {s.title}. University: {s.university}, {s.country}. Degree: {s.degree_level}. Minimum GPA: {s.minimum_gpa}. Major: {', '.join(s.tags)}"
        
        # Ask Gemini to turn that text into a 768-dimension math vector
        result = genai.embed_content(
            model="models/gemini-embedding-2",
            content=text_to_embed,
            task_type="retrieval_document"
        )
        
        # Save the vector to MongoDB
        s.embedding = result['embedding']
        s.save()
        count += 1
        print(f"AI read and saved: {s.title}")
        
    print("✅ All scholarships have been vectorized into MongoDB!")