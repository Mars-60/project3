from backend.agents.smart_memory_agent import (
    ask_memory
)

result = ask_memory(
    "What did I do yesterday?"
)

print("TYPE:")
print(type(result))

print("\nRESULT:")
print(repr(result))