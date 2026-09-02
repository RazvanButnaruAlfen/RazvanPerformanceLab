# Razvan Performance Lab

Personal Streamlit app for tracking bodybuilding, strength progression, conditioning-related training data, and weekly bodyweight.

## Included in v1

- Log workouts set by set
- Weight, reps and optional RIR
- Workout history
- Estimated 1RM trend
- Session training-volume trend
- Simple next-session progression suggestion
- Weekly bodyweight logging
- Bodyweight trend and check-in reminder
- Local SQLite mode for development
- Supabase support for persistent Streamlit Cloud storage

## Repository structure

```text
RazvanPerformanceLab/
├── app.py
├── Components/
│   ├── charts.py
│   ├── metrics.py
│   └── workout_form.py
├── Data/
│   └── exercises.json
├── Pages/
│   ├── 1_Log_Workout.py
│   ├── 2_Progress.py
│   ├── 3_Workout_History.py
│   └── 4_Body_Tracking.py
├── Services/
│   ├── analytics.py
│   ├── database.py
│   └── progression.py
├── .streamlit/
│   └── secrets.toml.example
├── .gitignore
├── requirements.txt
└── supabase_schema.sql
```

## Run locally

Create a virtual environment, install dependencies and launch Streamlit:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Without Supabase credentials the app automatically uses:

```text
Data/razvan_performance_lab.db
```

This is convenient for local testing.

## Persistent data on Streamlit Community Cloud

The filesystem of a deployed Streamlit app should not be treated as permanent storage. Use Supabase for your real workout history.

### 1. Create a Supabase project

Create a project in Supabase.

### 2. Create the tables

Open the Supabase SQL Editor and run the contents of:

```text
supabase_schema.sql
```

### 3. Add Streamlit secrets

In Streamlit Community Cloud open your app's settings and add:

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_SUPABASE_ANON_KEY"
```

Do not commit your real key in `.streamlit/secrets.toml`.

### 4. Deploy

Connect Streamlit Community Cloud to this GitHub repository and set:

```text
Main file path: app.py
```

## First useful upgrade ideas

- Workout templates (Push / Pull / Legs, Upper / Lower, etc.)
- Previous-session values shown while logging
- Rep PR and load PR detection
- Exercise-specific rep ranges
- More advanced progression rules
- Conditioning sessions
- Waist and other body measurements
- Dashboard combining bodyweight and strength trends
- Authentication if the app is ever used by more than one person
