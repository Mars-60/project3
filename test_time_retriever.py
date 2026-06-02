from backend.retrieval.time_retriever import (
    retrieve_by_time
)

activities = retrieve_by_time(
    "What did I do yesterday?"
)

print(
    "TOTAL:",
    len(activities)
)

for activity in activities[:10]:
    print(activity)