import json
import pandas as pd

from src.database.db import get_connection

def project_exists(project_name, location):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM projects
        WHERE project_name = ? AND location = ?
        """,
        (project_name, location),
    )

    count = cursor.fetchone()[0]
    conn.close()

    return count > 0

def save_project(project_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO projects (
            project_name,
            location,
            road_category,
            project_type,
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            project_data["project_name"],
            project_data["location"],
            project_data["road_category"],
            project_data.get("project_type", "New Construction"),
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

    conn.commit()
    conn.close()


def get_all_projects():
    conn = get_connection()

    df = pd.read_sql_query(
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
            created_at,
            prediction_data
        FROM projects
        ORDER BY created_at DESC
        """,
        conn,
    )

    conn.close()
    return df


def get_project_by_id(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT project_data FROM projects WHERE id = ?",
        (project_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return json.loads(row[0])


def delete_project(project_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM projects WHERE id = ?",
        (project_id,),
    )

    conn.commit()
    conn.close()


def update_project(project_id, project_data):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE projects
        SET
            project_name = ?,
            location = ?,
            road_category = ?,
            terrain_type = ?,
            road_length_km = ?,
            number_of_lanes = ?,
            design_speed_kmph = ?,
            aadt = ?,
            subgrade_cbr_pct = ?,
            risk_level = ?,
            prediction_status = ?,
            project_data = ?
        WHERE id = ?
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
            project_id,
        ),
    )

    conn.commit()
    conn.close()
    

def update_project_prediction(project_id, prediction_data):
    import json

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE projects
        SET prediction_status = ?, prediction_data = ?
        WHERE id = ?
        """,
        (
            "Completed",
            json.dumps(prediction_data),
            project_id,
        ),
    )
    
    conn.commit()
    conn.close()
    save_prediction_history(project_id, prediction_data)
    
def delete_duplicate_projects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM projects
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM projects
            GROUP BY project_name, location
        )
    """)

    conn.commit()
    conn.close()
    
def save_prediction_history(project_id, prediction_data):
    import json

    conn = get_connection()
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
            project_id,
            json.dumps(prediction_data),
        ),
    )

    conn.commit()
    conn.close()


def get_prediction_history(project_id):
    import json
    import pandas as pd

    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT
            id,
            project_id,
            prediction_data,
            created_at
        FROM prediction_history
        WHERE project_id = ?
        ORDER BY created_at DESC
        """,
        conn,
        params=(project_id,),
    )

    conn.close()

    if df.empty:
        return df

    df["prediction_data"] = df["prediction_data"].apply(json.loads)

    return df