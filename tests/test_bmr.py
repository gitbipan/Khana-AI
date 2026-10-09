"""
Tests for BMR, TDEE, BMI, and nutritional target calculations.
"""

import pytest
from core.bmr_calculator import (
    UserProfile,
    BiologicalSex,
    ActivityLevel,
    HealthGoal,
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    assess_nutrition,
)


def test_bmi_calculation():
    # 70 kg, 175 cm -> 70 / (1.75^2) = 22.86 -> 22.9
    bmi, cat = calculate_bmi(175.0, 70.0)
    assert 22.8 <= bmi <= 23.0
    assert not cat.is_malnourished
    assert "Healthy" in cat.category_en or "Normal" in cat.category_en


def test_bmi_malnourished_underweight():
    # 42 kg, 165 cm -> 42 / (1.65^2) = 15.43 (severe thinness)
    bmi, cat = calculate_bmi(165.0, 42.0)
    assert bmi < 16.0
    assert cat.is_malnourished
    assert "Severe" in cat.category_en


def test_bmr_mifflin_st_jeor():
    # Male: 25 yrs, 70kg, 175cm
    # BMR = 10*70 + 6.25*175 - 5*25 + 5 = 700 + 1093.75 - 125 + 5 = 1673.75
    profile_male = UserProfile(
        age_years=25,
        sex=BiologicalSex.MALE,
        height_cm=175.0,
        weight_kg=70.0,
        activity_level=ActivityLevel.SEDENTARY,
        goal=HealthGoal.MAINTAIN,
    )
    bmr_m = calculate_bmr(profile_male)
    assert abs(bmr_m - 1673.8) < 1.0

    # Female: 25 yrs, 55kg, 160cm
    # BMR = 10*55 + 6.25*160 - 5*25 - 161 = 550 + 1000 - 125 - 161 = 1264.0
    profile_female = UserProfile(
        age_years=25,
        sex=BiologicalSex.FEMALE,
        height_cm=160.0,
        weight_kg=55.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    bmr_f = calculate_bmr(profile_female)
    assert abs(bmr_f - 1264.0) < 1.0


def test_tdee_and_assessment():
    profile = UserProfile(
        age_years=24,
        sex=BiologicalSex.MALE,
        height_cm=170.0,
        weight_kg=60.0,
        activity_level=ActivityLevel.MODERATE,  # 1.55 multiplier
        goal=HealthGoal.MALNUTRITION_RECOVERY,
    )
    assessment = assess_nutrition(profile)
    assert assessment.bmr_kcal > 1400
    assert assessment.tdee_kcal > assessment.bmr_kcal
    # Malnutrition recovery adds 500 kcal surplus
    assert assessment.target_daily.calories > assessment.tdee_kcal
    assert assessment.target_daily.protein_g >= 100.0  # 60kg * 1.8g/kg = 108g
    assert len(assessment.clinical_notes_ne) > 0