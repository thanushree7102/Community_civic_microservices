from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import time
import logging

app = Flask(__name__)
CORS(app)

# -----------------------------
# Microservice URLs
# -----------------------------

CITIZEN_SERVICE_URL = "http://localhost:5001"
COMPLAINT_SERVICE_URL = "http://localhost:5002"
EMERGENCY_SERVICE_URL = "http://localhost:5003"

# -----------------------------
# Rate Limiting
# Maximum 100 requests/minute
# -----------------------------

RATE_LIMIT = 100
request_log = {}


def check_rate_limit():
    client_ip = request.remote_addr
    current_time = time.time()

    if client_ip not in request_log:
        request_log[client_ip] = []

    # Keep only requests from the last 60 seconds
    request_log[client_ip] = [
        timestamp
        for timestamp in request_log[client_ip]
        if current_time - timestamp < 60
    ]

    if len(request_log[client_ip]) >= RATE_LIMIT:
        return False

    request_log[client_ip].append(current_time)
    return True


# -----------------------------
# Logging
# -----------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# -----------------------------
# Security Headers
# -----------------------------

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"

    return response


# -----------------------------
# Global Request Logging
# -----------------------------

@app.before_request
def log_request():
    logging.info(
        "%s %s from %s",
        request.method,
        request.path,
        request.remote_addr
    )


# -----------------------------
# Rate Limit Middleware
# -----------------------------

@app.before_request
def rate_limit():
    if request.path == "/":
        return

    if not check_rate_limit():
        return jsonify({
            "error": "Rate limit exceeded",
            "limit": "100 requests per minute"
        }), 429


# -----------------------------
# Forward Request
# -----------------------------

def forward_request(target_url, path):
    url = f"{target_url}/{path}"

    try:
        response = requests.request(
            method=request.method,
            url=url,
            json=request.get_json(silent=True),
            params=request.args,
            headers={
                "Content-Type": request.headers.get(
                    "Content-Type",
                    "application/json"
                )
            },
            timeout=5
        )

    except requests.exceptions.RequestException:
        logging.error("Service unavailable: %s", target_url)

        return jsonify({
            "error": f"Service at {target_url} is unavailable"
        }), 503

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get(
            "Content-Type",
            "application/json"
        )
    )


# ============================================================
# API VERSION 1
# ============================================================


# -----------------------------
# Citizen Service
# /api/v1/citizens/*
# -----------------------------

@app.route(
    "/api/v1/citizens",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "DELETE"]
)
@app.route(
    "/api/v1/citizens/<path:path>",
    methods=["GET", "POST", "PUT", "DELETE"]
)
def route_citizens(path):
    full_path = f"citizens/{path}" if path else "citizens"

    return forward_request(
        CITIZEN_SERVICE_URL,
        full_path
    )


# -----------------------------
# Complaint Service
# /api/v1/complaints/*
# -----------------------------

@app.route(
    "/api/v1/complaints",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "DELETE"]
)
@app.route(
    "/api/v1/complaints/<path:path>",
    methods=["GET", "POST", "PUT", "DELETE"]
)
def route_complaints(path):
    full_path = f"complaints/{path}" if path else "complaints"

    return forward_request(
        COMPLAINT_SERVICE_URL,
        full_path
    )


# -----------------------------
# Emergency Service
# /api/v1/emergencies/*
# -----------------------------

@app.route(
    "/api/v1/emergencies",
    defaults={"path": ""},
    methods=["GET", "POST", "PUT", "DELETE"]
)
@app.route(
    "/api/v1/emergencies/<path:path>",
    methods=["GET", "POST", "PUT", "DELETE"]
)
def route_emergencies(path):
    full_path = f"emergencies/{path}" if path else "emergencies"

    return forward_request(
        EMERGENCY_SERVICE_URL,
        full_path
    )


# -----------------------------
# Gateway Health Check
# -----------------------------

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "message": "API Gateway is running",
        "port": 5000,
        "routes": {
            "/api/v1/citizens/*": "Citizen Service (port 5001)",
            "/api/v1/complaints/*": "Complaint Service (port 5002)",
            "/api/v1/emergencies/*": "Emergency Service (port 5003)"
        },
        "rate_limit": "100 requests per minute"
    })


# -----------------------------
# Run Gateway
# -----------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )