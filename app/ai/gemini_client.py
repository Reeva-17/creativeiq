
import os
from google import genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.client = None

    def _get_client(self):
        """Create the provider client only for an actual Gemini request.

        Importing a route or test must not fail solely because a local developer
        has not configured optional external credentials yet.
        """
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY missing in .env")
        if self.client is None:
            self.client = genai.Client(
                api_key=self.api_key,
                http_options={"timeout": 60000},
            )
        return self.client

    def generate(self, prompt: str) -> str:
        print(f"\n[Gemini] Sending request to {self.model}...", flush=True)

        try:
            response = self._get_client().models.generate_content(
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
