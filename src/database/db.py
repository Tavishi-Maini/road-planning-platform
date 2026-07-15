import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "road_projects.db"


def get_connection():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    return sqlite3.connect(
        DB_PATH,
        check_same_thread=False,
    )

def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            location TEXT NOT NULL,
            road_category TEXT,
            project_type TEXT,
            terrain_type TEXT,
            road_length_km REAL,
            number_of_lanes INTEGER,
            design_speed_kmph REAL,
            aadt INTEGER,
            subgrade_cbr_pct REAL,
            risk_level TEXT,
            prediction_status TEXT DEFAULT 'Pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            project_data TEXT NOT NULL,
            prediction_data TEXT
        )
    """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            prediction_data TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )
        """
    )
    
    try:
        cursor.execute("ALTER TABLE projects ADD COLUMN prediction_data TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()