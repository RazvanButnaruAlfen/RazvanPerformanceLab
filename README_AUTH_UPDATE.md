# Supabase Auth update

This update changes Razvan Performance Lab from a shared app into a secure per-user app.

## What changes

Each person now creates their own account with:

- name
- email
- password

After sign-in, all workouts and bodyweight entries are tied to that user's Supabase Auth ID.

Supabase Row Level Security prevents one authenticated user from reading or changing another user's data.

## Files in this update

Replace / add:

```text
app.py
Components/auth_ui.py
Services/auth.py
Services/database.py
Pages/log_workout.py
supabase_schema.sql
.streamlit/secrets.toml.example
```

## Supabase setup

### 1. Configure Authentication

In your Supabase project, enable Email authentication.

You can decide whether email confirmation is required.

If email confirmation is enabled, a new user receives a confirmation email before they can sign in.

### 2. Run the new SQL schema

Open:

```text
supabase_schema.sql
```

and run it in the Supabase SQL Editor.

The SQL creates:

- `profiles`
- `workouts`
- `workout_sets`
- `bodyweight_entries`
- per-user Row Level Security policies
- a trigger that creates a profile when a new Auth account is created

### Existing old database

If you created the previous non-user tables but have no data worth keeping, use the optional DROP statements at the top of `supabase_schema.sql`, then execute the full script.

If you already have workout history you want to preserve, do not drop the tables. Migrate the existing rows to your Auth user ID first.

## Streamlit secrets

In Streamlit Community Cloud:

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_SUPABASE_ANON_OR_PUBLISHABLE_KEY"
```

Use only the public anon/publishable key.

Do not use the Supabase `service_role` key.

## User flow

```text
Open app
    ↓
Sign in / Create account
    ↓
Authenticated personal profile
    ↓
Log Workout | Progress | History | Body
    ↓
Sign out
```

Your friend can create a separate account in the same app. Their workout and bodyweight data remain separated from yours.
