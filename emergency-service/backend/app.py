from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "emergency.db")

CITIZEN_SERVICE_URL = "http://localhost:5001"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS emergencies (
            emergency_id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_id INTEGER,
            type TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'REPORTED',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


@app.route("/emergencies", methods=["POST"])
def create_emergency():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = [
        "citizen_id",
        "type",
        "description",
        "location",
        "severity"
    ]

    for field in required_fields:
        if data.get(field) is None or data.get(field) == "":
            return jsonify({"error": f"{field} is required"}), 400

    try:
        citizen_id = int(data["citizen_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "citizen_id must be an integer"}), 400

    # Verify citizen through Citizen Service
    try:
        response = requests.get(
            f"{CITIZEN_SERVICE_URL}/citizens/{citizen_id}",
            timeout=3
        )

        if response.status_code == 404:
            return jsonify({
                "error": "Citizen not found",
                "citizen_id": citizen_id
            }), 404

        if response.status_code != 200:
            return jsonify({
                "error": "Citizen Service returned an unexpected response"
            }), 502

    except requests.exceptions.RequestException:
        return jsonify({
            "error": "Citizen Service is unavailable"
        }), 503

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()

    cursor = conn.execute("""
        INSERT INTO emergencies
        (citizen_id, type, description, location, severity, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        citizen_id,
        data["type"],
        data["description"],
        data["location"],
        data["severity"],
        "REPORTED",
        created_at
    ))

    emergency_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Emergency reported successfully",
        "emergency_id": emergency_id,
        "citizen_id": citizen_id,
        "status": "REPORTED"
    }), 201


@app.route("/emergencies", methods=["GET"])
def get_emergencies():
    conn = get_db_connection()

    emergencies = conn.execute("""
        SELECT * FROM emergencies
        ORDER BY emergency_id DESC
    """).fetchall()

    conn.close()

    return jsonify([dict(emergency) for emergency in emergencies]), 200


@app.route("/emergencies/<int:emergency_id>", methods=["GET"])
def get_emergency(emergency_id):
    conn = get_db_connection()

    emergency = conn.execute("""
        SELECT * FROM emergencies
        WHERE emergency_id = ?
    """, (emergency_id,)).fetchone()

    conn.close()

    if emergency is None:
        return jsonify({"error": "Emergency not found"}), 404

    return jsonify(dict(emergency)), 200


@app.route("/emergencies/<int:emergency_id>/status", methods=["PUT"])
def update_status(emergency_id):
    data = request.get_json()

    if not data or not data.get("status"):
        return jsonify({"error": "status is required"}), 400

    allowed_statuses = [
        "REPORTED",
        "IN_PROGRESS",
        "RESOLVED",
        "CANCELLED"
    ]

    status = data["status"].upper()

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status",
            "allowed_statuses": allowed_statuses
        }), 400

    conn = get_db_connection()

    cursor = conn.execute("""
        UPDATE emergencies
        SET status = ?
        WHERE emergency_id = ?
    """, (status, emergency_id))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        return jsonify({"error": "Emergency not found"}), 404

    conn.close()

    return jsonify({
        "message": "Emergency status updated successfully",
        "emergency_id": emergency_id,
        "status": status
    }), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "service": "Emergency Service",
        "status": "running"
    })


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5003, debug=True)