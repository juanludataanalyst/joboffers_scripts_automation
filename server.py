from flask import Flask, Response, jsonify
from aijobs_feed_data import get_aijobs_jobs
import os
import json

app = Flask(__name__)

@app.route('/jobs/aijobs', methods=['GET'])
def fetch_aijobs():
    jobs = get_aijobs_jobs()
    if jobs:
        return jsonify(jobs)
    return Response(json.dumps({"error": "No se pudieron obtener los trabajos"}), status=500, mimetype='application/json')


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Servicio de scraping de ofertas activo"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
