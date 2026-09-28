from flask import Flask, request, jsonify
from flask_cors import CORS

from agent import generate_meeting_brief

from hindsight_memory import (
    retain_meeting,
    retain_outcome,
)


app = Flask(__name__)

CORS(app)


# ==================================================
# HEALTH CHECK
# ==================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "status": "ok",
        "service": "Meeting Prep Agent"
    })


# ==================================================
# PREPARE MEETING
# ==================================================

@app.route("/api/prepare", methods=["POST"])
def prepare():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    person_name = data.get("person_name")
    company = data.get("company", "")
    role = data.get("role", "")
    meeting_goal = data.get("meeting_goal")

    if not person_name:
        return jsonify({
            "error": "person_name is required"
        }), 400

    if not meeting_goal:
        return jsonify({
            "error": "meeting_goal is required"
        }), 400

    try:

        result = generate_meeting_brief(
            person_name=person_name,
            company=company,
            role=role,
            meeting_goal=meeting_goal
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# SAVE MEETING
# ==================================================

@app.route("/api/meetings", methods=["POST"])
def save_meeting():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:

        result = retain_meeting(
            meeting_id=data.get("meeting_id"),
            meeting_date=data.get("meeting_date"),
            person_name=data.get("person_name"),
            company=data.get("company"),
            role=data.get("role"),
            purpose=data.get("purpose"),
            concerns=data.get("concerns", ""),
            preferences=data.get("preferences", ""),
            commitments=data.get("commitments", ""),
            outcome=data.get("outcome", "")
        )

        return jsonify({
            "success": True,
            "message": "Meeting stored in Hindsight"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# SAVE OUTCOME
# ==================================================

@app.route("/api/outcomes", methods=["POST"])
def save_outcome():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    try:

        result = retain_outcome(
            meeting_id=data.get("meeting_id"),
            person_name=data.get("person_name"),
            outcome=data.get("outcome", ""),
            reason=data.get("reason", ""),
            new_information=data.get(
                "new_information",
                ""
            ),
            commitment=data.get(
                "commitment",
                ""
            )
        )

        return jsonify({
            "success": True,
            "message": "Meeting outcome stored in Hindsight"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ==================================================
# RUN SERVER
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
