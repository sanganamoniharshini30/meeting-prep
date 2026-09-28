from groq import Groq

from config import GROQ_API_KEY
from hindsight_memory import recall_person


client = Groq(api_key=GROQ_API_KEY)


# ==================================================
# GENERATE MEETING BRIEF
# ==================================================

def generate_meeting_brief(
    person_name,
    company="",
    role="",
    meeting_goal=""
):

    # ----------------------------------------------
    # 1. Recall previous memories from Hindsight
    # ----------------------------------------------

    memories = recall_person(person_name)

    memory_text = "\n".join(
        f"- {memory['text']}"
        for memory in memories
    )

    # ----------------------------------------------
    # 2. Build meeting details
    # ----------------------------------------------

    meeting_details = f"""
Person: {person_name}

Company: {company}

Role: {role}

Meeting Goal:
{meeting_goal}
"""

    # ----------------------------------------------
    # 3. Ask Groq to prepare the meeting
    # ----------------------------------------------

    prompt = f"""
You are an AI Meeting Preparation Agent.

Prepare the user for an upcoming meeting using:

1. Current meeting details
2. Memories retrieved from Hindsight

CURRENT MEETING:

{meeting_details}

HINDSIGHT MEMORIES:

{memory_text}


Create a concise and practical meeting preparation brief.

Use these sections:

1. FACTS FROM MEMORY
- Only state facts explicitly supported by memory.

2. LEARNED PREFERENCES
- List preferences explicitly supported by memory.

3. PENDING COMMITMENTS
- List commitments found in memory.
- Identify who made the commitment when known.

4. PREVIOUS LESSONS
- Explain what previous meeting outcomes teach us.

5. TALKING POINTS
- Suggest practical points for the upcoming meeting.
- Clearly treat these as AI suggestions.

6. QUESTIONS TO ASK
- Suggest useful questions based on the meeting goal
  and known concerns.

7. WARNINGS
- Give warnings only when supported by previous meetings
  or known information.


IMPORTANT RULES:

- Never invent facts.
- Never invent dates, budgets, numbers, roles or commitments.
- If information is unavailable, say:
  "Not available in memory."
- Clearly distinguish stored facts from AI suggestions.
- Keep the response concise and practical.
"""

    # ----------------------------------------------
    # 4. Call Groq
    # ----------------------------------------------

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    brief = response.choices[0].message.content

    # ----------------------------------------------
    # 5. Return JSON-friendly result
    # ----------------------------------------------

    return {
        "success": True,
        "person_name": person_name,
        "memory_count": len(memories),
        "brief": brief
    }


# ==================================================
# TEST
# ==================================================

if __name__ == "__main__":

    print("\n======================================")
    print("MEETING PREP AGENT")
    print("======================================")

    result = generate_meeting_brief(
        person_name="Rahul Kumar",
        company="ABC Technologies",
        role="Product Manager",
        meeting_goal="Discuss a lower-cost deployment option."
    )

    print("\n======================================")
    print("MEETING PREPARATION BRIEF")
    print("======================================\n")

    print(result["brief"])

    print("\n======================================")
    print("DONE")
    print("======================================")
