import subprocess
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionTransitionCore(unittest.TestCase):
    def _run_node(self, js_code: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["node", "-e", js_code],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT)
        )

    def test_calculate_completed_session_focus_to_short_break(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.calculateCompletedSession !== 'function') {
            console.error('FAIL: calculateCompletedSession is not a function');
            process.exit(1);
        }

        // Cycle 1 focus completion -> short break, cycle becomes 2
        const res1 = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 1,
            focusDuration: 1500,
            totalFocusMinsToday: 0,
            currentStreak: 2,
            todayStr: '2026-11-09'
        });

        if (res1.nextMode !== 'shortBreak') process.exit(2);
        if (res1.nextCycleCount !== 2) process.exit(3);
        if (res1.addedFocusMins !== 25) process.exit(4);
        if (res1.nextTotalFocusMins !== 25) process.exit(5);
        if (res1.toastMessage !== 'SHORT BREAK STARTED') process.exit(6);
        if (res1.storage.cp_focus_mins_today !== '25') process.exit(7);
        if (res1.storage.cp_cycle !== '2') process.exit(8);
        if (res1.storage.cp_streak !== '2') process.exit(9);
        if (res1.storage.cp_last_date !== '2026-11-09') process.exit(10);

        // Cycle 3 focus completion -> short break, cycle becomes 4
        const res3 = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 3,
            focusDuration: 1500,
            totalFocusMinsToday: 50,
            currentStreak: 2,
            todayStr: '2026-11-09'
        });
        if (res3.nextMode !== 'shortBreak') process.exit(11);
        if (res3.nextCycleCount !== 4) process.exit(12);
        if (res3.nextTotalFocusMins !== 75) process.exit(13);
        if (res3.storage.cp_cycle !== '4') process.exit(14);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_completed_session_focus_to_long_break(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Cycle 4 focus completion -> long break, cycle becomes 5
        const res4 = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 4,
            focusDuration: 1500,
            totalFocusMinsToday: 75,
            currentStreak: 5,
            todayStr: '2026-11-09'
        });

        if (res4.nextMode !== 'longBreak') process.exit(1);
        if (res4.nextCycleCount !== 5) process.exit(2);
        if (res4.addedFocusMins !== 25) process.exit(3);
        if (res4.nextTotalFocusMins !== 100) process.exit(4);
        if (res4.toastMessage !== 'LONG BREAK STARTED') process.exit(5);
        if (res4.storage.cp_cycle !== '5') process.exit(6);
        if (res4.storage.cp_focus_mins_today !== '100') process.exit(7);

        // Cycle 8 focus completion -> long break, cycle becomes 9
        const res8 = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 8,
            focusDuration: 1800,
            totalFocusMinsToday: 200,
            currentStreak: 5,
            todayStr: '2026-11-09'
        });
        if (res8.nextMode !== 'longBreak') process.exit(8);
        if (res8.nextCycleCount !== 9) process.exit(9);
        if (res8.addedFocusMins !== 30) process.exit(10);
        if (res8.nextTotalFocusMins !== 230) process.exit(11);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_completed_session_break_to_focus(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Short break completed -> focus mode, cycle maintained
        const resShort = PomodoroCore.calculateCompletedSession({
            currentMode: 'shortBreak',
            cycleCount: 2,
            focusDuration: 1500,
            totalFocusMinsToday: 25,
            currentStreak: 2,
            todayStr: '2026-11-09'
        });

        if (resShort.nextMode !== 'focus') process.exit(1);
        if (resShort.nextCycleCount !== 2) process.exit(2);
        if (resShort.addedFocusMins !== 0) process.exit(3);
        if (resShort.nextTotalFocusMins !== 25) process.exit(4);
        if (resShort.toastMessage !== 'FOCUS SESSION STARTED') process.exit(5);
        if (Object.keys(resShort.storage).length !== 0) process.exit(6);

        // Long break completed -> focus mode, cycle maintained
        const resLong = PomodoroCore.calculateCompletedSession({
            currentMode: 'longBreak',
            cycleCount: 5,
            focusDuration: 1500,
            totalFocusMinsToday: 100,
            currentStreak: 2,
            todayStr: '2026-11-09'
        });

        if (resLong.nextMode !== 'focus') process.exit(7);
        if (resLong.nextCycleCount !== 5) process.exit(8);
        if (resLong.addedFocusMins !== 0) process.exit(9);
        if (resLong.nextTotalFocusMins !== 100) process.exit(10);
        if (resLong.toastMessage !== 'FOCUS SESSION STARTED') process.exit(11);
        if (Object.keys(resLong.storage).length !== 0) process.exit(12);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_completed_session_boundary_and_corrupted_inputs(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Corrupted cycle count string/null/NaN
        const resCorruptCycle = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 'corrupted',
            focusDuration: 1500,
            totalFocusMinsToday: 0
        });
        if (resCorruptCycle.nextCycleCount !== 2) process.exit(1);
        if (resCorruptCycle.storage.cp_cycle !== '2') process.exit(2);

        // Corrupted focusDuration (NaN / negative / zero)
        const resBadDuration = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 1,
            focusDuration: NaN,
            totalFocusMinsToday: 10
        });
        if (isNaN(resBadDuration.addedFocusMins) || resBadDuration.addedFocusMins !== 25) process.exit(3);
        if (isNaN(resBadDuration.nextTotalFocusMins) || resBadDuration.nextTotalFocusMins !== 35) process.exit(4);
        if (resBadDuration.storage.cp_focus_mins_today === 'NaN') process.exit(5);

        // Corrupted totalFocusMinsToday (NaN / string)
        const resBadTotal = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 1,
            focusDuration: 1500,
            totalFocusMinsToday: 'invalid'
        });
        if (isNaN(resBadTotal.nextTotalFocusMins) || resBadTotal.nextTotalFocusMins !== 25) process.exit(6);
        if (resBadTotal.storage.cp_focus_mins_today !== '25') process.exit(7);

        // Missing todayStr uses local date string
        const resMissingDate = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 1,
            focusDuration: 1500,
            totalFocusMinsToday: 0,
            todayStr: ''
        });
        const todayStr = PomodoroCore.getLocalDateString();
        if (resMissingDate.storage.cp_last_date !== todayStr) process.exit(8);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_completed_session_rejects_overflowing_cycle_string(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        const result = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: '9'.repeat(400),
            focusDuration: 1500,
            totalFocusMinsToday: 0,
            todayStr: '2026-11-09'
        });

        if (result.nextCycleCount !== 2) process.exit(1);
        if (result.storage.cp_cycle !== '2') process.exit(2);
        if (!Number.isFinite(result.nextCycleCount)) process.exit(3);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_calculate_completed_session_positional_and_object_arguments(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        // Positional argument invocation
        const resPos = PomodoroCore.calculateCompletedSession(
            'focus',
            2,
            1500,
            25,
            3,
            '2026-11-09'
        );
        if (resPos.nextMode !== 'shortBreak') process.exit(1);
        if (resPos.nextCycleCount !== 3) process.exit(2);
        if (resPos.nextTotalFocusMins !== 50) process.exit(3);
        if (resPos.storage.cp_focus_mins_today !== '50') process.exit(4);

        // Object argument invocation
        const resObj = PomodoroCore.calculateCompletedSession({
            mode: 'focus',
            cycleCount: 2,
            focusDuration: 1500,
            totalFocusMinsToday: 25,
            currentStreak: 3,
            today: '2026-11-09'
        });
        if (resObj.nextMode !== 'shortBreak') process.exit(5);
        if (resObj.nextCycleCount !== 3) process.exit(6);
        if (resObj.nextTotalFocusMins !== 50) process.exit(7);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_refresh_daily_stats_when_date_changes(self):
        js_code = """
        const { PomodoroCore } = require('./core.js');

        if (typeof PomodoroCore.refreshDailyStats !== 'function') {
            console.error('FAIL: refreshDailyStats is not a function');
            process.exit(1);
        }

        const nextDay = PomodoroCore.refreshDailyStats('2026-11-08', '2026-11-09', 50, 3);
        if (nextDay.totalFocusMinsToday !== 0) process.exit(2);
        if (nextDay.currentStreak !== 4) process.exit(3);
        if (nextDay.date !== '2026-11-09') process.exit(4);

        const completed = PomodoroCore.calculateCompletedSession({
            currentMode: 'focus',
            cycleCount: 1,
            focusDuration: 1500,
            totalFocusMinsToday: nextDay.totalFocusMinsToday,
            currentStreak: nextDay.currentStreak,
            todayStr: nextDay.date
        });
        if (completed.nextTotalFocusMins !== 25) process.exit(5);
        if (completed.storage.cp_streak !== '4') process.exit(6);
        if (completed.storage.cp_last_date !== '2026-11-09') process.exit(7);

        const sameDay = PomodoroCore.refreshDailyStats('2026-11-09', '2026-11-09', 25, 4);
        if (sameDay.totalFocusMinsToday !== 25) process.exit(8);
        if (sameDay.currentStreak !== 4) process.exit(9);

        console.log('SUCCESS');
        """
        proc = self._run_node(js_code)
        self.assertEqual(proc.returncode, 0, f"Error: {proc.stderr or proc.stdout}")
        self.assertIn("SUCCESS", proc.stdout)

    def test_index_html_wires_session_transition_core(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertIn(
            "PomodoroCore.calculateCompletedSession",
            html,
            "index.html must use PomodoroCore.calculateCompletedSession to decouple session completion state transition"
        )

    def test_index_html_recomputes_date_at_session_completion(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        # Verify that handleTimerComplete calls getLocalDateString() at completion time
        # instead of using the startup todayStr variable
        self.assertIn(
            "const completionDate = PomodoroCore.getLocalDateString()",
            html,
            "index.html must recompute local date at session completion for midnight crossing correctness"
        )
        self.assertIn("todayStr: completionDate", html)
        self.assertIn("PomodoroCore.refreshDailyStats(", html)


if __name__ == "__main__":
    unittest.main()
