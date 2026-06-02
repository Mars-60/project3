from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv(
    "GEMINI_API_KEY"
)

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )

client = genai.Client(
    api_key=api_key
)


def ask_gemini(prompt):

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        print(
            "\nDEBUG RESPONSE:"
        )

        print(response)

        if hasattr(
            response,
            "text"
        ):
            return response.text

        return str(response)

    except Exception as e:

        print(
            "GEMINI ERROR:",
            e
        )

        return None