from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

DB_PATH = Path("Data/razvan_performance_lab.db")


def _supabase_client():
    """Return a Supabase client when Streamlit secrets are configured."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
    except Exception:
        return None

    if not url or not key:
        return None

    from supabase import create_client
    return create_client(url, key)


def using_supabase() -> bool:
    return _supabase_client() is not None


def _sqlite_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Create local SQLite tables. Supabase tables are created with supabase_schema.sql."""
    if using_supabase():
        return

    with closing(_sqlite_connection()) as con:
        cur = con.cursor()

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_date TEXT NOT NULL,
                workout_name TEXT,
                notes TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS workout_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_id INTEGER NOT NULL,
                exercise TEXT NOT NULL,
                set_number INTEGER NOT NULL,
                weight_kg REAL NOT NULL,
                reps INTEGER NOT NULL,
                rir REAL,
                FOREIGN KEY(workout_id) REFERENCES workouts(id)
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bodyweight_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_date TEXT NOT NULL UNIQUE,
                weight_kg REAL NOT NULL,
                notes TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        con.commit()


def save_workout(
    workout_date: date,
    workout_name: str,
    notes: str,
    sets: list[dict[str, Any]],
) -> int:
    client = _supabase_client()
    created_at = datetime.utcnow().isoformat()

    if client:
        workout_payload = {
            "workout_date": workout_date.isoformat(),
            "workout_name": workout_name or None,
            "notes": notes or None,
            "created_at": created_at,
        }
        workout_result = client.table("workouts").insert(workout_payload).execute()
        workout_id = workout_result.data[0]["id"]

        rows = []
        for row in sets:
            rows.append(
                {
                    "workout_id": workout_id,
                    "exercise": row["exercise"],
                    "set_number": int(row["set_number"]),
                    "weight_kg": float(row["weight_kg"]),
                    "reps": int(row["reps"]),
                    "rir": None if row.get("rir") in ("", None) else float(row["rir"]),
                }
            )

        client.table("workout_sets").insert(rows).execute()
        return int(workout_id)

    init_db()
    with closing(_sqlite_connection()) as con:
        cur = con.cursor()
        cur.execute(
            """
            INSERT INTO workouts (workout_date, workout_name, notes, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (workout_date.isoformat(), workout_name or None, notes or None, created_at),
        )
        workout_id = cur.lastrowid

        cur.executemany(
            """
            INSERT INTO workout_sets
            (workout_id, exercise, set_number, weight_kg, reps, rir)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    workout_id,
                    row["exercise"],
                    int(row["set_number"]),
                    float(row["weight_kg"]),
                    int(row["reps"]),
                    None if row.get("rir") in ("", None) else float(row["rir"]),
                )
                for row in sets
            ],
        )
        con.commit()
        return int(workout_id)


def get_workout_sets() -> pd.DataFrame:
    client = _supabase_client()
    if client:
        workouts = client.table("workouts").select("*").order("workout_date", desc=True).execute().data
        sets = client.table("workout_sets").select("*").execute().data
        if not workouts or not sets:
            return pd.DataFrame()

        w = pd.DataFrame(workouts)
        s = pd.DataFrame(sets)
        return s.merge(
            w[["id", "workout_date", "workout_name", "notes"]],
            left_on="workout_id",
            right_on="id",
            suffixes=("", "_workout"),
        ).drop(columns=["id_workout"], errors="ignore")

    init_db()
    with closing(_sqlite_connection()) as con:
        return pd.read_sql_query(
            """
            SELECT
                ws.id,
                ws.workout_id,
                w.workout_date,
                w.workout_name,
                w.notes,
                ws.exercise,
                ws.set_number,
                ws.weight_kg,
                ws.reps,
                ws.rir
            FROM workout_sets ws
            JOIN workouts w ON w.id = ws.workout_id
            ORDER BY w.workout_date DESC, ws.workout_id DESC, ws.id ASC
            """,
            con,
        )


def get_workouts() -> pd.DataFrame:
    client = _supabase_client()
    if client:
        data = client.table("workouts").select("*").order("workout_date", desc=True).execute().data
        return pd.DataFrame(data)

    init_db()
    with closing(_sqlite_connection()) as con:
        return pd.read_sql_query(
            "SELECT * FROM workouts ORDER BY workout_date DESC, id DESC",
            con,
        )


def save_bodyweight(entry_date: date, weight_kg: float, notes: str = "") -> None:
    client = _supabase_client()
    payload = {
        "entry_date": entry_date.isoformat(),
        "weight_kg": float(weight_kg),
        "notes": notes or None,
        "created_at": datetime.utcnow().isoformat(),
    }

    if client:
        client.table("bodyweight_entries").upsert(
            payload, on_conflict="entry_date"
        ).execute()
        return

    init_db()
    with closing(_sqlite_connection()) as con:
        con.execute(
            """
            INSERT INTO bodyweight_entries (entry_date, weight_kg, notes, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(entry_date) DO UPDATE SET
                weight_kg = excluded.weight_kg,
                notes = excluded.notes,
                created_at = excluded.created_at
            """,
            (
                payload["entry_date"],
                payload["weight_kg"],
                payload["notes"],
                payload["created_at"],
            ),
        )
        con.commit()


def get_bodyweight_entries() -> pd.DataFrame:
    client = _supabase_client()
    if client:
        data = (
            client.table("bodyweight_entries")
            .select("*")
            .order("entry_date", desc=False)
            .execute()
            .data
        )
        return pd.DataFrame(data)

    init_db()
    with closing(_sqlite_connection()) as con:
        return pd.read_sql_query(
            "SELECT * FROM bodyweight_entries ORDER BY entry_date ASC",
            con,
        )
