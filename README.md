# ⚡ Cyberpunk Focus: Pomodoro Station

A neon sci-fi Pomodoro timer with a built-in ambient sound synthesizer. It runs in the browser with no build step and no external dependencies.

Live demo: https://okayokay101.github.io/cyberpunk-pomodoro/ · Test dashboard: https://okayokay101.github.io/cyberpunk-pomodoro/test.html

[ภาษาไทย](README_TH.md) · **English**

## Features
- **Pomodoro timer:** focus, short break, and long break. A long break comes after a set number of focus sessions.
- **Ambient sounds:** five sounds generated with the Web Audio API (Cyber Rain, Deep Space Hum, 40Hz Focus Wave, Server Fan, Cyber Storm). No audio files are downloaded.
- **Spectrum visualizer:** draws the live audio spectrum on a canvas.
- **Daily focus tracking:** a streak counter and today's focused minutes.
- **Mission list:** add tasks, tick them off, and keep several boards.
- **Four neon themes:** Cyan Matrix, Neon Pink, Night City Yellow, Emerald Hacker.
- **Data export:** an export button saves your data as a backup.

## Requirements
- A current desktop or mobile browser with Web Audio and `localStorage` support.
- For tests only: Node.js 20 and Python 3.12 (versions used in [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## Setup
```bash
git clone https://github.com/OkayOkay101/cyberpunk-pomodoro.git
cd cyberpunk-pomodoro
```
Open `index.html` in your browser. No install step is needed.

## Usage
| Key | Action |
|---|---|
| <kbd>Space</kbd> | Start or pause the timer |
| <kbd>R</kbd> | Reset the timer |
| <kbd>S</kbd> | Skip to the next session |
| <kbd>M</kbd> | Mute or unmute |
| <kbd>F</kbd> | Toggle fullscreen |

## Configuration
Set focus, break, and daily-goal durations in the Settings panel. All values and the glossary are on the [configuration page](docs/configuration.md). Data stays in your browser.

## Tests
```bash
node test-runner.js
python -m pip install -r requirements-dev.txt
python -m playwright install --with-deps chromium
python -m unittest discover -s tests -p "test_*.py"
python scripts/check_python_syntax.py
```
The browser test dashboard is [`test.html`](test.html).

## Project layout
- `index.html`: the app (markup, styles, and UI logic)
- `core.js`: shared logic for timing, keys, streaks, and labels
- `netrunner_leveling.js`: EXP and rank logic (tested, but not loaded by `index.html`)
- `service-worker.js`, `manifest.webmanifest`: cache the app shell for offline use and install support
- `test-runner.js`, `test.html`: Node and browser unit tests
- `tests/`: Python tests (unittest and Playwright)
- `scripts/`: repository check scripts
