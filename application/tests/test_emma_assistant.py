from __future__ import annotations

import ast
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Blueprint, Flask

from services.assistant_engine import build_assistant_response
from services.assistant_router import services_answer
from services.prometheus_service import PrometheusService
from routes.help import help_bp


ROOT = Path(__file__).resolve().parents[1]


class EmmaIntentTests(unittest.TestCase):
    class FakeEquipmentPrometheus:
        def get_equipment_metrics(self, equipment_id):
            equipment = {
                "vps-production": ("VPS Production", "Production unifiée", "linux", 5, 25, 65),
                "lab-vmware": ("Laboratoire VMware", "Extension de laboratoire", "linux", None, None, None),
                "pc-emmanuel": ("PC Emmanuel", "Poste d’administration", "windows", 20, 90, 70),
            }[equipment_id]
            metrics = {
                "cpu": equipment[3], "memory": equipment[4], "disk": equipment[5],
                "network_receive_kbps": 12, "uptime": "2 j",
            }
            if equipment_id == "pc-emmanuel":
                metrics["battery"] = {
                    "charge_percent": 96,
                    "on_ac_power": True,
                    "collector_age_seconds": 15,
                }
            if equipment_id == "vps-production":
                metrics["volumes"] = [
                    {"name": "prometheus-data", "used_bytes": 1024**3},
                    {"name": "grafana-data", "used_bytes": 512 * 1024**2},
                ]
            return {
                "equipment": {
                    "id": equipment_id, "name": equipment[0],
                    "role": equipment[1], "os": equipment[2],
                },
                "state": "disconnected" if equipment_id == "lab-vmware" else "up",
                "metrics": metrics,
            }

        def get_all_equipment_metrics(self):
            return [
                self.get_equipment_metrics(equipment_id)
                for equipment_id in ("vps-production", "pc-emmanuel", "lab-vmware")
            ]

    def render_equipment(self, question):
        app = Flask(__name__)
        app.extensions["prometheus_service"] = self.FakeEquipmentPrometheus()
        with app.app_context():
            return build_assistant_response(question)

    def test_equipment_state_uses_targeted_live_data(self):
        response = self.render_equipment("Quel est l’état actuel du VPS Production ?")
        self.assertEqual(response["intent"], "equipment")
        self.assertTrue(response["used_live_data"])
        self.assertIn("VPS Production", response["answer"])
        self.assertIn("65 %", response["answer"])

    def test_equipment_comparison_identifies_main_pressure(self):
        response = self.render_equipment("Compare les trois équipements")
        self.assertIn("PC Emmanuel", response["answer"])
        self.assertIn("RAM à 90 %", response["answer"])
        self.assertIn("Alerte critique", response["answer"])
        self.assertIn("état opérationnel", response["answer"])

    def test_pc_battery_is_explained(self):
        response = self.render_equipment("Quel est l’état de la batterie de mon PC ?")
        self.assertIn("96 %", response["answer"])
        self.assertIn("secteur", response["answer"])

    def test_monitoring_volumes_are_explained(self):
        response = self.render_equipment("Explique les volumes persistants")
        self.assertIn("prometheus-data", response["answer"])
        self.assertIn("grafana-data", response["answer"])
        self.assertIn("après le redémarrage", response["answer"])

    def test_empty_question_is_rejected_cleanly(self):
        response = build_assistant_response("   ")

        self.assertEqual(response["intent"], "unknown")
        self.assertEqual(response["confidence"], 0.0)
        self.assertFalse(response["used_live_data"])

    @patch(
        "services.assistant_engine.health_analysis_answer",
        return_value="analyse réelle",
    )
    def test_current_infrastructure_uses_live_data(self, mocked):
        response = build_assistant_response(
            "Quel est l’état actuel de mon infrastructure ?"
        )

        mocked.assert_called_once()
        self.assertEqual(response["intent"], "infrastructure")
        self.assertTrue(response["used_live_data"])
        self.assertEqual(response["answer"], "analyse réelle")

    @patch(
        "services.assistant_engine.health_analysis_answer",
        return_value="analyse lente Docker",
    )
    @patch(
        "services.assistant_engine.metrics_answer",
        return_value="CPU 10 %, RAM 20 %, disque 30 %",
    )
    def test_resources_with_accents_use_live_data(
        self,
        metrics_mocked,
        health_mocked,
    ):
        response = build_assistant_response(
            "Analyse l’utilisation actuelle du CPU, de la RAM et du disque."
        )

        metrics_mocked.assert_called_once()
        health_mocked.assert_not_called()
        self.assertEqual(response["intent"], "metrics")
        self.assertTrue(response["used_live_data"])
        self.assertEqual(
            response["sources"],
            ["Prometheus — métriques en temps réel"],
        )

    @patch(
        "services.assistant_engine.services_answer",
        return_value="Prometheus UP, cAdvisor UP",
    )
    def test_prometheus_cadvisor_state_is_live(self, mocked):
        response = build_assistant_response(
            "Quel est l’état actuel de Prometheus et de cAdvisor ?"
        )

        mocked.assert_called_once()
        self.assertEqual(response["intent"], "services")
        self.assertTrue(response["used_live_data"])

    @patch(
        "services.assistant_engine.services_answer",
        return_value="Grafana UP",
    )
    def test_grafana_failure_returns_targeted_diagnostic(self, mocked):
        app = Flask(__name__)
        app.config["GRAFANA_URL"] = "http://monitoring.test:3000"

        with app.app_context():
            response = build_assistant_response(
                "Que dois-je vérifier si Grafana ne répond plus ?"
            )

        mocked.assert_called_once()
        self.assertIn("Diagnostic ciblé de Grafana", response["answer"])
        self.assertIn("Sur srv-monitoring", response["answer"])
        self.assertIn("Sur srv-web", response["answer"])
        self.assertIn("http://monitoring.test:3000/api/health", response["answer"])
        self.assertTrue(response["used_live_data"])

    @patch(
        "services.assistant_engine.services_answer",
        return_value="Tous les services sont UP",
    )
    def test_security_question_distinguishes_audit_from_scan(self, mocked):
        response = build_assistant_response(
            "Quels sont les risques de sécurité actuels ?"
        )

        self.assertIn("Évaluation de sécurité actuelle", response["answer"])
        self.assertIn("pas un scan de vulnérabilités complet", response["answer"])
        self.assertTrue(response["used_live_data"])
        self.assertEqual(len(response["sources"]), 2)

    def test_priority_roadmap_has_five_steps(self):
        response = build_assistant_response(
            "Quelles améliorations restent prioritaires ?"
        )

        self.assertEqual(response["intent"], "documentation")
        self.assertEqual(response["confidence"], 0.94)
        for number in range(1, 6):
            self.assertIn(f"{number}.", response["answer"])

    def test_two_server_follow_up_uses_context(self):
        response = build_assistant_response(
            "Et pourquoi ?",
            context={
                "last_question": "Présente-moi toute la plateforme.",
                "last_intent": "documentation",
            },
        )

        self.assertTrue(response["follow_up"])
        self.assertIn("deux serveurs", response["answer"])
        self.assertIn("séparer les rôles", response["answer"])

    def test_every_successful_response_has_suggestions(self):
        response = build_assistant_response(
            "Quelles améliorations restent prioritaires ?"
        )

        self.assertEqual(len(response["suggestions"]), 3)


class EmmaContentTests(unittest.TestCase):
    def test_metrics_document_is_not_corrupted(self):
        content = (
            ROOT / "knowledge" / "docs" / "metrics.md"
        ).read_text(encoding="utf-8")

        self.assertNotIn("1~#", content)
        self.assertEqual(content.count("# Les métriques"), 1)

    def test_frontend_uses_safe_text_rendering(self):
        content = (
            ROOT / "static" / "js" / "emma-floating-chat.js"
        ).read_text(encoding="utf-8")

        self.assertIn("content.textContent = text", content)
        self.assertIn("details.sources", content)
        self.assertIn("details.suggestions", content)
        self.assertIn("details.confidence", content)

    def test_browser_history_is_limited_and_expires(self):
        paths = [
            ROOT / "static" / "js" / "emma-floating-chat.js",
            ROOT / "templates" / "assistant.html",
        ]

        for path in paths:
            content = path.read_text(encoding="utf-8")
            self.assertIn("historyRetentionMs", content)
            self.assertIn("maxStoredMessages = 40", content)
            self.assertIn("savedAt: Date.now()", content)
            self.assertIn("messages: conversation", content)
            self.assertIn('a[href$="/logout"]', content)

    def test_engine_does_not_execute_system_commands(self):
        paths = [
            ROOT / "services" / "assistant_engine.py",
            ROOT / "services" / "intent_router.py",
            ROOT / "services" / "knowledge_engine.py",
        ]
        forbidden_calls = {
            "eval",
            "exec",
            "system",
            "popen",
            "run",
            "call",
            "check_output",
        }

        for path in paths:
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue

                function_name = None
                if isinstance(node.func, ast.Name):
                    function_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    function_name = node.func.attr

                self.assertNotIn(
                    function_name,
                    forbidden_calls,
                    f"Appel dangereux trouvé dans {path.name}",
                )

    def test_active_emma_code_has_no_lab_ip(self):
        paths = [
            ROOT / "services" / "assistant_engine.py",
            ROOT / "services" / "assistant_router.py",
            ROOT / "services" / "prometheus_service.py",
            ROOT / "routes" / "help.py",
        ]

        for path in paths:
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("192.168.50.10", content, path.name)
            self.assertNotIn("192.168.50.20", content, path.name)

    def test_prometheus_labels_and_instances_are_configurable(self):
        service = PrometheusService(
            "http://prometheus.test:9090",
            node_exporter_job="custom-node",
            cadvisor_job="custom-cadvisor",
            node_exporter_instance="10.0.0.10:9100",
            cadvisor_instance="10.0.0.10:8080",
        )

        with patch.object(
            service,
            "query_scalar",
            return_value=1,
        ) as query:
            service.get_service_status_detailed()

        queries = " ".join(
            call.args[0]
            for call in query.call_args_list
        )
        self.assertIn("custom-node", queries)
        self.assertIn("custom-cadvisor", queries)
        self.assertIn("10.0.0.10:9100", queries)
        self.assertIn("10.0.0.10:8080", queries)


class EmmaServiceStateTests(unittest.TestCase):
    class FakePrometheus:
        def __init__(self, node="up", cadvisor="up", prometheus="up"):
            self.node = node
            self.cadvisor = cadvisor
            self.prometheus = prometheus

        def get_service_status_detailed(self):
            return {
                "node_exporter": self.node,
                "cadvisor": self.cadvisor,
            }

        def get_health_status(self):
            return self.prometheus

    class FakeSecurity:
        def __init__(self, grafana="up"):
            self.grafana = grafana

        def check_http_service_status(self, _url):
            return self.grafana

    def render(self, prometheus, security):
        app = Flask(__name__)
        app.config["GRAFANA_URL"] = "http://grafana:3000"
        app.extensions["prometheus_service"] = prometheus
        app.extensions["security_service"] = security

        with app.app_context():
            return services_answer()

    def test_unknown_is_not_reported_as_down(self):
        answer = self.render(
            self.FakePrometheus(
                node="unknown",
                cadvisor="up",
                prometheus="unknown",
            ),
            self.FakeSecurity(grafana="unknown"),
        )

        self.assertIn("Node Exporter : état inconnu", answer)
        self.assertIn("Prometheus : état inconnu", answer)
        self.assertIn("Grafana : état inconnu", answer)
        self.assertIn("Indisponibles : 0 | Inconnus : 3", answer)

    def test_confirmed_down_is_reported_as_unavailable(self):
        answer = self.render(
            self.FakePrometheus(cadvisor="down"),
            self.FakeSecurity(),
        )

        self.assertIn("cAdvisor : indisponible", answer)
        self.assertIn("Indisponibles : 1 | Inconnus : 0", answer)

    def test_service_answer_is_timestamped(self):
        answer = self.render(
            self.FakePrometheus(),
            self.FakeSecurity(),
        )

        self.assertIn("Contrôle effectué le", answer)
        self.assertIn("UTC", answer)


class EmmaApiTests(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config.update(
            SECRET_KEY="test-only-secret",
            TESTING=True,
        )

        auth = Blueprint("auth", __name__)

        @auth.get("/login")
        def login():
            return "login"

        app.register_blueprint(auth)
        app.register_blueprint(help_bp)
        self.app = app
        self.client = app.test_client()

    def authenticate(self):
        with self.client.session_transaction() as session:
            session["authenticated"] = True

    def test_api_requires_authentication(self):
        response = self.client.post(
            "/api/assistant",
            json={"question": "Bonjour"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_api_rejects_invalid_json_shape(self):
        self.authenticate()
        response = self.client.post(
            "/api/assistant",
            json=["question invalide"],
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Le corps JSON est invalide.",
        )

    def test_api_rejects_question_over_500_characters(self):
        self.authenticate()
        response = self.client.post(
            "/api/assistant",
            json={"question": "a" * 501},
        )

        self.assertEqual(response.status_code, 400)

    @patch("routes.help.build_assistant_response")
    def test_api_stores_small_conversation_context(self, mocked):
        mocked.return_value = {
            "answer": "Réponse",
            "intent": "services",
            "confidence": 0.9,
            "sources": ["test"],
            "suggestions": [],
            "used_live_data": True,
            "follow_up": False,
        }
        self.authenticate()

        response = self.client.post(
            "/api/assistant",
            json={"question": "État des services"},
        )

        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session:
            self.assertEqual(
                session["emma_context"],
                {
                    "last_question": "État des services",
                    "last_intent": "services",
                },
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
