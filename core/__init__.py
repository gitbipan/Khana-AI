"""
PoshanAI Core Engine Package
"""

from .nutrition_db import (
    NutritionDatabase,
    FoodItem,
    Nutrients,
    MealItemPortion,
    MealSummary,
    get_nutrition_db,
)
from .bmr_calculator import (
    UserProfile,
    BiologicalSex,
    ActivityLevel,
    HealthGoal,
    NutritionalAssessment,
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    assess_nutrition,
)
from .vision_engine import (
    DetectedItem,
    VisionRecognitionResult,
    analyze_food_image,
    FALLBACK_PRESETS,
)
from .advisor_engine import (
    MalnutritionFlag,
    MealEvaluationVerdict,
    evaluate_meal_against_bmr,
    PoshanChatbot,
)
from .config import (
    GEMMA_API_KEY,
    CHAT_MODEL,
    VISION_MODEL,
    HOST,
    PORT,
)

__all__ = [
    "NutritionDatabase",
    "FoodItem",
    "Nutrients",
    "MealItemPortion",
    "MealSummary",
    "get_nutrition_db",
    "UserProfile",
    "BiologicalSex",
    "ActivityLevel",
    "HealthGoal",
    "NutritionalAssessment",
    "calculate_bmi",
    "calculate_bmr",
    "calculate_tdee",
    "assess_nutrition",
    "DetectedItem",
    "VisionRecognitionResult",
    "analyze_food_image",
    "FALLBACK_PRESETS",
    "MalnutritionFlag",
    "MealEvaluationVerdict",
    "evaluate_meal_against_bmr",
    "PoshanChatbot",
    "GEMMA_API_KEY",
    "CHAT_MODEL",
    "VISION_MODEL",
    "HOST",
    "PORT",
]
