"""
Tests for Nepali food nutrition database queries and meal calculations.
"""

import pytest
from core.nutrition_db import get_nutrition_db, MealItemPortion


def test_db_loading():
    db = get_nutrition_db()
    foods = db.all_foods()
    assert len(foods) >= 20
    ids = [f.id for f in foods]
    assert "dal_bhat_tarkari" in ids
    assert "kodo_ko_dhindo" in ids
    assert "kwati_soup" in ids
    assert "gundruk_bhatmas_soup" in ids
    assert "boiled_egg" in ids


def test_search_functionality():
    db = get_nutrition_db()
    # Search by english
    res_en = db.search("momo")
    assert len(res_en) >= 3

    # Search by nepali
    res_ne = db.search("ढिँडो")
    assert len(res_ne) >= 1

    # Search by tag
    iron_foods = db.filter_by_tag("iron_rich")
    assert len(iron_foods) >= 4


def test_meal_summary_calculation():
    db = get_nutrition_db()
    portions = [
        MealItemPortion(food_id="plain_steamed_rice", weight_g=200),  # 260 kcal, 5.4g pro
        MealItemPortion(food_id="musuro_ko_dal", weight_g=150),       # 120 kcal, 8.4g pro
        MealItemPortion(food_id="rayo_ko_saag", weight_g=100),        # 48 kcal, 2.8g pro
        MealItemPortion(food_id="boiled_egg", weight_g=55),           # 85 kcal, 7.2g pro
    ]
    summary = db.calculate_meal(portions)
    assert len(summary.items) == 4
    # Calories: 260 + 120 + 48 + 85 = 513
    assert 500 <= summary.totals.calories <= 530
    # Protein: 5.4 + 8.4 + 2.8 + 7.2 = 23.8g
    assert 22.0 <= summary.totals.protein_g <= 25.0
    # Iron should be present
    assert summary.totals.iron_mg > 4.0
    # Macro percentages should sum close to 100
    assert 98.0 <= (summary.protein_calorie_pct + summary.carb_calorie_pct + summary.fat_calorie_pct) <= 102.0