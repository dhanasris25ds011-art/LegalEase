"""
ai_core/gemini_generator.py

Wraps the Google Gemini SDK to turn structured user input
(document_type, parties, terms, dates) into a full legal document draft.
"""
import time

from google import genai
from google.genai import errors

from config import GEMINI_API_KEY, GEMINI_MODEL

FALLBACK_MODELS = ["gemini-3.5-flash-lite", "gemini-3.5-flash"]
RETRY_CODES = {429, 500, 503, 504}
MAX_RETRIES = 3


class GeminiDocumentGenerator:
    def __init__(self, model_name: str = GEMINI_MODEL):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = model_name

    def _build_prompt(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        return (
            f"Generate a comprehensive legal document titled '{document_type}'.\n"
            f"Involved parties: {parties}\n"
            f"Effective Date: {dates}\n"
            f"Terms and conditions: {terms}\n"
            "Ensure a formal legal structure with multiple numbered sections and clauses "
            "(e.g. Services, Term and Termination, Payment, Intellectual Property Rights, "
            "Confidentiality, Governing Law, Entire Agreement, Severability, Signatures). "
            "Use plain, professional legal English. Do not include any explanation outside "
            "of the document itself."
        )

    def generate_document(self, document_type: str, parties: str, terms: str, dates: str) -> str:
        prompt = self._build_prompt(document_type, parties, terms, dates)

        models = [self.model_name] + [m for m in FALLBACK_MODELS if m != self.model_name]
        last_error = None

        for model in models:
            for attempt in range(MAX_RETRIES):
                try:
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                    return response.text
                except errors.APIError as exc:
                    last_error = exc
                    if exc.code in RETRY_CODES:
                        time.sleep(2 ** attempt)
                        continue
                    break
                except Exception as exc:  # noqa: BLE001
                    raise RuntimeError(f"Gemini generation failed: {exc}") from exc

        raise RuntimeError(f"Gemini generation failed: {last_error}") from last_error