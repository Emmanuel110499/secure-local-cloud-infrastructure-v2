import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VisualAssetsProTests(unittest.TestCase):
    def test_official_brand_assets_are_available(self):
        expected = (
            "docker.svg", "grafana.svg", "prometheus.svg", "cloudflare.svg",
            "flask.svg", "nginx.svg", "ubuntu.svg", "linux.svg",
        )
        for name in expected:
            with self.subTest(asset=name):
                self.assertTrue((ROOT / "static" / "brand" / name).exists())

    def test_realistic_world_asset_exists(self):
        image = ROOT / "static/images/world-presence-realistic.png"
        self.assertTrue(image.exists())
        self.assertGreater(image.stat().st_size, 100_000)

    def test_replacement_is_loaded_on_relevant_pages(self):
        for name in ("index_v2.html", "documentation.html", "login.html", "base.html"):
            with self.subTest(template=name):
                text = (ROOT / "templates" / name).read_text(encoding="utf-8")
                self.assertIn("css/visual-assets-pro.css", text)
                self.assertIn("js/visual-assets-pro.js", text)

    def test_replacement_uses_real_brand_files(self):
        script = (ROOT / "static/js/visual-assets-pro.js").read_text(encoding="utf-8")
        for name in ("docker.svg", "grafana.svg", "prometheus.svg"):
            self.assertIn(name, script)
        self.assertIn("world-presence-realistic.png", script)

    def test_styles_do_not_redesign_layout(self):
        stylesheet = (ROOT / "static/css/visual-assets-pro.css").read_text(encoding="utf-8")
        self.assertNotIn("body {", stylesheet)
        self.assertNotIn(".card {", stylesheet)
        self.assertNotIn("background-color:", stylesheet)


if __name__ == "__main__":
    unittest.main()
