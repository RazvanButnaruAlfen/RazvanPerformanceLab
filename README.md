# Razvan Performance Lab

Responsive Streamlit training tracker for desktop and mobile.

## Main navigation

The app uses horizontal tabs instead of the Streamlit sidebar:

- Log Workout
- Progress
- History
- Body

The sidebar is hidden.

## Responsive behavior

Desktop:
- Wide page layout
- Multiple columns where useful
- Full-width workout editor

Mobile:
- Tabs scroll horizontally when needed
- Columns stack vertically
- Buttons expand to full width
- Reduced page padding
- Data tables/editors can scroll horizontally
- Inputs use mobile-friendly sizing

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Cloud

Set the main file path to:

```text
app.py
```

For permanent storage, configure Supabase secrets in Streamlit Cloud:

```toml
[supabase]
url = "https://YOUR_PROJECT.supabase.co"
key = "YOUR_SUPABASE_ANON_KEY"
```

Run `supabase_schema.sql` once in the Supabase SQL Editor.
