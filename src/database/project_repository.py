from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd

from src.database.supabase_client import get_supabase_client


TABLE_NAME = "projects"


# These names must match the columns in your Supabase projects table.
PROJECT_INPUT_COLUMNS = [
    "project_name",
    "location",
    "road_category",
    "project_type",
    "project_owner",
    "terrain_type",
    "project_stage",
    "road_length_km",
    "carriageway_width_m",
    "number_of_lanes",
    "shoulder_width_m",
    "design_speed_kmph",
    "bridges_culverts",
    "aadt",
    "traffic_growth_rate_pct",
    "vdf",
    "pavement_type",
    "gsb_thickness_mm",
    "wmm_thickness_mm",
    "dbm_thickness_mm",
    "bc_thickness_mm",
    "concrete_thickness_mm",
    "soil_type",
    "subgrade_cbr_pct",
    "bitumen_grade",
    "aggregate_source_distance_km",
    "material_quality_index",
    "cement_grade",
    "land_acquisition_complexity",
    "rainfall_zone",
    "utility_shifting_required",
    "environmental_sensitivity",
    "water_body_distance_m",
    "soil_stabilization_required",
    "labour_rate_inr_day",
    "skilled_labour_pct",
    "machinery_availability_pct",
    "fuel_cost_inr_litre",
    "equipment_productivity_index",
    "contractor_experience_index",
    "risk_level",
    "contingency_pct",
    "escalation_pct",
    "prediction_status",
]


def _make_safe_value(value: Any) -> Any:
    """
    Convert NumPy, pandas and date values into data that Supabase can
    serialize safely.
    """
    if value is None:
        return None

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    # Converts values such as np.int64 and np.float64.
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (TypeError, ValueError):
            pass

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    return value


def _build_project_payload(
    project_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Keep only columns that exist in the Supabase projects table.
    """
    payload = {
        column: _make_safe_value(project_data[column])
        for column in PROJECT_INPUT_COLUMNS
        if column in project_data
    }

    payload.setdefault("project_type", "New Construction")
    payload.setdefault("prediction_status", "Pending")

    required_fields = [
        "project_name",
        "location",
        "road_category",
        "terrain_type",
    ]

    missing_fields = [
        field
        for field in required_fields
        if payload.get(field) is None
        or str(payload.get(field)).strip() == ""
    ]

    if missing_fields:
        raise ValueError(
            "Missing required project fields: "
            + ", ".join(missing_fields)
        )

    # Normalize text values.
    payload["project_name"] = str(
        payload["project_name"]
    ).strip()

    payload["location"] = str(
        payload["location"]
    ).strip()

    payload["road_category"] = str(
        payload["road_category"]
    ).strip()

    payload["terrain_type"] = str(
        payload["terrain_type"]
    ).strip()

    return payload


def _prediction_value(
    prediction_data: dict[str, Any],
    *possible_keys: str,
) -> float:
    """
    Read a prediction while supporting both model keys and database keys.
    """
    for key in possible_keys:
        if key in prediction_data:
            value = _make_safe_value(prediction_data[key])

            if value is None:
                continue

            try:
                return float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Prediction value for {key!r} is not numeric: "
                    f"{value!r}"
                ) from exc

    raise KeyError(
        "Prediction is missing the required value. "
        f"Supported keys: {possible_keys}. "
        f"Available keys: {list(prediction_data.keys())}"
    )


def save_project(project_data: dict[str, Any]) -> int:
    """
    Save a project permanently in Supabase and return its generated ID.
    """
    supabase = get_supabase_client()
    payload = _build_project_payload(project_data)

    try:
        response = (
            supabase.table(TABLE_NAME)
            .insert(payload)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to save project to Supabase: {exc}"
        ) from exc

    if not response.data:
        raise RuntimeError(
            "Supabase did not return the saved project."
        )

    return int(response.data[0]["id"])


def get_all_projects() -> pd.DataFrame:
    """
    Return all projects, newest first.
    """
    supabase = get_supabase_client()

    try:
        response = (
            supabase.table(TABLE_NAME)
            .select("*")
            .order("id", desc=True)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to load projects from Supabase: {exc}"
        ) from exc

    records = response.data or []

    if not records:
        return pd.DataFrame()

    return pd.DataFrame(records)


def get_project_by_id(
    project_id: int,
) -> dict[str, Any] | None:
    """
    Return one complete project from Supabase.
    """
    supabase = get_supabase_client()
    project_id = int(project_id)

    try:
        response = (
            supabase.table(TABLE_NAME)
            .select("*")
            .eq("id", project_id)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to load project ID {project_id}: {exc}"
        ) from exc

    if not response.data:
        return None

    return dict(response.data[0])


def project_exists(
    project_name: str,
    location: str,
) -> bool:
    """
    Check whether the same project name and location already exist.
    """
    supabase = get_supabase_client()

    normalized_name = str(project_name).strip()
    normalized_location = str(location).strip()

    if not normalized_name or not normalized_location:
        return False

    try:
        response = (
            supabase.table(TABLE_NAME)
            .select("id,project_name,location")
            .ilike("project_name", normalized_name)
            .ilike("location", normalized_location)
            .limit(10)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to check whether project exists: {exc}"
        ) from exc

    for row in response.data or []:
        saved_name = str(
            row.get("project_name", "")
        ).strip().casefold()

        saved_location = str(
            row.get("location", "")
        ).strip().casefold()

        if (
            saved_name == normalized_name.casefold()
            and saved_location == normalized_location.casefold()
        ):
            return True

    return False


def update_project_prediction(
    project_id: int,
    prediction_data: dict[str, Any],
) -> bool:
    """
    Save the five prediction outputs in their individual Supabase columns.

    The deployed models currently use these keys:
        total_cost
        duration
        material_index
        manpower_hours_per_km
        machinery_hours_per_km
    """
    supabase = get_supabase_client()
    project_id = int(project_id)

    payload = {
        "prediction_status": "Completed",

        "total_cost_lakhs": _prediction_value(
            prediction_data,
            "total_cost_lakhs",
            "total_cost",
        ),

        "construction_duration_months": _prediction_value(
            prediction_data,
            "construction_duration_months",
            "duration",
        ),

        "material_index": _prediction_value(
            prediction_data,
            "material_index",
        ),

        "manpower_hours_per_km": _prediction_value(
            prediction_data,
            "manpower_hours_per_km",
        ),

        "machinery_hours_per_km": _prediction_value(
            prediction_data,
            "machinery_hours_per_km",
        ),

        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    try:
        existing = (
            supabase.table(TABLE_NAME)
            .select("id")
            .eq("id", project_id)
            .limit(1)
            .execute()
        )

        if not existing.data:
            raise RuntimeError(
                f"Project ID {project_id} does not exist in Supabase."
            )

        response = (
            supabase.table(TABLE_NAME)
            .update(payload)
            .eq("id", project_id)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to save prediction for project "
            f"ID {project_id}: {exc}"
        ) from exc

    if not response.data:
        raise RuntimeError(
            f"No project was updated for ID {project_id}."
        )

    return True


def get_prediction_history() -> pd.DataFrame:
    """
    Return all completed projects, ordered from newest to oldest.

    This represents the latest saved prediction for every project.
    """
    projects = get_all_projects()

    if projects.empty:
        return pd.DataFrame()

    if "prediction_status" not in projects.columns:
        return pd.DataFrame()

    completed = projects[
        projects["prediction_status"]
        .astype(str)
        .str.strip()
        .str.casefold()
        == "completed"
    ].copy()

    if completed.empty:
        return completed

    if "created_at" in completed.columns:
        completed["created_at"] = pd.to_datetime(
            completed["created_at"],
            errors="coerce",
            utc=True,
        )

        completed = completed.sort_values(
            by="created_at",
            ascending=False,
        )

    return completed.reset_index(drop=True)


def save_prediction_history(
    project_id: int,
    prediction_data: dict[str, Any],
) -> None:
    """
    Compatibility function.

    Your current Supabase schema has no separate prediction_history table.
    The latest prediction is already saved in the projects table by
    update_project_prediction().

    Keep this function so old imports do not break.
    """
    return None


def delete_project(project_id: int) -> bool:
    """
    Delete one project from Supabase.
    """
    supabase = get_supabase_client()
    project_id = int(project_id)

    try:
        response = (
            supabase.table(TABLE_NAME)
            .delete()
            .eq("id", project_id)
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to delete project ID {project_id}: {exc}"
        ) from exc

    return bool(response.data)


def delete_duplicate_projects() -> int:
    """
    Delete older projects having the same normalized name and location.

    Keeps the project with the highest ID.
    """
    projects = get_all_projects()

    if projects.empty:
        return 0

    required_columns = {
        "id",
        "project_name",
        "location",
    }

    if not required_columns.issubset(projects.columns):
        return 0

    sorted_projects = projects.sort_values(
        by="id",
        ascending=False,
    )

    seen: set[tuple[str, str]] = set()
    duplicate_ids: list[int] = []

    for row in sorted_projects.itertuples():
        key = (
            str(row.project_name).strip().casefold(),
            str(row.location).strip().casefold(),
        )

        if key in seen:
            duplicate_ids.append(int(row.id))
        else:
            seen.add(key)

    deleted_count = 0

    for project_id in duplicate_ids:
        if delete_project(project_id):
            deleted_count += 1

    return deleted_count