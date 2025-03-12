import requests
import xml.etree.ElementTree as ET
import json
import sys
import html
import unicodedata
from datetime import datetime

# Configurar la salida para usar UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def parse_date(pubdate_str):
    """Convierte una fecha como 'Tue, 04 Mar 2025 00:17:05 +0000' a 'YYYY-MM-DD'"""
    try:
        dt = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""

def clean_text(text):
    """Limpia texto: decodifica HTML, normaliza Unicode y elimina caracteres extraños"""
    if not text:
        return ""
    # Decodificar entidades HTML (ej. &amp; → &)
    text = html.unescape(text)
    # Normalizar Unicode a forma NFC (combina caracteres como 'e' + '́' en 'é')
    text = unicodedata.normalize('NFC', text)
    return text.strip()

def get_aijobs_jobs():
    url = "https://aijobs.net/feed"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión: {e}", file=sys.stderr)
        return None
    
    if response.status_code == 200:
        try:
            root = ET.fromstring(response.content)
            jobs = []
            
            for item in root.findall('.//item'):
                job = {
                    "title": clean_text(item.find('title').text if item.find('title') is not None else ""),
                    "date": parse_date(item.find('pubDate').text) if item.find('pubDate') is not None else "",
                    "company": clean_text(item.find('job_listing:company', namespaces={'job_listing': 'https://aijobs.net'}).text if item.find('job_listing:company', namespaces={'job_listing': 'https://aijobs.net'}) is not None else "Empresa no especificada"),
                    "location": clean_text(item.find('job_listing:location', namespaces={'job_listing': 'https://aijobs.net'}).text if item.find('job_listing:location', namespaces={'job_listing': 'https://aijobs.net'}) is not None else "Ubicación no especificada"),
                    "type": clean_text(item.find('job_listing:job_type', namespaces={'job_listing': 'https://aijobs.net'}).text if item.find('job_listing:job_type', namespaces={'job_listing': 'https://aijobs.net'}) is not None else "No especificado"),
                    "description": clean_text(item.find('description').text if item.find('description') is not None else ""),
                    "link": clean_text(item.find('link').text if item.find('link') is not None else ""),
                    "source": "aijobs"
                }
                jobs.append(job)
            
            # Solo imprimimos el JSON por salida estándar
            print(json.dumps(jobs, indent=4, ensure_ascii=False))
            return jobs
        except ET.ParseError as e:
            print(f"Error al parsear XML: {e}", file=sys.stderr)
            return None
    else:
        print(f"Error inesperado: {response.status_code}", file=sys.stderr)
        return None

if __name__ == "__main__":
    get_aijobs_jobs()