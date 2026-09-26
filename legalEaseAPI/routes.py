"""
legalEaseAPI/routes.py

Defines the DocumentRequest schema and the /generate endpoint that
bridges the frontend to the Gemini-powered document generator.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ai_core.gemini_generator import GeminiDocumentGenerator

router = APIRouter()
gemini_generator = GeminiDocumentGenerator()


class DocumentRequest(BaseModel):
    document_type: str = Field(..., min_length=1, example="Freelance Work Contract")
    parties: str = Field(..., min_length=1, example="Jane Doe (Service Provider), TechNova Inc. (Client)")
    terms: str = Field(..., min_length=1, example="Payment due within 30 days; Confidentiality required")
    dates: str = Field(..., min_length=1, example="April 15, 2025")


@router.post("/generate")
def generate_legal_document(request: DocumentRequest):
    try:
        response = gemini_generator.generate_document(
            request.document_type,
            request.parties,
            request.terms,
            request.dates,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"document": response}
