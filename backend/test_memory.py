from hindsight_memory import (
    setup_memory_bank,
    retain_meeting,
    recall_person,
    prepare_meeting,
    retain_outcome,
)


print("======================================")
print("MEETING PREP AGENT - MEMORY TEST")
print("======================================")

# 1. Make sure the memory bank exists
print("\n1. Setting up memory bank...")
setup_memory_bank()


# 2. Store the first meeting
print("\n2. Storing Meeting 1...")

retain_meeting(
    meeting_id="rahul-meeting-001",
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

print("Meeting 1 stored successfully.")


# 3. Recall Rahul's information
print("\n3. Recalling Rahul's memories...")

memories = recall_person("Rahul Kumar")

print("\nMEMORIES FOUND:")

for memory in memories:
    print("--------------------------------------")
    print(memory["text"])


# 4. Prepare for next meeting
print("\n4. Preparing for Meeting 2...")

brief = prepare_meeting(
    person_name="Rahul Kumar",
    meeting_goal="Discuss the revised deployment architecture."
)

print("\nMEETING PREPARATION:")
print("--------------------------------------")
print(brief)


# 5. Store what happened after Meeting 2
print("\n5. Storing Meeting 2 outcome...")

retain_outcome(
    meeting_id="rahul-meeting-002",
    person_name="Rahul Kumar",
    outcome="Rahul agreed to continue if deployment cost is reduced.",
    reason="The previous deployment proposal was too expensive.",
    new_information="Rahul needs deployment completed within four weeks.",
    commitment="We will provide a lower-cost architecture proposal."
)

print("Meeting 2 outcome stored.")


# 6. Prepare again
print("\n6. Preparing for the next meeting...")

improved_brief = prepare_meeting(
    person_name="Rahul Kumar",
    meeting_goal="Finalize the lower-cost deployment architecture."
)

print("\nIMPROVED MEETING PREPARATION:")
print("--------------------------------------")
print(improved_brief)


print("\n======================================")
print("MEMORY TEST COMPLETE")
print("======================================")
