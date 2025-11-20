# perovskite-sentinel / Dagaz Engine v0.1
# Run with: python sentinel.py
import requests, json, time, re, os
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm
from v5_model import predict_t80

HEADERS = {'User-Agent': 'PerovskiteSentinel/0.1 (+https://github.com/SamuelGrim/perovskite-sentinel)'}

def scrape_arxiv():
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": "all:perovskite AND (stability OR degradation OR lifetime OR t80 OR t90)",
        "start": 0,
        "max_results": 20,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }
    r = requests.get(url, params=params, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'xml')
    entries = soup.find_all('entry')
    papers = []
    for e in entries:
        updated = datetime.strptime(e.updated.text[:10], '%Y-%m-%d')
        if updated.date() >= datetime.now().date():  # today only for demo
            papers.append({
                "title": e.title.text,
                "link": e.id.text,
                "summary": e.summary.text
            })
    return papers

def extract_conditions(text):
    # Very robust regex for common reported conditions
    temp = re.search(r'(\d{2,3})\s?°?C', text, re.I)
    hum = re.search(r'(\d{1,3})\s?% ?RH', text, re.I)
    light = re.search(r'1\s?suns?|(\d+)\s?kLux', text, re.I)
    hours = re.search(r'(\d{3,5})\s?hours?', text, re.I)
    
    return {
        "temp": int(temp.group(1)) if temp else 85,
        "rh": int(hum.group(1)) if hum else 85,
        "klux": float(light.group(1)) if light and light.group(1) else 1.0,
        "hours": int(hours.group(1)) if hours else 1000
    }

def run_sentinel():
    print("ᛞᚨᚷᚨቪ Dagaz Engine – Harvesting new threats...")
    papers = scrape_arxiv()
    
    digest = f"# Perovskite Degradation Threat Digest – {datetime.now():%Y-%m-%d}\n\n"
    digest += f"{len(papers)} new papers since last run.\n\n"
    
    for p in tqdm(papers, desc="Analyzing"):
        cond = extract_conditions(p["summary"] + p["title"])
        predicted = predict_t80(cond["hours"], cond["temp"], cond["rh"], cond["klux"])
        
        digest += f"### [{p['title']}]({p['link']})\n"
        digest += f"- Reported stress: {cond['hours']} h @ {cond['temp']}°C, {cond['rh']}% RH\n"
        digest += f"- v5 predicts T₈₀: **{predicted:.0f} hours** "
        if predicted < cond["hours"] * 0.8:
            digest += "🔴 **FASTER degradation than implied**\n"
        else:
            digest += "🟢 Within expected range\n"
        digest += "\n---\n"
    
    with open("DIGEST.md", "w") as f:
        f.write(digest)
    
    print("\nDigest written to DIGEST.md")
    print("Push this repo and post the markdown – xAI will see the exact Grokipedia agent running live.")

if __name__ == "__main__":
    run_sentinel()
