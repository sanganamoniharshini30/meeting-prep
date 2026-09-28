import os
from dotenv import load_dotenv
from hindsight_client import Hindsight

# Load variables from .env
load_dotenv()

# --------------------------------------------------
# HINDSIGHT CONFIGURATION
# --------------------------------------------------

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = "https://api.hindsight.vectorize.io"

# Our application's memory bank
BANK_ID = "meeting-prep"

if not HINDSIGHT_API_KEY:
    raise ValueError(
        "HINDSIGHT_API_KEY is missing. "
        "Please add it to your .env file."
    )

# Create Hindsight client
client = Hindsight(
    base_url=HINDSIGHT_BASE_URL,
    api_key=HINDSIGHT_API_KEY
)


# --------------------------------------------------
# 1. CREATE MEMORY BANK
# --------------------------------------------------

def setup_memory_bank():
    """
    Creates the Hindsight memory bank for our application.
    """

    try:
        bank = client.create_bank(
            bank_id=BANK_ID,
            name="Meeting Prep Agent",
            background=(
                "This memory bank stores information about meetings, "
                "people, concerns, preferences, commitments, outcomes, "
                "and lessons learned for an AI Meeting Prep Agent."
            )
        )

        print(f"Memory bank created: {bank.bank_id}")
        return bank

    except Exception as e:
        # The bank may already exist.
        print(f"Memory bank setup message: {e}")


# --------------------------------------------------
# 2. RETAIN A MEETING
# --------------------------------------------------

def retain_meeting(
    meeting_id,
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
    """
    Store information from a meeting in Hindsight.
    """

    meeting_content = f"""
Meeting Date: {meeting_date}

Person: {person_name}

Company: {company}

Role: {role}

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

    result = client.retain(
        bank_id=BANK_ID,
        content=meeting_content,
        context="Meeting history for the Meeting Prep Agent",
        document_id=meeting_id
    )

    print(f"Meeting stored in Hindsight: {meeting_id}")

    return result


# --------------------------------------------------
# 3. RECALL INFORMATION ABOUT A PERSON
# --------------------------------------------------

def recall_person(person_name):
    """
    Search Hindsight for everything relevant about a person.
    """

    query = f"""
What do we know about {person_name} from previous meetings?

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
"""

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


# --------------------------------------------------
# 4. REFLECT AND PREPARE FOR THE NEXT MEETING
# --------------------------------------------------

def prepare_meeting(person_name, meeting_goal):
    """
    Ask Hindsight to reason over previous memories
    and prepare a personalized meeting brief.
    """

    query = f"""
Prepare me for my upcoming meeting with {person_name}.

Meeting goal:
{meeting_goal}

Based on everything you know from previous meetings:

1. Summarize the relationship/history.
2. Identify their important concerns.
3. Identify their preferences.
4. Identify unresolved commitments.
5. Identify previous problems.
6. Identify previous outcomes.
7. Identify lessons learned.
8. Suggest useful talking points.
9. Suggest questions I should ask.
10. Give me warnings about things I should avoid.
11. Tell me what I should follow up on.

Only use information supported by the stored memories.
"""

    response = client.reflect(
        bank_id=BANK_ID,
        query=query,
        budget="mid"
    )

    return response.text


# --------------------------------------------------
# 5. STORE A MEETING OUTCOME
# --------------------------------------------------

def retain_outcome(
    meeting_id,
    person_name,
    outcome,
    reason="",
    new_information="",
    commitment=""
):
    """
    Store what happened after a meeting.
    """

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

    result = client.retain(
        bank_id=BANK_ID,
        content=outcome_content,
        context="Post-meeting outcome and learning",
        document_id=f"{meeting_id}-outcome"
    )

    print(f"Meeting outcome stored for {person_name}")

    return result


# --------------------------------------------------
# 6. TEST EVERYTHING
# --------------------------------------------------

if __name__ == "__main__":

    print("\n======================================")
    print("MEETING PREP AGENT - HINDSIGHT TEST")
    print("======================================\n")

    # Step 1: Create memory bank
    print("1. Setting up memory bank...")
    setup_memory_bank()

    # Step 2: Store first meeting
    print("\n2. Storing first meeting...")

    retain_meeting(
        meeting_id="meeting-001-rahul",
        meeting_date="2026-09-25",
        person_name="Rahul Kumar",
        company="ABC Technologies",
        role="Product Manager",
        purpose="Discuss deployment architecture",
        concerns="Rahul is concerned about deployment cost.",
        preferences="Rahul prefers short and practical technical explanations.",
        commitments="We promised to send the deployment architecture.",
        outcome="Rahul requested a lower-cost deployment option."
    )

    print("First meeting stored.")

    # Step 3: Recall Rahul
    print("\n3. Recalling Rahul's information...")

    memories = recall_person("Rahul Kumar")

    print("\nRelevant memories:")

    for memory in memories:
        print(f"\n[{memory['type']}]")
        print(memory["text"])

    # Step 4: Ask Hindsight to prepare us
    print("\n4. Preparing for next meeting...")

    brief = prepare_meeting(
        person_name="Rahul Kumar",
        meeting_goal="Discuss the revised deployment architecture."
    )

    print("\n======================================")
    print("MEETING PREP BRIEF")
    print("======================================")
    print(brief)

    # Step 5: Store outcome from second interaction
    print("\n5. Storing new outcome...")

    retain_outcome(
        meeting_id="meeting-002-rahul",
        person_name="Rahul Kumar",
        outcome="Rahul agreed to continue if deployment cost is reduced.",
        reason="The previous deployment proposal was too expensive.",
        new_information="Rahul needs deployment completed within four weeks.",
        commitment="We will provide a lower-cost architecture proposal."
    )

    print("\nNew information successfully stored.")

    # Step 6: Prepare again
    print("\n6. Preparing for the next meeting again...")

    improved_brief = prepare_meeting(
        person_name="Rahul Kumar",
        meeting_goal="Finalize the lower-cost deployment architecture."
    )

    print("\n======================================")
    print("IMPROVED MEETING PREP")
    print("======================================")
    print(improved_brief)

    print("\n======================================")
    print("HINDSIGHT TEST COMPLETE")
    print("======================================")
