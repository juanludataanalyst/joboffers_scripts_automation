import requests
import xml.etree.ElementTree as ET
import json
import sys
import html
import unicodedata
from datetime import datetime
from bs4 import BeautifulSoup

# Configurar la salida para usar UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def parse_date(pubdate_str):
    """Convierte una fecha como 'Wed, 12 Mar 2025 20:51:28 GMT' a 'YYYY-MM-DD'"""
    try:
        dt = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %Z")
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
    # Eliminar <![CDATA[...]]> si existe
    text = html_text.replace('<![CDATA[', '').replace(']]>', '')
    # Parsear HTML y separar elementos con \n
    soup = BeautifulSoup(text, 'html.parser')
    return clean_text(soup.get_text(separator='\n'))

def get_remotive_jobs():
    url = "https://remotive.com/remote-jobs/feed"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        print(f"Intentando RSS: {url}", file=sys.stderr)
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
                id_source = item.find('guid').text.split('-')[-1] if item.find('guid') is not None else ""
                job = {
                    "title": clean_text(item.find('title').text if item.find('title') is not None else ""),
                    "date": parse_date(item.find('pubDate').text) if item.find('pubDate') is not None else "",
                    "company": clean_text(item.find('company').text if item.find('company') is not None else "Empresa no especificada"),
                    "location": clean_text(item.find('location').text if item.find('location') is not None else "Ubicación no especificada"),
                    "category": [clean_text(item.find('category').text)] if item.find('category') is not None else [],
                    "type": clean_text(item.find('type').text if item.find('type') is not None else "No especificado"),
                    "description": clean_html_description(item.find('description').text if item.find('description') is not None else ""),
                    "link": clean_text(item.find('link').text if item.find('link') is not None else ""),
                    "source": "remotive",
                    "id_source": id_source
                }
                jobs.append(job)
            
            print(json.dumps(jobs, indent=4, ensure_ascii=False))
            return jobs
        except ET.ParseError as e:
            print(f"Error al parsear XML: {e}", file=sys.stderr)
            return None
    else:
        print(f"Error inesperado: {response.status_code}", file=sys.stderr)
        return None

if __name__ == "__main__":
    get_remotive_jobs()