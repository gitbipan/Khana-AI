"""
PoshanAI Configuration & Environment Settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

# Server host & port
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Default Google GenAI / Gemma API Key provided by user
DEFAULT_API_KEY = "AQ.Ab8RN6LpTEAa92_XrPft5-AjRjDfpEz8mJEElGjRv2pQNyDaCA"
GEMMA_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GEMMA_API_KEY", DEFAULT_API_KEY)).strip()

# Gemini / Gemma Model Fallback Hierarchy
# Primary model tested for stability, followed by flash-lite and flash-3.8
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-3.5-flash")
VISION_MODEL = os.getenv("VISION_MODEL", "gemini-3.5-flash")
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
