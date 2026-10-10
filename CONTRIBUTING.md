# Contributing to Khana-AI 🎃

Thank you for your interest in contributing to **Khana-AI** during **Hacktoberfest 2026**!
Our mission is to build an open-source, culturally tailored AI nutrition platform to address malnutrition and promote healthy eating across Nepal.

---

## 🌟 Hacktoberfest Guidelines

- Quality contributions over quantity! Spam or superficial PRs (e.g. changing whitespace) will be marked as invalid.
- Meaningful contributions include adding authentic regional Nepali recipes, translating UI strings, optimizing portion estimation algorithms, or writing tests.

---

## 🛠️ How to Add a New Nepali Food Item

You can easily expand the database by editing `data/nepali_foods.json`.

Each food entry follows this schema:
```json
{
  "id": "unique_slug",
  "name_en": "English Name",
  "name_ne": "नेपाली नाम (देवनागरी)",
  "category": "staple | plant_protein | meat_protein | greens | fermented | traditional_superfood | festive",
  "serving_unit": "1 bowl (150g)",
  "serving_weight_g": 150,
  "per_100g": {
    "calories": 120,
    "protein_g": 6.5,
    "carbs_g": 18.0,
    "fat_g": 2.5,
    "fiber_g": 3.0,
    "iron_mg": 2.1,
    "calcium_mg": 40,
    "vitamin_a_mcg": 15
  },
  "per_serving": {
    "calories": 180,
    "protein_g": 9.75,
    "carbs_g": 27.0,
    "fat_g": 3.75,
    "fiber_g": 4.5,
    "iron_mg": 3.15,
    "calcium_mg": 60,
    "vitamin_a_mcg": 22.5
  },
  "malnutrition_benefits": "English description of nutritional significance.",
  "malnutrition_benefits_ne": "नेपाली भाषामा पोषण र स्वास्थ्य महत्त्व।",
  "tags": ["plant_protein", "iron_rich", "low_cost"]
}
```

Ensure nutritional values correspond to authentic references such as the *Food Composition Table for Nepal* (DFTQC).

---

## 🧪 Testing Your Changes

Before submitting a Pull Request, run the automated test suite:

```bash
uv run pytest
```

All tests must pass. If you added a new calculation or feature, please add a corresponding unit test in `tests/`.

---

## 📬 Pull Request Checklist

- [ ] Fork the repo and create your branch from `master`.
- [ ] Ensure `uv run pytest` runs cleanly with 100% passes.
- [ ] Use meaningful commit messages (e.g. `feat(data): add Jhol Momo nutritional profile`).
- [ ] Submit a PR with a clear summary of changes.

Happy Hacking and Namaste! 🙏
