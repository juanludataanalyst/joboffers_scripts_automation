import requests
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import json
import sys
from flask import Flask, Response

# Configurar la salida para usar UTF-8 en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

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
                    "title": item.find('title').text if item.find('title') is not None else "",
                    "company": item.find('job_listing:company', namespaces={'job_listing': 'https://aijobs.net'}).text if item.find('job_listing:company', namespaces={'job_listing': 'https://aijobs.net'}) is not None else "Empresa no especificada",
                    "description": item.find('description').text if item.find('description') is not None else "",
                    "pubdate": item.find('pubDate').text if item.find('pubDate') is not None else "",
                    "link": item.find('link').text if item.find('link') is not None else "",
                    "location": item.find('job_listing:location', namespaces={'job_listing': 'https://aijobs.net'}).text if item.find('job_listing:location', namespaces={'job_listing': 'https://aijobs.net'}) is not None else "Ubicación no especificada",
                    "jobtype": item.find('job_listing:job_type', namespaces={'job_listing': 'https://aijobs.net'}).text if item.find('job_listing:job_type', namespaces={'job_listing': 'https://aijobs.net'}) is not None else "No especificado",
                }
                jobs.append(job)
            
            today = datetime.now().strftime("%Y-%m-%d")
            hour = datetime.now().strftime("%H")
            aijobs_dir = os.path.join("data", "aijobs")
            os.makedirs(aijobs_dir, exist_ok=True)
            file_path = os.path.join(aijobs_dir, f"{today}_aijobs_jobs_{hour}h.json")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=4)
            
            # Imprimir el JSON de trabajos en lugar de retornarlo como respuesta HTTP
            print(json.dumps(jobs, indent=4))
            return jobs
        except ET.ParseError as e:
            print(f"Error al parsear XML: {e}", file=sys.stderr)
            return None
    else:
        print(f"Error inesperado: {response.status_code}", file=sys.stderr)
        return None

@app.route('/jobs', methods=['GET'])
def fetch_jobs():
    result = get_aijobs_jobs()
    if result is not None:
        # Ahora devuelve la respuesta como json de la misma forma
        return Response(json.dumps(result, indent=4), mimetype='application/json')
    else:
        error_msg = json.dumps({"error": "No se pudieron obtener los trabajos"})
        return Response(error_msg, mimetype='application/json', status=500)

@app.route('/', methods=['GET'])
def health_check():
    return Response(json.dumps({"message": "Servicio de AIJobs activo"}), mimetype='application/json')

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
