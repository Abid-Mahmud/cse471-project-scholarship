import os
import time
import requests
import urllib3
from urllib.parse import urlparse
from dotenv import load_dotenv
from ddgs import DDGS
from app import create_app, db
from app.models.scholarship import Scholarship

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()
app = create_app()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
}

UNWANTED_DOMAINS = [
    'pinterest.com', 'facebook.com', 'linkedin.com', 'wikipedia.org',
    'sugarmom.com.ng', 'bestfullyfundedscholarships.com', 'studyhunt.info',
    'greatyop.com', 'opportunitiescorners.com', 'scholarships365.info',
    'globalscholarships.com', 'mastersportal.com', 'scholyhub.com'
]

def extract_domain(url):
    try:
        parsed = urlparse(url)
        return parsed.netloc if parsed.netloc else ""
    except Exception:
        return ""

def find_official_deep_link(title, university, current_url):
    domain = extract_domain(current_url)
    
    if domain and not any(bad in domain for bad in UNWANTED_DOMAINS):
        query = f'"{title}" site:{domain}'
    else:
        query = f'"{title}" "{university}" official scholarship'

    try:
        # Respect search service rate limits with a small pause
        time.sleep(1.5)
        results = list(DDGS().text(query=query, max_results=5))
        for r in results:
            link = r.get('href', '') or r.get('url', '')
            if link and link.startswith('http') and not any(bad in link for bad in UNWANTED_DOMAINS + ['/clev?']):
                return link
    except Exception as e:
        print(f"⚠️ Search error for '{title}': {e}")
    return None

def check_and_repair_deep_links():
    with app.app_context():
        scholarships = Scholarship.objects.all()
        print(f"🔍 Scanning {len(scholarships)} scholarship entries for link integrity...\n")

        active_count = 0
        repaired_count = 0
        failed_count = 0

        for item in scholarships:
            url = item.official_url
            is_broken = False

            if not url or url == "#" or url.count('/') <= 3 or any(bad in url for bad in UNWANTED_DOMAINS):
                is_broken = True
            else:
                try:
                    res = requests.get(url, headers=headers, timeout=8, verify=False, allow_redirects=True)
                    if res.status_code not in [200, 301, 302, 307, 403]:
                        is_broken = True
                except requests.RequestException:
                    is_broken = True

            if is_broken:
                print(f"🛠️ Resolving official URL for: '{item.title}'...")
                official_url = find_official_deep_link(item.title, item.university, item.official_url)
                
                if official_url:
                    item.official_url = official_url
                    item.save()
                    repaired_count += 1
                    print(f"✅ Updated MongoDB: {official_url}\n")
                else:
                    failed_count += 1
                    print(f"❌ Could not resolve official page for '{item.title}'\n")
            else:
                active_count += 1

        print("="*50)
        print("📊 DEEP SYNC SUMMARY:")
        print(f"✅ Valid Official Links: {active_count}")
        print(f"🛠️ Repaired Deep Links: {repaired_count}")
        print(f"❌ Failed Resolutions: {failed_count}")

        try:
            db.connection.close()
            print("🔒 MongoDB connection closed cleanly.")
        except Exception:
            pass

if __name__ == "__main__":
    check_and_repair_deep_links()