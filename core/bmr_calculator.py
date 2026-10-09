"""
PoshanAI BMR & TDEE Clinical Calculator (दैनिक क्यालोरी तथा पोषण मापक)
Implements Mifflin-St Jeor & WHO South Asian BMI standards for malnutrition assessment.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Optional
from pydantic import BaseModel, Field


class BiologicalSex(str, Enum):
    MALE = "male"
    FEMALE = "female"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"                # Little or no exercise, desk job (1.20)
    LIGHT = "light"                        # Light exercise 1-3 days/wk (1.375)
    MODERATE = "moderate"                  # Moderate exercise / active job 3-5 days/wk (1.55)
    VERY_ACTIVE = "very_active"            # Hard physical labor / intense farming / athletics (1.725)
    EXTRA_ACTIVE = "extra_active"          # Extreme physical work (e.g. porter, heavy agriculture) (1.90)


class HealthGoal(str, Enum):
    MAINTAIN = "maintain"                                # Maintain weight & balanced vitality
    MALNUTRITION_RECOVERY = "malnutrition_recovery"      # Combat underweight / muscle wasting (+500 kcal, high protein)
    WEIGHT_LOSS = "weight_loss"                          # Healthy gradual fat loss (-500 kcal)
    MUSCLE_GAIN = "muscle_gain"                          # Lean mass building (+350 kcal)


class BMICategory(BaseModel):
    category_en: str
    category_ne: str
    risk_level_en: str
    risk_level_ne: str
    is_malnourished: bool


class UserProfile(BaseModel):
    age_years: int = Field(..., ge=1, le=120, description="Age in years")
    sex: BiologicalSex = Field(..., description="Biological sex")
    height_cm: float = Field(..., ge=40, le=250, description="Height in centimeters")
    weight_kg: float = Field(..., ge=2.5, le=300, description="Weight in kilograms")
    activity_level: ActivityLevel = Field(default=ActivityLevel.MODERATE)
    goal: HealthGoal = Field(default=HealthGoal.MAINTAIN)


class DailyTargets(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    water_liters: float
    iron_mg: float
    calcium_mg: float
    vitamin_a_mcg: float


class NutritionalAssessment(BaseModel):
    bmi: float
    bmi_category: BMICategory
    bmr_kcal: float
    tdee_kcal: float
    target_daily: DailyTargets
    protein_per_kg: float
    clinical_notes_en: list[str]
    clinical_notes_ne: list[str]


ACTIVITY_MULTIPLIERS: Dict[ActivityLevel, float] = {
    ActivityLevel.SEDENTARY: 1.20,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.55,
    ActivityLevel.VERY_ACTIVE: 1.725,
    ActivityLevel.EXTRA_ACTIVE: 1.90,
}


def calculate_bmi(height_cm: float, weight_kg: float) -> tuple[float, BMICategory]:
    """Calculate BMI using South Asian WHO-adjusted cutoffs."""
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)

    if bmi < 16.0:
        cat = BMICategory(
            category_en="Severe Thinness (Severe Acute Malnutrition)",
            category_ne="अत्यधिक दुब्लोपन (गम्भीर कुपोषण)",
            risk_level_en="Critical nutritional deficiency risk",
            risk_level_ne="अत्यन्तै उच्च स्वास्थ्य जोखिम",
            is_malnourished=True,
        )
    elif bmi < 17.0:
        cat = BMICategory(
            category_en="Moderate Thinness (Moderate Malnutrition)",
            category_ne="मध्यम दुब्लोपन (मध्यम कुपोषण)",
            risk_level_en="Moderate nutritional wasting",
            risk_level_ne="मध्यम जोखिम",
            is_malnourished=True,
        )
    elif bmi < 18.5:
        cat = BMICategory(
            category_en="Mild Thinness (Underweight)",
            category_ne="कम तौल (हल्का कुपोषण)",
            risk_level_en="Low muscle reserve and anemia risk",
            risk_level_ne="रक्तअल्पता र कमजोरीको सम्भावना",
            is_malnourished=True,
        )
    elif bmi < 23.0:
        # Note: WHO South Asian cutoff for normal is 18.5 - 22.9
        cat = BMICategory(
            category_en="Normal Healthy Weight (South Asian Standard)",
            category_ne="सामान्य स्वस्थ तौल",
            risk_level_en="Healthy baseline",
            risk_level_ne="स्वस्थ अवस्था",
            is_malnourished=False,
        )
    elif bmi < 27.5:
        cat = BMICategory(
            category_en="Overweight (South Asian Cutoff)",
            category_ne="बढी तौल",
            risk_level_en="Elevated cardiometabolic risk",
            risk_level_ne="मधुमेह तथा मुटु रोगको जोखिम",
            is_malnourished=False,
        )
    else:
        cat = BMICategory(
            category_en="Obese",
            category_ne="मोटोपन",
            risk_level_en="High metabolic risk",
            risk_level_ne="उच्च स्वास्थ्य जोखिम",
            is_malnourished=False,
        )

    return bmi, cat


def calculate_bmr(profile: UserProfile) -> float:
    """Calculate Basal Metabolic Rate using the clinical Mifflin-St Jeor formula."""
    # Men: BMR = 10*weight + 6.25*height - 5*age + 5
    # Women: BMR = 10*weight + 6.25*height - 5*age - 161
    base = (10.0 * profile.weight_kg) + (6.25 * profile.height_cm) - (5.0 * profile.age_years)
    if profile.sex == BiologicalSex.MALE:
        bmr = base + 5.0
    else:
        bmr = base - 161.0
    return round(max(bmr, 600.0), 1)


def calculate_tdee(bmr: float, activity: ActivityLevel) -> float:
    """Calculate Total Daily Energy Expenditure from BMR and physical activity."""
    multiplier = ACTIVITY_MULTIPLIERS.get(activity, 1.55)
    return round(bmr * multiplier, 1)


def assess_nutrition(profile: UserProfile) -> NutritionalAssessment:
    """Complete personalized clinical nutritional assessment and macro target formulation."""
    bmi, bmi_cat = calculate_bmi(profile.height_cm, profile.weight_kg)
    bmr = calculate_bmr(profile)
    tdee = calculate_tdee(bmr, profile.activity_level)

    # Goal adjustment
    notes_en = []
    notes_ne = []

    target_calories = tdee
    if profile.goal == HealthGoal.MALNUTRITION_RECOVERY or bmi_cat.is_malnourished:
        target_calories = tdee + 500.0
        protein_per_kg = 1.8  # Elevated protein to rebuild lean tissue
        notes_en.append(
            "Targeting +500 kcal caloric surplus with 1.8g/kg protein to safely reverse nutritional wasting and muscle loss."
        )
        notes_ne.append(
            "कुपोषण र कमजोरी हटाउन दैनिक ५०० क्यालोरी बढी र प्रति केजी १.८ ग्राम प्रोटिन सिफारिस गरिएको छ।"
        )
    elif profile.goal == HealthGoal.WEIGHT_LOSS:
        target_calories = max(tdee - 500.0, bmr)  # Never drop below resting BMR
        protein_per_kg = 1.6  # High protein preserves lean mass in deficit
        notes_en.append(
            f"Moderate 500 kcal deficit. Floor set at BMR ({bmr} kcal) to preserve metabolic rate."
        )
        notes_ne.append(
            f"स्वस्थ रूपमा बोसो घटाउन ५०० क्यालोरी कम। तर आधारभूत BMR ({bmr} क्यालोरी) भन्दा तल नघटाउने।"
        )
    elif profile.goal == HealthGoal.MUSCLE_GAIN:
        target_calories = tdee + 350.0
        protein_per_kg = 1.7
        notes_en.append("Caloric surplus of +350 kcal optimized for hypertrophy and lean mass accretion.")
        notes_ne.append("मांसपेशीको विकासका लागि दैनिक ३५० क्यालोरी थप र उच्च प्रोटिन सिफारिस।")
    else:  # MAINTAIN
        target_calories = tdee
        protein_per_kg = 1.2
        notes_en.append("Caloric intake set to match TDEE for body weight stabilization and metabolic balance.")
        notes_ne.append("तौल स्थिर राख्न र ऊर्जा कायम राख्न दैनिक TDEE बराबरको क्यालोरी सिफारिस।")

    # Macro distribution
    target_protein_g = round(profile.weight_kg * protein_per_kg, 1)
    protein_cals = target_protein_g * 4.0

    # Healthy fats: 25% of target calories (1g fat = 9 kcal)
    fat_cals = target_calories * 0.25
    target_fat_g = round(fat_cals / 9.0, 1)

    # Carbohydrates: remaining calories (1g carb = 4 kcal)
    carb_cals = max(target_calories - (protein_cals + fat_cals), 0.0)
    target_carbs_g = round(carb_cals / 4.0, 1)

    # Water requirement: roughly 35ml per kg of bodyweight
    water_liters = round(max((profile.weight_kg * 0.035), 2.0), 1)

    # Micronutrient guidelines (RDA based on age & sex)
    # Women of reproductive age require significantly more iron (18-27mg) due to anemia risks in Nepal
    if profile.sex == BiologicalSex.FEMALE and 14 <= profile.age_years <= 50:
        iron_target = 18.0
    else:
        iron_target = 10.0

    calcium_target = 1000.0 if profile.age_years < 50 else 1200.0
    vitamin_a_target = 700.0 if profile.sex == BiologicalSex.FEMALE else 900.0

    daily_targets = DailyTargets(
        calories=round(target_calories, 1),
        protein_g=target_protein_g,
        carbs_g=target_carbs_g,
        fat_g=target_fat_g,
        water_liters=water_liters,
        iron_mg=iron_target,
        calcium_mg=calcium_target,
        vitamin_a_mcg=vitamin_a_target,
    )

    if bmi_cat.is_malnourished:
        notes_en.append(
            "Priority alert: Diet should actively incorporate iron-dense and protein-rich local foods (Kwati, Bhatmas, Gundruk, Eggs, Saag)."
        )
        notes_ne.append(
            "विशेष ध्यान: खानामा गेडागुडी, भटमास, अण्डा, हरियो साग र क्वाँटी जस्ता पौष्टिक खानेकुरा अनिवार्य समावेश गर्नुहोस्।"
        )

    return NutritionalAssessment(
        bmi=bmi,
        bmi_category=bmi_cat,
        bmr_kcal=bmr,
        tdee_kcal=tdee,
        target_daily=daily_targets,
        protein_per_kg=protein_per_kg,
        clinical_notes_en=notes_en,
        clinical_notes_ne=notes_ne,
    )
