from backend.ai.query_engine import (
    answer_question
)

response = answer_question(
    "What was I doing recently?"
)

print(response)