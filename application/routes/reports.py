from datetime import datetime
from io import BytesIO
import socket
from xml.sax.saxutils import escape

from flask import (
    Blueprint,
    current_app,
    send_file,
    session,
)

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    ParagraphStyle,
    getSampleStyleSheet,
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from decorators import login_required


reports_bp = Blueprint(
    "reports",
    __name__,
)


def safe_value(value, default="Indisponible"):
    if value is None or value == "":
        return default

    return value


def format_percent(value):
    try:
        return f"{float(value):.1f} %"
    except (TypeError, ValueError):
        return "Indisponible"


def status_label(value):
    return "Opérationnel" if value else "Indisponible"


def add_page_decoration(canvas, document):
    canvas.saveState()

    width, height = A4

    canvas.setFillColor(
        colors.HexColor("#1746BD")
    )
    canvas.rect(
        0,
        height - 13 * mm,
        width,
        13 * mm,
        fill=1,
        stroke=0,
    )

    canvas.setFillColor(
        colors.HexColor("#FFFFFF")
    )
    canvas.setFont(
        "Helvetica-Bold",
        9,
    )
    canvas.drawString(
        17 * mm,
        height - 8.5 * mm,
        "SECURE LOCAL CLOUD INFRASTRUCTURE",
    )

    canvas.setFillColor(
        colors.HexColor("#64748B")
    )
    canvas.setFont(
        "Helvetica",
        8,
    )
    canvas.drawString(
        17 * mm,
        10 * mm,
        "Rapport automatique de supervision",
    )

    canvas.drawRightString(
        width - 17 * mm,
        10 * mm,
        f"Page {document.page}",
    )

    canvas.restoreState()


@reports_bp.route("/export/pdf")
@login_required
def export_pdf():
    prometheus = current_app.extensions[
        "prometheus_service"
    ]

    docker_service = current_app.extensions[
        "docker_service"
    ]

    security_service = current_app.extensions[
        "security_service"
    ]

    metrics = prometheus.get_system_metrics()
    containers = docker_service.list_containers()
    security = security_service.get_security_status()

    try:
        from routes.dashboard import (
            get_complete_services_status,
        )

        services = get_complete_services_status()

    except Exception:
        services = prometheus.get_service_status()

    generated_at = datetime.now()

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=22 * mm,
        bottomMargin=18 * mm,
        title="Rapport Secure Local Cloud Infrastructure",
        author="Secure Local Cloud Infrastructure",
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=27,
        textColor=colors.HexColor("#17243C"),
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=15,
        textColor=colors.HexColor("#64748B"),
        alignment=TA_CENTER,
        spaceAfter=8 * mm,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#1746BD"),
        spaceBefore=5 * mm,
        spaceAfter=4 * mm,
    )

    normal_style = ParagraphStyle(
        "ReportNormal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=14,
        textColor=colors.HexColor("#334155"),
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#64748B"),
    )

    story = []

    story.append(
        Paragraph(
            "Secure Local Cloud Infrastructure",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Rapport de supervision et d’état de l’infrastructure",
            subtitle_style,
        )
    )

    general_data = [
        [
            "Date de génération",
            generated_at.strftime(
                "%d/%m/%Y à %H:%M:%S"
            ),
        ],
        [
            "Utilisateur",
            safe_value(
                session.get("username"),
                "Utilisateur authentifié",
            ),
        ],
        [
            "Serveur",
            socket.gethostname(),
        ],
        [
            "Adresse du serveur",
            "192.168.50.10",
        ],
        [
            "État général",
            (
                "Infrastructure opérationnelle"
                if all(services.values())
                else "Vérification nécessaire"
            ),
        ],
    ]

    general_table = Table(
        general_data,
        colWidths=[
            55 * mm,
            110 * mm,
        ],
    )

    general_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.HexColor("#EDF3FF"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (0, -1),
                colors.HexColor("#1746BD"),
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (1, 0),
                (1, -1),
                "Helvetica",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                9,
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#D6E2F5"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(general_table)
    story.append(Spacer(1, 5 * mm))

    story.append(
        Paragraph(
            "1. Ressources système",
            heading_style,
        )
    )

    metrics_data = [
        [
            "Indicateur",
            "Valeur actuelle",
            "Interprétation",
        ],
        [
            "CPU",
            format_percent(
                metrics.get("cpu")
            ),
            (
                "Utilisation normale"
                if float(metrics.get("cpu", 0) or 0) < 80
                else "Utilisation élevée"
            ),
        ],
        [
            "Mémoire RAM",
            format_percent(
                metrics.get("memory")
            ),
            (
                "Utilisation normale"
                if float(metrics.get("memory", 0) or 0) < 85
                else "Utilisation élevée"
            ),
        ],
        [
            "Disque",
            format_percent(
                metrics.get("disk")
            ),
            (
                "Espace disponible"
                if float(metrics.get("disk", 0) or 0) < 85
                else "Espace faible"
            ),
        ],
        [
            "Charge système",
            safe_value(
                metrics.get("load_1m")
            ),
            "Charge moyenne sur une minute",
        ],
        [
            "Temps de fonctionnement",
            safe_value(
                metrics.get("uptime")
            ),
            "Durée depuis le dernier redémarrage",
        ],
    ]

    metrics_table = Table(
        metrics_data,
        colWidths=[
            45 * mm,
            42 * mm,
            78 * mm,
        ],
        repeatRows=1,
    )

    metrics_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1746BD"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5,
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F7F9FD"),
                ],
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#DCE5F2"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(metrics_table)

    story.append(
        Paragraph(
            "2. État des services",
            heading_style,
        )
    )

    service_names = {
        "flask": "Application Flask",
        "prometheus": "Prometheus",
        "grafana": "Grafana",
        "node_exporter": "Node Exporter",
        "cadvisor": "cAdvisor",
        "alertmanager": "Alertmanager",
    }

    services_data = [
        [
            "Service",
            "État",
        ]
    ]

    for name, value in services.items():
        services_data.append([
            service_names.get(
                name,
                name.replace("_", " ").title(),
            ),
            status_label(value),
        ])

    services_table = Table(
        services_data,
        colWidths=[
            105 * mm,
            60 * mm,
        ],
        repeatRows=1,
    )

    services_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1746BD"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F7F9FD"),
                ],
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#DCE5F2"),
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.5,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(services_table)

    story.append(PageBreak())

    story.append(
        Paragraph(
            "3. Conteneurs Docker",
            heading_style,
        )
    )

    containers_data = [[
        "Conteneur",
        "Image",
        "État",
        "CPU",
        "Mémoire",
        "Uptime",
    ]]

    if containers:
        for container in containers:
            containers_data.append([
                safe_value(
                    container.get("name")
                ),
                Paragraph(
                    escape(
                        str(
                            safe_value(
                                container.get("image")
                            )
                        )
                    ),
                    small_style,
                ),
                safe_value(
                    container.get("status")
                ),
                format_percent(
                    container.get("cpu")
                ),
                (
                    f"{safe_value(container.get('memory_mb'), 0)} Mo"
                ),
                safe_value(
                    container.get("uptime")
                ),
            ])

    else:
        containers_data.append([
            "Aucun conteneur détecté",
            "-",
            "-",
            "-",
            "-",
            "-",
        ])

    containers_table = Table(
        containers_data,
        colWidths=[
            35 * mm,
            44 * mm,
            22 * mm,
            18 * mm,
            24 * mm,
            25 * mm,
        ],
        repeatRows=1,
    )

    containers_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1746BD"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, -1),
                "Helvetica",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                7.2,
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F7F9FD"),
                ],
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#DCE5F2"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6,
            ),
        ])
    )

    story.append(containers_table)

    story.append(
        Paragraph(
            "4. État de la sécurité",
            heading_style,
        )
    )

    https_status = security.get(
        "https",
        {},
    )

    security_data = [
        [
            "Protection",
            "État",
            "Information",
        ],
        [
            "HTTPS / TLS",
            status_label(
                https_status.get("enabled")
            ),
            (
                "Expiration : "
                + str(
                    safe_value(
                        https_status.get("expires_at")
                    )
                )
            ),
        ],
        [
            "Authentification",
            status_label(
                security.get("authentication")
            ),
            "Accès aux pages protégé par session",
        ],
        [
            "Pare-feu UFW",
            status_label(
                security.get("ufw")
            ),
            "Filtrage des connexions entrantes",
        ],
        [
            "Fail2ban",
            status_label(
                security.get("fail2ban")
            ),
            "Protection contre les tentatives répétées",
        ],
        [
            "Nginx",
            status_label(
                security.get("nginx")
            ),
            "Reverse proxy applicatif",
        ],
        [
            "Alertmanager",
            status_label(
                security.get("alertmanager")
            ),
            "Gestion et routage des alertes",
        ],
    ]

    security_table = Table(
        security_data,
        colWidths=[
            48 * mm,
            38 * mm,
            79 * mm,
        ],
        repeatRows=1,
    )

    security_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1746BD"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F7F9FD"),
                ],
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#DCE5F2"),
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8.2,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    story.append(security_table)

    story.append(
        Paragraph(
            "5. Recommandations",
            heading_style,
        )
    )

    recommendations = []

    cpu = float(
        metrics.get("cpu", 0) or 0
    )
    memory = float(
        metrics.get("memory", 0) or 0
    )
    disk = float(
        metrics.get("disk", 0) or 0
    )

    if cpu >= 80:
        recommendations.append(
            "Analyser les processus responsables de la forte utilisation CPU."
        )

    if memory >= 85:
        recommendations.append(
            "Contrôler les applications consommant le plus de mémoire."
        )

    if disk >= 85:
        recommendations.append(
            "Libérer de l’espace disque ou augmenter la capacité de stockage."
        )

    unavailable_services = [
        service_names.get(
            name,
            name,
        )
        for name, value in services.items()
        if not value
    ]

    if unavailable_services:
        recommendations.append(
            "Vérifier les services indisponibles : "
            + ", ".join(unavailable_services)
            + "."
        )

    days_remaining = https_status.get(
        "days_remaining"
    )

    if (
        isinstance(days_remaining, int)
        and days_remaining <= 30
    ):
        recommendations.append(
            "Renouveler prochainement le certificat TLS."
        )

    recommendations.extend([
        "Contrôler régulièrement les journaux SSH et Fail2ban.",
        "Tester périodiquement la réception des alertes Alertmanager.",
        "Conserver une sauvegarde de la configuration Docker et de l’application.",
    ])

    for number, recommendation in enumerate(
        recommendations,
        start=1,
    ):
        story.append(
            Paragraph(
                (
                    f"<b>{number}.</b> "
                    f"{escape(str(recommendation))}"
                ),
                normal_style,
            )
        )

        story.append(
            Spacer(
                1,
                2.5 * mm,
            )
        )

    story.append(
        Spacer(
            1,
            5 * mm,
        )
    )

    story.append(
        Paragraph(
            (
                "Ce rapport a été généré automatiquement à partir "
                "des données actuellement disponibles sur la plateforme. "
                "Il constitue une aide à la supervision et ne remplace pas "
                "une analyse approfondie par un administrateur."
            ),
            small_style,
        )
    )

    document.build(
        story,
        onFirstPage=add_page_decoration,
        onLaterPages=add_page_decoration,
    )

    buffer.seek(0)

    filename = (
        "secure-local-cloud-report-"
        + generated_at.strftime("%Y%m%d-%H%M%S")
        + ".pdf"
    )

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
        max_age=0,
    )
