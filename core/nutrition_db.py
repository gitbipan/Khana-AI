"""
PoshanAI Nutrition Database Engine (पोषण ज्ञानकोष)
Loads and queries curated nutritional metrics for traditional Nepali foods.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FOODS_FILE = DATA_DIR / "nepali_foods.json"


class Nutrients(BaseModel):
    calories: float = Field(..., description="Energy in kcal")
    protein_g: float = Field(..., description="Protein in grams")
    carbs_g: float = Field(..., description="Carbohydrates in grams")
    fat_g: float = Field(..., description="Fats in grams")
    fiber_g: float = Field(0.0, description="Dietary fiber in grams")
    iron_mg: float = Field(0.0, description="Iron in milligrams")
    calcium_mg: float = Field(0.0, description="Calcium in milligrams")
    vitamin_a_mcg: float = Field(0.0, description="Vitamin A in micrograms RAE")


class FoodItem(BaseModel):
    id: str
    name_en: str
    name_ne: str
    category: str
    serving_unit: str
    serving_weight_g: float
    per_100g: Nutrients
    per_serving: Nutrients
    malnutrition_benefits: str
    malnutrition_benefits_ne: str
    tags: List[str] = Field(default_factory=list)

    def calculate_for_weight(self, weight_g: float) -> Nutrients:
        """Scale nutrients proportionally for an arbitrary portion in grams."""
        factor = weight_g / 100.0
        return Nutrients(
            calories=round(self.per_100g.calories * factor, 1),
            protein_g=round(self.per_100g.protein_g * factor, 1),
            carbs_g=round(self.per_100g.carbs_g * factor, 1),
            fat_g=round(self.per_100g.fat_g * factor, 1),
            fiber_g=round(self.per_100g.fiber_g * factor, 1),
            iron_mg=round(self.per_100g.iron_mg * factor, 2),
            calcium_mg=round(self.per_100g.calcium_mg * factor, 1),
            vitamin_a_mcg=round(self.per_100g.vitamin_a_mcg * factor, 1),
        )


class MealItemPortion(BaseModel):
    food_id: str
    weight_g: float
    notes: Optional[str] = None


class MealSummary(BaseModel):
    items: List[dict]
    totals: Nutrients
    protein_calorie_pct: float
    carb_calorie_pct: float
    fat_calorie_pct: float
    key_highlights_en: List[str]
    key_highlights_ne: List[str]


class NutritionDatabase:
    """Singleton-style database manager for Nepali foods."""

    def __init__(self, data_path: Path = FOODS_FILE):
        self.data_path = data_path
        self._foods: Dict[str, FoodItem] = {}
        self.load_data()

    def load_data(self) -> None:
        if not self.data_path.exists():
            raise FileNotFoundError(f"Nutrition database not found at {self.data_path}")
        with open(self.data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            for entry in raw:
                item = FoodItem(**entry)
                self._foods[item.id] = item

    def all_foods(self) -> List[FoodItem]:
        return list(self._foods.values())

    def get_by_id(self, food_id: str) -> Optional[FoodItem]:
        return self._foods.get(food_id)

    def search(self, query: str) -> List[FoodItem]:
        """Case-insensitive search across English name, Nepali name, and tags."""
        q = query.strip().lower()
        if not q:
            return self.all_foods()

        results = []
        for food in self._foods.values():
            if (
                q in food.name_en.lower()
                or q in food.name_ne.lower()
                or q in food.id.lower()
                or any(q in tag.lower() for tag in food.tags)
            ):
                results.append(food)
        return results

    def filter_by_tag(self, tag: str) -> List[FoodItem]:
        t = tag.strip().lower()
        return [f for f in self._foods.values() if any(t == item_tag.lower() for item_tag in f.tags)]

    def calculate_meal(self, portions: List[MealItemPortion]) -> MealSummary:
        """Aggregate total nutrients for a multi-item Nepali meal/thali."""
        tot_cal = 0.0
        tot_pro = 0.0
        tot_carb = 0.0
        tot_fat = 0.0
        tot_fib = 0.0
        tot_iron = 0.0
        tot_calc = 0.0
        tot_vita = 0.0

        item_breakdowns = []
        highlights_en = []
        highlights_ne = []

        for p in portions:
            food = self.get_by_id(p.food_id)
            if not food:
                continue

            n = food.calculate_for_weight(p.weight_g)
            tot_cal += n.calories
            tot_pro += n.protein_g
            tot_carb += n.carbs_g
            tot_fat += n.fat_g
            tot_fib += n.fiber_g
            tot_iron += n.iron_mg
            tot_calc += n.calcium_mg
            tot_vita += n.vitamin_a_mcg

            item_breakdowns.append({
                "food_id": food.id,
                "name_en": food.name_en,
                "name_ne": food.name_ne,
                "weight_g": p.weight_g,
                "nutrients": n.model_dump(),
                "notes": p.notes or ""
            })

            if "malnutrition_superfood" in food.tags or "high_protein" in food.tags:
                highlights_en.append(f"{food.name_en}: {food.malnutrition_benefits}")
                highlights_ne.append(f"{food.name_ne}: {food.malnutrition_benefits_ne}")

        # Macro caloric percentages
        # 1g protein = 4 kcal, 1g carb = 4 kcal, 1g fat = 9 kcal
        pro_cals = tot_pro * 4.0
        carb_cals = tot_carb * 4.0
        fat_cals = tot_fat * 9.0
        sum_cals = (pro_cals + carb_cals + fat_cals) or 1.0

        pro_pct = round((pro_cals / sum_cals) * 100.0, 1)
        carb_pct = round((carb_cals / sum_cals) * 100.0, 1)
        fat_pct = round((fat_cals / sum_cals) * 100.0, 1)

        totals = Nutrients(
            calories=round(tot_cal, 1),
            protein_g=round(tot_pro, 1),
            carbs_g=round(tot_carb, 1),
            fat_g=round(tot_fat, 1),
            fiber_g=round(tot_fib, 1),
            iron_mg=round(tot_iron, 2),
            calcium_mg=round(tot_calc, 1),
            vitamin_a_mcg=round(tot_vita, 1),
        )

        return MealSummary(
            items=item_breakdowns,
            totals=totals,
            protein_calorie_pct=pro_pct,
            carb_calorie_pct=carb_pct,
            fat_calorie_pct=fat_pct,
            key_highlights_en=highlights_en,
            key_highlights_ne=highlights_ne,
        )


# Global singleton helper
_db_instance: Optional[NutritionDatabase] = None


def get_nutrition_db() -> NutritionDatabase:
    global _db_instance
    if _db_instance is None:
        _db_instance = NutritionDatabase()
    return _db_instance
