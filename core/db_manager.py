"""
Khana-AI Centralized Database Manager
Supports Hosted MySQL for cross-computer synchronization with graceful SQLite fallback.
"""

from __future__ import annotations
import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Tuple
from contextlib import contextmanager

from core.config import (
    BASE_DIR,
    DB_TYPE,
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE,
    DATABASE_URL,
)

SQLITE_PATH = BASE_DIR / "data" / "diet_history.db"

# Global database status flag
_USE_MYSQL = False
_INITIALIZED = False


def _parse_database_url(url: str) -> Dict[str, Any]:
    """Parse a MySQL database URL string if provided."""
    import re
    # Format: mysql://user:password@host:port/dbname
    pattern = r"mysql://(?:([^:@]+)(?::([^@]*))?@)?([^:/]+)(?::(\d+))?/(.+)"
    m = re.match(pattern, url)
    if not m:
        return {}
    user, password, host, port, dbname = m.groups()
    return {
        "host": host or "localhost",
        "port": int(port or 3306),
        "user": user or "root",
        "password": password or "",
        "database": dbname or "khana_ai",
    }


def get_mysql_config() -> Dict[str, Any]:
    """Get the active MySQL configuration dictionary."""
    if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
        cfg = _parse_database_url(DATABASE_URL)
        if cfg:
            return cfg
    return {
        "host": MYSQL_HOST,
        "port": MYSQL_PORT,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "database": MYSQL_DATABASE,
    }


def can_connect_mysql() -> bool:
    """Test if the configured MySQL database is reachable."""
    if DB_TYPE != "mysql":
        return False
    try:
        import pymysql
        cfg = get_mysql_config()
        # Connect with a short timeout so we don't hang if MySQL is offline
        conn = pymysql.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            connect_timeout=3,
        )
        conn.close()
        return True
    except Exception as e:
        print(f"[DatabaseManager] MySQL not reachable ({e}). Falling back to SQLite.")
        return False


class DBWrapper:
    """Wrapper that normalizes query execution across MySQL and SQLite."""
    def __init__(self, conn, is_mysql: bool):
        self.conn = conn
        self.is_mysql = is_mysql

    def execute(self, query: str, params: Tuple = ()) -> Any:
        # Convert ? to %s for MySQL if needed
        if self.is_mysql:
            query = query.replace("?", "%s")
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor

    def commit(self):
        self.conn.commit()

    def fetchall(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        cur = self.execute(query, params)
        if self.is_mysql:
            rows = cur.fetchall()
            cur.close()
            return list(rows) if rows else []
        else:
            rows = cur.fetchall()
            result = [dict(r) for r in rows]
            cur.close()
            return result

    def fetchone(self, query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        cur = self.execute(query, params)
        row = cur.fetchone()
        cur.close()
        if not row:
            return None
        return dict(row) if not self.is_mysql else row

    def lastrowid(self, cursor) -> int:
        return cursor.lastrowid or 0


@contextmanager
def get_db():
    """Context manager providing an active database connection."""
    global _USE_MYSQL
    if _USE_MYSQL:
        import pymysql
        from pymysql.cursors import DictCursor
        cfg = get_mysql_config()
        conn = pymysql.connect(
            host=cfg["host"],
            port=cfg["port"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            cursorclass=DictCursor,
            autocommit=False,
        )
        wrapper = DBWrapper(conn, is_mysql=True)
        try:
            yield wrapper
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    else:
        SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        wrapper = DBWrapper(conn, is_mysql=False)
        try:
            yield wrapper
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


def init_db(force: bool = False):
    """Initializes tables in the active database (MySQL or SQLite)."""
    global _USE_MYSQL, _INITIALIZED
    if _INITIALIZED and not force:
        return

    _USE_MYSQL = can_connect_mysql()
    print(f"[DatabaseManager] Active database engine: {'MySQL (Hosted)' if _USE_MYSQL else 'SQLite (Local)'}")

    with get_db() as db:
        if _USE_MYSQL:
            # MySQL DDL
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    name VARCHAR(150) NOT NULL,
                    age_years INT NOT NULL,
                    sex VARCHAR(20) NOT NULL,
                    height_cm FLOAT NOT NULL,
                    weight_kg FLOAT NOT NULL,
                    activity_level VARCHAR(50) NOT NULL,
                    goal VARCHAR(50) NOT NULL,
                    assessment_json TEXT,
                    created_at VARCHAR(50),
                    updated_at VARCHAR(50)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            db.execute("""
                CREATE TABLE IF NOT EXISTS diet_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100) DEFAULT 'default',
                    date VARCHAR(20) NOT NULL,
                    timestamp VARCHAR(50) NOT NULL,
                    meal_type VARCHAR(50) NOT NULL,
                    food_name VARCHAR(255) NOT NULL,
                    portion_desc VARCHAR(255) DEFAULT '',
                    calories FLOAT NOT NULL,
                    protein_g FLOAT DEFAULT 0.0,
                    carbs_g FLOAT DEFAULT 0.0,
                    fat_g FLOAT DEFAULT 0.0,
                    is_cheat INT DEFAULT 0,
                    notes TEXT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)

            db.execute("""
                CREATE TABLE IF NOT EXISTS planner_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(100) DEFAULT 'default',
                    date VARCHAR(20) NOT NULL,
                    meal_type VARCHAR(50) NOT NULL,
                    food_name VARCHAR(255) NOT NULL,
                    portion_desc VARCHAR(255) DEFAULT '',
                    weight_g FLOAT DEFAULT 100.0,
                    calories FLOAT NOT NULL,
                    protein_g FLOAT DEFAULT 0.0,
                    carbs_g FLOAT DEFAULT 0.0,
                    fat_g FLOAT DEFAULT 0.0,
                    is_completed INT DEFAULT 0,
                    is_custom INT DEFAULT 1,
                    notes TEXT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
        else:
            # SQLite DDL
            db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    age_years INTEGER NOT NULL,
                    sex TEXT NOT NULL,
                    height_cm REAL NOT NULL,
                    weight_kg REAL NOT NULL,
                    activity_level TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    assessment_json TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)

            db.execute("""
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

            db.execute("""
                CREATE TABLE IF NOT EXISTS planner_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    date TEXT NOT NULL,
                    meal_type TEXT NOT NULL,
                    food_name TEXT NOT NULL,
                    portion_desc TEXT DEFAULT '',
                    weight_g REAL DEFAULT 100.0,
                    calories REAL NOT NULL,
                    protein_g REAL DEFAULT 0.0,
                    carbs_g REAL DEFAULT 0.0,
                    fat_g REAL DEFAULT 0.0,
                    is_completed INTEGER DEFAULT 0,
                    is_custom INTEGER DEFAULT 1,
                    notes TEXT DEFAULT ''
                )
            """)

    _INITIALIZED = True


# =====================================================================
# USER PROFILE OPERATIONS (Shared across all computers via hosted DB)
# =====================================================================

def save_or_update_user(
    username: str,
    name: str,
    age_years: int,
    sex: str,
    height_cm: float,
    weight_kg: float,
    activity_level: str,
    goal: str,
    assessment: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Store or update user profile in the central hosted database."""
    init_db()
    now_str = datetime.now().isoformat()
    assess_str = json.dumps(assessment) if assessment else "{}"

    with get_db() as db:
        existing = db.fetchone("SELECT id FROM users WHERE username = ?", (username,))
        if existing:
            db.execute(
                """
                UPDATE users
                SET name = ?, age_years = ?, sex = ?, height_cm = ?, weight_kg = ?,
                    activity_level = ?, goal = ?, assessment_json = ?, updated_at = ?
                WHERE username = ?
                """,
                (name, age_years, sex, height_cm, weight_kg, activity_level, goal, assess_str, now_str, username)
            )
        else:
            db.execute(
                """
                INSERT INTO users (
                    username, name, age_years, sex, height_cm, weight_kg,
                    activity_level, goal, assessment_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (username, name, age_years, sex, height_cm, weight_kg, activity_level, goal, assess_str, now_str, now_str)
            )

    return get_user_by_username(username)


def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Retrieve profile from central database by username."""
    init_db()
    with get_db() as db:
        user = db.fetchone("SELECT * FROM users WHERE username = ?", (username,))
        if not user:
            return None
        res = dict(user)
        if res.get("assessment_json"):
            try:
                res["assessment"] = json.loads(res["assessment_json"])
            except Exception:
                res["assessment"] = None
        return res


def list_all_users() -> List[Dict[str, Any]]:
    """List all registered profiles in the database."""
    init_db()
    with get_db() as db:
        users = db.fetchall("SELECT username, name, age_years, sex, height_cm, weight_kg, activity_level, goal, updated_at FROM users ORDER BY updated_at DESC")
        return users


# =====================================================================
# DIET LOGS & MEAL HISTORY OPERATIONS
# =====================================================================

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
    """Log an eaten meal record."""
    init_db()
    today_str = log_date or date.today().isoformat()
    now_iso = datetime.now().isoformat()

    with get_db() as db:
        cur = db.execute(
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
            )
        )
        log_id = db.lastrowid(cur)
        cur.close()
        return log_id


def get_history(user_id: str = "default", days: int = 30) -> List[Dict[str, Any]]:
    """Retrieve historical diet logs within the last N days."""
    init_db()
    cutoff_date = (date.today() - timedelta(days=days)).isoformat()
    with get_db() as db:
        rows = db.fetchall(
            """
            SELECT * FROM diet_logs
            WHERE user_id = ? AND date >= ?
            ORDER BY date DESC, id DESC
            """,
            (user_id, cutoff_date),
        )
        for r in rows:
            r["is_cheat"] = bool(r.get("is_cheat", 0))
        return rows


def delete_log(log_id: int) -> bool:
    """Delete a diet log by id."""
    init_db()
    with get_db() as db:
        cur = db.execute("DELETE FROM diet_logs WHERE id = ?", (log_id,))
        cur.close()
        return True


# =====================================================================
# DIET PLANNER ITEMS OPERATIONS (Checklists & Custom Entries)
# =====================================================================

def add_planner_item(
    user_id: str = "default",
    meal_type: str = "lunch",
    food_name: str = "Custom Entry",
    portion_desc: str = "1 serving",
    weight_g: float = 100.0,
    calories: float = 300.0,
    protein_g: float = 10.0,
    carbs_g: float = 40.0,
    fat_g: float = 5.0,
    is_custom: bool = True,
    notes: str = "",
    plan_date: Optional[str] = None,
) -> int:
    """Add a food item / custom entry directly into the Daily Planner."""
    init_db()
    today_str = plan_date or date.today().isoformat()
    with get_db() as db:
        cur = db.execute(
            """
            INSERT INTO planner_items (
                user_id, date, meal_type, food_name, portion_desc, weight_g,
                calories, protein_g, carbs_g, fat_g, is_completed, is_custom, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                today_str,
                meal_type,
                food_name,
                portion_desc,
                round(weight_g, 1),
                round(calories, 1),
                round(protein_g, 1),
                round(carbs_g, 1),
                round(fat_g, 1),
                0,
                1 if is_custom else 0,
                notes,
            )
        )
        item_id = db.lastrowid(cur)
        cur.close()
        return item_id


def get_planner_items(user_id: str = "default", plan_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all planner food items for a specific date."""
    init_db()
    today_str = plan_date or date.today().isoformat()
    with get_db() as db:
        rows = db.fetchall(
            """
            SELECT * FROM planner_items
            WHERE user_id = ? AND date = ?
            ORDER BY id ASC
            """,
            (user_id, today_str),
        )
        for r in rows:
            r["is_completed"] = bool(r.get("is_completed", 0))
            r["is_custom"] = bool(r.get("is_custom", 0))
        return rows


def set_planner_item_completion(item_id: int, is_completed: bool) -> bool:
    """Toggle completion status of an individual food item in the planner."""
    init_db()
    with get_db() as db:
        cur = db.execute(
            "UPDATE planner_items SET is_completed = ? WHERE id = ?",
            (1 if is_completed else 0, item_id)
        )
        cur.close()
        return True


def delete_planner_item(item_id: int) -> bool:
    """Delete a planner food item."""
    init_db()
    with get_db() as db:
        cur = db.execute("DELETE FROM planner_items WHERE id = ?", (item_id,))
        cur.close()
        return True


# =====================================================================
# WEEKLY CALORIE BUDGET TRACKER (With Target Range, Overshoot & Undershoot)
# =====================================================================

def get_weekly_calorie_tracker(user_id: str = "default", daily_target_kcal: int = 2100) -> Dict[str, Any]:
    """
    Computes a 7-day adherence report with Upper/Lower Target Range.
    Days above the upper bound are categorized as 'overshot'.
    Days below the lower bound are categorized as 'undershot'.
    Days within range are categorized as 'on_target'.
    """
    init_db()
    days_data = []
    total_consumed = 0.0
    undershot_count = 0
    overshot_count = 0
    on_target_count = 0

    nepali_day_names = ["आइत", "सोम", "मंगल", "बुध", "बिही", "शुक्र", "शनि"]
    english_day_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Upper and Lower limits for target range (+10% / -10%)
    upper_target_kcal = round(daily_target_kcal * 1.10)
    lower_target_kcal = round(daily_target_kcal * 0.90)

    today = date.today()
    for i in range(6, -1, -1):
        cur_date = today - timedelta(days=i)
        date_str = cur_date.isoformat()
        day_of_week = cur_date.weekday()
        idx = (day_of_week + 1) % 7
        ne_day = nepali_day_names[idx]
        en_day = english_day_names[idx]

        with get_db() as db:
            row = db.fetchone(
                """
                SELECT SUM(calories) as total_cal, SUM(protein_g) as total_pro, COUNT(*) as meal_count
                FROM diet_logs
                WHERE user_id = ? AND date = ?
                """,
                (user_id, date_str),
            )

        cal = (row.get("total_cal") or 0.0) if row else 0.0
        pro = (row.get("total_pro") or 0.0) if row else 0.0
        count = (row.get("meal_count") or 0) if row else 0

        deviation = cal - daily_target_kcal
        if cal == 0:
            status = "no_data"
        elif cal > upper_target_kcal:
            status = "overshot"
            overshot_count += 1
        elif cal < lower_target_kcal:
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
            "upper_target": upper_target_kcal,
            "lower_target": lower_target_kcal,
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
        "upper_target_kcal": upper_target_kcal,
        "lower_target_kcal": lower_target_kcal,
        "weekly_total_kcal": round(total_consumed),
        "weekly_avg_daily_kcal": avg_calories,
        "on_target_days": on_target_count,
        "undershot_days": undershot_count,
        "overshot_days": overshot_count,
        "adherence_rate_pct": round((on_target_count / max(len(active_days), 1)) * 100, 1),
        "db_engine": "mysql" if _USE_MYSQL else "sqlite",
    }


def seed_demo_history_if_empty(user_id: str = "default", target_kcal: int = 2100) -> None:
    """Seeds realistic demo data for the last 6 days if the database is brand new."""
    init_db()
    with get_db() as db:
        row = db.fetchone("SELECT COUNT(*) as count FROM diet_logs WHERE user_id = ?", (user_id,))
        count = row.get("count", 0) if row else 0
        if count > 0:
            return

    # Seed realistic Nepali meals
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
            ("lunch", "दाल भात र माछाको झोल", "१ कचौरा भात + माछा", 750, 28.0, 90.0, 14.0, False, "माछाको पौष्टिक थाली"),
            ("snack", "चनाको सातु र कागती पानी", "१ गिलास सातु", 240, 12.0, 36.0, 3.0, False, "सस्तो शक्तिवर्धक पेय"),
            ("dinner", "ढिँडो र रायोको साग", "२०० ग्राम ढिँडो", 610, 15.0, 78.0, 5.0, False, "फाइबरयुक्त साँझ"),
        ],
        # Day -2 (Overshot): Feast with friends
        [
            ("breakfast", "सेल रोटी र चिया", "३ वटा सेल रोटी", 550, 6.0, 75.0, 24.0, False, "बिहानीको खाजा"),
            ("lunch", "दाल भात र खसीको मासु", "ठूलो थाली", 950, 34.0, 125.0, 26.0, False, "शनिबारको भोज"),
            ("snack", "कुखुराको म:म: र अचार", "१० पिस", 480, 24.0, 52.0, 12.0, True, "साथीहरूसँग खाजा"),
            ("dinner", "चाउमिन र कोक", "१ प्लेट चाउमिन", 720, 14.0, 88.0, 22.0, True, "रेस्टुरेन्ट डिनर"),
        ],
        # Day -1 (On target): Recovery day
        [
            ("breakfast", "दही चिउरा र केरा", "१ कचौरा दही + चिउरा", 390, 11.5, 62.0, 6.5, False, "हलुका बिहानी"),
            ("lunch", "दाल भात, सिमी र गोलभेँडा अचार", "मध्यम थाली", 680, 17.0, 105.0, 7.0, False, "सन्तुलित खाना"),
            ("snack", "उसिनेको अण्डा र फलफूल", "१ अण्डा + स्याउ", 190, 8.0, 22.0, 5.0, False, "फलफूल खाजा"),
            ("dinner", "गहुँको रोटी र काउलीको तरकारी", "३ रोटी + तरकारी", 560, 14.0, 74.0, 6.0, False, "साँझको खाना"),
        ],
    ]

    for offset, schedule in enumerate(sample_schedules, start=1):
        d_str = (today - timedelta(days=6 - offset)).isoformat()
        for meal in schedule:
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
                log_date=d_str,
            )
