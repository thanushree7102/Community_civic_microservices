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
    "../database/scheme_feedback.db"
)

CITIZEN_SERVICE_URL = "http://localhost:5001"
COMPLAINT_SERVICE_URL = "http://localhost:5002"

FREE_UNITS = 200
RATE_PER_UNIT_ABOVE_LIMIT = 6
GRUHA_LAKSHMI_AMOUNT = 2000


def get_db():
    return sqlite3.connect(DATABASE)


def initialize_database():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id INTEGER NOT NULL,
            actually_solved TEXT NOT NULL,
            satisfaction_rating INTEGER NOT NULL,
            comments TEXT,
            submitted_at TEXT NOT NULL
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS scheme_bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_id INTEGER NOT NULL,
            citizen_name TEXT NOT NULL,
            units_consumed INTEGER NOT NULL,
            is_woman BOOLEAN NOT NULL,
            gruha_jyothi_discount INTEGER NOT NULL,
            gruha_lakshmi_amount INTEGER NOT NULL,
            final_amount INTEGER NOT NULL,
            calculated_at TEXT NOT NULL
        )
    """)
    db.commit()
    db.close()


@app.route("/feedback/<int:complaint_id>", methods=["POST"])
def submit_feedback(complaint_id):
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
    actually_solved = data["actually_solved"]
    satisfaction_rating = data["satisfaction_rating"]
    comments = data.get("comments", "")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO feedback
        (complaint_id, actually_solved, satisfaction_rating, comments, submitted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (complaint_id, actually_solved, satisfaction_rating, comments,
          datetime.now().isoformat()))
    db.commit()
    feedback_id = cursor.lastrowid
    db.close()

    return jsonify({
        "feedback_id": feedback_id,
        "complaint_id": complaint_id,
        "complaint_status": complaint["status"],
        "actually_solved": actually_solved,
        "satisfaction_rating": satisfaction_rating,
        "comments": comments
    }), 201


@app.route("/feedback/<int:complaint_id>", methods=["GET"])
def get_feedback(complaint_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, complaint_id, actually_solved, satisfaction_rating, comments, submitted_at
        FROM feedback
        WHERE complaint_id = ?
        ORDER BY submitted_at DESC
        LIMIT 1
    """, (complaint_id,))
    row = cursor.fetchone()
    db.close()

    if row is None:
        return jsonify({"error": "No feedback found for this complaint"}), 404

    return jsonify({
        "feedback_id": row[0],
        "complaint_id": row[1],
        "actually_solved": row[2],
        "satisfaction_rating": row[3],
        "comments": row[4],
        "submitted_at": row[5]
    })


@app.route("/scheme/<int:citizen_id>", methods=["POST"])
def calculate_bill(citizen_id):
    try:
        response = requests.get(
            f"{CITIZEN_SERVICE_URL}/citizens/{citizen_id}",
            timeout=3
        )
    except requests.exceptions.RequestException:
        return jsonify({"error": "Citizen Service is unavailable"}), 503

    if response.status_code == 404:
        return jsonify({"error": "Citizen does not exist"}), 400
    if response.status_code != 200:
        return jsonify({"error": "Unable to verify citizen"}), 500

    citizen = response.json()

    data = request.json
    units_consumed = data["units_consumed"]
    is_woman = data.get("is_woman", False)

    units_above_limit = max(0, units_consumed - FREE_UNITS)
    electricity_charge = units_above_limit * RATE_PER_UNIT_ABOVE_LIMIT
    gruha_jyothi_discount = min(units_consumed, FREE_UNITS) * RATE_PER_UNIT_ABOVE_LIMIT

    gruha_lakshmi_amount = GRUHA_LAKSHMI_AMOUNT if is_woman else 0
    final_amount = max(0, electricity_charge - gruha_lakshmi_amount)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO scheme_bills
        (citizen_id, citizen_name, units_consumed, is_woman,
         gruha_jyothi_discount, gruha_lakshmi_amount, final_amount, calculated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (citizen_id, citizen["name"], units_consumed, is_woman,
          gruha_jyothi_discount, gruha_lakshmi_amount, final_amount,
          datetime.now().isoformat()))
    db.commit()
    bill_id = cursor.lastrowid
    db.close()

    return jsonify({
        "bill_id": bill_id,
        "citizen_id": citizen_id,
        "citizen_name": citizen["name"],
        "units_consumed": units_consumed,
        "free_units": FREE_UNITS,
        "electricity_charge_before_lakshmi": electricity_charge,
        "gruha_jyothi_discount": gruha_jyothi_discount,
        "is_woman": is_woman,
        "gruha_lakshmi_amount": gruha_lakshmi_amount,
        "final_amount": final_amount
    }), 201


@app.route("/scheme/<int:citizen_id>", methods=["GET"])
def get_bill(citizen_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, citizen_id, citizen_name, units_consumed, is_woman,
               gruha_jyothi_discount, gruha_lakshmi_amount, final_amount, calculated_at
        FROM scheme_bills
        WHERE citizen_id = ?
        ORDER BY calculated_at DESC
        LIMIT 1
    """, (citizen_id,))
    row = cursor.fetchone()
    db.close()

    if row is None:
        return jsonify({"error": "No bill found for this citizen"}), 404

    return jsonify({
        "bill_id": row[0],
        "citizen_id": row[1],
        "citizen_name": row[2],
        "units_consumed": row[3],
        "is_woman": bool(row[4]),
        "gruha_jyothi_discount": row[5],
        "gruha_lakshmi_amount": row[6],
        "final_amount": row[7],
        "calculated_at": row[8]
    })


if __name__ == "__main__":
    initialize_database()
    app.run(port=5003, debug=True)