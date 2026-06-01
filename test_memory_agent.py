from backend.agents.memory_agent import (
    ask_memory
)

response = ask_memory(
    "What websites did I visit recently?"
)

print(response)