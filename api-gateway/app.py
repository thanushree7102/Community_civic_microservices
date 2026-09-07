from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

CITIZEN_SERVICE_URL = "http://localhost:5001"
COMPLAINT_SERVICE_URL = "http://localhost:5002"
SURVEY_SERVICE_URL = "http://localhost:5003"


def forward_request(target_url, path):
    url = f"{target_url}/{path}"
    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json(silent=True),
            params=request.args,
            timeout=5
        )
    except requests.exceptions.RequestException:
        return jsonify({
            "error": f"Service at {target_url} is unavailable"
        }), 503
    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/json")
    )


@app.route("/citizens", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/citizens/<path:path>", methods=["GET", "POST"])
def route_citizens(path):
    full_path = f"citizens/{path}" if path else "citizens"
    return forward_request(CITIZEN_SERVICE_URL, full_path)


@app.route("/complaints", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/complaints/<path:path>", methods=["GET", "POST"])
def route_complaints(path):
    full_path = f"complaints/{path}" if path else "complaints"
    return forward_request(COMPLAINT_SERVICE_URL, full_path)


@app.route("/survey/<path:path>", methods=["GET", "POST"])
def route_survey(path):
    return forward_request(SURVEY_SERVICE_URL, f"survey/{path}")


@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "message": "API Gateway is running",
        "routes": {
            "/citizens/*": "Citizen Service (port 5001)",
            "/complaints/*": "Complaint Service (port 5002)",
            "/survey/*": "Survey Service (port 5003)"
        }
    })


if __name__ == "__main__":
    app.run(port=5000, debug=True)
