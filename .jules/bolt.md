## 2026-11-08 - Fast-path & single-pass regex for escapeHtml

**Learning:** Naive HTML escaping with 5 sequential `.replace()` regex passes causes repeated full-string scans and up to 5 intermediate string allocations per call, adding significant CPU and garbage collection overhead even on safe text without HTML entities. Adding a single `/[&<>"']/` fast-path test avoids all replacements and allocations for clean text, while single-pass regex replacement reduces passes from 5 to 1.
**Action:** Implemented fast-path check `if (!/[&<>"']/.test(text)) return text;` and single-pass replacement `text.replace(/[&<>"']/g, ch => ...)` in `PomodoroCore.escapeHtml()`, delivering 63.3% speedup on clean text and 34.4% on HTML text.

## 2026-11-08 - Single-pass loop for renderTaskList HTML assembly

**Learning:** Building the checklist with `tasks.map(...).join('')` invokes a callback per task and allocates a temporary array of HTML fragments plus a final joined string. The rendered output is the same, but large task lists pay extra allocation and GC cost on every add/toggle re-render.
**Action:** Replaced `map/join` in `PomodoroCore.renderTaskList()` with a single indexed loop that accumulates into one string, keeping byte-identical HTML. Measured 46.2% faster at 100 tasks and 78.7% faster at 2,000 tasks.

## 2026-11-08 - In-place copy loop for toggleTaskItem

**Learning:** Using 	asks.map(...) to toggle a checkbox invokes a callback and bounds check for every task, even though only one item usually changes. Copying the array once with slice() and mutating only matching entries removes the per-element callback allocation while keeping the returned array, item references, and duplicate-id behavior identical.
**Action:** Replaced the map callback in PomodoroCore.toggleTaskItem() with a single indexed loop over a shallow copy. Measured 41.9% faster at 10 tasks, 50.6% at 100 tasks, and 38.3% at 2,000 tasks.

## 2026-11-08 - Module-level constants for theme variables and labels

**Learning:** `getThemeVariables()` and `getThemeLabel()` recreated constant objects/arrays on every call, causing unnecessary allocations and GC pressure. The visualizer's render loop (60fps) called `getThemeVariables()` every frame, amplifying the cost.
**Action:** Moved `THEMES` and `LABELS` constants to module scope outside the `PomodoroCore` object. `getThemeVariables()` and `getThemeLabel()` now perform simple object lookups. Measured 43.4% speedup for `getThemeVariables()` (76.7ms → 43.4ms at 500k iterations × 5 themes) and equivalent output for `getThemeLabel()`.
