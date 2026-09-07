from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATABASE = os.path.join(
    os.path.dirname(__file__),
    "../database/survey.db"
)

COMPLAINT_SERVICE_URL = "http://localhost:5002"


def get_db():
    return sqlite3.connect(DATABASE)


def initialize_database():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS survey_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            actually_solved TEXT NOT NULL,
            aware_of_scheme TEXT NOT NULL,
            satisfaction_rating INTEGER NOT NULL,
            comments TEXT,
            submitted_at TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()


@app.route("/survey/<int:complaint_id>", methods=["POST"])
def submit_survey(complaint_id):
    # Verify the complaint exists via REST call to Complaint Service
    try:
        response = requests.get(
            f"{COMPLAINT_SERVICE_URL}/complaints/{complaint_id}",
            timeout=3
        )
    except requests.exceptions.RequestException:
        return jsonify({"error": "Complaint Service is unavailable"}), 503

    if response.status_code == 404:
        return jsonify({"error": "Complaint does not exist"}), 400
    if response.status_code != 200:
        return jsonify({"error": "Unable to verify complaint"}), 500

    complaint = response.json()

    data = request.json
    actually_solved = data["actually_solved"]          # "Yes" or "No"
    aware_of_scheme = data["aware_of_scheme"]           # "Yes" or "No"
    satisfaction_rating = data["satisfaction_rating"]    # 1-5
    comments = data.get("comments", "")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO survey_responses
        (complaint_id, actually_solved, aware_of_scheme, satisfaction_rating, comments, submitted_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (complaint_id, actually_solved, aware_of_scheme, satisfaction_rating,
          comments, datetime.now().isoformat()))
    db.commit()
    survey_id = cursor.lastrowid
    db.close()

    return jsonify({
        "survey_id": survey_id,
        "complaint_id": complaint_id,
        "complaint_status": complaint["status"],
        "actually_solved": actually_solved,
        "aware_of_scheme": aware_of_scheme,
        "satisfaction_rating": satisfaction_rating,
        "comments": comments
    }), 201


@app.route("/survey/<int:complaint_id>", methods=["GET"])
def get_survey(complaint_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, complaint_id, actually_solved, aware_of_scheme,
               satisfaction_rating, comments, submitted_at
        FROM survey_responses
        WHERE complaint_id = ?
        ORDER BY submitted_at DESC
        LIMIT 1
    """, (complaint_id,))
    row = cursor.fetchone()
    db.close()

    if row is None:
        return jsonify({"error": "No survey found for this complaint"}), 404

    return jsonify({
        "survey_id": row[0],
        "complaint_id": row[1],
        "actually_solved": row[2],
        "aware_of_scheme": row[3],
        "satisfaction_rating": row[4],
        "comments": row[5],
        "submitted_at": row[6]
    })


if __name__ == "__main__":
    initialize_database()
    app.run(port=5003, debug=True)