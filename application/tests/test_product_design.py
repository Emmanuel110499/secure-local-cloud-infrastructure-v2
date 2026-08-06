import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProductDesignTests(unittest.TestCase):
    def test_product_system_is_loaded_on_every_primary_page(self):
        templates = (
            "index_v2.html", "monitoring.html", "containers.html",
            "infrastructure.html", "security.html", "audit.html",
            "documentation.html", "assistant.html", "account.html",
            "login.html", "portal_v3_base.html",
        )
        for filename in templates:
            with self.subTest(template=filename):
                text = (ROOT / "templates" / filename).read_text(encoding="utf-8")
                self.assertIn("css/product-system.css", text)

    def test_sidebar_icons_are_real_svg(self):
        script = (ROOT / "static/js/product-icons.js").read_text(encoding="utf-8")
        self.assertIn('viewBox="0 0 24 24"', script)
        self.assertIn('name = "monitoring"', script)
        self.assertIn('name = "security"', script)
        self.assertIn('name = "documentation"', script)

    def test_homepage_copy_is_product_oriented(self):
        template = (ROOT / "templates/index_v2.html").read_text(encoding="utf-8")
        self.assertIn("Console d’exploitation", template)
        self.assertIn("État du périmètre", template)
        self.assertNotIn("Bienvenue sur Secure Local Cloud Infrastructure", template)

    def test_design_system_uses_controlled_tokens(self):
        stylesheet = (ROOT / "static/css/product-system.css").read_text(encoding="utf-8")
        self.assertIn("--slc-navy: #101c2f", stylesheet)
        self.assertIn("--slc-blue: #2f64d6", stylesheet)
        self.assertIn("--slc-radius: 11px", stylesheet)


if __name__ == "__main__":
    unittest.main()
