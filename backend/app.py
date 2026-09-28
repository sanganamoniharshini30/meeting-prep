import os
import json
from datetime import datetime

from flask import (
    Flask,
    request,
    jsonify,
    send_from_directory
)

from flask_cors import CORS

from agent import generate_meeting_brief

from hindsight_memory import (
    retain_meeting,
    retain_outcome,
    recall_person
)


# ============================================================
# PROJECT / FRONTEND PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

PROJECT_DIR = os.path.dirname(
    BASE_DIR
)

FRONTEND_DIR = os.path.join(
    PROJECT_DIR,
    "frontend"
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(
    __name__,
    static_folder=FRONTEND_DIR,
    static_url_path=""
)

CORS(app)


# ============================================================
# DASHBOARD DATA FILE
# ============================================================

DASHBOARD_FILE = os.path.join(
    BASE_DIR,
    "dashboard_data.json"
)


def load_dashboard_data():

    if not os.path.exists(DASHBOARD_FILE):

        return {
            "meetings": [],
            "outcomes": []
        }

    try:

        with open(
            DASHBOARD_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if "meetings" not in data:

                data["meetings"] = []

            if "outcomes" not in data:

                data["outcomes"] = []

            return data

    except (
        json.JSONDecodeError,
        OSError
    ):

        return {
            "meetings": [],
            "outcomes": []
        }


def save_dashboard_data(data):

    with open(
        DASHBOARD_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def calculate_dashboard_stats(data):

    meetings = data.get(
        "meetings",
        []
    )

    outcomes = data.get(
        "outcomes",
        []
    )

    memories = (
        len(meetings)
        +
        len(outcomes)
    )

    contacts = set()

    for meeting in meetings:

        person_name = meeting.get(
            "person_name",
            ""
        ).strip()

        if person_name:

            contacts.add(
                person_name.lower()
            )

    pending_commitments = 0

    for meeting in meetings:

        commitment = meeting.get(
            "commitments",
            ""
        ).strip()

        outcome = meeting.get(
            "outcome",
            ""
        ).strip()

        if commitment and not outcome:

            pending_commitments += 1

    return {

        "memories":
            memories,

        "contacts":
            len(contacts),

        "pending_commitments":
            pending_commitments

    }


# ============================================================
# HOME / FRONTEND ROUTES
# ============================================================

@app.route("/")
def home():

    return send_from_directory(
        FRONTEND_DIR,
        "login.html"
    )


@app.route("/<path:page>")
def frontend_page(page):

    return send_from_directory(
        FRONTEND_DIR,
        page
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "ok",

        "service":
            "Meeting Prep Agent"

    })


# ============================================================
# PREPARE MEETING
# ============================================================

@app.route(
    "/api/prepare",
    methods=["POST"]
)
def prepare():

    data = request.get_json()

    if not data:

        return jsonify({

            "error":
                "Request body is required"

        }), 400


    # ========================================================
    # USER EMAIL
    # ========================================================

    user_email = data.get(
        "user_email",
        ""
    ).strip()


    if not user_email:

        return jsonify({

            "success":
                False,

            "error":
                "user_email is required"

        }), 400


    # ========================================================
    # GET FORM DATA
    # ========================================================

    person_name = data.get(
        "person_name"
    )

    company = data.get(
        "company",
        ""
    )

    role = data.get(
        "role",
        ""
    )

    meeting_date = data.get(
        "meeting_date",
        ""
    )

    meeting_time = data.get(
        "meeting_time",
        ""
    )

    meeting_goal = data.get(
        "meeting_goal",
        ""
    )

    purpose = data.get(
        "purpose",
        ""
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if not person_name:

        return jsonify({

            "error":
                "person_name is required"

        }), 400


    if not meeting_goal:

        return jsonify({

            "error":
                "meeting_goal is required"

        }), 400


    try:

        # ====================================================
        # CREATE UNIQUE MEETING ID
        # ====================================================

        meeting_id = (
            "meeting-"
            +
            datetime.now().strftime(
                "%Y%m%d%H%M%S%f"
            )
        )


        # ====================================================
        # GENERATE AI MEETING BRIEF
        # ====================================================

        result = generate_meeting_brief(
            user_email=user_email,
            person_name=person_name,
            company=company,
            role=role,
            meeting_goal=meeting_goal,
            meeting_date=meeting_date,
            meeting_time=meeting_time
        )

        # ====================================================
        # STORE CURRENT MEETING IN HINDSIGHT
        # ====================================================

        retain_meeting(
            meeting_id=meeting_id,
            user_email=user_email,
            meeting_date=meeting_date,
            person_name=person_name,
            company=company,
            role=role,
            purpose=purpose,
            concerns="",
            preferences="",
            commitments="",
            outcome=""
        )

        # ====================================================
        # SAVE MEETING TO DASHBOARD DATA
        # ====================================================

        dashboard = load_dashboard_data()


        new_meeting = {

            "meeting_id":
                meeting_id,

            "user_email":
                user_email,

            "person_name":
                person_name,

            "company":
                company,

            "role":
                role,

            "purpose":
                purpose,

            "meeting_goal":
                meeting_goal,

            "meeting_date":
                meeting_date,

            "meeting_time":
                meeting_time,

            "concerns":
                "",

            "preferences":
                "",

            "commitments":
                "",

            "outcome":
                "",

            "brief":
                result.get(
                    "brief",
                    ""
                )

        }


        dashboard["meetings"].insert(

            0,

            new_meeting

        )


        save_dashboard_data(
            dashboard
        )


        # ====================================================
        # RETURN RESULT TO FRONTEND
        # ====================================================

        return jsonify({

            "success":
                True,

            "meeting_id":
                meeting_id,

            "person_name":
                person_name,

            "memory_count":
                result.get(
                    "memory_count",
                    0
                ),

            "memories":
                result.get(
                    "memories",
                    []
                ),

            "brief":
                result.get(
                    "brief",
                    ""
                )

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# SAVE / STORE MEETING
# ============================================================

@app.route(
    "/api/meetings",
    methods=["POST"]
)
def save_meeting():

    data = request.get_json()

    if not data:

        return jsonify({

            "error":
                "Request body is required"

        }), 400


    # ========================================================
    # USER EMAIL
    # ========================================================

    user_email = data.get(
        "user_email",
        ""
    ).strip()


    if not user_email:

        return jsonify({

            "success":
                False,

            "error":
                "user_email is required"

        }), 400


    try:

        # ====================================================
        # MEETING ID
        # ====================================================

        meeting_id = data.get(
            "meeting_id"
        )

        if not meeting_id:

            meeting_id = (
                "meeting-"
                +
                datetime.now().strftime(
                    "%Y%m%d%H%M%S%f"
                )
            )


        # ====================================================
        # STORE IN HINDSIGHT
        # ====================================================

        retain_meeting(

            meeting_id=meeting_id,

            meeting_date=data.get(
                "meeting_date",
                datetime.now().strftime(
                    "%Y-%m-%d"
                )
            ),

            person_name=data.get(
                "person_name",
                ""
            ),

            company=data.get(
                "company",
                ""
            ),

            role=data.get(
                "role",
                ""
            ),

            purpose=data.get(
                "purpose",
                ""
            ),

            concerns=data.get(
                "concerns",
                ""
            ),

            preferences=data.get(
                "preferences",
                ""
            ),

            commitments=data.get(
                "commitments",
                ""
            ),

            outcome=data.get(
                "outcome",
                ""
            )

        )


        # ====================================================
        # SAVE TO DASHBOARD
        # ====================================================

        dashboard = load_dashboard_data()


        new_meeting = {

            "meeting_id":
                meeting_id,

            "user_email":
                user_email,

            "person_name":
                data.get(
                    "person_name",
                    ""
                ),

            "company":
                data.get(
                    "company",
                    ""
                ),

            "role":
                data.get(
                    "role",
                    ""
                ),

            "purpose":
                data.get(
                    "purpose",
                    ""
                ),

            "meeting_goal":
                data.get(
                    "meeting_goal",
                    ""
                ),

            "meeting_date":
                data.get(
                    "meeting_date",
                    datetime.now().isoformat()
                ),

            "meeting_time":
                data.get(
                    "meeting_time",
                    ""
                ),

            "concerns":
                data.get(
                    "concerns",
                    ""
                ),

            "preferences":
                data.get(
                    "preferences",
                    ""
                ),

            "commitments":
                data.get(
                    "commitments",
                    ""
                ),

            "outcome":
                data.get(
                    "outcome",
                    ""
                ),

            "brief":
                data.get(
                    "brief",
                    ""
                )

        }


        dashboard["meetings"].insert(

            0,

            new_meeting

        )


        save_dashboard_data(
            dashboard
        )


        return jsonify({

            "success":
                True,

            "message":
                "Meeting stored successfully",

            "meeting":
                new_meeting

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# SAVE OUTCOME
# ============================================================

@app.route(
    "/api/outcomes",
    methods=["POST"]
)
def save_outcome():

    data = request.get_json()

    if not data:

        return jsonify({

            "error":
                "Request body is required"

        }), 400


    # ========================================================
    # USER EMAIL
    # ========================================================

    user_email = data.get(
        "user_email",
        ""
    ).strip()


    if not user_email:

        return jsonify({

            "success":
                False,

            "error":
                "user_email is required"

        }), 400


    try:

        # ====================================================
        # GET OUTCOME DATA
        # ====================================================

        meeting_id = data.get(
            "meeting_id"
        )

        person_name = data.get(
            "person_name",
            ""
        )

        outcome = data.get(
            "outcome",
            ""
        )

        reason = data.get(
            "reason",
            ""
        )

        new_information = data.get(
            "new_information",
            ""
        )

        commitment = data.get(
            "commitment",
            ""
        )


        # ====================================================
        # STORE OUTCOME IN HINDSIGHT
        # ====================================================

        retain_outcome(

            meeting_id=meeting_id,

            person_name=person_name,

            outcome=outcome,

            reason=reason,

            new_information=new_information,

            commitment=commitment

        )


        # ====================================================
        # UPDATE DASHBOARD DATA
        # ====================================================

        dashboard = load_dashboard_data()


        new_outcome = {

            "meeting_id":
                meeting_id,

            "user_email":
                user_email,

            "person_name":
                person_name,

            "outcome":
                outcome,

            "reason":
                reason,

            "new_information":
                new_information,

            "commitment":
                commitment,

            "date":
                datetime.now().isoformat()

        }


        dashboard["outcomes"].insert(

            0,

            new_outcome

        )


        # ====================================================
        # UPDATE ORIGINAL MEETING
        # ====================================================

        for meeting in dashboard["meetings"]:

            if (
                meeting.get(
                    "meeting_id"
                )
                ==
                meeting_id
            ):

                meeting["outcome"] = outcome

                meeting["commitments"] = commitment

                break


        save_dashboard_data(
            dashboard
        )


        return jsonify({

            "success":
                True,

            "message":
                "Meeting outcome stored successfully"

        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# GET ONE MEETING
# ============================================================

@app.route("/api/meetings/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id):

    try:

        user_email = request.args.get(
            "user_email",
            ""
        ).strip()

        if not user_email:
            return jsonify({
                "success": False,
                "error": "user_email is required"
            }), 400

        data = load_dashboard_data()

        for meeting in data.get("meetings", []):

            if meeting.get("meeting_id") == meeting_id:

                meeting_user_email = (
                    meeting.get(
                        "user_email",
                        ""
                    ).strip().lower()
                )

                # Make sure this meeting belongs
                # to the currently logged-in user.
                if meeting_user_email != user_email.lower():

                    return jsonify({
                        "success": False,
                        "error": "You do not have access to this meeting"
                    }), 403

                person_name = meeting.get(
                    "person_name",
                    ""
                )

                memories = []

                if person_name:

                    memories = recall_person(
                        user_email,
                        person_name
                    )

                return jsonify({
                    "success": True,
                    "meeting": meeting,
                    "memories": memories
                })

        return jsonify({
            "success": False,
            "error": "Meeting not found"
        }), 404

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
# ============================================================
# DASHBOARD API
# ============================================================

@app.route(
    "/api/dashboard",
    methods=["GET"]
)
def dashboard():

    try:

        # ====================================================
        # GET LOGGED-IN USER EMAIL
        # ====================================================

        user_email = request.args.get(
            "user_email",
            ""
        ).strip()


        if not user_email:

            return jsonify({

                "success":
                    False,

                "error":
                    "user_email is required"

            }), 400


        # ====================================================
        # LOAD ALL DASHBOARD DATA
        # ====================================================

        data = load_dashboard_data()


        # ====================================================
        # FILTER MEETINGS FOR THIS USER
        # ====================================================

        user_meetings = [

            meeting

            for meeting in data.get(
                "meetings",
                []
            )

            if meeting.get(
                "user_email",
                ""
            ).strip().lower()
            ==
            user_email.lower()

        ]


        # ====================================================
        # FILTER OUTCOMES FOR THIS USER
        # ====================================================

        user_outcomes = [

            outcome

            for outcome in data.get(
                "outcomes",
                []
            )

            if outcome.get(
                "user_email",
                ""
            ).strip().lower()
            ==
            user_email.lower()

        ]
        user_memories = []

        for meeting in user_meetings:

            person_name = meeting.get(
                "person_name",
                ""
            ).strip()

            if person_name:
                memories = recall_person(
                    user_email,
                    person_name
                )

                user_memories.extend(memories)

        # ====================================================
        # USER-SPECIFIC DATA
        # ====================================================

        user_data = {

            "meetings":
                user_meetings,

            "outcomes":
                user_outcomes

        }


        # ====================================================
        # CALCULATE USER-SPECIFIC STATISTICS
        # ====================================================

        stats = calculate_dashboard_stats(
            user_data
        )


        recent_meetings = []


        # ====================================================
        # LATEST 10 MEETINGS FOR THIS USER
        # ====================================================

        for meeting in user_meetings[:10]:

            recent_meetings.append({

                "meeting_id":
                    meeting.get(
                        "meeting_id"
                    ),

                "person_name":
                    meeting.get(
                        "person_name",
                        ""
                    ),

                "company":
                    meeting.get(
                        "company",
                        ""
                    ),

                "role":
                    meeting.get(
                        "role",
                        ""
                    ),

                "purpose":
                    meeting.get(
                        "purpose",
                        ""
                    ),

                "meeting_goal":
                    meeting.get(
                        "meeting_goal",
                        ""
                    ),

                "meeting_date":
                    meeting.get(
                        "meeting_date",
                        ""
                    ),

                "meeting_time":
                    meeting.get(
                        "meeting_time",
                        ""
                    ),

                "brief":
                    meeting.get(
                        "brief",
                        ""
                    )

            })


        # ====================================================
        # RETURN USER DASHBOARD
        # ====================================================

        return jsonify({
            "success": True,
            "user_email": user_email,
            "stats": stats,
            "recent_meetings": recent_meetings,
            "memories": user_memories
        })


    except Exception as e:

        return jsonify({

            "success":
                False,

            "error":
                str(e)

        }), 500


# ============================================================
# START FLASK
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
