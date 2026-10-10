"""
PoshanAI FastAPI Backend Server
Serves the modern Single-Page Application (SPA) and provides high-performance REST APIs.
"""

from __future__ import annotations
import io
import json
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from PIL import Image

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from core.config import HOST, PORT, GEMMA_API_KEY
from core.bmr_calculator import (
    UserProfile,
    BiologicalSex,
    ActivityLevel,
    HealthGoal,
    NutritionalAssessment,
    assess_nutrition,
)
from core.nutrition_db import (
    get_nutrition_db,
    MealItemPortion,
    MealSummary,
    FoodItem,
    estimate_food_nutrition,
)
from core.vision_engine import analyze_food_image, VisionRecognitionResult
from core.advisor_engine import (
    evaluate_meal_against_bmr,
    PoshanChatbot,
    MealEvaluationVerdict,
    generate_nepali_diet_plan,
    DailyDietPlan,
)
from core.diet_history import (
    log_meal,
    get_history,
    delete_log,
    get_weekly_calorie_tracker,
    seed_demo_history_if_empty,
    add_planner_item,
    get_planner_items,
    set_planner_item_completion,
    delete_planner_item,
    save_or_update_user,
    get_user_by_username,
    list_all_users,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
SAMPLES_DIR = STATIC_DIR / "sample_images"

app = FastAPI(
    title="PoshanAI API",
    description="Open-Source Nepali Nutrition & Malnutrition Prevention Platform",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize database & chatbot
db = get_nutrition_db()
chatbot = PoshanChatbot()


# Pydantic Request Models
class LoginRequest(BaseModel):
    name: str = "अतिथि प्रयोगकर्ता (Guest)"
    age_years: int = 24
    sex: BiologicalSex = BiologicalSex.MALE
    height_cm: float = 170.0
    weight_kg: float = 62.0
    activity_level: ActivityLevel = ActivityLevel.MODERATE
    goal: HealthGoal = HealthGoal.MAINTAIN


class ChatRequest(BaseModel):
    message: str
    language: str = "ne"
    profile: Optional[UserProfile] = None
    meal_context: Optional[dict] = None


class SampleAnalyzeRequest(BaseModel):
    sample_filename: str
    custom_profile: Optional[UserProfile] = None


class CustomMealCalculateRequest(BaseModel):
    portions: List[MealItemPortion]
    custom_profile: Optional[UserProfile] = None


class PlanGenerateRequest(BaseModel):
    profile: Optional[UserProfile] = None
    preference: str = "all"  # "all", "veg", "budget"


class CustomPlannerEntryRequest(BaseModel):
    user_id: str = "default"
    meal_type: str = "lunch"
    food_name: str
    portion_desc: str = "१ भाग"
    weight_g: float = 100.0
    calories: Optional[float] = None
    protein_g: Optional[float] = None
    carbs_g: Optional[float] = None
    fat_g: Optional[float] = None
    notes: str = ""
    date: Optional[str] = None


class TogglePlannerItemRequest(BaseModel):
    item_id: int
    is_completed: bool
    user_id: str = "default"
    food_name: str = ""
    meal_type: str = "lunch"
    portion_desc: str = ""
    calories: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0


class FoodEstimateRequest(BaseModel):
    food_name: str
    portion_desc: str = ""


class LogMealRequest(BaseModel):
    user_id: str = "default"
    meal_type: str = "lunch"
    food_name: str
    portion_desc: str = ""
    calories: float
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    is_cheat: bool = False
    notes: str = ""
    date: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_file)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Lightweight health check endpoint for deployment monitoring."""
    return {"status": "ok", "service": "PoshanAI API"}

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    """User onboarding & instant assessment computation stored in centralized database."""
    profile = UserProfile(
        age_years=req.age_years,
        sex=req.sex,
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
        activity_level=req.activity_level,
        goal=req.goal,
    )
    assessment = assess_nutrition(profile)
    # Store profile in central database (MySQL / SQLite) so it syncs across computers
    save_or_update_user(
        username=req.name,
        name=req.name,
        age_years=req.age_years,
        sex=req.sex.value if hasattr(req.sex, "value") else str(req.sex),
        height_cm=req.height_cm,
        weight_kg=req.weight_kg,
        activity_level=req.activity_level.value if hasattr(req.activity_level, "value") else str(req.activity_level),
        goal=req.goal.value if hasattr(req.goal, "value") else str(req.goal),
        assessment=assessment.model_dump(),
    )
    # Seed sample weekly history if new so weekly chart displays immediate insights
    seed_demo_history_if_empty(user_id=req.name, target_kcal=int(assessment.tdee_kcal))
    return {
        "status": "success",
        "user_name": req.name,
        "profile": profile.model_dump(),
        "assessment": assessment.model_dump(),
    }


@app.get("/api/profile/get")
async def get_profile(username: str):
    """Retrieve profile from central database by username."""
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")
    profile = UserProfile(
        age_years=user["age_years"],
        sex=user["sex"],
        height_cm=user["height_cm"],
        weight_kg=user["weight_kg"],
        activity_level=user["activity_level"],
        goal=user["goal"],
    )
    assessment = assess_nutrition(profile)
    return {
        "status": "success",
        "user": user,
        "profile": profile.model_dump(),
        "assessment": assessment.model_dump(),
    }


@app.get("/api/profile/users")
async def get_users_list():
    """List all registered profiles in central database."""
    users = list_all_users()
    return {"status": "success", "count": len(users), "users": users}


@app.post("/api/foods/estimate")
async def estimate_food(req: FoodEstimateRequest):
    """Estimate calories and macronutrients for food item."""
    est = estimate_food_nutrition(req.food_name, req.portion_desc)
    return {"status": "success", "estimate": est}


@app.post("/api/planner/custom-entry")
async def add_custom_planner_entry(req: CustomPlannerEntryRequest):
    """Add a custom food entry directly into the Daily Planner."""
    cal = req.calories
    pro = req.protein_g
    carb = req.carbs_g
    fat = req.fat_g

    # If calories not provided or <= 0, automatically estimate from food name!
    if cal is None or cal <= 0:
        est = estimate_food_nutrition(req.food_name, req.portion_desc)
        cal = est["calories"]
        if pro is None or pro <= 0:
            pro = est["protein_g"]
        if carb is None or carb <= 0:
            carb = est["carbs_g"]
        if fat is None or fat <= 0:
            fat = est["fat_g"]

    item_id = add_planner_item(
        user_id=req.user_id,
        meal_type=req.meal_type,
        food_name=req.food_name,
        portion_desc=req.portion_desc,
        weight_g=req.weight_g,
        calories=cal or 300.0,
        protein_g=pro or 0.0,
        carbs_g=carb or 0.0,
        fat_g=fat or 0.0,
        is_custom=True,
        notes=req.notes,
        plan_date=req.date,
    )
    return {
        "status": "success",
        "item_id": item_id,
        "entry": {
            "id": item_id,
            "meal_type": req.meal_type,
            "food_name": req.food_name,
            "portion_desc": req.portion_desc,
            "weight_g": req.weight_g,
            "calories": cal or 300.0,
            "protein_g": pro or 0.0,
            "carbs_g": carb or 0.0,
            "fat_g": fat or 0.0,
            "is_completed": False,
            "is_custom": True,
            "notes": req.notes,
        },
        "message": "Custom entry added to daily planner.",
    }


@app.get("/api/planner/items")
async def list_planner_items(user_id: str = "default", date: Optional[str] = None):
    """Retrieve planner items for user and date."""
    items = get_planner_items(user_id=user_id, plan_date=date)
    return {"status": "success", "count": len(items), "items": items}


@app.post("/api/planner/toggle-item")
async def toggle_item(req: TogglePlannerItemRequest):
    """Toggle individual food item completion in planner and log to consumed totals."""
    set_planner_item_completion(req.item_id, req.is_completed)
    if req.is_completed and req.calories > 0:
        log_meal(
            user_id=req.user_id,
            meal_type=req.meal_type,
            food_name=req.food_name or "Planned Food Item",
            portion_desc=req.portion_desc or "1 serving",
            calories=req.calories,
            protein_g=req.protein_g,
            carbs_g=req.carbs_g,
            fat_g=req.fat_g,
            is_cheat=False,
            notes="Logged via Planner Food Checklist",
        )
    return {"status": "success", "item_id": req.item_id, "is_completed": req.is_completed}


@app.delete("/api/planner/items/{item_id}")
async def remove_planner_item(item_id: int):
    """Delete a custom entry from daily planner."""
    ok = delete_planner_item(item_id)
    return {"status": "success" if ok else "failed", "deleted": ok}



@app.post("/api/profile/calculate")
async def calculate_profile(profile: UserProfile):
    """Calculate BMR, TDEE, and daily nutrient targets."""
    assessment = assess_nutrition(profile)
    return {
        "status": "success",
        "profile": profile.model_dump(),
        "assessment": assessment.model_dump(),
    }


@app.get("/api/foods")
async def list_foods(query: Optional[str] = None, tag: Optional[str] = None):
    """Search and filter authentic Nepali foods."""
    if query:
        results = db.search(query)
    elif tag and tag != "all":
        results = db.filter_by_tag(tag)
    else:
        results = db.all_foods()
    return {"status": "success", "count": len(results), "foods": [f.model_dump() for f in results]}


@app.get("/api/samples")
async def list_samples():
    """List available sample dishes for quick 1-click test recognition."""
    samples = [
        {
            "id": "dal_bhat",
            "filename": "dal_bhat_tarkari.jpg",
            "name_ne": "दाल भात तरकारी थाली",
            "name_en": "Dal Bhat Tarkari Thali",
            "description_ne": "परम्परागत नेपाली थाली (भात, दाल, रायोको साग, गोलभेँडाको अचार)",
            "description_en": "Iconic Nepali staple with steamed rice, lentils, greens, and achar",
        },
        {
            "id": "momo",
            "filename": "momo_plate.jpg",
            "name_ne": "कुखुराको म:म: (१० पिस)",
            "name_en": "Chicken Momo Platter (10 pcs)",
            "description_ne": "उसिनेको म:म: र तिल-गोलभेँडाको अचार (उच्च प्रोटिन खाजा)",
            "description_en": "Steamed lean chicken dumplings with spiced dipping achar",
        },
        {
            "id": "dhindo",
            "filename": "dhindo_gundruk.jpg",
            "name_ne": "कोदोको ढिँडो र गुन्द्रुक",
            "name_en": "Millet Dhindo & Gundruk",
            "description_ne": "उच्च क्याल्सियम, आइरन र फाइबर भएको रैथाने नेपाली सुपरफुड",
            "description_en": "Indigenous superfood high in calcium, plant iron, and probiotics",
        },
        {
            "id": "kwati",
            "filename": "kwati_soup.jpg",
            "name_ne": "क्वाँटी (९ थरी गेडागुडीको रस)",
            "name_en": "Sprouted 9-Bean Kwati Soup",
            "description_ne": "कुपोषण र कमजोरी हटाउने उमारेको गेडागुडीको अचुक झोल",
            "description_en": "Sprouted multi-bean stew rich in bioavailable iron and zinc",
        },
        {
            "id": "sel_roti",
            "filename": "sel_roti.jpg",
            "name_ne": "सेल रोटी र अचार",
            "name_en": "Festive Sel Roti Platter",
            "description_ne": "चाडपर्वको परम्परागत सेल रोटी र आलुको अचार",
            "description_en": "Traditional ring rice doughnut with spiced pickle",
        },
    ]
    return {"status": "success", "samples": samples}


@app.post("/api/analyze/sample")
async def analyze_sample(req: SampleAnalyzeRequest):
    """Analyze a predefined authentic Nepali food sample image."""
    filepath = SAMPLES_DIR / req.sample_filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Sample image not found")

    img = Image.open(filepath)
    recognition = analyze_food_image(
        img,
        image_name_hint=req.sample_filename,
    )

    # Calculate meal summary
    portions = [
        MealItemPortion(
            food_id=item.food_id_guess,
            weight_g=item.estimated_weight_g,
            notes=item.notes,
        )
        for item in recognition.items
    ]
    meal_summary = db.calculate_meal(portions)

    # Use custom profile or default
    profile = req.custom_profile or UserProfile(
        age_years=24,
        sex=BiologicalSex.MALE,
        height_cm=170.0,
        weight_kg=62.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)
    evaluation = evaluate_meal_against_bmr(meal_summary, assessment)

    return {
        "status": "success",
        "recognition": recognition.model_dump(),
        "meal": meal_summary.model_dump(),
        "evaluation": evaluation.model_dump(),
        "assessment": assessment.model_dump(),
    }


@app.post("/api/analyze/upload")
async def analyze_upload(
    file: UploadFile = File(...),
    age: int = Form(24),
    sex: str = Form("male"),
    height_cm: float = Form(170.0),
    weight_kg: float = Form(62.0),
    activity: str = Form("moderate"),
    goal: str = Form("maintain"),
):
    """Upload food photo or camera snapshot for vision recognition."""
    content = await file.read()
    try:
        img = Image.open(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid image file")

    recognition = analyze_food_image(
        img,
        image_name_hint=file.filename or "upload.jpg",
    )

    portions = [
        MealItemPortion(
            food_id=item.food_id_guess,
            weight_g=item.estimated_weight_g,
            notes=item.notes,
        )
        for item in recognition.items
    ]
    meal_summary = db.calculate_meal(portions)

    sex_enum = BiologicalSex.FEMALE if sex.lower() == "female" else BiologicalSex.MALE
    act_enum = ActivityLevel(activity) if activity in [e.value for e in ActivityLevel] else ActivityLevel.MODERATE
    goal_enum = HealthGoal(goal) if goal in [g.value for g in HealthGoal] else HealthGoal.MAINTAIN

    profile = UserProfile(
        age_years=age,
        sex=sex_enum,
        height_cm=height_cm,
        weight_kg=weight_kg,
        activity_level=act_enum,
        goal=goal_enum,
    )
    assessment = assess_nutrition(profile)
    evaluation = evaluate_meal_against_bmr(meal_summary, assessment)

    return {
        "status": "success",
        "recognition": recognition.model_dump(),
        "meal": meal_summary.model_dump(),
        "evaluation": evaluation.model_dump(),
        "assessment": assessment.model_dump(),
    }


@app.post("/api/meal/recalculate")
async def recalculate_meal(req: CustomMealCalculateRequest):
    """Recalculate nutrition when user manually adjusts weights/portions."""
    meal_summary = db.calculate_meal(req.portions)
    profile = req.custom_profile or UserProfile(
        age_years=24,
        sex=BiologicalSex.MALE,
        height_cm=170.0,
        weight_kg=62.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)
    evaluation = evaluate_meal_against_bmr(meal_summary, assessment)

    return {
        "status": "success",
        "meal": meal_summary.model_dump(),
        "evaluation": evaluation.model_dump(),
    }


@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Interactive nutrition chatbot endpoint."""
    assessment = assess_nutrition(req.profile) if req.profile else None

    meal_summary = None
    if req.meal_context:
        try:
            meal_summary = MealSummary(**req.meal_context)
        except Exception:
            pass

    reply = chatbot.answer_question(
        user_message=req.message,
        user_profile=req.profile,
        assessment=assessment,
        meal_context=meal_summary,
        language=req.language,
    )
    return {"status": "success", "reply": reply}


@app.post("/api/planner/generate")
async def generate_plan(req: PlanGenerateRequest):
    """Generate personalized daily Nepali meal plan based on BMR/TDEE & dietary goals."""
    profile = req.profile or UserProfile(
        age_years=24,
        sex=BiologicalSex.MALE,
        height_cm=170.0,
        weight_kg=62.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)
    plan = generate_nepali_diet_plan(profile, assessment, preference=req.preference)
    return {
        "status": "success",
        "plan": plan.model_dump(),
        "assessment": assessment.model_dump(),
    }


@app.post("/api/history/log")
async def add_history_log(req: LogMealRequest):
    """Log an eaten meal or cheat meal to persistent diet history."""
    log_id = log_meal(
        user_id=req.user_id,
        meal_type=req.meal_type,
        food_name=req.food_name,
        portion_desc=req.portion_desc,
        calories=req.calories,
        protein_g=req.protein_g,
        carbs_g=req.carbs_g,
        fat_g=req.fat_g,
        is_cheat=req.is_cheat,
        notes=req.notes,
        log_date=req.date,
    )
    return {
        "status": "success",
        "log_id": log_id,
        "message": "Meal logged to diet history successfully.",
    }


@app.get("/api/history/list")
async def list_history(user_id: str = "default", days: int = 30):
    """Retrieve user diet history logs up to 30 days."""
    logs = get_history(user_id=user_id, days=days)
    return {"status": "success", "count": len(logs), "logs": logs}


@app.delete("/api/history/{log_id}")
async def remove_history_log(log_id: int):
    """Delete a diet history entry."""
    ok = delete_log(log_id)
    return {"status": "success" if ok else "failed", "deleted": ok}


@app.get("/api/history/weekly-tracker")
async def get_weekly_tracker(user_id: str = "default", target_kcal: float= 2100):
    """Weekly calorie intake vs budget tracker for homepage chart."""
    target_kcal = int(round(target_kcal))
    # Ensure some history is seeded for guest demo if empty
    seed_demo_history_if_empty(user_id=user_id, target_kcal=target_kcal)
    stats = get_weekly_calorie_tracker(user_id=user_id, daily_target_kcal=target_kcal)
    return {"status": "success", "stats": stats}


@app.get("/api/history/doctor-report-data")
async def get_doctor_report_data(user_id: str = "default", target_kcal: float= 2100):
    """Compile 1-month comprehensive diet history and stats for physician report."""
    target_kcal = int(round(target_kcal))
    seed_demo_history_if_empty(user_id=user_id, target_kcal=target_kcal)
    logs = get_history(user_id=user_id, days=30)
    tracker = get_weekly_calorie_tracker(user_id=user_id, daily_target_kcal=target_kcal)
    return {
        "status": "success",
        "user_id": user_id,
        "logs_30_days": logs,
        "weekly_stats": tracker,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


if __name__ == "__main__":
    import uvicorn
    print(f"Starting PoshanAI Server at http://{HOST}:{PORT} ...")
    uvicorn.run("server:app", host=HOST, port=PORT, reload=True)
