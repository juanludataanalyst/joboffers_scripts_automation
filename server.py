from flask import Flask, Response, jsonify
from aijobs_feed_data import get_aijobs_jobs
from remotive_feed_data import get_remotive_jobs
from remoteok_data import get_remoteok_jobs
from jobicy_feed_data import get_jobicy_jobs
from weworkremotely_feed_data import get_weworkremotely_jobs

import os
import json

app = Flask(__name__)

@app.route('/jobs/aijobs', methods=['GET'])
def fetch_aijobs():
    jobs = get_aijobs_jobs()
    if jobs:
        return jsonify(jobs)
    return Response(json.dumps({"error": "No se pudieron obtener los trabajos ai platform"}), status=500, mimetype='application/json')


@app.route('/jobs/remotivejobs', methods=['GET'])
def fetch_remotivejobs():  # Renombrado
    jobs = get_remotive_jobs()
    if jobs:
        return jsonify(jobs)
    return Response(json.dumps({"error": "No se pudieron obtener los trabajos remotive jobs"}), status=500, mimetype='application/json')



@app.route('/jobs/remoteokjobs', methods=['GET'])
def fetch_remoteokjobs():  # Renombrado
    jobs = get_remoteok_jobs()
    if jobs:
        return jsonify(jobs)
    return Response(json.dumps({"error": "No se pudieron obtener los trabajos remotive jobs"}), status=500, mimetype='application/json')

@app.route('/jobs/jobicyjobs', methods=['GET'])
def fetch_jobicyjobs():  # Renombrado
    jobs = get_jobicy_jobs()
    if jobs:
        return jsonify(jobs)
    return Response(json.dumps({"error": "No se pudieron obtener los trabajos remotive jobs"}), status=500, mimetype='application/json')


@app.route('/jobs/weworkremotelyjobs', methods=['GET'])
def fetch_weworkremotelyjobs():  # Renombrado
    jobs = get_weworkremotely_jobs()
    if jobs:
        return jsonify(jobs)
    return Response(json.dumps({"error": "No se pudieron obtener los trabajos remotive jobs"}), status=500, mimetype='application/json')




@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"message": "Servicio de scraping de ofertas activo"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
