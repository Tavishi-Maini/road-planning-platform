from typing import Any

import pandas as pd

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

def save_project(project_data: dict[str, Any]) -> int:
    client = get_supabase_client()

    payload = project_data.copy()
    payload.setdefault("project_type", "New Construction")
    payload.setdefault("prediction_status", "Pending")

    response = (
        client.table(TABLE_NAME)
        .insert(payload)
        .execute()
    )

    if not response.data:
        raise RuntimeError("Supabase did not return the inserted project.")

    return int(response.data[0]["id"])


def get_all_projects() -> pd.DataFrame:
    client = get_supabase_client()

    response = (
        client.table(TABLE_NAME)
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return pd.DataFrame(response.data or [])


def get_project_by_id(project_id: int) -> dict[str, Any] | None:
    client = get_supabase_client()

    response = (
        client.table(TABLE_NAME)
        .select("*")
        .eq("id", project_id)
        .limit(1)
        .execute()
    )

    if not response.data:
        return None

    return response.data[0]


def project_exists(project_name: str, location: str) -> bool:
    client = get_supabase_client()

    response = (
        client.table(TABLE_NAME)
        .select("id")
        .eq("project_name", project_name)
        .eq("location", location)
        .limit(1)
        .execute()
    )

    return bool(response.data)


def update_project_prediction(
    project_id: int,
    predictions: dict[str, float],
) -> None:
    client = get_supabase_client()

    payload = {
        "total_cost_lakhs": predictions.get("total_cost"),
        "construction_duration_months": predictions.get(
            "construction_duration_months"
        ),
        "material_index": predictions.get("material_index"),
        "manpower_hours_per_km": predictions.get(
            "manpower_hours_per_km"
        ),
        "machinery_hours_per_km": predictions.get(
            "machinery_hours_per_km"
        ),
        "prediction_status": "Completed",
    }

    response = (
        client.table(TABLE_NAME)
        .update(payload)
        .eq("id", project_id)
        .execute()
    )

    if response.data is None:
        raise RuntimeError(
            f"Failed to update prediction for project {project_id}."
        )


def delete_project(project_id: int) -> None:
    client = get_supabase_client()

    response = (
        client.table(TABLE_NAME)
        .delete()
        .eq("id", project_id)
        .execute()
    )

    if response.data is None:
        raise RuntimeError(
            f"Failed to delete project {project_id}."
        )
        
def delete_duplicate_projects() -> int:
    """
    Deletes duplicate projects that have the same project_name and location.

    Keeps the newest record and removes older duplicates.
    Returns the number of deleted rows.
    """
    client = get_supabase_client()

    response = (
        client.table(TABLE_NAME)
        .select("id, project_name, location, created_at")
        .order("created_at", desc=True)
        .execute()
    )

    rows = response.data or []

    seen = set()
    duplicate_ids = []

    for row in rows:
        key = (
            str(row.get("project_name", "")).strip().lower(),
            str(row.get("location", "")).strip().lower(),
        )

        if key in seen:
            duplicate_ids.append(row["id"])
        else:
            seen.add(key)

    deleted_count = 0

    for project_id in duplicate_ids:
        delete_response = (
            client.table(TABLE_NAME)
            .delete()
            .eq("id", project_id)
            .execute()
        )

        if delete_response.data is not None:
            deleted_count += 1

    return deleted_count