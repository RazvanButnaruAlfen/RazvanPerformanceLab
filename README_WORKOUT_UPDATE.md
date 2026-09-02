# Workout workflow update

This update adds three requested features.

## 1. Fresh workout form after save

After saving a workout, the Log Workout form is reset automatically.

The app reruns and returns to a clean form ready for the next session. A success message confirms that the workout was saved.

## 2. Edit previously recorded workouts

Open the History tab and expand a workout.

You can change:

- workout date
- workout name
- exercise
- set number
- weight
- reps
- RIR
- notes

Press **Save changes** to replace the stored details for that workout.

## 3. Add exercises from inside the app

The Log Workout tab now has an **Add a new exercise** section.

Type an exercise name.

- If it already exists, the app tells you.
- If it does not exist, the app offers an Add button.
- Added exercises are stored in Supabase for the signed-in user.
- They immediately become available in the exercise dropdown.
- A friend's custom exercises remain separate from yours.

## Database update

Run `supabase_schema.sql` in Supabase SQL Editor.

If your current Supabase Auth schema is already installed, the only new database object required is the `user_exercises` table and its policies. That section is clearly marked near the bottom of the SQL file.
