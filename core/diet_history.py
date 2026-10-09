"""
PoshanAI Diet History & Medical Report Storage
Persistent SQLite engine tracking daily meal adherence, cheat meals, and 30-day physician reports.
"""

from __future__ import annotations
import sqlite3
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "diet_history.db"


def get_db_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS diet_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT DEFAULT 'default',
                date TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                food_name TEXT NOT NULL,
                portion_desc TEXT DEFAULT '',
                calories REAL NOT NULL,
                protein_g REAL DEFAULT 0.0,
                carbs_g REAL DEFAULT 0.0,
                fat_g REAL DEFAULT 0.0,
                is_cheat INTEGER DEFAULT 0,
                notes TEXT DEFAULT ''
            )
        """)
        conn.commit()


def log_meal(
    user_id: str = "default",
    meal_type: str = "lunch",
    food_name: str = "Nepali Meal",
    portion_desc: str = "",
    calories: float = 500.0,
    protein_g: float = 15.0,
    carbs_g: float = 65.0,
    fat_g: float = 8.0,
    is_cheat: bool = False,
    notes: str = "",
    log_date: Optional[str] = None,
) -> int:
    init_db()
    today_str = log_date or date.today().isoformat()
    now_iso = datetime.now().isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO diet_logs (
                user_id, date, timestamp, meal_type, food_name, portion_desc,
                calories, protein_g, carbs_g, fat_g, is_cheat, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                today_str,
                now_iso,
                meal_type,
                food_name,
                portion_desc,
                round(calories, 1),
                round(protein_g, 1),
                round(carbs_g, 1),
                round(fat_g, 1),
                1 if is_cheat else 0,
                notes,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_history(user_id: str = "default", days: int = 30) -> List[Dict[str, Any]]:
    init_db()
    cutoff = (date.today() - timedelta(days=days)).isoformat()
    with get_db_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM diet_logs
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC, id DESC
            """,
            (user_id, cutoff),
        ).fetchall()
        return [dict(r) for r in rows]


def delete_log(log_id: int) -> bool:
    init_db()
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM diet_logs WHERE id = ?", (log_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_weekly_calorie_tracker(user_id: str = "default", daily_target_kcal: int = 2100) -> Dict[str, Any]:
    """
    Computes calorie consumption vs target budget for each of the past 7 days (Sunday to Saturday / last 7 days).
    Categorizes each day into: 'on_target', 'undershot', or 'overshot'.
    """
    init_db()
    days_data = []
    total_consumed = 0
    overshot_count = 0
    undershot_count = 0
    on_target_count = 0

    nepali_day_names = ["आइत", "सोम", "मंगल", "बुध", "बिही", "शुक्र", "शनि"]
    english_day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    today = date.today()
    # Past 7 days from (today - 6 days) to today
    for i in range(6, -1, -1):
        cur_date = today - timedelta(days=i)
        date_str = cur_date.isoformat()
        day_of_week = cur_date.weekday() # 0 = Monday, 6 = Sunday
        # Map to Sun-Sat (Sun = 0)
        idx = (day_of_week + 1) % 7
        ne_day = nepali_day_names[idx]
        en_day = english_day_names[idx]

        with get_db_connection() as conn:
            row = conn.execute(
                """
                SELECT SUM(calories) as total_cal, SUM(protein_g) as total_pro, COUNT(*) as meal_count
                FROM diet_logs
                WHERE user_id = ? AND date = ?
                """,
                (user_id, date_str),
            ).fetchone()

        cal = row["total_cal"] or 0.0
        pro = row["total_pro"] or 0.0
        count = row["meal_count"] or 0

        # Calculate deviation vs budget
        deviation = cal - daily_target_kcal
        # Status determination:
        # within 12% is on-target
        if cal == 0:
            status = "no_data"
        elif cal > daily_target_kcal * 1.10:
            status = "overshot"
            overshot_count += 1
        elif cal < daily_target_kcal * 0.88:
            status = "undershot"
            undershot_count += 1
        else:
            status = "on_target"
            on_target_count += 1

        total_consumed += cal
        days_data.append({
            "date": date_str,
            "day_ne": ne_day,
            "day_en": en_day,
            "calories": round(cal),
            "target": daily_target_kcal,
            "deviation": round(deviation),
            "protein_g": round(pro, 1),
            "meal_count": count,
            "status": status,
        })

    active_days = [d for d in days_data if d["calories"] > 0]
    avg_calories = round(total_consumed / len(active_days)) if active_days else daily_target_kcal

    return {
        "days": days_data,
        "daily_target_kcal": daily_target_kcal,
        "weekly_total_kcal": round(total_consumed),
        "weekly_avg_daily_kcal": avg_calories,
        "on_target_days": on_target_count,
        "undershot_days": undershot_count,
        "overshot_days": overshot_count,
        "adherence_rate_pct": round((on_target_count / max(len(active_days), 1)) * 100, 1),
    }


def seed_demo_history_if_empty(user_id: str = "default", target_kcal: int = 2100) -> None:
    """Seeds realistic demo data for the last 6 days if the database is brand new."""
    init_db()
    with get_db_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM diet_logs WHERE user_id = ?", (user_id,)).fetchone()[0]
        if count > 0:
            return  # Already has logs

    # Seed 6 days of realistic Nepali meals
    today = date.today()
    sample_schedules = [
        # Day -5 (On target): Dhindo & Kwati
        [
            ("breakfast", "चिउरा र कालो चनाको तरकारी", "१ प्लेट", 380, 11.0, 55.0, 4.0, False, "बिहानीको खाजा"),
            ("lunch", "कोदोको ढिँडो र क्वाँटीको रस", "२५० ग्राम ढिँडो + क्वाँटी", 780, 24.5, 95.0, 6.0, False, "रैथाने पौष्टिक खाना"),
            ("snack", "भुटेको भटमास र मकै", "५० ग्राम", 220, 14.0, 18.0, 5.0, False, "सस्तो प्रोटिन खाजा"),
            ("dinner", "फापरको रोटी र गुन्द्रुक झोल", "२ वटा रोटी + १ कचौरा गुन्द्रुक", 580, 16.0, 68.0, 5.0, False, "साँझको हलुका खाना"),
        ],
        # Day -4 (Undershot): Busy day
        [
            ("breakfast", "कालो चिया र २ वटा बिस्कुट", "सामान्य", 140, 2.0, 28.0, 2.5, False, "हतारमा खाएको"),
            ("lunch", "दाल भात तरकारी", "मध्यम थाली", 620, 15.0, 110.0, 7.0, False, "दिउँसोको खाना"),
            ("dinner", "उसिनेको चाउचाउ", "१ प्याकेट", 380, 7.0, 52.0, 12.0, False, "थकाइ लागेर"),
        ],
        # Day -3 (On target): High protein
        [
            ("breakfast", "२ वटा उसिनेको अण्डा र दूध", "२ अण्डा + १ गिलास दूध", 320, 20.0, 14.0, 16.0, False, "उच्च प्रोटिन बिहानी"),
            ("lunch", "दाल भात, कुखुराको मासु र साग", "नेपाली थाली", 850, 36.0, 115.0, 14.0, False, "सन्तुलित थाली"),
            ("snack", "स्याउ र १ मुठ्ठी भटमास", "सामान्य", 190, 8.5, 24.0, 3.5, False, "ताजा फलफूल र प्रोटिन"),
            ("dinner", "रोटी र मुसुरोको बाक्लो दाल", "३ वटा रोटी + १ कचौरा दाल", 680, 22.0, 92.0, 6.0, False, "बेलुकीको दाल रोटी"),
        ],
        # Day -2 (Overshot): Cheat day with friends!
        [
            ("breakfast", "चिउरा र आलुचना", "१ प्लेट", 390, 10.5, 60.0, 5.0, False, "खाजा"),
            ("lunch", "दाल भात तरकारी", "ठूलो थाली", 840, 18.0, 145.0, 9.0, False, "धेरै भात खाइयो"),
            ("snack", "कुखुराको म:म: (१० पिस) र कोल्ड ड्रिंक", "१० पिस म:म:", 620, 26.0, 65.0, 18.0, True, "साथीहरूसँग म:म: (चिट मिल)"),
            ("dinner", "सेल रोटी र आलु दम", "२ वटा सेल रोटी", 580, 6.0, 78.0, 20.0, True, "चाडपर्वको परिकार"),
        ],
        # Day -1 (On target): Clean eating
        [
            ("breakfast", "सातुको सर्बत र १ अण्डा", "१ गिलास सातु + १ अण्डा", 340, 18.0, 32.0, 8.0, False, "सातु सर्बत"),
            ("lunch", "कोदोको ढिँडो, रायोको साग र दाल", "ढिँडो थाली", 740, 19.5, 88.0, 6.0, False, "स्वस्थ थाली"),
            ("snack", "ताजा मोही र भटमास", "१ गिलास मोही", 210, 13.0, 15.0, 4.0, False, "खाजा"),
            ("dinner", "रोटी र तरकारी", "२ रोटी + मिक्स तरकारी", 590, 15.0, 72.0, 7.0, False, "बेलुकीको खाना"),
        ],
    ]

    for d_offset, day_meals in enumerate(sample_schedules):
        log_d = (today - timedelta(days=5 - d_offset)).isoformat()
        for meal in day_meals:
            log_meal(
                user_id=user_id,
                meal_type=meal[0],
                food_name=meal[1],
                portion_desc=meal[2],
                calories=meal[3],
                protein_g=meal[4],
                carbs_g=meal[5],
                fat_g=meal[6],
                is_cheat=meal[7],
                notes=meal[8],
                log_date=log_d,
            )
