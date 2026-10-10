"""
Tests for PoshanAI Diet Planner, Todo Checklist Tracking, Weekly Calorie Budget & Doctor Report.
"""

from fastapi.testclient import TestClient
from server import app
from core.bmr_calculator import UserProfile, BiologicalSex, ActivityLevel, HealthGoal, assess_nutrition
from core.advisor_engine import generate_nepali_diet_plan
from core.diet_history import log_meal, get_history, delete_log, get_weekly_calorie_tracker

client = TestClient(app)


def test_diet_planner_generation():
    profile = UserProfile(
        age_years=25,
        sex=BiologicalSex.MALE,
        height_cm=172.0,
        weight_kg=65.0,
        activity_level=ActivityLevel.MODERATE,
        goal=HealthGoal.MAINTAIN,
    )
    assessment = assess_nutrition(profile)
    plan = generate_nepali_diet_plan(profile, assessment, preference="all")

    assert len(plan.meals) == 4
    meal_types = [m.meal_type for m in plan.meals]
    assert "breakfast" in meal_types
    assert "lunch" in meal_types
    assert "snack" in meal_types
    assert "dinner" in meal_types

    # Ensure calories are within reasonable bounds of daily target
    assert abs(plan.total_planned_calories - assessment.target_daily.calories) < 250
    assert plan.total_planned_protein_g > 40.0


def test_diet_history_crud():
    # Log a meal
    log_id = log_meal(
        user_id="test_user",
        meal_type="lunch",
        food_name="दाल भात तरकारी थाली",
        portion_desc="१ थाली",
        calories=650.0,
        protein_g=18.0,
        carbs_g=110.0,
        fat_g=8.0,
        is_cheat=False,
        notes="घरको ताजा खाना",
    )
    assert log_id > 0

    # Retrieve history
    history = get_history(user_id="test_user", days=7)
    assert len(history) >= 1
    assert any(h["food_name"] == "दाल भात तरकारी थाली" for h in history)

    # Delete log
    deleted = delete_log(log_id)
    assert deleted is True


def test_weekly_tracker():
    tracker = get_weekly_calorie_tracker(user_id="test_user", daily_target_kcal=2200)
    assert "days" in tracker
    assert len(tracker["days"]) == 7
    assert "daily_target_kcal" in tracker
    assert tracker["daily_target_kcal"] == 2200
    for day in tracker["days"]:
        assert day["status"] in ["on_target", "undershot", "overshot", "no_data"]


def test_planner_and_history_api_endpoints():
    # Test Planner API
    res_plan = client.post("/api/planner/generate", json={"preference": "all"})
    assert res_plan.status_code == 200
    plan_data = res_plan.json()
    assert plan_data["status"] == "success"
    assert len(plan_data["plan"]["meals"]) == 4

    # Test History Log API
    log_payload = {
        "user_id": "api_test_user",
        "meal_type": "snack",
        "food_name": "कुखुराको म:म: (१० पिस)",
        "portion_desc": "१० पिस",
        "calories": 480.0,
        "protein_g": 24.0,
        "carbs_g": 52.0,
        "fat_g": 12.0,
        "is_cheat": True,
        "notes": "Cheat meal with friends",
    }
    res_log = client.post("/api/history/log", json=log_payload)
    assert res_log.status_code == 200
    log_res_data = res_log.json()
    assert log_res_data["status"] == "success"
    log_id = log_res_data["log_id"]

    # Test History List API
    res_list = client.get("/api/history/list?user_id=api_test_user&days=7")
    assert res_list.status_code == 200
    list_data = res_list.json()
    assert list_data["count"] >= 1

    # Test Weekly Tracker API
    res_tracker = client.get("/api/history/weekly-tracker?user_id=api_test_user&target_kcal=2100")
    assert res_tracker.status_code == 200
    assert "stats" in res_tracker.json()

    # Test Doctor Report Data API
    res_report = client.get("/api/history/doctor-report-data?user_id=api_test_user&target_kcal=2100")
    assert res_report.status_code == 200
    report_data = res_report.json()
    assert "logs_30_days" in report_data
    assert "weekly_stats" in report_data

    # Cleanup
    client.delete(f"/api/history/{log_id}")


def test_food_nutrition_auto_estimation():
    # Test estimation with food name that matches database
    res = client.post("/api/foods/estimate", json={"food_name": "म:म:", "portion_desc": "१० पिस"})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["estimate"]["calories"] > 0
    assert data["estimate"]["protein_g"] > 0

    # Test estimation with common dish heuristics (e.g. samosa)
    res2 = client.post("/api/foods/estimate", json={"food_name": "समोसा", "portion_desc": "२ वटा"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["status"] == "success"
    assert data2["estimate"]["calories"] > 300  # 2 pieces multiplied


def test_custom_planner_entry_and_checklist_flow():
    # Add custom entry to planner without specifying calories (testing auto-estimate)
    custom_payload = {
        "user_id": "test_planner_user",
        "meal_type": "snack",
        "food_name": "चाउमिन (Chowmein)",
        "portion_desc": "१ प्लेट",
        "notes": "Custom evening snack"
    }
    res_entry = client.post("/api/planner/custom-entry", json=custom_payload)
    assert res_entry.status_code == 200
    entry_data = res_entry.json()
    assert entry_data["status"] == "success"
    assert entry_data["entry"]["calories"] > 0  # Auto-estimated!
    item_id = entry_data["item_id"]

    # Verify item is retrieved in planner
    res_items = client.get("/api/planner/items?user_id=test_planner_user")
    assert res_items.status_code == 200
    items_data = res_items.json()
    assert any(it["id"] == item_id for it in items_data["items"])

    # Test toggling item checklist
    res_toggle = client.post("/api/planner/toggle-item", json={
        "item_id": item_id,
        "is_completed": True,
        "user_id": "test_planner_user",
        "food_name": "चाउमिन (Chowmein)",
        "meal_type": "snack",
        "calories": entry_data["entry"]["calories"],
        "protein_g": entry_data["entry"]["protein_g"]
    })
    assert res_toggle.status_code == 200
    assert res_toggle.json()["is_completed"] is True

    # Test weekly tracker target range properties
    res_tracker = client.get("/api/history/weekly-tracker?user_id=test_planner_user&target_kcal=2200")
    stats = res_tracker.json()["stats"]
    assert stats["upper_target_kcal"] == round(2200 * 1.10)
    assert stats["lower_target_kcal"] == round(2200 * 0.90)

    # Cleanup planner item
    client.delete(f"/api/planner/items/{item_id}")


def test_central_database_profile_sync():
    # Login and save user
    login_payload = {
        "name": "राम_बहादुर",
        "age_years": 28,
        "sex": "male",
        "height_cm": 175.0,
        "weight_kg": 68.0,
        "activity_level": "moderate",
        "goal": "maintain"
    }
    res_login = client.post("/api/auth/login", json=login_payload)
    assert res_login.status_code == 200

    # Retrieve from database
    res_profile = client.get("/api/profile/get?username=राम_बहादुर")
    assert res_profile.status_code == 200
    prof_data = res_profile.json()
    assert prof_data["status"] == "success"
    assert prof_data["profile"]["height_cm"] == 175.0
    assert prof_data["profile"]["weight_kg"] == 68.0

    # List all users
    res_users = client.get("/api/profile/users")
    assert res_users.status_code == 200
    users_list = res_users.json()["users"]
    assert any(u["username"] == "राम_बहादुर" for u in users_list)

