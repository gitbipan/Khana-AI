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
DEFAULT_API_KEY = "AQ.Ab8RN6Laec08QMu_AaWoT94NiTfAEPX8rVzzzO4W-Yq0pmFrSQ"
GEMMA_API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GEMMA_API_KEY", DEFAULT_API_KEY)).strip()

# Gemma Model Hierarchy - Prioritizes Gemma 4 31B
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemma-4-31b-it")
VISION_MODEL = os.getenv("VISION_MODEL", "gemma-4-31b-it")
FALLBACK_MODELS = ["gemma-4-31b-it", "gemma-4-26b-a4b-it", "gemini-3.8-flash", "gemini-3.5-flash-lite"]

# Centralized Hosted Database Configuration (MySQL / SQLite)
DB_TYPE = os.getenv("DB_TYPE", "mysql" if (os.getenv("MYSQL_HOST") or os.getenv("DATABASE_URL")) else "sqlite").lower()
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "khana_ai")
DATABASE_URL = os.getenv("DATABASE_URL", "")

