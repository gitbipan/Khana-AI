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

    def fuzzy_match(self, query: str) -> Optional[FoodItem]:
        """Fuzzy match food names, ingredients, or IDs to nearest authentic Nepali food."""
        import re
        q = (query or "").lower().strip()
        if not q:
            return None
        if q in self._foods:
            return self._foods[q]

        token_map = [
            (["momo", "dumpling"], "momo_chicken"),
            (["rice", "bhat", "steamed"], "plain_steamed_rice"),
            (["dhindo", "millet", "kodo"], "kodo_ko_dhindo"),
            (["kwati", "sprout", "bean"], "kwati_soup"),
            (["gundruk", "ferment"], "gundruk_bhatmas_soup"),
            (["bhatmas", "soybean"], "bhatmas_sadeko"),
            (["achar", "pickle", "chutney", "tomato", "golbheda", "sesame"], "golbheda_ko_achar"),
            (["dal", "lentil", "musuro"], "musuro_ko_dal"),
            (["saag", "green", "spinach", "mustard", "rayo"], "rayo_ko_saag"),
            (["sel", "roti", "doughnut"], "sel_roti"),
            (["egg", "anda"], "boiled_egg"),
            (["chiura", "beaten"], "chiura_beaten_rice"),
            (["jaulo", "khichdi"], "jaulo_porridge"),
            (["sattu", "gram"], "sattu_flour"),
        ]
        for tokens, fid in token_map:
            if any(t in q for t in tokens) and fid in self._foods:
                return self._foods[fid]

        hits = self.search(q)
        if hits:
            return hits[0]

        words = [w for w in re.split(r"\W+", q) if len(w) > 2]
        for w in words:
            hits = self.search(w)
            if hits:
                return hits[0]

        return None

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
            food = self.get_by_id(p.food_id) or self.fuzzy_match(p.food_id)
            if not food and p.notes:
                food = self.fuzzy_match(p.notes)
            if not food:
                food = self.get_by_id("plain_steamed_rice") or list(self._foods.values())[0]

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


def estimate_food_nutrition(food_name: str, portion_desc: str = "") -> Dict[str, Any]:
    """
    Intelligently estimates calories and macros (protein, carbs, fat)
    from food name and portion description.
    Uses authentic Nepali food database first, then smart food heuristics.
    """
    db = get_nutrition_db()
    name = (food_name or "").strip()
    portion = (portion_desc or "").strip().lower()

    # Multiplier based on portion words
    mult = 1.0
    if any(w in portion for w in ["२", "2", "two", "double", "ठूलो", "large"]):
        mult = 1.8
    elif any(w in portion for w in ["३", "3", "three"]):
        mult = 2.5
    elif any(w in portion for w in ["आधा", "half", "0.5", "सानो", "small"]):
        mult = 0.6
    elif any(w in portion for w in ["१०", "10"]):
        mult = 1.0  # e.g. 10 pcs momo is standard 1 plate

    # 1. Search in Nepali foods database
    match = db.fuzzy_match(name)
    if not match:
        results = db.search(name)
        if results:
            match = results[0]

    if match:
        serv = match.per_serving
        return {
            "calories": round(serv.calories * mult, 1),
            "protein_g": round(serv.protein_g * mult, 1),
            "carbs_g": round(serv.carbs_g * mult, 1),
            "fat_g": round(serv.fat_g * mult, 1),
            "source": f"Database match: {match.name_ne} ({match.name_en})",
            "matched_id": match.id,
        }

    # 2. Heuristics based on common dishes
    n_lower = name.lower()
    heuristics = [
        (["momo", "मम", "म:म:"], 420.0, 22.0, 52.0, 12.0),
        (["pizza", "पिज्जा"], 320.0, 13.0, 38.0, 12.0),
        (["burger", "बर्गर"], 440.0, 19.0, 46.0, 18.0),
        (["samosa", "समोसा", "सिङ्घाडा"], 260.0, 4.5, 30.0, 14.0),
        (["chowmein", "चाउमिन", "chaumin", "noodles"], 380.0, 10.0, 56.0, 12.0),
        (["thukpa", "थुक्पा"], 360.0, 16.0, 52.0, 9.0),
        (["chiya", "चिया", "tea"], 95.0, 2.0, 15.0, 2.5),
        (["coffee", "कफी"], 90.0, 2.0, 13.0, 2.5),
        (["biscuit", "बिस्कुट", "cookie"], 130.0, 1.8, 22.0, 4.0),
        (["anda", "अण्डा", "egg"], 140.0, 12.0, 1.0, 9.5),
        (["roti", "रोटी", "chapati", "fulka"], 120.0, 3.5, 24.0, 1.2),
        (["bhat", "भात", "rice", "chawal"], 240.0, 4.5, 52.0, 0.8),
        (["dal", "दाल", "lentil"], 150.0, 9.0, 24.0, 1.5),
        (["tarkari", "तरकारी", "curry"], 160.0, 3.5, 20.0, 7.5),
        (["masu", "मासु", "meat", "chicken", "buff", "mutton"], 310.0, 28.0, 2.0, 20.0),
        (["dhindo", "ढिँडो"], 340.0, 8.5, 72.0, 1.8),
        (["kwati", "क्वाँटी"], 260.0, 15.5, 44.0, 2.5),
        (["gundruk", "गुन्द्रुक"], 85.0, 5.0, 12.0, 1.5),
        (["salad", "सलाद"], 70.0, 1.8, 12.0, 1.2),
        (["fruit", "फलफूल", "apple", "banana", "स्याउ", "केरा"], 105.0, 1.2, 26.0, 0.4),
        (["dahi", "दही", "curd", "yogurt"], 140.0, 6.0, 11.0, 6.5),
        (["mohi", "मोही", "buttermilk"], 80.0, 4.0, 8.0, 3.0),
    ]

    for keywords, c, p, cr, f in heuristics:
        if any(k in n_lower for k in keywords):
            return {
                "calories": round(c * mult, 1),
                "protein_g": round(p * mult, 1),
                "carbs_g": round(cr * mult, 1),
                "fat_g": round(f * mult, 1),
                "source": "Smart heuristic estimation",
                "matched_id": None,
            }

    # Default general Nepali dish estimate (~300 kcal)
    return {
        "calories": round(300.0 * mult, 1),
        "protein_g": round(8.0 * mult, 1),
        "carbs_g": round(45.0 * mult, 1),
        "fat_g": round(7.0 * mult, 1),
        "source": "General dish estimation",
        "matched_id": None,
    }

