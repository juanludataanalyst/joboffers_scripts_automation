import requests
import xml.etree.ElementTree as ET
import json
import sys
import html
import unicodedata
from datetime import datetime
from bs4 import BeautifulSoup
import time
import random

# Configurar la salida para usar UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def parse_date(pubdate_str):
    """Convierte una fecha como 'Thu, 06 Mar 2025 03:23:17 +0000' a 'YYYY-MM-DD'"""
    try:
        dt = datetime.strptime(pubdate_str, "%a, %d %b %Y %H:%M:%S %z")
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

def extract_id_from_guid(guid):
    """Extrae el ID numérico del guid (ej. '451872' de 'https://jobscollider.com/jobs/...-451872')"""
    if guid and guid.startswith("https://jobscollider.com/jobs/"):
        return guid.split('-')[-1]
    return ""

def get_jobscollider_jobs():
    # Lista de feeds por categoría según JobsCollider
    feeds = [
        ("software_development", "https://jobscollider.com/remote-software-development-jobs.rss"),
        ("cybersecurity", "https://jobscollider.com/remote-cybersecurity-jobs.rss"),
        ("customer_service", "https://jobscollider.com/remote-customer-service-jobs.rss"),
        ("design", "https://jobscollider.com/remote-design-jobs.rss"),
        ("marketing", "https://jobscollider.com/remote-marketing-jobs.rss"),
        ("sales", "https://jobscollider.com/remote-sales-jobs.rss"),
        ("product", "https://jobscollider.com/remote-product-jobs.rss"),
        ("business", "https://jobscollider.com/remote-business-jobs.rss"),
        ("data", "https://jobscollider.com/remote-data-jobs.rss"),
        ("devops", "https://jobscollider.com/remote-devops-jobs.rss"),
        ("finance_legal", "https://jobscollider.com/remote-finance-legal-jobs.rss"),
        ("human_resources", "https://jobscollider.com/remote-human-resources-jobs.rss"),
        ("qa", "https://jobscollider.com/remote-qa-jobs.rss"),
        ("writing", "https://jobscollider.com/remote-writing-jobs.rss"),
        ("project_management", "https://jobscollider.com/remote-project-management-jobs.rss"),
        ("all_others", "https://jobscollider.com/remote-all-others-jobs.rss")
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    all_jobs = []
    
    for category_name, url in feeds:
        try:
            print(f"Intentando RSS: {url}", file=sys.stderr)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP: {e}", file=sys.stderr)
            continue
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}", file=sys.stderr)
            continue
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                for item in root.findall('.//item'):
                    title = clean_text(item.find('title').text if item.find('title') is not None else "")
                    company = title.split(' at ', 1)[1] if ' at ' in title else "Empresa no especificada"
                    guid = item.find('guid').text if item.find('guid') is not None else ""
                    
                    job = {
                        "title": title,
                        "date": parse_date(item.find('pubDate').text) if item.find('pubDate') is not None else "",
                        "company": company,
                        "location": "Not available",
                        "category": [category_name],
                        "description": clean_html_description(item.find('description').text if item.find('description') is not None else ""),
                        "link": clean_text(item.find('link').text if item.find('link') is not None else ""),
                        "source": "jobscollider",
                        "id_source": extract_id_from_guid(guid)
                    }
                    all_jobs.append(job)
                
                print(f"Procesados {len(all_jobs)} trabajos hasta ahora.", file=sys.stderr)
                
            except ET.ParseError as e:
                print(f"Error al parsear XML de {url}: {e}", file=sys.stderr)
            
            # Sleep aleatorio entre 0.1 y 0.5 segundos
            sleep_time = random.uniform(0.1, 0.5)
            print(f"Esperando {sleep_time:.2f} segundos antes de la siguiente llamada...", file=sys.stderr)
            time.sleep(sleep_time)
        else:
            print(f"Error inesperado: {response.status_code} para {url}", file=sys.stderr)
    
    # Imprimir el JSON por salida estándar
    if all_jobs:
        print(json.dumps(all_jobs, indent=4, ensure_ascii=False))
    else:
        print("No se encontraron trabajos.", file=sys.stderr)
    
    return all_jobs

if __name__ == "__main__":
    get_jobscollider_jobs()