# Exercise collapse + History grouping

Replace:

```text
Components/workout_form.py
Pages/workout_history.py
```

Changes:

1. Workout entry
- Each exercise is now a collapsible section.
- The current/latest exercise is expanded.
- When you press `Add exercise`, the previous exercise collapses and the new exercise opens.
- Add/remove set keeps the current exercise open.
- Existing values are preserved by the callback-based state handling from the previous fix.

2. History
- Sets are grouped by exercise.
- Each exercise gets its own heading and set table.
- History no longer visually interleaves all Set 1 rows, then all Set 2 rows, etc.
- Exercise order follows the order in which exercises were recorded.

No Supabase/database changes are required.
