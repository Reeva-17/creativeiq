import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ai.gemini_client import gemini_client

from app.ai.gemini_client import gemini_client


def test_gemini_connection():
    print("Testing Gemini API connection...")

    response = gemini_client.generate(
        "Reply with exactly: "
        "CREATIVEIQ GEMINI CONNECTION SUCCESSFUL"
    )

    print("\nGemini Response:")
    print(response)

    assert response, "Gemini returned an empty response."

    print("\nConnection test passed!")


if __name__ == "__main__":
    test_gemini_connection()
