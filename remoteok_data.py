import requests
import json
import sys
import html
import unicodedata
from datetime import datetime
from bs4 import BeautifulSoup

# Configurar la salida para usar UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def parse_date(date_str):
    """Convierte una fecha como '2025-03-11T21:00:08+00:00' a 'YYYY-MM-DD'"""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""

def clean_text(text):
    """Limpia texto: decodifica HTML, normaliza Unicode y preserva saltos de línea"""
    if not text:
        return ""
    text = html.unescape(text)
    text = unicodedata.normalize('NFC', text)
    return text.strip()

def clean_html_description(html_text):
    """Convierte HTML a texto plano preservando saltos de línea"""
    if not html_text:
        return ""
    # Parsear HTML y separar elementos con \n
    soup = BeautifulSoup(html_text, 'html.parser')
    return clean_text(soup.get_text(separator='\n'))

def get_remoteok_jobs():
    url = "https://remoteok.com/api"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        print(f"Intentando API: {url}", file=sys.stderr)
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}", file=sys.stderr)
        return None
    
    if response.status_code == 200:
        data = response.json()
        
        # La API devuelve una lista, el primer elemento es metadata
        if isinstance(data, list) and len(data) > 1:
            jobs_raw = data[1:]  # Excluir el primer elemento (legal info)
        else:
            print("Formato inesperado de la API.", file=sys.stderr)
            return None
        
        jobs = []
        for job_raw in jobs_raw:
            job = {
                "title": clean_text(job_raw.get("position", "")),
                "date": parse_date(job_raw.get("date", "")),
                "company": clean_text(job_raw.get("company", "Empresa no especificada")),
                "location": clean_text(job_raw.get("location", "Ubicación no especificada")),
                "tags": [clean_text(tag) for tag in job_raw.get("tags", [])] if job_raw.get("tags") else [],
                "type": "Full-Time",  # Asumimos por defecto, ajustable si hay más datos
                "description": clean_html_description(job_raw.get("description", "")),
                "link": clean_text(job_raw.get("url", "")),
                "source": "remoteok",
                "id_source": clean_text(job_raw.get("id", "")),
                "salary_min": job_raw.get("salary_min", None),
                "salary_max": job_raw.get("salary_max", None)
            }
            jobs.append(job)
        
        # Imprimir el JSON por salida estándar
        print(json.dumps(jobs, indent=4, ensure_ascii=False))
        return jobs
    else:
        print(f"Error inesperado: {response.status_code}", file=sys.stderr)
        return None

if __name__ == "__main__":
    get_remoteok_jobs()