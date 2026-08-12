import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL"
)


if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. Please add it to the .env file."
    )

if not GEMINI_MODEL:
    raise ValueError(
        "GEMINI_MODEL is missing. Please add it to the .env file."
    )