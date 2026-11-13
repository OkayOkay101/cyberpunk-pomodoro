## 2026-11-08 - Fast-path & single-pass regex for escapeHtml

**Learning:** Naive HTML escaping with 5 sequential `.replace()` regex passes causes repeated full-string scans and up to 5 intermediate string allocations per call, adding significant CPU and garbage collection overhead even on safe text without HTML entities. Adding a single `/[&<>"']/` fast-path test avoids all replacements and allocations for clean text, while single-pass regex replacement reduces passes from 5 to 1.
**Action:** Implemented fast-path check `if (!/[&<>"']/.test(text)) return text;` and single-pass replacement `text.replace(/[&<>"']/g, ch => ...)` in `PomodoroCore.escapeHtml()`, delivering 63.3% speedup on clean text and 34.4% on HTML text.

## 2026-11-08 - Single-pass loop for renderTaskList HTML assembly

**Learning:** Building the checklist with `tasks.map(...).join('')` invokes a callback per task and allocates a temporary array of HTML fragments plus a final joined string. The rendered output is the same, but large task lists pay extra allocation and GC cost on every add/toggle re-render.
**Action:** Replaced `map/join` in `PomodoroCore.renderTaskList()` with a single indexed loop that accumulates into one string, keeping byte-identical HTML. Measured 46.2% faster at 100 tasks and 78.7% faster at 2,000 tasks.

## 2026-11-08 - In-place copy loop for toggleTaskItem

**Learning:** Using 	tasks.map(...) to toggle a checkbox invokes a callback and bounds check for every task, even though only one item usually changes. Copying the array once with slice() and mutating only matching entries removes the per-element callback allocation while keeping the returned array, item references, and duplicate-id behavior identical.
**Action:** Replaced the map callback in PomodoroCore.toggleTaskItem() with a single indexed loop over a shallow copy. Measured 41.9% faster at 10 tasks, 50.6% at 100 tasks, and 38.3% at 2,000 tasks.

## 2026-11-08 - Module-level constants for theme variables and labels

**Learning:** `getThemeVariables()` and `getThemeLabel()` recreated constant objects/arrays on every call, causing unnecessary allocations and GC pressure. The visualizer's render loop (60fps) called `getThemeVariables()` every frame, amplifying the cost.
**Action:** Moved `THEMES` and `LABELS` constants to module scope outside the `PomodoroCore` object. `getThemeVariables()` and `getThemeLabel()` now perform simple object lookups. Measured 43.4% speedup for `getThemeVariables()` (76.7ms → 43.4ms at 500k iterations × 5 themes) and equivalent output for `getThemeLabel()`.

## 2026-11-08 - Complete module-level constants optimization for theme functions

**Learning:** The previous optimization moved `THEMES` and `LABELS` to module scope but `getThemeVariables()` and `getThemeLabel()` still called `Object.keys()` on every invocation, recreating the valid keys arrays. The visualizer (60fps) and settings UI call these functions frequently.
**Action:** Pre-computed `VALID_THEMES` and `VALID_LABELS` as module-level constants. Functions now only do a simple array lookup and object property access. Measured 67.0% speedup for `getThemeVariables()` (17.7ms → 5.8ms at 500k iters) and 52.9% for `getThemeLabel()` (12.6ms → 5.9ms at 500k iters).

## 2026-11-08 - Fast-path dangerous key check for deserializeConfig

**Learning:** `deserializeConfig()` recreated a `dangerousKeys` array and used `Array.includes()` (O(n)) for every key in the parsed config object on every call, adding allocation and linear lookup overhead. The common case (valid config without dangerous keys) paid this cost despite no prototype pollution risk.
**Action:** Moved `DANGEROUS_KEYS` to a module-level `Set` for O(1) lookup. Added a fast-path check that scans keys once for dangerous keys; if none found, merges with a single spread `{ ...defaults, ...parsed }` avoiding an intermediate sanitized object. If dangerous keys exist, falls back to filtered merge. Measured 29.8% speedup for valid object (293.8ms → 206.1ms at 500k iters) and 29.0% for object with extra keys (425.8ms → 302.5ms at 500k iters), while preserving prototype pollution protection.

## 2026-11-08 - Pre-computed lookup table for formatTime

**Learning:** Formatting minutes and seconds using `String(mins).padStart(2, '0')` and `String(secs).padStart(2, '0')` incurs multiple number-to-string conversions, method calls, and intermediate string allocations on every timer tick (up to 5 allocations per call). Using a pre-computed 2-digit lookup array (`PAD_TWO`) at module scope eliminates `.padStart()` calls and intermediate conversions for standard durations.
**Action:** Created module-level `PAD_TWO` lookup array (00..99) and updated `PomodoroCore.formatTime()` to use direct indexing `mins < 100 ? PAD_TWO[mins] : String(mins)` and `mStr + ':' + PAD_TWO[secs]`. Measured 82.3% speedup on typical 1499s timer workload (17.69ms → 3.12ms at 1M iters) and 68.5% on mixed duration workload (34.36ms → 10.83ms at 1M iters) while preserving exact output equality for all edge cases.


## 2026-11-08 - Module-level constants for formatTabLabel

**Learning:** Recreating static label dictionaries inside `formatTabLabel` (`{ focus: 'FOCUS', shortBreak: 'SHORT', longBreak: 'LONG' }`) causes repeated object allocations and garbage collection overhead on every tab label format or render cycle.
**Action:** Extracted `TAB_LABELS` to module scope outside `PomodoroCore`. `formatTabLabel()` now performs direct property access on `TAB_LABELS[mode] || 'FOCUS'`. Measured 86.9% speedup on standard tab cycles (36.95ms → 4.84ms at 3,000,000 calls) and 89.4% on mixed inputs (52.52ms → 5.56ms at 4,000,000 calls) with zero temporary object allocations.


## 2026-11-08 - Eliminate Date object allocations in calculateStreak

**Learning:** `calculateStreak()` instantiated two `new Date()` instances on every call to parse `lastDateStr` and `todayStr` and calculate day differences, creating unnecessary heap objects and GC pressure. Using native `Date.parse()` avoids intermediate `Date` object allocations while returning identical millisecond timestamps. Reusing a module-level `MS_PER_DAY` constant eliminates repeated arithmetic evaluation.
**Action:** Updated `PomodoroCore.calculateStreak()` to compute time differences via `Date.parse()` and `MS_PER_DAY` (86,400,000 ms), with graceful fallback for non-string timestamps. Measured 54.5% speedup on consecutive day streaks (161.47ms → 73.50ms at 500k iterations) and 50.1% on mixed date workloads (144.23ms → 71.90ms at 500k iterations) with 100% exact equality across all edge cases.

## 2026-11-08 - Pre-computed lookup table for formatSessionLabel

**Learning:** `formatSessionLabel()` used `String(validCycle).padStart(2, '0')` for zero-padding cycle numbers, incurring number-to-string conversion, method call, and intermediate string allocation on every session label format. The existing module-level `PAD_TWO` lookup array (00..99) from the `formatTime` optimization can be reused for cycles 1-99 (the vast majority of cases), eliminating `.padStart()` overhead.
**Action:** Updated `PomodoroCore.formatSessionLabel()` to use `PAD_TWO[validCycle]` for cycles < 100 with fallback to `String(validCycle)` for 100+. Measured 50.7% speedup on typical cycles 1-99 (30.6ms → 15.1ms at 3M iterations) and 46.4% on mixed cycles 1-999 (39.6ms → 21.2ms at 3M iterations) with 100% exact output equality across all edge cases.


## 2026-11-08 - Eliminate duplicate Date allocation and padStart in getLocalDateString

**Learning:** `getLocalDateString()` used a default parameter `date = new Date()` and immediately instantiated a second `new Date(date)`, causing redundant heap object allocations even on routine calls. Additionally, formatting month and day with `String().padStart(2, '0')` incurred repeated number-to-string conversions, method dispatch, and temporary string allocations. Using a single `new Date()` allocation, avoiding re-wrapping existing `Date` instances, and reusing the pre-computed `PAD_TWO` lookup table eliminates unnecessary object creations and string formatting overhead.
**Action:** Updated `PomodoroCore.getLocalDateString()` to allocate `new Date()` only when needed, reuse valid `Date` objects directly without re-instantiation, and format 2-digit month and day via `PAD_TWO`. Measured 37.3% speedup on no-args calls (193.00ms → 121.11ms at 1M iters), 83.0% on existing Date instances (100.32ms → 17.03ms at 1M iters), and 33.3% on mixed inputs with 100% exact equality across all edge cases.


## 2026-11-08 - Fast-path tag check and KEY_ACTIONS lookup for resolveKeyboardAction

**Learning:** `resolveKeyboardAction()` unconditionally called `targetTagName.toUpperCase()` on every keypress event across the page, causing unnecessary temporary string allocations even when the active element was already uppercase (`BODY`, `BUTTON`, `DIV`) or irrelevant. Additionally, evaluating up to 9 sequential `if` string comparisons on every keystroke added linear dispatch overhead for navigation and unmapped keys.
**Action:** Implemented a fast-path tag check that bypasses `.toUpperCase()` unless `targetTagName` length is 5 or 8, and extracted keyboard shortcuts to a module-level `KEY_ACTIONS` dictionary with `null` prototype (`Object.create(null)`). Measured 64.1% speedup on common UI keypresses (322.8ms → 115.9ms at 10M calls) and 54.2% on mixed exhaustive cases (639.0ms → 292.9ms at 21M calls) with 100% exact output equality across all edge cases.


## 2026-11-09 - Fast-path numeric check and lookup table for volume formatting

**Learning:** `clampVolume()` unconditionally passed `vol` through `parseFloat()`, which in JavaScript engines causes numeric values to be coerced into temporary strings before parsing them back into floats, incurring garbage collection and allocation overhead on every slider drag and volume check. Furthermore, `formatVolumePercent()` repeatedly performed number-to-string conversions and template allocations (`${...}%`), while `getVolumeIcon()` unnecessarily evaluated `clampVolume()` even when `isMuted` was true.
**Action:** Implemented numeric fast-path `typeof vol === 'number' ? vol : parseFloat(vol)` with direct ternary bounds check in `PomodoroCore.clampVolume()`. Extracted module-level `PERCENT_LOOKUP` array (0%..100%) for `PomodoroCore.formatVolumePercent()`, and added short-circuit `if (isMuted) return '🔇'` in `PomodoroCore.getVolumeIcon()`. Measured 63.1% speedup on `clampVolume` alone (13.67ms → 5.04ms at 2M iters), 45.1% speedup on volume slider interactions (26.44ms → 14.51ms at 2M iters), and 44.4% on mixed volume states with 100% exact equality across all edge cases.


## 2026-11-09 - Fast-path and pre-computed lookup tables for HUD stats badges

**Learning:** `formatStreakBadge()` and `formatFocusTimeBadge()` unconditionally passed numeric values to `parseInt()`, which coerces numbers to temporary strings in JavaScript engines before parsing them back into integers. Additionally, every invocation assembled dynamic template literals (``⚡ STREAK: ${valid} DAY${valid > 1 ? 'S' : ''}`` and ``🎯 ${valid} MINS TODAY``), creating new heap string allocations on each stats HUD refresh. Using a numeric fast-path avoids `parseInt` string coercion, while pre-computed module-level lookup tables (`STREAK_BADGES` and `FOCUS_BADGES`) eliminate string allocations for all standard streak (1..100) and focus duration (0..1440 mins) ranges.
**Action:** Implemented numeric fast-paths and module-level `STREAK_BADGES` (0..100) and `FOCUS_BADGES` (0..1440) lookup arrays in `core.js`. Measured 51.9% speedup on routine stats HUD synchronization (31.92ms → 15.35ms at 3M iterations), 46.6% speedup on `formatStreakBadge` alone (14.72ms → 7.87ms), and 42.4% speedup on `formatFocusTimeBadge` alone (18.81ms → 10.85ms) with 100% exact equality across all edge cases.


## 2026-11-09 - Early key check, switch dispatch, and numeric fast-path for getNextTabIndex

**Learning:** `getNextTabIndex()` unconditionally executed `parseInt()` on both `totalTabs` and `currentIndex` upon every keystroke within the tab container, causing number-to-string coercion and string parsing overhead even when given native numeric values (such as `tabs.length` and `tabs.indexOf()`). Furthermore, inspecting up to four sequential `if` conditions on unhandled or non-navigation keystrokes (such as `Tab`, `Enter`, `Space`) created redundant branching and parsing overhead. Early-exiting unhandled keys and using integer fast-paths with V8-optimized `switch(key)` dispatch avoids string coercion and redundant branches.
**Action:** Implemented early navigation key validation and integer fast-path checks using bitwise truncation (`| 0`) alongside `switch(key)` branch dispatch in `PomodoroCore.getNextTabIndex()`. Measured 57.6% speedup on routine arrow navigation (14.17ms → 6.01ms at 5M iterations), 55.3% on `ArrowRight` forward cycling (13.12ms → 5.87ms), 54.2% on `Home`/`End` boundary jumps (14.57ms → 6.67ms), and 56.9% on unhandled keys with 100% exact equality verified across 26,400 test cases.


## 2026-11-09 - Fast-path and pre-computed lookup table for session completion notifications

**Learning:** `getSessionNotification()` dynamically allocated a new notification object and constructed an interpolated Thai template string (`` `จบ Session ${validCycle} เรียบร้อยแล้ว ได้เวลาพักผ่อน!` ``) upon every focus session completion, creating unnecessary heap object churn and garbage collection overhead. In addition, `parseCycleCount()` unconditionally called `parseInt()`, which coerces native JavaScript numbers into temporary strings before parsing them back into integers. Because break notifications already reused a frozen module-level constant (`BREAK_NOTIFICATION`), pre-computing standard focus notifications (cycles 1..100) in a frozen `FOCUS_NOTIFICATIONS` array and fast-pathing finite numbers in `parseCycleCount()` eliminates heap object allocations and string coercion entirely.
**Action:** Implemented numeric fast-path in `PomodoroCore.parseCycleCount()` and module-level pre-computed `FOCUS_NOTIFICATIONS` array (1..100) in `core.js`. Measured 87.4% speedup on focus notifications (69.99ms → 8.84ms at 2M iterations) and 66.6% speedup across routine pomodoro session cycles (30.76ms → 10.29ms at 2M iterations) with 100% exact equality verified across all edge cases.


## 2026-11-09 - Numeric fast-path and single-subtraction for calculateRemainingSeconds

**Learning:** `calculateRemainingSeconds()` is invoked continuously every 250ms during active countdown timer ticks. Unconditionally passing native timestamp numbers through `Number()` caused redundant type conversion checks, while sequentially evaluating `isNaN()`, `!isFinite()`, and `Math.max(0, ...)` added multiple redundant branches and function calls per tick. By fast-pathing native numeric timestamps, evaluating timestamp difference once (`const diff = targetEndTimeMs - nowMs`), and short-circuiting non-positive or non-finite values (`diff <= 0 || !Number.isFinite(diff)`), redundant subtraction, redundant isNaN/isFinite checks, and Math.max calls are completely eliminated while guaranteeing identical seconds rounding.
**Action:** Implemented numeric fast-path with single difference computation and single non-finite check in `PomodoroCore.calculateRemainingSeconds()`. Measured 23.2% speedup on active countdown timer ticks (33.96ms → 26.09ms at 5M iterations) and 30.4% speedup on expired timer intervals (21.77ms → 15.16ms at 5M iterations) with 100% exact equality verified across 640 matrix cases and 50,000 randomized fuzz tests.


## 2026-11-09 - Fast-path and pre-computed lookup tables for calculateSkipTransition

**Learning:** `calculateSkipTransition()` dynamically instantiated a new transition object (`{ nextMode, toastMessage, cycleCount }`) on every invocation and made redundant function calls to `getNextMode()` (which coerced numeric cycle counts to strings inside `parseInt`) and `getModeToastMessage()`, generating unnecessary heap object churn and GC pressure. Pre-computing frozen lookup arrays (`FOCUS_SKIP_LOOKUP` and `BREAK_SKIP_LOOKUP`) for standard cycles (1..100) and adding a positional numeric fast-path eliminates object allocations, function invocation overhead, and string coercion completely.
**Action:** Implemented positional numeric fast-path and module-level frozen lookup tables (`FOCUS_SKIP_LOOKUP` and `BREAK_SKIP_LOOKUP` for cycles 0..100) in `core.js`. Measured 67.6% speedup on routine positional skips (60.42ms → 19.56ms at 5M iterations), 78.9% on focus mode skips (75.88ms → 16.01ms), and 42.2% on object parameter invocations (102.76ms → 59.38ms) with 100% exact equality verified across 948 matrix cases and 100,000 randomized fuzz tests.


## 2026-11-09 - Fast-path and pre-computed lookup tables for calculateCompletedSession

**Learning:** `calculateCompletedSession()` is executed upon every completed session to advance mode state, record cycle count, and accumulate daily focus statistics. Unconditionally delegating to `getNextMode()` caused redundant function calls and numeric-to-string coercion via `parseInt()`. Furthermore, invoking `parseInt()` on native numeric values for `totalFocusMinsToday` and `currentStreak`, calling `String()` repeatedly for local storage dictionary values, and dynamically recomputing mode/toast transitions caused unnecessary CPU branching and heap allocations. Pre-computing frozen `FOCUS_SESSION_LOOKUP` transition states for standard cycles (1..100) alongside a `NUM_STRINGS` array (0..1499) and fast-pathing native numbers eliminates redundant function calls, string coercion, and allocations entirely.
**Action:** Implemented numeric fast-paths, pre-computed frozen `FOCUS_SESSION_LOOKUP` array (0..100), and `NUM_STRINGS` lookup table in `core.js`. Measured 37.9% speedup on routine focus session completions with object payloads (198.03ms → 122.95ms at 4M iterations) and 30.1% speedup across alternating focus/break session cycles (135.80ms → 94.91ms at 4M iterations) with 100% exact equality verified across 69,120 matrix cases.


## 2026-11-09 - Fast-path and pre-computed lookup table for getModeSessionLabel

**Learning:** `getModeSessionLabel()` called whenever switching modes or resetting sessions delegated focus mode to `formatSessionLabel()`, which unconditionally executed `parseInt()` (coercing native numbers into strings) and dynamically constructed template strings (`SESSION ${cycleStr} // DEEP WORK`) on the heap upon every call. Because break modes already returned frozen constants (`MODE_SESSION_LABELS`), pre-computing standard focus session labels (cycles 1..100) in a `SESSION_LABELS` lookup table and fast-pathing numeric cycle counts eliminates heap string allocations, dynamic string interpolation, and `parseInt` overhead completely.
**Action:** Implemented numeric fast-path in `PomodoroCore.getModeSessionLabel()` and `PomodoroCore.formatSessionLabel()` alongside module-level pre-computed `SESSION_LABELS` lookup table (1..100) in `core.js`. Measured 84.4% speedup on focus mode session labels (66.81ms → 10.44ms at 4M iterations), 61.2% speedup on mixed mode transitions (78.27ms → 30.33ms at 4M iterations), and 61.3% speedup on mixed types and boundaries (123.94ms → 48.03ms at 4M iterations) with 100% exact equality verified across 686 matrix cases and 50,000 fuzz cases.

## 2026-11-10 - Numeric fast-path and cached frozen objects for getTimerStatus

**Learning:** `getTimerStatus()` is invoked on every timer tick (every ~250ms) to determine button text and system status. The original implementation unconditionally passed `timeLeft` and `duration` through `Number()` coercion even when they were already native numbers, incurring redundant type checks. Additionally, it allocated new status objects on every call instead of returning frozen module-level constants (`TIMER_STATUS_RUNNING`, `TIMER_STATUS_PAUSED`, `TIMER_STATUS_READY`). A numeric fast-path using `typeof === 'number'` combined with `x !== x` NaN checks and direct comparison (`time > 0 && time < dur`) eliminates `Number()` coercion for the hot path. Returning cached frozen objects removes all heap allocations for the running/paused/ready states.
**Action:** Added numeric fast-path in `PomodoroCore.getTimerStatus()` with `typeof` guards and `x !== x` NaN check, simplified comparison by removing redundant `dur > 0` check (implied by `time > 0 && time < dur`), and ensured all three return paths use frozen module-level constants. Verified strict output equality against baseline across 1,344 matrix cases and 100,000 fuzz cases. Initial benchmark reported an 11.2% speedup on the numeric path, but that workload used times far above the duration and never reached the PAUSED branch, and its checksum concatenated objects instead of comparing results. Re-measured with a benchmark that covers PAUSED/READY branches, string inputs, and true object inputs using numeric status codes. On the numeric path there is no measurable gain: repeated single runs (1M iterations) gave between -1.0% and +2.0% (e.g. 7.28ms → 7.14ms), which is within noise. String inputs showed about 4–7% and object inputs about 38–42% (single runs; noisy).


## 2026-11-10 - Numeric fast-path for calculateProgressOffset SVG dashoffset

**Learning:** `calculateProgressOffset()` runs on every ~250ms timer tick to update the SVG progress circle but paid unconditional `isNaN()`/`isFinite()` checks and `Math.max()`/`Math.min()` calls even when `timeLeft`, `duration`, and `circumference` were already native numbers. Because it sits on the critical rendering path alongside `formatTime()` and `getTimerStatus()`, removing those redundant checks and function calls yields a direct per-tick win.

**Action:** Added a numeric fast-path `typeof timeLeft === 'number' && typeof duration === 'number' && typeof circumference === 'number'` that short-circuits validation and uses plain comparisons instead of `Math.max`/`Math.min`, falling back to the original `isNaN`/`isFinite` logic for non-numeric inputs. Measured 33–41% speedup on active countdown ticks (12.00ms → 7.71ms at 3M iters) and 37–41% on boundary ticks (13.19ms → 8.26ms at 3M iters) with 100% exact SVG dashoffset equality across all numeric, NaN, Infinity, string, null, and undefined cases.

## 2026-11-12 - Stop validating session history at its output limit

**Learning:** `validateSessionHistory()` returns at most 20 valid records but previously scanned and allocated sanitized copies for every later entry before discarding them with `slice()`. For oversized histories this performs work proportional to the entire input despite a fixed-size output.
**Action:** Stop the validation loop immediately after collecting `SESSION_HISTORY_LIMIT` records and return that already-bounded array. A 10,000-valid-entry workload (200 calls, median of 5 rounds) improved from 330.60ms to 0.65ms (~99.8%), with output equality and exactly 20 indexed history reads verified.

## 2026-11-12 - Skip code-point expansion for short missions

**Learning:** `sanitizeMission()` converted every trimmed mission to a code-point array and joined it again, even though ordinary titles already fit within the 80-code-point limit. Checking the UTF-16 length first avoids the array allocation in this common case; over-limit strings still use code-point slicing to preserve surrogate pairs.
**Action:** Return the trimmed string directly when its UTF-16 length is at most 80, retaining the existing `Array.from(...).slice(0, 80)` behavior for longer titles. On four representative titles across 250,000 calls × 5 rounds, median runtime improved from 139.72ms to 67.04ms (52.0%) with exact output equality.

## 2026-11-12 - Avoid duplicate session history validation

**Learning:** `recordCompletedSession()` first validates and normalizes stored history, then prepends one session and runs the full validator again. The new record can be checked directly with the same date, mode, and focus-duration rules; because the existing array is already normalized and bounded, trimming it to 19 and prepending the valid entry preserves the exact output while avoiding a second scan and allocation pass.
**Action:** Validate the new entry directly and reuse the normalized history array in `recordCompletedSession()`. A workload with 20 history entries across 100,000 calls per round (median of 7 rounds) improved from 698.69ms to 376.50ms (46.1%), with exact baseline equality across valid/invalid inputs and a 20-entry history.

## 2026-11-12 - Direct Netrunner rank threshold selection

**Learning:** `getNetrunnerRank()` scanned all six ranks backwards and clamped progress even though the selected rank guarantees progress is within its range. Selecting by ascending thresholds and calculating the in-range progress directly avoids the scan and redundant clamp.
**Action:** Replaced the threshold loop with direct rank selection and removed the redundant progress clamp. On active progression EXP values (0–1,499), 256 mixed values × 1,000,000 calls per round (median of 7 rounds) improved from 83.04ms to 60.72ms (26.9% faster); exact output equality was verified across all 10,013 progression and edge values, and a regression test was added.

## 2026-11-12 - Direct theme-name dispatch

**Learning:** `getThemeVariables()` and `getThemeLabel()` searched a four-name array with `.includes()` on every call, including frequent theme reads during rendering. Exact string dispatch avoids allocating/reading the key list and preserves the cyan fallback for every unsupported input.
**Action:** Replaced `VALID_THEMES.includes()` and `VALID_LABELS.includes()` checks with direct theme-name comparisons and removed the now-unused key arrays. For 3,000,000 calls across five common/invalid inputs (median of 7 rounds), theme-variable lookup improved from 46.16ms to 20.93ms (54.6%) and label lookup from 41.35ms to 18.21ms (56.0%); exact output equality was verified.

## 2026-11-12 - Set audio visualizer fill style once per frame

**Learning:** `startVisualizer()` assigns the same canvas `fillStyle` once for every bar even though the theme color is constant throughout a frame. With 128 frequency bars, this repeats 127 unnecessary canvas state writes per animation frame.
**Action:** Moved the color assignment before the bar loop. A 128-bar rendering workload across 50,000 frames per round (median of 7 rounds) improved from 799.05ms to 93.69ms (88.3% faster), with identical drawing checksums and fill-style writes reduced from 128 to 1 per frame.

## 2026-11-12 - Delegate task checkbox changes

**Learning:** `renderTasks()` replaced the task-list HTML and then attached a new `change` callback to every checkbox on each render. A single listener on the persistent checklist container handles delegated events for newly-rendered inputs and avoids allocating/registering per-checkbox callbacks repeatedly.
**Action:** Replaced per-render checkbox listener registration with one delegated `change` handler. For a 100-checkbox/10,000-render workload across 7 measured rounds, listener setup+render improved from 83.05ms to 0.11ms (99.9% faster), while the compared checked-state output matched and registrations dropped from 7,000,000 to 1.

## 2026-11-12 - Precompute audio visualizer bar heights

**Learning:** `startVisualizer()` recalculated `(byte / 255) * canvas.height` for every frequency bin on every animation frame, even though frequency samples are always 8-bit values and canvas height is fixed for the visualizer lifetime. A 256-entry height table replaces repeated division and multiplication with indexed reads.
**Action:** Precomputed all 256 possible bar heights once in `startVisualizer()` and used the table in the render loop. A 32-bar calculation workload across 1,000,000 frames per round (median of 9 rounds) measured 34.53ms → 26.87ms (22.2%), 33.93ms → 26.95ms (20.6%), and 34.88ms → 27.20ms (22.0%) in three repeat runs; exact height/output equality was verified for every byte value and sum checksum.
