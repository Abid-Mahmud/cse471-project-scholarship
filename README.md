#  ScholarMatch: AI-Powered Scholarship Platform

ScholarMatch is an intelligent, full-stack web application designed to seamlessly connect students with global funding opportunities. By leveraging **Retrieval-Augmented Generation (RAG)**, Vector Search, and large language models (LLMs), ScholarMatch provides highly personalized scholarship recommendations, AI-driven application timelines, and an automated tracking system.

##  Key Features

* ** AI Scholarship Discovery (RAG):** Uses Google Gemini embeddings and MongoDB Vector Search to match students with scholarships based on their GPA, nationality, degree level, and major.
* ** Context-Aware AI Chatbot:** An integrated academic advisor chatbot powered by Groq (Llama-3.3-70b-versatile) that answers questions using real, verified data from the scholarship database.
* ** Interactive Application Tracker:** A Kanban-style board (To Do, In Progress, Completed) to track saved scholarships. Features click-to-move and drag-and-drop functionality.
* ** Automated AI Timeline Generator:** Instantly generates a customized, step-by-step application timeline working backward from the official scholarship deadline.
* ** Background Email Notifications:** Automatically drafts and sends beautifully formatted HTML emails with application deadlines, OTPs, and study tips to the user's inbox using an asynchronous background thread (SMTP).
* ** AI Document Reviewer:** Generates accurate, university-specific document checklists to ensure students don't miss crucial application requirements.
* ** Role-Based Authentication & 2-Step Verification:** Secure login and registration (Student, Professor, Admin) with domain restrictions (e.g., restricted access for `@g.bracu.ac.bd` emails), Google OAuth integration, and secure 6-digit OTP verification for students.

##  Tech Stack

* **Backend:** Python, Flask, Flask-Login, threading (for async background tasks)
* **Database:** MongoDB (MongoEngine / PyMongo), MongoDB Atlas Vector Search
* **AI & LLMs:** 
  * **Groq API** (Llama-3.3-70b-versatile) for fast text generation, JSON structuring, and chat.
  * **Google GenAI API** for text embeddings and vectorization.
* **Frontend:** HTML5, Tailwind CSS (via CDN), Vanilla JavaScript, Glassmorphism UI
* **Email:** Python `smtplib` and `email.message`

##  Project Structure

The project uses a highly modular **Flask Blueprint** architecture to keep the codebase clean and maintainable:

```text
Scholarship website/
│
├── .venv/                     # Python Virtual Environment
├── run.py                     # Entry point to start the Flask server
├── .env                       # Environment variables (API keys, secrets)
├── requirements.txt           # Python dependencies
│
└── app/
    ├── __init__.py            # Main application factory
    ├── extensions.py          # Database and Login Manager initialization
    ├── models/                # MongoDB database schemas (User, Scholarship, Timeline, etc.)
    ├── routes/                # Modular routing logic
    │   ├── auth.py            # Login, Registration, 2-Step Verification, Google OAuth
    │   ├── admin/             # Admin portal routes
    │   └── student/           # Modularized Student features
    │       ├── __init__.py 
    │       ├── scholarship_discovery.py
    │       ├── app_tracker.py
    │       ├── checklist.py
    │       └── chatbot.py
    │
    ├── static/                # Images, CSS, JS
    └── templates/             # Jinja2 HTML Templates (Tailwind styled)
```

##  Setup & Installation

**1. Clone the repository and navigate to the project directory:**
```bash
git clone <repository-url>
cd "Scholarship website"
```

**2. Create and activate a virtual environment:**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Configure Environment Variables:**
Create a `.env` file in the root directory (next to `run.py`) and add the following keys:

```env
# Flask Setup
SECRET_KEY=your_secure_flask_secret_key

# Database
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0...

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# AI APIs
GEMINI_API_KEY=your_google_gemini_key
GROQ_API_KEY=your_groq_api_key

# Email Server (SMTP)
MAIL_USERNAME=your.sender.email@gmail.com
MAIL_PASSWORD=your_16_character_app_password



**5. Run the Application:**
```bash
python run.py
```
The server will start on `http://127.0.0.1:5000/`.

## 📌 Future Enhancements
* Implementing automated web scraping scripts  to continuously update the database with fresh scholarships.
* Adding a Professor portal for drafting Letters of Recommendation.