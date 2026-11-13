import json
import re
import struct
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPwaAssets(unittest.TestCase):
    def test_index_references_manifest_and_registers_service_worker(self):
        html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")

        self.assertRegex(html, r'<link[^>]+rel="manifest"[^>]+href="manifest\.webmanifest"')
        self.assertIn("navigator.serviceWorker.register('./service-worker.js')", html)

    def test_manifest_has_installable_metadata_and_app_icons(self):
        manifest = json.loads((REPO_ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))

        self.assertTrue(manifest["name"])
        self.assertTrue(manifest["short_name"])
        self.assertEqual(manifest["start_url"], "./")
        self.assertEqual(manifest["display"], "standalone")
        self.assertEqual(manifest["theme_color"], "#070913")
        self.assertEqual(manifest["background_color"], "#070913")
        icons = {icon["sizes"]: icon for icon in manifest["icons"]}
        self.assertEqual(set(icons), {"192x192", "512x512"})
        for size, icon in ((192, icons["192x192"]), (512, icons["512x512"])):
            self.assertEqual(icon["src"], f"icons/icon-{size}.png")
            self.assertEqual(icon["type"], "image/png")
            self.assertIn("any", icon["purpose"])

    def test_service_worker_caches_app_shell_and_falls_back_offline(self):
        worker = (REPO_ROOT / "service-worker.js").read_text(encoding="utf-8")

        for asset in (
            "./",
            "./index.html",
            "./core.js",
            "./manifest.webmanifest",
            "./icons/icon-192.png",
            "./icons/icon-512.png",
        ):
            self.assertIn(asset, worker)
        self.assertRegex(worker, r"addAll\(ASSETS\)")
        self.assertIn("caches.match(event.request)", worker)
        self.assertIn("caches.match('./index.html')", worker)
        self.assertIn("event.waitUntil", worker)

    def test_icons_are_valid_pngs_with_expected_dimensions(self):
        for size in (192, 512):
            icon_path = REPO_ROOT / "icons" / f"icon-{size}.png"
            data = icon_path.read_bytes()

            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", data[16:24]), (size, size))


if __name__ == "__main__":
    unittest.main()
