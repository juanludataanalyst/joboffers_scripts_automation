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
    """Convierte una fecha como '12.03.2025' a 'YYYY-MM-DD'"""
    try:
        dt = datetime.strptime(pubdate_str, "%d.%m.%Y")
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime.now().strftime("%Y-%m-%d")

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
    soup = BeautifulSoup(html_text, 'html.parser')
    return clean_text(soup.get_text(separator='\n'))

def get_jobicy_jobs():
    url = "https://jobicy.com/feed/newjobs"
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
            
            for job_elem in root.findall('.//job'):
                job_id = job_elem.get('id', "")
                job = {
                    "title": clean_text(job_elem.find('name').text if job_elem.find('name') is not None else ""),
                    "date": parse_date(job_elem.find('pubdate').text) if job_elem.find('pubdate') is not None else "",
                    "company": clean_text(job_elem.find('company').text if job_elem.find('company') is not None else "Empresa no especificada"),
                    "location": clean_text(job_elem.find('region').text if job_elem.find('region') is not None else "Not available"),
                    "type": clean_text(job_elem.find('jobtype').text if job_elem.find('jobtype') is not None else "Not specified"),
                    "description": clean_html_description(job_elem.find('description').text if job_elem.find('description') is not None else ""),
                    "link": clean_text(job_elem.find('link').text if job_elem.find('link') is not None else ""),
                    "source": "jobicy",
                    "id_source": job_id
                }
                jobs.append(job)
            
            # Imprimir el JSON por salida estándar
            print(json.dumps(jobs, indent=4, ensure_ascii=False))
            return jobs
        
        except ET.ParseError as e:
            print(f"Error al parsear XML: {e}", file=sys.stderr)
            return None
    else:
        print(f"Error inesperado: {response.status_code}", file=sys.stderr)
        return None

if __name__ == "__main__":
    get_jobicy_jobs()