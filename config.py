"""
Central configuration for LegalEase.
Loads environment variables from .env and exposes them as constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Paths used by the frontend for branding
WEB_LOGO_PATH = os.path.join("Image", "Logo.png")
INVERSE_LOGO_PATH = os.path.join("Image", "inverseLogo.png")

if not GEMINI_API_KEY:
    print("[WARNING] GEMINI_API_KEY is not set. Add it to your .env file.")
