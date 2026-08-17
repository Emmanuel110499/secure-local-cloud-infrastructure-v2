import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InfrastructureMultiEquipmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = (ROOT / "templates/infrastructure.html").read_text(
            encoding="utf-8"
        )

    def test_architecture_lists_all_three_equipment(self):
        for label in ("PC Emmanuel", "VPS Production", "Laboratoire VMware"):
            with self.subTest(label=label):
                self.assertIn(label, self.template)

        topology = self.template.split(
            '<section class="topology-section">', 1
        )[1].split('</section>', 1)[0]
        self.assertEqual(topology.count("PC Emmanuel"), 1)
        self.assertNotIn('class="topology-node admin-node"', topology)

    def test_windows_collection_is_explained(self):
        self.assertIn("Windows Exporter", self.template)
        self.assertIn("Collecteur batterie", self.template)
        self.assertIn("192.168.154.1", self.template)
        self.assertIn("/api/equipment", self.template)

    def test_linux_and_observability_collectors_are_visible(self):
        for label in (
            "Node Exporter",
            "cAdvisor",
            "Prometheus",
            "Grafana",
            "Alertmanager",
            "Nginx",
            "Cloudflare Tunnel",
            "Docker Engine",
        ):
            with self.subTest(label=label):
                self.assertIn(label, self.template)

    def test_summary_is_multi_equipment(self):
        self.assertIn("CPU consolidé", self.template)
        self.assertIn("RAM consolidée", self.template)
        self.assertIn("Disque le plus utilisé", self.template)
        self.assertNotIn("CPU srv-web", self.template)
        self.assertIn("203.0.113.10", self.template)


if __name__ == "__main__":
    unittest.main()
