from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd

from Services.auth import current_user, get_supabase_client


def _user_id() -> str:
    user = current_user()
    if not user:
        raise RuntimeError("You must be signed in.")
    return str(user.id)


def using_supabase() -> bool:
    return True


def init_db() -> None:
    return


def save_workout(
    workout_date: date,
    workout_name: str,
    notes: str,
    sets: list[dict[str, Any]],
) -> int:
    client = get_supabase_client()
    user_id = _user_id()

    workout_payload = {
        "user_id": user_id,
        "workout_date": workout_date.isoformat(),
        "workout_name": workout_name or None,
        "notes": notes or None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    workout_result = client.table("workouts").insert(workout_payload).execute()
    workout_id = workout_result.data[0]["id"]

    rows = [
        {
            "workout_id": workout_id,
            "exercise": row["exercise"],
            "set_number": int(row["set_number"]),
            "weight_kg": float(row["weight_kg"]),
            "reps": int(row["reps"]),
            "rir": None if row.get("rir") in ("", None) else float(row["rir"]),
        }
        for row in sets
    ]

    client.table("workout_sets").insert(rows).execute()
    return int(workout_id)


def update_workout(
    workout_id: int,
    workout_date: date,
    workout_name: str,
    notes: str,
    sets: list[dict[str, Any]],
) -> None:
    client = get_supabase_client()
    user_id = _user_id()

    # The user_id filter plus RLS prevents editing another user's workout.
    (
        client.table("workouts")
        .update(
            {
                "workout_date": workout_date.isoformat(),
                "workout_name": workout_name or None,
                "notes": notes or None,
            }
        )
        .eq("id", workout_id)
        .eq("user_id", user_id)
        .execute()
    )

    # RLS on workout_sets verifies ownership through the parent workout.
    client.table("workout_sets").delete().eq("workout_id", workout_id).execute()

    rows = [
        {
            "workout_id": workout_id,
            "exercise": row["exercise"],
            "set_number": int(row["set_number"]),
            "weight_kg": float(row["weight_kg"]),
            "reps": int(row["reps"]),
            "rir": None if row.get("rir") in ("", None) else float(row["rir"]),
        }
        for row in sets
    ]

    if rows:
        client.table("workout_sets").insert(rows).execute()


def get_workout_sets() -> pd.DataFrame:
    client = get_supabase_client()
    user_id = _user_id()

    workouts = (
        client.table("workouts")
        .select("id, workout_date, workout_name, notes")
        .eq("user_id", user_id)
        .order("workout_date", desc=True)
        .execute()
        .data
    )

    if not workouts:
        return pd.DataFrame()

    workout_ids = [str(row["id"]) for row in workouts]

    sets = (
        client.table("workout_sets")
        .select("*")
        .in_("workout_id", workout_ids)
        .execute()
        .data
    )

    if not sets:
        return pd.DataFrame()

    w = pd.DataFrame(workouts)
    s = pd.DataFrame(sets)

    merged = s.merge(
        w,
        left_on="workout_id",
        right_on="id",
        suffixes=("", "_workout"),
    ).drop(columns=["id_workout"], errors="ignore")

    return merged.sort_values(
        ["workout_date", "workout_id", "set_number"],
        ascending=[False, False, True],
    )


def save_bodyweight(
    entry_date: date,
    weight_kg: float,
    notes: str = "",
) -> None:
    client = get_supabase_client()
    user_id = _user_id()

    payload = {
        "user_id": user_id,
        "entry_date": entry_date.isoformat(),
        "weight_kg": float(weight_kg),
        "notes": notes or None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    (
        client.table("bodyweight_entries")
        .upsert(payload, on_conflict="user_id,entry_date")
        .execute()
    )


def get_bodyweight_entries() -> pd.DataFrame:
    client = get_supabase_client()
    user_id = _user_id()

    data = (
        client.table("bodyweight_entries")
        .select("*")
        .eq("user_id", user_id)
        .order("entry_date", desc=False)
        .execute()
        .data
    )

    return pd.DataFrame(data)


def get_user_exercises() -> list[str]:
    client = get_supabase_client()
    user_id = _user_id()

    data = (
        client.table("user_exercises")
        .select("name")
        .eq("user_id", user_id)
        .order("name")
        .execute()
        .data
    )

    return [row["name"] for row in data]


def add_user_exercise(name: str) -> None:
    clean_name = " ".join(name.strip().split())
    if not clean_name:
        raise ValueError("Exercise name cannot be empty.")

    client = get_supabase_client()
    user_id = _user_id()

    existing = get_user_exercises()
    if clean_name.casefold() in {item.casefold() for item in existing}:
        return

    (
        client.table("user_exercises")
        .insert(
            {
                "user_id": user_id,
                "name": clean_name,
            }
        )
        .execute()
    )
