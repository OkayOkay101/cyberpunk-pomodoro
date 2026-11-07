# ⚡ Cyberpunk Focus // Pomodoro Station & Neural Synthesizer

> **A futuristic, distraction-free sci-fi HUD Pomodoro timer & Web Audio ambient synthesizer designed for deep focus work, studying, and cybernetic productivity.**  
> Built with Vanilla JavaScript, Web Audio API, and Zero External Dependencies.

🌐 **Live Demo:** [https://okayokay101.github.io/cyberpunk-pomodoro/](https://okayokay101.github.io/cyberpunk-pomodoro/)  
🧪 **Interactive Unit Test Suite:** [https://okayokay101.github.io/cyberpunk-pomodoro/test.html](https://okayokay101.github.io/cyberpunk-pomodoro/test.html)

---

## 📑 Table of Contents / สารบัญ
1. [English Documentation](#-english-documentation)
2. [คู่มือภาษาไทย (Thai Documentation)](#-คู่มือภาษาไทย-thai-documentation)
3. [Unit Testing Suite](#-unit-testing-suite)
4. [Tech Stack](#-tech-stack)

---

## 🇬🇧 English Documentation

### 🚀 Overview & About
**Cyberpunk Focus** is an ultra-modern, immersive Pomodoro Station tailored for developers, students, gamers, and digital nomads. Operating directly inside your browser with a responsive neon sci-fi HUD interface, it leverages raw **Web Audio API synthesizers** to produce custom generative ambient soundscapes (Pink/White noise rain, deep space sub-bass hum, 40Hz binaural gamma waves, server rack cooling fan, and cybernetic storm) with zero streaming latency and zero external audio files.

### ✨ Key Features
1. **Customizable Pomodoro Engine:**
   - **Focus Mode:** Default 25 min (customizable 1–90 min)
   - **Short Break:** Default 5 min (customizable 1–30 min)
   - **Long Break:** Default 15 min (customizable 1–60 min)
   - Automatic 4th cycle long-break progression and optional auto-start.
2. **Neural Ambient Audio Synthesizer (5 Generative Synths):**
   - 🌧️ **Cyber Rain:** Calibrated pink noise generator for masking vocal chatter.
   - 🚀 **Deep Space Hum:** Dual sine/sawtooth low-frequency resonance.
   - ⚡ **40Hz Focus Wave:** Binaural gamma-wave frequency modulation for cognitive stimulation.
   - 🌀 **Server Fan:** Bandpass-filtered airflow white noise simulation.
   - ⛈️ **Cyber Storm:** Ambient rain combined with low-frequency oscillator thunder rumbles.
3. **Real-time Audio Spectrum Visualizer:**
   - HTML5 `<canvas>` powered by `AnalyserNode` rendering live neon audio frequencies.
4. **Productivity & Streak Tracker:**
   - Daily consecutive streak counter (`⚡ STREAK: X DAYS`) and cumulative focused minutes (`🎯 X MINS TODAY`).
5. **Interactive Mission Checklist:**
   - Add focus objectives and check off completed subtasks saved to `localStorage`.
6. **4 Neon Cyberpunk Themes:**
   - `Cyan Matrix` (Default), `Neon Pink / Outrun`, `Night City Yellow (2077)`, and `Emerald Hacker Green`.
7. **Keyboard Shortcuts:**
   - <kbd>Space</kbd> Start / Pause
   - <kbd>R</kbd> Reset (With accidental double-press protection)
   - <kbd>S</kbd> Skip session
   - <kbd>M</kbd> Mute / Unmute
   - <kbd>F</kbd> Fullscreen Immersion Mode

---

## 🇹🇭 คู่มือภาษาไทย (Thai Documentation)

### 🚀 เกี่ยวกับโปรเจกต์ (About)
**Cyberpunk Focus** คือเว็บแอปพลิเคชันจับเวลาโฟกัสทำงานและอ่านหนังสือในธีม Cyberpunk Sci-Fi HUD ระดับพรีเมียม ออกแบบมาเพื่อตัดสิ่งรบกวนรอบตัวและสร้างบรรยากาศการจดจ่ออย่างลึกซึ้ง (Deep Work) โดยจุดเด่นสำคัญคือเครื่องกำเนิดเสียงบรรยากาศสังเคราะห์ (Neural Ambient Synthesizer) ที่สร้างเสียงขึ้นมาสดๆ ผ่าน Web Audio API โดยไม่ต้องดาวน์โหลดไฟล์เสียงภายนอก โหลดเร็ว เล่นได้ทันที และลื่นไหลทุกอุปกรณ์

### ✨ ฟีเจอร์เด่น
1. **ระบบจับเวลา Pomodoro มาตรฐานสากล & กำหนดเวลาเองได้:**
   - ปรับแต่งเวลา Focus, Short Break และ Long Break ได้อย่างอิสระผ่านเมนู Settings
   - ระบบนับรอบอัตโนมัติ สลับเข้าสู่ Long Break หลังครบ 4 รอบโฟกัส
2. **เครื่องสังเคราะห์เสียงบรรยากาศ 5 รูปแบบ (Zero-file Synthesizers):**
   - 🌧️ **Cyber Rain:** เสียงฝนสังเคราะห์ระดับ Pink Noise ตัดเสียงรบกวนภายนอก
   - 🚀 **Deep Space Hum:** คลื่นความถี่ต่ำผ่อนคลายความตึงเครียดของสมอง
   - ⚡ **40Hz Focus Wave:** คลื่นความถี่แกมมากระตุ้นสมาธิและการเรียนรู้
   - 🌀 **Server Fan:** เสียงพัดลมระบายความร้อนเซิร์ฟเวอร์ความถี่คงที่
   - ⛈️ **Cyber Storm:** เสียงพายุฝนและฟ้าร้องความถี่ต่ำสไตล์โลกอนาคต
3. **เส้นคลื่นเสียง Visualizer แสดงผลตามเวลาจริง:**
   - วาดคลื่นเสียง Audio Spectrum Visualizer บน Canvas ตามความถี่เสียงสังเคราะห์จริง
4. **ระบบบันทึกสถิติรายวันและ Streak:**
   - บันทึกเวลารวมที่โฟกัสสำเร็จในแต่ละวัน และนับจำนวนวันที่ทำงานต่อเนื่อง
5. **แผงรายการงานย่อย (Mission Checklist):**
   - พิมพ์เป้าหมายภารกิจ ติ๊กถูกเมื่อทำงานสำเร็จ พร้อมบันทึกลง LocalStorage อัตโนมัติ
6. **ปรับแต่งสีธีมนีออนได้ 4 รูปแบบ:**
   - Cyan Matrix, Neon Pink (Outrun), Night City Yellow (2077), และ Emerald Hacker
7. **ปุ่มลัดคีย์บอร์ดอำนวยความสะดวก:**
   - <kbd>Space</kbd> เริ่ม/หยุดตัวจับเวลา
   - <kbd>R</kbd> รีเซ็ตเวลา (พร้อมระบบป้องกันเผลอกดโดน)
   - <kbd>S</kbd> ข้ามรอบ
   - <kbd>M</kbd> เปิด/ปิดเสียง
   - <kbd>F</kbd> เข้าสู่โหมดเต็มจอ

---

## 🧪 Unit Testing Suite

The repository includes a comprehensive, zero-dependency unit test suite in [`test-runner.js`](test-runner.js) and an interactive visual dashboard in [`test.html`](test.html).

### Running Unit Tests via CLI (Node.js)
```bash
node test-runner.js
# Output: Unit Tests Completed: 27/27 passed, 0 failed.
```

### Running Unit Tests in Browser
Simply open `test.html` or click the **🧪 TESTS** button in the web HUD header to view real-time passing status across all 27 core module tests:
1. `formatTime()` - Formats MM:SS cleanly.
2. `calculateProgressOffset()` - Accurate circular SVG dashoffset mapping.
3. `getNextMode()` - Correct 4th cycle long break progression.
4. `clampVolume()` - Enforces safe audio thresholds (0.0 to 1.0).
5. `calculateStreak()` - Validates consecutive day streak increments and reset logic.
6. `formatSessionLabel()` - Formats double-digit padded session labels.
7. `sanitizeMission()` - Trims whitespace and caps text at 80 characters.
8. `validateCustomDuration()` - Guards minimum and maximum timer boundaries.
9. `getThemeVariables()` - Resolves neon CSS palette variables for all 4 themes.
10. `storage roundtrip` - Confirms JSON serialization and deserialization safety.
11. `deserializeConfig()` - Preserves Array instance and elements during array deserialization.
12. `deserializeConfig()` - Safely rejects primitive/corrupted payloads and falls back to defaults.
13. `formatSessionLabel()` - Resilient handling of non-numeric, negative, and NaN cycle inputs.
14. `formatTime()` - Clean truncation of fractional seconds and non-finite numbers.
15. `getNextMode()` - Guards against zero or negative cycle counts.
16. `calculateStreak()` - Safely resets on corrupted dates and recovers from invalid streak values.
17. `calculateProgressOffset()` - Handles NaN timeLeft and non-positive circle circumferences.
18. `escapeHtml()` - Escapes HTML special characters to prevent stored XSS and UI breakout.
19. `calculateDailyFocusMins()` - Resets focus minutes to 0 on date change or missing date, preventing indefinite carry-over.
20. `formatStreakBadge()` & `formatFocusTimeBadge()` - Pure formatting of HUD stats badges with boundary protection.
21. `calculateRemainingSeconds()` - Accurate countdown math guarding against NaN and negative intervals.
22. `formatDocumentTitle()` - Formats browser window title reflecting paused vs running state.
23. `formatTabLabel()` - Converts duration seconds to minutes and formats mode tab headers.
24. `calculateMuteToggle()` - Pure calculation of mute toggle states and audio volume restoration.
25. `formatVolumePercent()` & `getVolumeIcon()` - Resolves HUD volume percentage and dynamic speaker icon.
26. `createTaskItem()` & `toggleTaskItem()` - Immutable task object creation and status toggling.
27. `getThemeVariables()` & `formatTabLabel()` - Guards dictionary lookups against prototype pollution and prototype chain inheritance.

---

## 🛠️ Tech Stack
- **Frontend Core:** HTML5, CSS3 (CSS Variables, Flexbox, Grid, Animations, Glow effects)
- **Programming Language:** Vanilla JavaScript (ES6+)
- **Audio Synthesis Engine:** Web Audio API (`AudioContext`, `OscillatorNode`, `BiquadFilterNode`, `DynamicsCompressorNode`, `AnalyserNode`, `AudioBuffer`)
- **Testing:** Vanilla JS Test Runner & Interactive Web Dashboard (`test.html`)
- **Deployment:** GitHub Pages
