from backend.ai.query_engine import (
    answer_question
)

questions = [
    "What was I coding?",
    "What websites did I visit?",
    "What was I doing?"
]

for q in questions:

    print("=" * 60)
    print(q)
    print("=" * 60)

    response = answer_question(
        q
    )

    print(response)
    print()