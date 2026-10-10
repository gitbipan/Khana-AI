"""
PoshanAI Diet History & Medical Report Storage
Seamless interface to the Centralized Database Manager (MySQL & SQLite).
Tracks daily meal adherence, custom entries, and 30-day physician reports.
"""

from __future__ import annotations
import sqlite3
from typing import List, Dict, Any, Optional
from core.db_manager import (
    SQLITE_PATH,
    init_db,
    log_meal,
    get_history,
    delete_log,
    get_weekly_calorie_tracker,
    seed_demo_history_if_empty,
    add_planner_item,
    get_planner_items,
    set_planner_item_completion,
    delete_planner_item,
    save_or_update_user,
    get_user_by_username,
    list_all_users,
)

DB_PATH = SQLITE_PATH


def get_db_connection() -> sqlite3.Connection:
    """Legacy helper for direct sqlite access in legacy scripts if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
