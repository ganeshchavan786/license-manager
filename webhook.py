"""
GitHub Webhook Server
GitHub push → trigger deploy.sh automatically

Run: pm2 start webhook.py --name salarypay-webhook --interpreter python3
"""

import hmac
import hashlib
import subprocess
import logging
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# .env मधून secret घ्या
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-this-secret")
APP_DIR = "/var/www/salarypay"
LOG_FILE = "/var/log/salarypay/webhook.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def verify_signature(payload_body: bytes, signature: str) -> bool:
    """GitHub webhook signature verify करतो"""
    if not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route("/deploy", methods=["POST"])
def deploy():
    # Signature verify करा
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.data, signature):
        logging.warning("Unauthorized webhook request!")
        return jsonify({"error": "Unauthorized"}), 403

    # फक्त main branch वर push झाल्यावर deploy करा
    payload = request.json or {}
    ref = payload.get("ref", "")
    if ref != "refs/heads/main":
        logging.info(f"Skipping deploy for branch: {ref}")
        return jsonify({"message": f"Skipped (branch: {ref})"}), 200

    # Deploy script run करा
    logging.info("Deploy triggered!")
    try:
        result = subprocess.run(
            ["bash", f"{APP_DIR}/deploy.sh"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        if result.returncode == 0:
            logging.info("Deploy successful!")
            return jsonify({"message": "Deploy successful"}), 200
        else:
            logging.error(f"Deploy failed: {result.stderr}")
            return jsonify({"error": result.stderr}), 500
    except subprocess.TimeoutExpired:
        logging.error("Deploy timed out!")
        return jsonify({"error": "Deploy timed out"}), 500
    except Exception as e:
        logging.error(f"Deploy error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=9000)  # localhost only - NPM मार्फत expose करा
