from typing import Any
import json
import pandas as pd
from src.database.db import get_connection
from src.database.supabase_client import get_supabase_client


TABLE_NAME = "projects"

def get_prediction_history():
    """
    Returns all projects that have completed predictions,
    ordered by newest first.
    """
    projects = get_all_projects()

    if projects.empty:
        return pd.DataFrame()

    if "prediction_status" in projects.columns:
        projects = projects[
            projects["prediction_status"] == "Completed"
        ]

    if "created_at" in projects.columns:
        projects = projects.sort_values(
            by="created_at",
            ascending=False,
        )

    return projects

def save_prediction_history(project_id, prediction_data):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO prediction_history (
                project_id,
                prediction_data
            )
            VALUES (?, ?)
            """,
            (
                int(project_id),
                json.dumps(prediction_data),
            ),
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        

def save_project(project_data):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO projects (
                project_name,
                location,
                road_category,
                terrain_type,
                road_length_km,
                number_of_lanes,
                design_speed_kmph,
                aadt,
                subgrade_cbr_pct,
                risk_level,
                prediction_status,
                project_data
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_data["project_name"],
                project_data["location"],
                project_data["road_category"],
                project_data["terrain_type"],
                project_data["road_length_km"],
                project_data["number_of_lanes"],
                project_data["design_speed_kmph"],
                project_data["aadt"],
                project_data["subgrade_cbr_pct"],
                project_data["risk_level"],
                project_data.get("prediction_status", "Pending"),
                json.dumps(project_data),
            ),
        )

        new_project_id = cursor.lastrowid
        conn.commit()

        return new_project_id

    except Exception:
        conn.rollback()
        raise
    
    finally:
        conn.close()

def get_all_projects():
    conn = get_connection()

    try:
        return pd.read_sql_query(
            """
            SELECT
                id,
                project_name,
                location,
                road_category,
                terrain_type,
                road_length_km,
                number_of_lanes,
                design_speed_kmph,
                aadt,
                subgrade_cbr_pct,
                risk_level,
                prediction_status,
                prediction_data,
                project_data,
                created_at
            FROM projects
            ORDER BY id DESC
            """,
            conn,
        )

    finally:
        conn.close()


def get_project_by_id(project_id): #no
    conn = get_connection()

    try:
        cursor = conn.cursor() 

        cursor.execute(
            """
            SELECT
                id,
                project_name,
                location,
                road_category,
                terrain_type,
                road_length_km,
                number_of_lanes,
                design_speed_kmph,
                aadt,
                subgrade_cbr_pct,
                risk_level,
                prediction_status,
                prediction_data,
                project_data,
                created_at
            FROM projects
            WHERE id = ?
            LIMIT 1
            """,
            (int(project_id),),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [description[0] for description in cursor.description]
        record = dict(zip(columns, row))

        # Return the full saved project input dictionary when available
        if record.get("project_data"):
            try:
                saved_project_data = json.loads(record["project_data"])
                saved_project_data["id"] = record["id"]
                saved_project_data["prediction_status"] = record["prediction_status"]
                saved_project_data["prediction_data"] = record["prediction_data"]
                saved_project_data["created_at"] = record["created_at"]
                return saved_project_data
            except (json.JSONDecodeError, TypeError):
                pass

        return record

    finally:
        conn.close()


def project_exists(project_name, location): #no
    conn = get_connection()
    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id
            FROM projects
            WHERE LOWER(TRIM(project_name)) = LOWER(TRIM(?))
              AND LOWER(TRIM(location)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (
                project_name.strip(),
                location.strip(),
            ),
        )
        return cursor.fetchone() is not None

    finally:
        conn.close()


def update_project_prediction(project_id, prediction_data):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        project_id = int(project_id)

        cursor.execute(
            """
            SELECT id
            FROM projects
            WHERE id = ?
            """,
            (project_id,),
        )

        existing_project = cursor.fetchone()

        if existing_project is None:
            raise RuntimeError(
                f"Project ID {project_id} does not exist in the active database."
            )

        cursor.execute(
            """
            UPDATE projects
            SET
                prediction_status = ?,
                prediction_data = ?
            WHERE id = ?
            """,
            (
                "Completed",
                json.dumps(prediction_data),
                project_id,
            ),
        )

        conn.commit()

        save_prediction_history(
            project_id,
            prediction_data,
        )

        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        

def delete_project(project_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()
        project_id = int(project_id)

        cursor.execute(
            """
            DELETE FROM prediction_history
            WHERE project_id = ?
            """,
            (project_id,),
        )

        cursor.execute(
            """
            DELETE FROM projects
            WHERE id = ?
            """,
            (project_id,),
        )

        deleted_rows = cursor.rowcount
        conn.commit()

        return deleted_rows > 0

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()
        
def delete_duplicate_projects() -> int:
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM projects
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM projects
                GROUP BY
                    LOWER(TRIM(project_name)),
                    LOWER(TRIM(location))
            )
            """
        )

        deleted_count = cursor.rowcount
        conn.commit()

        return deleted_count

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()