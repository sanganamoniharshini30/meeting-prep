import os

from dotenv import load_dotenv

from hindsight_client import Hindsight


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

HINDSIGHT_API_KEY = os.getenv(
    "HINDSIGHT_API_KEY"
)

HINDSIGHT_BASE_URL = (
    "https://api.hindsight.vectorize.io"
)

BANK_ID = "meeting-prep"


if not HINDSIGHT_API_KEY:

    raise ValueError(
        "HINDSIGHT_API_KEY is missing. "
        "Please add it to your .env file."
    )


# ============================================================
# CREATE HINDSIGHT CLIENT
# ============================================================

def get_hindsight_client():

    return Hindsight(

        base_url=HINDSIGHT_BASE_URL,

        api_key=HINDSIGHT_API_KEY
    )


# ============================================================
# CREATE MEMORY BANK
# ============================================================

def setup_memory_bank():

    client = get_hindsight_client()

    try:

        bank = client.create_bank(

            bank_id=BANK_ID,

            name="Meeting Prep Agent",

            background=(
                "This memory bank stores information "
                "about meetings, people, concerns, "
                "preferences, commitments, outcomes, "
                "and lessons learned for an AI "
                "Meeting Prep Agent."
            )
        )

        print(
            f"Memory bank created: "
            f"{bank.bank_id}"
        )

        return bank

    except Exception as e:

        print(
            f"Memory bank setup message: {e}"
        )

    finally:

        client.close()


# ============================================================
# STORE MEETING
# ============================================================

def retain_meeting(

    meeting_id,
    user_email,
    meeting_date,
    person_name,
    company,
    role,
    purpose,
    concerns="",
    preferences="",
    commitments="",
    outcome=""

):
    meeting_content = f"""
    User Email:
    {user_email}

    Meeting Date:
    {meeting_date}

    Person:
    {person_name}

    Company:
    {company}

    Role:
    {role}

    Meeting Purpose:
    {purpose}

    Concerns:
    {concerns}

    Preferences:
    {preferences}

    Commitments:
    {commitments}

    Outcome:
    {outcome}
    """

    client = get_hindsight_client()

    try:

        result = client.retain(

            bank_id=BANK_ID,

            content=meeting_content,

            context=f"Meeting history for user {user_email}",
            document_id=meeting_id

        )

        print(
            "Meeting stored in Hindsight: "
            f"{meeting_id}"
        )

        return result

    finally:

        client.close()


# ============================================================
# RECALL PERSON
# ============================================================

def recall_person(user_email, person_name):

    query = f"""
Find previous meeting information for this user.

User Email:
{user_email}

Person:
{person_name}

Only return information belonging to this exact user.

Find relevant information about:

- their role and company
- their concerns
- their preferences
- previous discussions
- previous problems
- commitments we made
- commitments they made
- previous meeting outcomes
- important new information
- lessons learned

Do not return information belonging to another user.
"""

    client = get_hindsight_client()

    try:

        result = client.recall(
            bank_id=BANK_ID,
            query=query
        )

        memories = []

        for memory in result.results:

            memories.append({
                "type": memory.type,
                "text": memory.text
            })

        return memories

    finally:

        client.close()
# ============================================================
# PREPARE MEETING USING HINDSIGHT
# ============================================================

def prepare_meeting(

    person_name,

    meeting_goal

):

    query = f"""

Prepare me for my upcoming meeting
with {person_name}.

Meeting goal:

{meeting_goal}

Based on everything you know from
previous meetings:

1. Summarize the relationship/history.
2. Identify their important concerns.
3. Identify their preferences.
4. Identify unresolved commitments.
5. Identify previous problems.
6. Identify previous outcomes.
7. Identify lessons learned.
8. Suggest useful talking points.
9. Suggest questions I should ask.
10. Give me warnings about things
    I should avoid.
11. Tell me what I should follow up on.

Only use information supported by
the stored memories.

"""


    client = get_hindsight_client()

    try:

        response = client.reflect(

            bank_id=BANK_ID,

            query=query,

            budget="mid"

        )

        return response.text

    finally:

        client.close()


# ============================================================
# STORE MEETING OUTCOME
# ============================================================

def retain_outcome(

    meeting_id,

    person_name,

    outcome,

    reason="",

    new_information="",

    commitment=""

):

    outcome_content = f"""

Meeting Outcome

Person:
{person_name}

Outcome:
{outcome}

Reason:
{reason}

New Information:
{new_information}

New Commitment:
{commitment}

"""


    client = get_hindsight_client()

    try:

        result = client.retain(

            bank_id=BANK_ID,

            content=outcome_content,

            context=(
                "Post-meeting outcome "
                "and learning"
            ),

            document_id=
                f"{meeting_id}-outcome"

        )

        print(
            "Meeting outcome stored for "
            f"{person_name}"
        )

        return result

    finally:

        client.close()
