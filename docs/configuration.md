# Configuration and glossary

[ภาษาไทย](configuration_TH.md) · **English** · Back to [README](../README.md)

## Settings
Change these in the Settings panel. Values are saved in the browser.

| Setting | Default | Allowed range |
|---|---|---|
| Focus duration (minutes) | 25 | 1–90 |
| Short break (minutes) | 5 | 1–30 |
| Long break (minutes) | 15 | 1–60 |
| Long break cadence (focus sessions) | 4 | 1–12 |
| Daily focus goal (minutes) | 120 | 1–1440 |

## Browser storage
All data stays in your browser's `localStorage`. Keys start with `cp_`, for example:

- `cp_theme`: selected theme
- `cp_streak`: current streak
- `cp_tasks`, `cp_mission_boards`: mission lists
- `cp_session_history`: session history

Clearing the site's data resets the app. Use the export button to keep a backup first.

## Glossary
| Term | Meaning |
|---|---|
| Focus session | One work interval of the timer |
| Cadence | The number of focus sessions before a long break |
| Streak | Consecutive days with at least one focus session |
| Mission board | A named list of tasks |
