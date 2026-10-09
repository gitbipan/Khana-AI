"""
Tests for PoshanAI Nutrition Advisor & Chatbot (Module 3).
"""

import pytest
from core.bmr_calculator import (
    UserProfile,
    BiologicalSex,
    ActivityLevel,
    HealthGoal,
    assess_nutrition,
)
from core.nutrition_db import get_nutrition_db, MealItemPortion
from core.advisor_engine import (
    evaluate_meal_against_bmr,
    PoshanChatbot,
)


def test_high_carb_low_protein_meal_evaluation():
    db = get_nutrition_db()
    profile = UserProfile(
        age_years=25,
        sex=BiologicalSex.MALE,
        height_cm=175.0,
        weight_kg=65.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)

    # Imbalanced meal: big bowl of white rice, no protein source
    portions = [
        MealItemPortion(food_id="plain_steamed_rice", weight_g=350),  # lots of carbs, low protein
    ]
    meal = db.calculate_meal(portions)

    verdict = evaluate_meal_against_bmr(meal, assessment)

    # Should flag low protein and/or high carb
    flag_codes = [f.code for f in verdict.malnutrition_flags]
    assert "low_protein" in flag_codes or "high_carb_ratio" in flag_codes
    assert len(verdict.actionable_advice_en) > 0
    assert len(verdict.actionable_advice_ne) > 0
    assert len(verdict.suggested_local_additions_ne) > 0
    assert "अण्डा" in " ".join(verdict.suggested_local_additions_ne) or "भटमास" in " ".join(verdict.suggested_local_additions_ne)


def test_balanced_meal_evaluation():
    db = get_nutrition_db()
    profile = UserProfile(
        age_years=22,
        sex=BiologicalSex.FEMALE,
        height_cm=160.0,
        weight_kg=52.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)

    # Well balanced traditional meal: Kodo Dhindo + Kwati Soup + Boiled Egg + Saag
    portions = [
        MealItemPortion(food_id="kodo_ko_dhindo", weight_g=200),
        MealItemPortion(food_id="kwati_soup", weight_g=200),
        MealItemPortion(food_id="boiled_egg", weight_g=55),
        MealItemPortion(food_id="rayo_ko_saag", weight_g=100),
    ]
    meal = db.calculate_meal(portions)
    verdict = evaluate_meal_against_bmr(meal, assessment)

    assert verdict.score_out_of_10 >= 7.0
    assert len(verdict.key_positives_en) > 0
    assert len(verdict.key_positives_ne) > 0


def test_chatbot_offline_responses():
    bot = PoshanChatbot(api_key=None)
    profile = UserProfile(
        age_years=28,
        sex=BiologicalSex.MALE,
        height_cm=172.0,
        weight_kg=68.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)

    # Nepali BMR response
    resp_ne = bot.answer_question("मेरो BMR कति छ?", profile, assessment, language="ne")
    assert "क्यालोरी" in resp_ne
    assert str(int(assessment.bmr_kcal)) in resp_ne

    # English protein question
    resp_en = bot.answer_question("What are cheap protein foods in Nepal?", profile, assessment, language="en")
    assert "Bhatmas" in resp_en or "Egg" in resp_en

    # Anemia question in Nepali
    resp_anemia = bot.answer_question("रगतको कमी वा आइरन बढाउन के खाने?", profile, assessment, language="ne")
    assert "साग" in resp_anemia or "आइरन" in resp_anemia