import json
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OUTPUT_FILE = Path(__file__).with_name("infos_recues.jsonl")

@app.route("/", methods=["GET"])
def home():
    return "<h1>Collecteur d'infos actif</h1><p>Ce service reçoit les données envoyées par une page web.</p>", 200

@app.route("/collect", methods=["POST"])
def collect():
    payload = request.get_json(silent=True) or {"message": "Aucune donnée JSON reçue"}

    safe_payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "ipPublic": payload.get("data", {}).get("ipPublic"),
        "pays": payload.get("data", {}).get("localisation", {}).get("pays"),
        "ville": payload.get("data", {}).get("localisation", {}).get("ville"),
        "langue": payload.get("data", {}).get("infosNavigateur", {}).get("langue"),
        "plateforme": payload.get("data", {}).get("infosNavigateur", {}).get("plateforme"),
    }

    with OUTPUT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(safe_payload, ensure_ascii=False) + "\n")

    return jsonify({"status": "ok", "file": str(OUTPUT_FILE.name)}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
