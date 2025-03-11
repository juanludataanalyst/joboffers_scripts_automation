import requests
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import json
from bs4 import BeautifulSoup
import time
import random

def get_jobscollider_jobs():
    # Lista de feeds por categoría según la documentación de JobsCollider
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
            print(f"Intentando RSS: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"Error HTTP: {e}")
            print(f"Respuesta del servidor: {response.text if 'response' in locals() else 'No disponible'}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            continue
        
        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                namespaces = {'content': 'http://purl.org/rss/1.0/modules/content/'}
                
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    company = title.split(' at ', 1)[1] if ' at ' in title else "Empresa no especificada"
                    description = item.find('description').text if item.find('description') is not None else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    link = item.find('link').text if item.find('link') is not None else ""
                    guid = item.find('guid').text if item.find('guid') is not None else ""

                    # Limpiar el HTML del campo description
                    soup = BeautifulSoup(description, 'html.parser')
                    cleaned_description = soup.get_text()

                    # Formatear la fecha
                    try:
                        date_obj = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except ValueError:
                        formatted_date = datetime.now().strftime("%Y-%m-%d")

                    job = {
                        "title": title,
                        "company": company,
                        "region": "Ubicación no especificada",
                        "category": category_name,
                        "type": "No especificado",
                        "description": cleaned_description,
                        "pubDate": formatted_date,
                        "link": link,
                        "guid": guid,
                        "source": "jobscollider"
                    }
                    all_jobs.append(job)
                
                print(f"Procesados {len(all_jobs)} trabajos hasta ahora.")
                
            except ET.ParseError as e:
                print(f"Error al parsear XML de {url}: {e}")
            
            # Sleep aleatorio entre 1 y 5 segundos
            sleep_time = random.uniform(0.1, 0.5)
            print(f"Esperando {sleep_time:.2f} segundos antes de la siguiente llamada...")
            time.sleep(sleep_time)
        else:
            print(f"Error inesperado: {response.status_code} para {url}")
    
    # Guardar todos los trabajos en un solo archivo
    if all_jobs:
        today = datetime.now().strftime("%Y-%m-%d")
        jc_dir = os.path.join("data", "jobscollider")
        os.makedirs(jc_dir, exist_ok=True)
        file_path = os.path.join(jc_dir, f"{today}_jobscollider_jobs_all.json")
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_jobs, f, indent=4, ensure_ascii=False)
        
        print(f"Datos guardados en: {file_path}. Total de trabajos: {len(all_jobs)}")
        
        # Imprimir el JSON de trabajos
        print(json.dumps(all_jobs, indent=4))
        
    return all_jobs



