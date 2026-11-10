
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        if not api_key:
            raise ValueError("GEMINI_API_KEY missing in .env")

        self.client = genai.Client(
            api_key=api_key,
            http_options={
                "timeout": 60000
            }
        )

    def generate(self, prompt: str) -> str:
        print(f"\n[Gemini] Sending request to {self.model}...", flush=True)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if not response.text:
                raise RuntimeError("Gemini returned an empty response.")

            print("[Gemini] Response received.", flush=True)
            return response.text

        except Exception as exc:
            print(f"[Gemini ERROR] {exc}", flush=True)
            raise


gemini_client = GeminiClient()
