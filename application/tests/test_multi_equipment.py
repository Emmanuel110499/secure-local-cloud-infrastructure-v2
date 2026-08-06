import unittest
from unittest.mock import patch
import sys
import types

try:
    import requests  # noqa: F401
except ModuleNotFoundError:
    requests_stub = types.ModuleType("requests")
    requests_stub.RequestException = RuntimeError
    requests_stub.get = None
    sys.modules["requests"] = requests_stub

from services.prometheus_service import PrometheusService


EQUIPMENTS = {
    "srv-web": {
        "id": "srv-web",
        "name": "srv-web",
        "role": "Serveur applicatif",
        "os": "linux",
        "job": "srv-web",
        "instance": "10.0.0.10:9100",
        "docker_job": "cadvisor",
        "docker_instance": "10.0.0.10:8080",
    },
    "srv-monitoring": {
        "id": "srv-monitoring",
        "name": "srv-monitoring",
        "role": "Serveur d’observabilité",
        "os": "linux",
        "job": "srv-monitoring",
        "instance": "10.0.0.20:9100",
    },
    "pc-emmanuel": {
        "id": "pc-emmanuel",
        "name": "PC Emmanuel",
        "role": "Poste d’administration",
        "os": "windows",
        "job": "pc-windows",
        "instance": "10.0.0.1:9182",
        "equipment_label": "pc-emmanuel",
    },
}


def make_service():
    return PrometheusService(
        "http://prometheus.test:9090",
        node_exporter_job="srv-web",
        cadvisor_job="cadvisor",
        node_exporter_instance="10.0.0.10:9100",
        cadvisor_instance="10.0.0.10:8080",
        equipments=EQUIPMENTS,
    )


class MultiEquipmentTests(unittest.TestCase):
    def test_catalog_does_not_expose_instances(self):
        catalog = make_service().get_equipment_catalog()

        self.assertEqual(len(catalog), 3)
        self.assertNotIn("instance", catalog[0])
        self.assertEqual(catalog[2]["os"], "windows")

    def test_unknown_equipment_returns_none(self):
        self.assertIsNone(
            make_service().get_equipment_metrics("not-configured")
        )

    def test_linux_metrics_use_selected_job_and_instance(self):
        service = make_service()

        with patch.object(service, "query_scalar", return_value=1) as query:
            result = service.get_equipment_metrics("srv-monitoring")

        queries = " ".join(call.args[0] for call in query.call_args_list)
        self.assertIn('job="srv-monitoring"', queries)
        self.assertIn('instance="10.0.0.20:9100"', queries)
        self.assertEqual(result["state"], "up")

    def test_windows_metrics_include_battery(self):
        service = make_service()

        with patch.object(service, "query_scalar", return_value=1) as query:
            result = service.get_equipment_metrics("pc-emmanuel")

        queries = " ".join(call.args[0] for call in query.call_args_list)
        self.assertIn("windows_cpu_time_total", queries)
        self.assertIn("secure_windows_battery_charge_percent", queries)
        self.assertEqual(
            result["metrics"]["battery"]["charge_percent"],
            1,
        )

    def test_missing_target_is_unknown_not_down(self):
        service = make_service()

        with patch.object(service, "query_scalar", return_value=None):
            result = service.get_equipment_metrics("srv-web")

        self.assertEqual(result["state"], "unknown")
        self.assertIsNone(result["metrics"]["cpu"])


if __name__ == "__main__":
    unittest.main()
