## 2026-11-08 - Fast-path & single-pass regex for escapeHtml

**Learning:** Naive HTML escaping with 5 sequential `.replace()` regex passes causes repeated full-string scans and up to 5 intermediate string allocations per call, adding significant CPU and garbage collection overhead even on safe text without HTML entities. Adding a single `/[&<>"']/` fast-path test avoids all replacements and allocations for clean text, while single-pass regex replacement reduces passes from 5 to 1.
**Action:** Implemented fast-path check `if (!/[&<>"']/.test(text)) return text;` and single-pass replacement `text.replace(/[&<>"']/g, ch => ...)` in `PomodoroCore.escapeHtml()`, delivering 63.3% speedup on clean text and 34.4% on HTML text.

## 2026-11-08 - Single-pass loop for renderTaskList HTML assembly

**Learning:** Building the checklist with `tasks.map(...).join('')` invokes a callback per task and allocates a temporary array of HTML fragments plus a final joined string. The rendered output is the same, but large task lists pay extra allocation and GC cost on every add/toggle re-render.
**Action:** Replaced `map/join` in `PomodoroCore.renderTaskList()` with a single indexed loop that accumulates into one string, keeping byte-identical HTML. Measured 46.2% faster at 100 tasks and 78.7% faster at 2,000 tasks.
