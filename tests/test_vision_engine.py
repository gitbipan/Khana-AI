
from pathlib import Path
from PIL import Image
import pytest
from core.vision_engine import (
    analyze_food_image,
    _extract_json_from_text,
    FALLBACK_PRESETS,
)
from core.nutrition_db import get_nutrition_db

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "static" / "sample_images"


def test_extract_json_from_text():
    raw_str = '{"dish_title_en": "Momo", "items": []}'
    parsed = _extract_json_from_text(raw_str)
    assert parsed["dish_title_en"] == "Momo"

    fenced_str = '```json\n{"dish_title_en": "Dal Bhat", "items": []}\n```'
    parsed_fenced = _extract_json_from_text(fenced_str)
    assert parsed_fenced["dish_title_en"] == "Dal Bhat"


def test_vision_fallback_with_sample_images():
    db = get_nutrition_db()

    # Test with Momo sample
    momo_path = SAMPLES_DIR / "momo_plate.jpg"
    assert momo_path.exists(), "Sample image should exist"
    img = Image.open(momo_path)
    res = analyze_food_image(img, api_key=None, image_name_hint="momo_plate.jpg")

    assert res.source == "heuristic_fallback"
    assert "Momo" in res.dish_title_en
    assert len(res.items) >= 2
    for item in res.items:
        # Check that food_id_guess is valid in database
        food = db.get_by_id(item.food_id_guess)
        assert food is not None, f"Item {item.food_id_guess} should exist in db"


def test_vision_fallback_presets():
    dummy_img = Image.new("RGB", (100, 100), color=(200, 200, 200))
    for key in FALLBACK_PRESETS:
        res = analyze_food_image(dummy_img, api_key=None, image_name_hint=f"{key}_sample.jpg")
        assert len(res.items) > 0
        assert res.dish_title_en
        assert res.dish_title_ne


def test_fuzzy_match_mapping():
    db = get_nutrition_db()
    assert db.fuzzy_match("chicken_dumplings").id == "momo_chicken"
    assert db.fuzzy_match("tomato_achar").id == "golbheda_ko_achar"
    assert db.fuzzy_match("sprouted_bean_soup").id == "kwati_soup"
    assert db.fuzzy_match("steamed_rice").id == "plain_steamed_rice"