"""E2E tests that drive index.html in a real Chromium browser via Playwright.

These cover the parts of the UI that the unit tests (which only exercise core.js)
cannot see: the task delete button, the settings modal (Escape to close, focus
return), and the export/import data flow.

Run locally:
    pip install -r requirements-dev.txt
    python -m playwright install chromium
    python -m unittest tests.test_ui_e2e_playwright -v
"""
import json
import tempfile
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO_ROOT = Path(__file__).resolve().parent.parent
INDEX_URI = (REPO_ROOT / "index.html").as_uri()


class PlaywrightUiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._playwright = sync_playwright().start()
        cls.browser = cls._playwright.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls._playwright.stop()

    def setUp(self):
        # Fresh context per test => empty localStorage, no state leaks between tests.
        self.context = self.browser.new_context(accept_downloads=True)
        # Block any network access (fonts, CDNs). The page must work offline.
        self.context.route(
            "http*://**/*",
            lambda route: route.abort(),
        )
        self.page = self.context.new_page()
        self.page_errors = []
        self.page.on("pageerror", lambda exc: self.page_errors.append(str(exc)))

    def tearDown(self):
        self.context.close()

    def open_app(self):
        self.page.goto(INDEX_URI)
        self.page.wait_for_selector("#taskChecklist")

    def add_task(self, text):
        mission = self.page.locator("#missionInput")
        mission.fill(text)
        mission.press("Enter")


class TestTaskDeleteInBrowser(PlaywrightUiTestCase):
    def test_remove_button_deletes_only_that_task_and_persists(self):
        self.open_app()
        self.add_task("ทดสอบลบภารกิจ E2E")
        remove = self.page.get_by_role(
            "button", name="ลบภารกิจ: ทดสอบลบภารกิจ E2E"
        )
        remove.wait_for()

        before = self.page.locator(".task-item").count()
        remove.click()

        self.assertEqual(self.page.locator(".task-item").count(), before - 1)
        self.assertEqual(self.page.locator(".task-remove", has_text="").count(), before - 1)
        self.assertEqual(
            self.page.get_by_role("button", name="ลบภารกิจ: ทดสอบลบภารกิจ E2E").count(),
            0,
        )
        stored = json.loads(self.page.evaluate("localStorage.getItem('cp_tasks')"))
        self.assertFalse(any(t["text"] == "ทดสอบลบภารกิจ E2E" for t in stored))
        self.assertEqual(self.page_errors, [])


class TestSettingsModalInBrowser(PlaywrightUiTestCase):
    def test_escape_closes_settings_modal_and_returns_focus(self):
        self.open_app()
        settings_btn = self.page.locator("#settingsBtn")
        modal = self.page.locator("#settingsModal")

        settings_btn.click()
        self.assertTrue(modal.evaluate("el => el.classList.contains('open')"))

        self.page.keyboard.press("Escape")

        self.assertFalse(modal.evaluate("el => el.classList.contains('open')"))
        focused_id = self.page.evaluate("document.activeElement && document.activeElement.id")
        self.assertEqual(focused_id, "settingsBtn")
        self.assertEqual(self.page_errors, [])


class TestExportImportInBrowser(PlaywrightUiTestCase):
    def open_settings(self):
        self.page.locator("#settingsBtn").click()
        self.page.locator("#settingsModal.open").wait_for()

    def test_export_then_import_restores_tasks_after_reload(self):
        self.open_app()
        self.add_task("ภารกิจสำรองข้อมูล")
        self.page.get_by_role("button", name="ลบภารกิจ: ภารกิจสำรองข้อมูล").wait_for()

        self.open_settings()
        with self.page.expect_download() as dl_info:
            self.page.locator("#exportDataBtn").click()
        backup_path = Path(tempfile.mkdtemp()) / "backup.json"
        dl_info.value.save_as(backup_path)
        self.assertEqual(
            self.page.locator("#dataBackupStatus").text_content(),
            "ข้อมูลสำรองถูกส่งออกแล้ว",
        )

        # Wipe the task list, then restore from the exported file.
        self.page.evaluate("localStorage.setItem('cp_tasks', JSON.stringify([]))")
        self.open_app()
        self.assertEqual(self.page.locator(".task-item").count(), 0)

        self.open_settings()
        self.page.once("dialog", lambda d: d.accept())
        with self.page.expect_navigation():
            self.page.locator("#importDataInput").set_input_files(str(backup_path))

        self.page.wait_for_selector("#taskChecklist")
        self.assertTrue(
            self.page.get_by_role("button", name="ลบภารกิจ: ภารกิจสำรองข้อมูล").count() == 1
        )
        self.assertEqual(self.page_errors, [])

    def test_import_cancelled_keeps_existing_data(self):
        self.open_app()
        self.add_task("ภารกิจเดิมที่ต้องคงไว้")
        self.page.get_by_role("button", name="ลบภารกิจ: ภารกิจเดิมที่ต้องคงไว้").wait_for()

        backup = {
            "version": 1,
            "exportedAt": "2026-01-01T00:00:00.000Z",
            "data": {"cp_tasks": json.dumps([{"id": 99, "text": "ไม่ควรถูกนำเข้า", "done": False}])},
        }
        backup_path = Path(tempfile.mkdtemp()) / "other.json"
        backup_path.write_text(json.dumps(backup, ensure_ascii=False), encoding="utf-8")

        self.open_settings()
        self.page.once("dialog", lambda d: d.dismiss())
        self.page.locator("#importDataInput").set_input_files(str(backup_path))

        self.page.locator("#dataBackupStatus").filter(has_text="ยกเลิก").wait_for()
        stored = json.loads(self.page.evaluate("localStorage.getItem('cp_tasks')"))
        self.assertTrue(any(t["text"] == "ภารกิจเดิมที่ต้องคงไว้" for t in stored))
        self.assertFalse(any(t["text"] == "ไม่ควรถูกนำเข้า" for t in stored))
        self.assertEqual(self.page_errors, [])


if __name__ == "__main__":
    unittest.main()
