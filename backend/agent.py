from groq import Groq

from config import GROQ_API_KEY
from hindsight_memory import recall_person


# ============================================================
# CREATE GROQ CLIENT
# ============================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# ============================================================
# GENERATE MEETING BRIEF
# ============================================================

def generate_meeting_brief(
    user_email,
    person_name,
    company="",
    role="",
    meeting_goal="",
    meeting_date="",
    meeting_time=""
):
    """
    Generate a personalized meeting brief using
    Hindsight memories and Groq.
    """

    # ========================================================
    # GET PREVIOUS MEMORIES FROM HINDSIGHT
    # ========================================================

    memories = recall_person(
        user_email,
        person_name
    )


    # ========================================================
    # CONVERT MEMORIES INTO READABLE TEXT
    # ========================================================

    memory_text = ""


    if memories:

        for memory in memories:

            memory_text += (

                f"\n[{memory['type']}]\n"

                f"{memory['text']}\n"

            )

    else:

        memory_text = (
            "No previous memories found."
        )


    # ========================================================
    # CREATE PROMPT FOR GROQ
    # ========================================================

    prompt = f"""
You are an AI Meeting Preparation Agent.

Prepare me for an upcoming meeting.

Person:
{person_name}

Company:
{company}

Role:
{role}

Meeting Date:
{meeting_date}

Meeting Time:
{meeting_time}

Meeting Goal:
{meeting_goal}


Previous information from Hindsight:

{memory_text}


Using the information above, create a useful meeting preparation brief.

Include:

1. Relationship/history
2. Important concerns
3. Preferences
4. Previous discussions
5. Previous problems
6. Previous commitments
7. Previous outcomes
8. Useful talking points
9. Questions I should ask
10. Things I should avoid
11. Follow-up items

Only use information supported by the memories.

If there is no previous information, clearly say that there are no previous memories available.
"""


    # ========================================================
    # ASK GROQ TO GENERATE THE BRIEF
    # ========================================================

    response = client.chat.completions.create(

        model="openai/gpt-oss-120b",

        messages=[

            {
                "role": "system",

                "content":
                    "You are a helpful AI meeting preparation assistant."
            },

            {
                "role": "user",

                "content":
                    prompt
            }

        ],

        temperature=0.2
    )


    # ========================================================
    # GET GENERATED BRIEF
    # ========================================================

    brief = response.choices[0].message.content


    # ========================================================
    # RETURN EVERYTHING TO app.py
    #
    # IMPORTANT:
    # "memories" contains the actual Hindsight memories.
    # app.py can send these to brief.html.
    # ========================================================

    return {

        "success":
            True,

        "person_name":
            person_name,

        "memory_count":
            len(memories),

        "memories":
            memories,

        "brief":
            brief

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    result = generate_meeting_brief(
        user_email="test@gmail.com",
        person_name="Rahul Kumar",

        company="ABC Technologies",

        role="Product Manager",

        meeting_goal=
            "Discuss the revised deployment architecture."

    )


    print(
        "\n======================================"
    )

    print(
        "MEETING PREP BRIEF"
    )

    print(
        "======================================"
    )

    print(
        result
    )
