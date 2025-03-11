import requests
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import json

def get_aijobs_jobs():
    url = "https://aijobs.net/feed"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}")
        return None

    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            jobs = []
            for item in root.findall('.//item'):
                job = {
                    "title": item.find('title').text or "",
                    "company": item.find('job_listing:company').text or "No especificado",
                    "description": item.find('description').text or "",
                    "pubdate": item.find('pubDate').text or "",
                    "link": item.find('link').text or "",
                    "location": item.find('job_listing:location').text or "No especificado",
                    "jobtype": item.find('job_listing:job_type').text or "No especificado",
                }
                jobs.append(job)

            today = datetime.now().strftime("%Y-%m-%d")
            hour = datetime.now().strftime("%H")
            os.makedirs("data/aijobs", exist_ok=True)
            file_path = f"data/aijobs/{today}_aijobs_jobs_{hour}h.json"

            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=4)

            return jobs
        except ET.ParseError as e:
            print(f"Error al parsear XML: {e}")
            return None
    else:
        return None
