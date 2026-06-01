from backend.ai.query_engine import (
    answer_question
)

print("PersonalOS AI")
print("Type 'exit' to quit.\n")

while True:

    question = input("You: ")

    if question.lower() == "exit":
        break

    answer = answer_question(
        question
    )

    print("\nAI:")
    print(answer)
    print()