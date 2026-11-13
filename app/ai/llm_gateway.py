import json
import os
import re
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()


def clean_json_string(text: str) -> str:
    """Strip markdown fences, leading/trailing notes, and locate JSON block."""
    if not text or not text.strip():
        raise ValueError("Model returned an empty response.")

    cleaned = text.strip()
    # Strip markdown code blocks
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"\s*```$", "", cleaned, flags=re.MULTILINE)

    # First attempt: parse directly
    try:
        json.loads(cleaned)
        return cleaned
    except json.JSONDecodeError:
        pass

    # Second attempt: locate outer JSON object '{ ... }' or array '[ ... ]'
    start_bracket = -1
    for i, ch in enumerate(cleaned):
        if ch in "{[":
            start_bracket = i
            break

    if start_bracket != -1:
        decoder = json.JSONDecoder()
        try:
            obj, _ = decoder.raw_decode(cleaned[start_bracket:])
            return json.dumps(obj)
        except json.JSONDecodeError:
            pass

    # Fallback regex search
    match = re.search(r"(\{.*\}|\[.*\])", cleaned, re.DOTALL)
    if match:
        return match.group(0)

    return cleaned


class LLMGateway:
    """
    Unified LLM Gateway for Person 2 (Creative Director).
    Supports Groq (Llama / OSS models) with automatic Gemini fallback,
    ensuring continuous availability and adherence to project requirements.
    """

    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        groq_model: Optional[str] = None,
        gemini_api_key: Optional[str] = None,
        gemini_model: Optional[str] = None,
        preferred_provider: str = "groq"
    ):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.groq_model = groq_model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.gemini_api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_model = gemini_model or os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
        self.preferred_provider = preferred_provider

        # Initialize Groq Client if key exists
        self.groq_client = None
        if self.groq_api_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_api_key.strip())
            except Exception as e:
                print(f"[LLMGateway] Groq init notice: {e}")

        # Initialize Gemini Client if key exists
        self.gemini_client = None
        if self.gemini_api_key:
            try:
                from google import genai
                self.gemini_client = genai.Client(
                    api_key=self.gemini_api_key.strip(),
                    http_options={"timeout": 60000}
                )
            except Exception as e:
                print(f"[LLMGateway] Gemini init notice: {e}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> str:
        """Generate response with provider fallback."""
        if not 1 <= max_tokens <= 8192:
            raise ValueError("max_tokens must be between 1 and 8192.")
        providers = ["groq", "gemini"] if self.preferred_provider == "groq" else ["gemini", "groq"]
        last_exception = None

        for provider in providers:
            if provider == "groq" and self.groq_client:
                try:
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})

                    completion = self.groq_client.chat.completions.create(
                        model=self.groq_model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=max_tokens,
                    )
                    content = completion.choices[0].message.content
                    if content and content.strip():
                        return content
                except Exception as exc:
                    print(f"[LLMGateway] Groq ({self.groq_model}) encountered: {exc}. Trying fallback...")
                    last_exception = exc

            elif provider == "gemini" and self.gemini_client:
                try:
                    full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
                    from google.genai import types

                    response = self.gemini_client.models.generate_content(
                        model=self.gemini_model,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            max_output_tokens=max_tokens
                        ),
                    )
                    if response.text and response.text.strip():
                        return response.text
                except Exception as exc:
                    print(f"[LLMGateway] Gemini ({self.gemini_model}) encountered: {exc}.")
                    last_exception = exc

        raise RuntimeError(f"All LLM providers failed. Last error: {last_exception}")

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> dict[str, Any]:
        """Generate and parse structured JSON with repair logic."""
        json_sys_prompt = (
            "You are an expert AI Creative Director. "
            "You must return ONLY valid, well-formed JSON matching the specified schema. "
            "Do NOT wrap in markdown formatting, backticks, or write conversational introductory text."
        )
        if system_prompt:
            json_sys_prompt = f"{system_prompt}\n\n{json_sys_prompt}"

        raw_output = self.generate(prompt, system_prompt=json_sys_prompt)
        cleaned = clean_json_string(raw_output)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            # Attempt one repair pass
            print(f"[LLMGateway] JSON decode error: {exc}. Attempting repair pass...")
            repair_prompt = f"The following string is supposed to be valid JSON, but has a syntax error:\n{cleaned}\n\nFix the syntax and return ONLY valid JSON:"
            repaired = self.generate(repair_prompt, system_prompt="You are a JSON syntax repair specialist. Return ONLY valid raw JSON.")
            repaired_clean = clean_json_string(repaired)
            return json.loads(repaired_clean)


# Default singleton instance
llm_gateway = LLMGateway()
