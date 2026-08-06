
from routes.help import help_bp
from routes.audit import audit_bp
from flask import Flask
from config import Config
from extensions import initialize_services
from routes.auth import auth_bp
from routes.containers import containers_bp
from routes.dashboard import dashboard_bp
from routes.logs import logs_bp
from routes.monitoring import monitoring_bp
from routes.prometheus import prometheus_bp
from routes.security import security_bp
from routes.reports import reports_bp


def create_app() -> Flask:
    """Crée et configure l'application Flask."""

    app = Flask(__name__)

    app.config.from_object(Config)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY est absente. Vérifie le fichier .env."
        )

    initialize_services(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(containers_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(monitoring_bp)
    app.register_blueprint(prometheus_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(reports_bp)

    return app


app = create_app()



# VISITOR ANALYTICS REGISTRATION
from visitor_analytics import (
    register_visitor_analytics,
)

register_visitor_analytics(app)


# RECENT ACTIVITY SESSION
from recent_activity import register_recent_activity

register_recent_activity(app)


# DAILY ALERTS REGISTRATION
from daily_alerts import register_daily_alerts

register_daily_alerts(app)
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )
