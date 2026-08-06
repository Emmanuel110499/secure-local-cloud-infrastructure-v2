import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VisualInterfaceTests(unittest.TestCase):
    def test_dashboard_navigation_has_no_duplicate_dashboard(self):
        template = (ROOT / "templates/index_v2.html").read_text(
            encoding="utf-8"
        )
        self.assertNotIn('href="#dashboard"', template)
        self.assertNotIn("Gérer mon compte", template)

    def test_only_compact_emma_launcher_remains(self):
        template = (ROOT / "templates/index_v2.html").read_text(
            encoding="utf-8"
        )
        self.assertIn('id="emma-chat-launcher"', template)
        self.assertNotIn("Demandez à Emma_IA", template)
        self.assertNotIn('class="pdf-export-button', template)
        self.assertIn('href="/documentation" class="nav-item"', template)
        self.assertIn('class="sidebar-premium-card"', template)
        self.assertNotIn("Surveillance continue · Europe/Paris", template)

    def test_monitoring_offers_both_print_orientations(self):
        script = (ROOT / "static/js/monitoring-clean.js").read_text(
            encoding="utf-8"
        )
        report = (ROOT / "static/js/monitoring-export-pro.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('data-print-orientation="portrait"', script)
        self.assertIn('data-print-orientation="landscape"', script)
        self.assertIn("A4 ${printOrientation}", report)
        self.assertIn('class="orientation-${printOrientation}"', report)
        self.assertIn("body.orientation-portrait .metrics-grid", report)

    def test_sidebar_clock_uses_paris_local_time(self):
        script = (ROOT / "static/js/sidebar-premium-clock.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('timeZone: "Europe/Paris"', script)
        self.assertIn('document.getElementById(\n        "last-update"', script)

    def test_emma_close_button_stays_above_mobile_account_ribbon(self):
        stylesheet = (ROOT / "static/css/emma-floating-chat.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("z-index: 13050", stylesheet)
        self.assertIn("#emma-chat-close", stylesheet)
        self.assertNotIn("@media (min-width: 701px)", stylesheet)
        self.assertIn("top: max(118px", stylesheet)
        self.assertIn("height: min(64dvh, 560px)", stylesheet)
        self.assertIn("grid-template-columns: repeat(2", stylesheet)

    def test_search_hides_only_while_scrolling(self):
        script = (ROOT / "static/js/platform-search.js").read_text(
            encoding="utf-8"
        )
        stylesheet = (ROOT / "static/css/platform-search.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("platform-search-hidden", script)
        self.assertIn("platform-search-hidden", stylesheet)
        self.assertIn("}, 550)", script)
        self.assertIn('matchMedia("(max-width: 820px)")', script)

    def test_monitoring_has_a_useful_summary_and_no_visible_legacy_empty_state(self):
        template = (ROOT / "templates/monitoring.html").read_text(
            encoding="utf-8"
        )
        script = (ROOT / "static/js/monitoring-clean.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('class="empty-state" hidden', template)
        self.assertIn('class="cm-insights"', script)
        self.assertIn("loadCurrentMetrics", script)
        self.assertIn("Valeurs actuelles de Prometheus", script)

    def test_documentation_status_is_left_and_dashboard_return_is_right(self):
        template = (ROOT / "templates/documentation.html").read_text(
            encoding="utf-8"
        )
        self.assertLess(
            template.index('class="doc-status"'),
            template.index('class="doc-back"'),
        )


if __name__ == "__main__":
    unittest.main()
