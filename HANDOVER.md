# 🤝 PoshanAI Team Handover Guide
### For Baibhav, Biraj & Bipan (Hacktoberfest Hackathon Team)

> [!IMPORTANT]
> **To Biraj and Bipan**:
> Welcome! Baibhav has initiated the project and **all 5 foundational modules are 100% complete, fully tested, and committed to git**. You can resume work or launch the project immediately without starting from scratch.

---

## 📍 Project Location & Environment

- **Root Directory**: `C:\Users\baibh\.gemini\antigravity\scratch\poshan-ai`
- **Package Manager**: `uv` (Located at `C:\Users\baibh\.local\bin\uv.exe`)
- **Python Version**: Python 3.11 (`.python-version` configured)
- **Git Status**: Clean git history on branch `master` with modular commits.

---

## ⚡ Instant Commands

Open PowerShell in `C:\Users\baibh\.gemini\antigravity\scratch\poshan-ai`:

### 1. Launch the Live Web App
```powershell
& "C:\Users\baibh\.local\bin\uv.exe" run python server.py
```
App will open automatically at: **`http://localhost:8000`**

### 2. Run the Full Test Suite
```powershell
& "C:\Users\baibh\.local\bin\uv.exe" run pytest
```
*(All 19/19 tests currently pass: BMR, BMI, Nutrition DB, Vision Fallback, Advisor Heuristics, and FastAPI REST endpoints)*

---

## 📦 What Has Been Built (Completed Modules Checklist)

- [x] **Module 1: Foundation & Nepali Nutritional Knowledge Engine**
  - `data/nepali_foods.json`: 40+ authentic Nepali foods (Dal Bhat, Dhindo, Kwati, Gundruk, Momo, Sel Roti, Yomari, Lito, Jaulo, Sattu, etc.) with verified DFTQC nutritional metrics.
  - `core/nutrition_db.py`: Fast Pydantic querying, fuzzy search in English/Nepali, and meal calorie/macro aggregator.
  - `core/bmr_calculator.py`: Clinical Mifflin-St Jeor formula, TDEE, WHO South Asian adjusted BMI cutoffs, and daily macro/micronutrient RDA.
  - `tests/test_bmr.py` & `tests/test_nutrition_db.py`: Passing unit tests.

- [x] **Module 2: Multimodal Food Vision Engine (Gemma / Gemini)**
  - `core/vision_engine.py`: Multi-provider multimodal food analyzer.
  - Connects to Google GenAI / Gemma API for live recognition.
  - **Zero-Cost Offline Fallback**: Works seamlessly without any API key using pattern-matched Nepali meal presets and sample image libraries so judging never fails!
  - `core/generate_samples.py`: Pre-rendered high-res test plates (`static/sample_images/`).
  - `tests/test_vision_engine.py`: Passing unit tests.

- [x] **Module 3: AI Nutrition & Malnutrition Advisory Chatbot**
  - `core/advisor_engine.py`: Evaluates meal composition against BMR/TDEE targets.
  - Screens for malnutrition: High-carb ratio (excessive white rice), protein deficiency, and iron/anemia risks.
  - Generates culturally actionable low-cost suggestions (Boiled eggs, roasted Bhatmas, Kwati soup, Rayo Saag).
  - `PoshanChatbot`: Bilingual conversational AI in native Nepali (नेपाली भाषा) and English.
  - `tests/test_advisor.py`: Passing unit tests.

- [x] **Module 4: Bilingual Interactive Web Dashboard**
  - `app.py`: Full modern Streamlit web application.
  - 🇳🇵 Nepali / 🇬🇧 English language toggle.
  - Tab 1: Health Profile & BMR/TDEE Calculator with gauge metrics.
  - Tab 2: Food Scanner & Meal Analyzer (Camera snapshot, custom file upload, or quick 1-click sample gallery).
  - Tab 3: Poshan Saathi (पोषण साथी) Interactive Chat with quick question shortcuts.
  - Tab 4: Nepali Foods Nutrition Encyclopaedia.

- [x] **Module 5: Hacktoberfest Open-Source Assets & Handover Docs**
  - `README.md`: High-impact GitHub repository presentation with architecture diagrams and badges.
  - `CONTRIBUTING.md`: Beginner-friendly guidelines for open-source contributors.
  - `LICENSE`: MIT License.
  - `HANDOVER.md`: This document.

---

## 🔮 Suggested Next Features (For Extra Hackathon Winning Points!)

If Biraj or Bipan have remaining tokens and want to add bonus features:

1. **PDF Nutrition Export**:
   - Add a "Download My Daily Nutrition Report (PDF)" button using `reportlab` or `fpdf2`.
2. **Nepali Voice Input (Speech-to-Text)**:
   - Allow users to speak their meal or ask questions using speech recognition for illiterate or rural users.
3. **Local SQLite Meal History Tracker**:
   - Store scanned meals per day to display a 7-day calorie and protein intake chart.

---

## 💬 Prompt Template to Resume Work (Copy & Paste this!)

When Biraj or Bipan start a new session from their Gmail account, simply paste this prompt:

> *"Hi! I am Biraj/Bipan continuing our Hacktoberfest project **PoshanAI** from Baibhav's session. The workspace is located at `C:\Users\baibh\.gemini\antigravity\scratch\poshan-ai`. All 5 foundation modules are complete and tested. Please inspect `HANDOVER.md` and help me [run the app / test / add feature X]."*
