from backend.agents.unified_memory_agent import (
    answer_memory_question
)


answer = answer_memory_question(
    "What was I studying yesterday?"
)

print(
    "Unified Memory Answer:"
)

print(
    answer
)
