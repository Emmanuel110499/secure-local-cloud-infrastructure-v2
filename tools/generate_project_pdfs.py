from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Flowable, Frame, KeepTogether, PageBreak, PageTemplate,
    Image as RLImage, Paragraph, Spacer, Table, TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf"
OUTPUT.mkdir(parents=True, exist_ok=True)

NAVY = colors.HexColor("#0B1F3A")
BLUE = colors.HexColor("#2563EB")
CYAN = colors.HexColor("#0891B2")
GREEN = colors.HexColor("#059669")
AMBER = colors.HexColor("#D97706")
RED = colors.HexColor("#DC2626")
INK = colors.HexColor("#14213D")
MUTED = colors.HexColor("#5F6F89")
PALE = colors.HexColor("#F3F7FD")
LINE = colors.HexColor("#D8E2F0")
WHITE = colors.white


class NumberedDocTemplate(BaseDocTemplate):
    def __init__(self, filename: str, title: str, audience: str):
        self.report_title = title
        self.audience = audience
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=21 * mm,
            bottomMargin=18 * mm,
            title=title,
            author="Secure Local Cloud Infrastructure",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="body",
        )
        self.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=self._page))

    def _page(self, canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 11 * mm, A4[0], 11 * mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(18 * mm, A4[1] - 7 * mm, "SECURE LOCAL CLOUD")
        canvas.setFont("Helvetica", 7.5)
        canvas.drawRightString(A4[0] - 18 * mm, A4[1] - 7 * mm, self.audience)
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(18 * mm, 8 * mm, self.report_title[:74])
        canvas.drawRightString(A4[0] - 18 * mm, 8 * mm, f"Page {doc.page}")
        canvas.restoreState()

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in {"H1", "H2"}:
            level = 0 if flowable.style.name == "H1" else 1
            text = flowable.getPlainText()
            key = f"section-{self.seq.nextf('section')}"
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text, key, level=level, closed=False)
            self.notify("TOCEntry", (level, text, self.page, key))


def styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="Helvetica-Bold", fontSize=26, leading=30, textColor=WHITE, alignment=TA_LEFT, spaceAfter=10),
        "subtitle": ParagraphStyle("CoverSubtitle", parent=base["BodyText"], fontSize=11, leading=16, textColor=colors.HexColor("#DCE8FF")),
        "h1": ParagraphStyle("H1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceBefore=10, spaceAfter=8, keepWithNext=True),
        "h2": ParagraphStyle("H2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=BLUE, spaceBefore=9, spaceAfter=5, keepWithNext=True),
        "h3": ParagraphStyle("H3", parent=base["Heading3"], fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=INK, spaceBefore=7, spaceAfter=4, keepWithNext=True),
        "body": ParagraphStyle("Body", parent=base["BodyText"], fontName="Helvetica", fontSize=9.2, leading=13.2, textColor=INK, spaceAfter=5),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontSize=7.8, leading=10.5, textColor=MUTED),
        "bullet": ParagraphStyle("Bullet", parent=base["BodyText"], fontSize=9, leading=12.5, leftIndent=12, firstLineIndent=-7, bulletIndent=3, textColor=INK, spaceAfter=3),
        "code": ParagraphStyle("Code", parent=base["Code"], fontName="Courier", fontSize=7.2, leading=9.5, textColor=colors.HexColor("#E6EDF7"), backColor=NAVY, borderPadding=8, borderRadius=4, spaceBefore=4, spaceAfter=7),
        "callout": ParagraphStyle("Callout", parent=base["BodyText"], fontSize=9, leading=13, textColor=INK, backColor=colors.HexColor("#EAF2FF"), borderColor=colors.HexColor("#BFD2FA"), borderWidth=0.7, borderPadding=8, leftIndent=0, spaceBefore=4, spaceAfter=8),
        "warning": ParagraphStyle("Warning", parent=base["BodyText"], fontSize=9, leading=13, textColor=colors.HexColor("#7C2D12"), backColor=colors.HexColor("#FFF4E5"), borderColor=colors.HexColor("#FDBA74"), borderWidth=0.7, borderPadding=8, spaceBefore=4, spaceAfter=8),
    }


S = styles()


def cover(title: str, subtitle: str, label: str, version: str = "Edition 2026"):
    block = Table(
        [[Paragraph(label.upper(), S["small"])], [Paragraph(title, S["title"])], [Paragraph(subtitle, S["subtitle"])], [Spacer(1, 8 * mm)], [Paragraph(version, S["subtitle"])]],
        colWidths=[174 * mm],
        rowHeights=[10 * mm, None, None, 10 * mm, 12 * mm],
    )
    block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("TEXTCOLOR", (0, 0), (0, 0), colors.HexColor("#7DD3FC")),
        ("BOX", (0, 0), (-1, -1), 0, NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 15 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 15 * mm),
        ("TOPPADDING", (0, 0), (-1, 0), 9 * mm),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 9 * mm),
    ]))
    return [Spacer(1, 22 * mm), block, Spacer(1, 12 * mm), Paragraph("Document de référence - aucune valeur secrète n’est incluse.", S["small"]), PageBreak()]


def toc():
    t = TableOfContents()
    t.levelStyles = [
        ParagraphStyle("TOC1", fontName="Helvetica-Bold", fontSize=10, leading=14, leftIndent=0, textColor=NAVY, spaceBefore=3),
        ParagraphStyle("TOC2", fontName="Helvetica", fontSize=8.5, leading=12, leftIndent=12, textColor=MUTED),
    ]
    return [Paragraph("Sommaire", S["h1"]), t, PageBreak()]


def p(text: str, style="body"):
    return Paragraph(text, S[style])


def bullets(items):
    return [Paragraph(f"• {escape(item)}", S["bullet"]) for item in items]


def code(text: str):
    return Paragraph(escape(text).replace("\n", "<br/>"), S["code"])


def table(headers, rows, widths=None, font=7.7):
    data = [[Paragraph(f"<b>{escape(str(x))}</b>", S["small"]) for x in headers]]
    for row in rows:
        data.append([Paragraph(escape(str(x)).replace("\n", "<br/>"), ParagraphStyle("Cell", parent=S["small"], fontSize=font, leading=font + 2, textColor=INK)) for x in row])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, PALE]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def architecture_diagram():
    d = Drawing(480, 300)
    def box(x, y, w, h, title, lines, fill, stroke=LINE):
        d.add(Rect(x, y, w, h, rx=8, ry=8, fillColor=fill, strokeColor=stroke, strokeWidth=1))
        d.add(String(x + 9, y + h - 17, title, fontName="Helvetica-Bold", fontSize=9, fillColor=NAVY))
        for idx, line in enumerate(lines):
            d.add(String(x + 9, y + h - 32 - idx * 12, line, fontName="Helvetica", fontSize=7.2, fillColor=INK))
    box(185, 250, 110, 38, "Internet + Cloudflare", ["DNS, HTTPS, Zero Trust"], colors.HexColor("#E0F2FE"), CYAN)
    box(176, 185, 128, 45, "srv-web", ["cloudflared -> Nginx", "Flask/Gunicorn, Docker"], colors.HexColor("#EAF2FF"), BLUE)
    box(22, 82, 192, 78, "srv-monitoring", ["Prometheus :9090", "Grafana :3000", "Alertmanager :9093", "Node Exporter :9100"], colors.HexColor("#ECFDF5"), GREEN)
    box(266, 82, 192, 78, "PC Emmanuel", ["Windows Exporter :9182", "Collecteur batterie", "SSH + navigateur", "Réplication des sauvegardes"], colors.HexColor("#FFF7ED"), AMBER)
    box(22, 8, 192, 48, "Volumes persistants", ["Prometheus, Grafana, Alertmanager"], colors.HexColor("#F5F3FF"))
    box(266, 8, 192, 48, "Sauvegardes PC", ["Archives + SHA-256 vérifié"], colors.HexColor("#F5F3FF"))
    for x1, y1, x2, y2, label in [
        (240, 250, 240, 230, "Tunnel chiffré"), (210, 185, 140, 160, "API Prometheus"),
        (275, 185, 350, 160, "HTTPS / admin"), (118, 82, 118, 56, "données"),
        (362, 82, 362, 56, "SCP"), (214, 120, 266, 120, "scrape 15 s"),
    ]:
        d.add(Line(x1, y1, x2, y2, strokeColor=BLUE, strokeWidth=1.4))
        d.add(String((x1+x2)/2 + 3, (y1+y2)/2 + 3, label, fontName="Helvetica", fontSize=6.5, fillColor=MUTED))
    return d


def code_map_diagram():
    d = Drawing(480, 220)
    boxes = [
        (10, 150, "app.py", "création Flask"), (125, 150, "routes/", "pages et API"),
        (240, 150, "services/", "logique métier"), (355, 150, "Prometheus", "PromQL / métriques"),
        (65, 65, "templates/", "HTML Jinja"), (205, 65, "static/", "CSS et JavaScript"),
        (345, 65, "data/", "état local privé"),
    ]
    for x, y, title, subtitle in boxes:
        d.add(Rect(x, y, 105, 46, rx=6, ry=6, fillColor=PALE, strokeColor=BLUE))
        d.add(String(x+8, y+27, title, fontName="Helvetica-Bold", fontSize=9, fillColor=NAVY))
        d.add(String(x+8, y+12, subtitle, fontName="Helvetica", fontSize=7, fillColor=MUTED))
    for x1,y1,x2,y2 in [(115,173,125,173),(230,173,240,173),(345,173,355,173),(177,150,115,111),(177,150,257,111),(292,150,397,111)]:
        d.add(Line(x1,y1,x2,y2,strokeColor=GREEN,strokeWidth=1.5))
    d.add(String(10, 20, "Flux principal : requête -> route -> service -> Prometheus -> réponse -> interface", fontName="Helvetica-Bold", fontSize=8, fillColor=INK))
    return d


def full_architecture_diagram():
    """Architecture physique détaillée, lisible sur une page complète."""
    d = Drawing(480, 590)

    def box(x, y, w, h, title, lines, fill, stroke=BLUE):
        d.add(Rect(x, y, w, h, rx=8, ry=8, fillColor=fill, strokeColor=stroke, strokeWidth=1.2))
        d.add(String(x + 10, y + h - 18, title, fontName="Helvetica-Bold", fontSize=10, fillColor=NAVY))
        for idx, line in enumerate(lines):
            d.add(String(x + 10, y + h - 34 - idx * 13, line, fontName="Helvetica", fontSize=7.5, fillColor=INK))

    def arrow(x1, y1, x2, y2, label):
        d.add(Line(x1, y1, x2, y2, strokeColor=BLUE, strokeWidth=1.7))
        d.add(String((x1 + x2) / 2 + 4, (y1 + y2) / 2 + 4, label, fontName="Helvetica-Bold", fontSize=6.7, fillColor=MUTED))

    d.add(String(8, 570, "ARCHITECTURE PHYSIQUE ET EMPLACEMENT DES SERVICES", fontName="Helvetica-Bold", fontSize=12, fillColor=NAVY))
    box(150, 512, 180, 42, "UTILISATEUR INTERNET", ["Navigateur - https://app.emmanuelinfra.fr"], colors.HexColor("#E0F2FE"), CYAN)
    box(150, 445, 180, 48, "CLOUDFLARE", ["DNS public - terminaison HTTPS", "Zero Trust - tunnel sortant"], colors.HexColor("#EAF2FF"), BLUE)
    box(24, 278, 202, 135, "srv-web - 192.168.50.10", [
        "Hôte Ubuntu / VM VMware", "cloudflared : tunnel vers Cloudflare", "Nginx : reverse proxy HTTPS local",
        "Docker : secure-web-app-v2", "Gunicorn -> application Flask :5000", "Node Exporter :9100 - cAdvisor :8080",
        "Données : comptes, historique, rapports"
    ], colors.HexColor("#EFF6FF"), BLUE)
    box(254, 278, 202, 135, "srv-monitoring - 192.168.50.20", [
        "Hôte Ubuntu / VM VMware", "Prometheus :9090 - collecte et règles", "Grafana :3000 - tableaux avancés",
        "Alertmanager :9093 - routage Telegram", "Node Exporter :9100", "Volumes Docker persistants :",
        "prometheus-data / grafana-data / alertmanager-data"
    ], colors.HexColor("#ECFDF5"), GREEN)
    box(24, 112, 202, 126, "PC EMMANUEL - 192.168.154.1", [
        "Windows - poste d'administration", "Navigateur et accès SSH aux deux VM", "Windows Exporter :9182",
        "Collecteur batterie personnalisé", "CPU, RAM, disque C:, réseau, batterie", "Copie locale des sauvegardes vérifiées"
    ], colors.HexColor("#FFF7ED"), AMBER)
    box(254, 112, 202, 126, "RÉSEAUX PRIVÉS", [
        "192.168.50.0/24 : services et scraping", "192.168.154.0/24 : administration",
        "VMware NAT : sortie Internet des VM", "Docker bridge : échanges conteneurs", "Pare-feu : ports limités aux sources autorisées"
    ], colors.HexColor("#F5F3FF"), colors.HexColor("#7C3AED"))
    box(24, 24, 432, 58, "DESTINATION DE SECOURS HORS VM", [
        r"C:\Users\Emman\SecureLocalCloud-Backups\srv-web", r"C:\Users\Emman\SecureLocalCloud-Backups\srv-monitoring",
        "Archives .tar.gz + fichiers .sha256 + journal de réplication"
    ], colors.HexColor("#FEF2F2"), RED)
    arrow(240, 512, 240, 493, "HTTPS 443")
    arrow(200, 445, 125, 413, "tunnel chiffré")
    arrow(226, 346, 254, 346, "PromQL / API")
    arrow(125, 278, 125, 238, "administration")
    arrow(355, 278, 355, 238, "réseau privé")
    arrow(125, 112, 125, 82, "réplication SCP")
    return d


def equipment_architecture_diagram():
    """Schéma vectoriel avec dessins d'équipements et technologies localisées."""
    d = Drawing(480, 630)

    def label(x, y, text, size=7.2, bold=False, color=INK):
        d.add(String(x, y, text, fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size, fillColor=color))

    def arrow(x1, y1, x2, y2, caption):
        d.add(Line(x1, y1, x2, y2, strokeColor=BLUE, strokeWidth=1.8))
        angle = 5
        d.add(Polygon([x2, y2, x2-angle, y2+angle, x2+angle, y2+angle], fillColor=BLUE, strokeColor=BLUE))
        label((x1+x2)/2+5, (y1+y2)/2+4, caption, 6.3, True, MUTED)

    def server_icon(x, y, width=84, height=43):
        d.add(Rect(x, y, width, height, rx=4, ry=4, fillColor=colors.HexColor("#CBD5E1"), strokeColor=NAVY, strokeWidth=1.2))
        for row in range(2):
            yy = y + 8 + row * 15
            d.add(Rect(x+8, yy, width-27, 10, rx=2, ry=2, fillColor=colors.HexColor("#334155"), strokeColor=colors.HexColor("#64748B")))
            for slot in range(5):
                d.add(Rect(x+13+slot*9, yy+3, 6, 4, fillColor=colors.HexColor("#0F172A"), strokeColor=None))
            d.add(Circle(x+width-12, yy+5, 2.4, fillColor=GREEN, strokeColor=None))
        d.add(Rect(x+width-5, y+5, 4, height-10, fillColor=colors.HexColor("#94A3B8"), strokeColor=NAVY))

    def pc_icon(x, y):
        d.add(Rect(x, y+16, 86, 55, rx=5, ry=5, fillColor=colors.HexColor("#1E293B"), strokeColor=NAVY, strokeWidth=1.2))
        d.add(Rect(x+6, y+22, 74, 43, fillColor=colors.HexColor("#DBEAFE"), strokeColor=BLUE))
        d.add(Line(x+43, y+16, x+43, y+8, strokeColor=NAVY, strokeWidth=2))
        d.add(Rect(x+25, y+3, 36, 6, rx=2, ry=2, fillColor=colors.HexColor("#64748B"), strokeColor=NAVY))
        # Windows-like four-pane mark, kept generic.
        for dx, dy in ((23,39),(42,39),(23,24),(42,24)):
            d.add(Rect(x+dx, y+dy, 14, 11, fillColor=BLUE, strokeColor=WHITE, strokeWidth=.5))

    def nas_icon(x, y):
        d.add(Rect(x, y, 78, 75, rx=8, ry=8, fillColor=colors.HexColor("#334155"), strokeColor=NAVY, strokeWidth=1.2))
        for idx in range(4):
            d.add(Rect(x+9+idx*16, y+16, 12, 45, rx=2, ry=2, fillColor=colors.HexColor("#0F172A"), strokeColor=colors.HexColor("#64748B")))
            d.add(Circle(x+15+idx*16, y+23, 1.8, fillColor=GREEN, strokeColor=None))
        d.add(Circle(x+68, y+65, 3, fillColor=GREEN, strokeColor=None))

    def cloud_icon(cx, cy):
        for ox, oy, radius in ((-30,0,17),(-12,12,23),(12,15,27),(35,2,19),(5,-2,32)):
            d.add(Circle(cx+ox, cy+oy, radius, fillColor=colors.HexColor("#E0F2FE"), strokeColor=CYAN, strokeWidth=1))

    def switch_icon(x, y):
        d.add(Rect(x, y, 118, 31, rx=5, ry=5, fillColor=colors.HexColor("#334155"), strokeColor=NAVY))
        for idx in range(8):
            d.add(Rect(x+10+idx*11, y+11, 8, 7, fillColor=colors.HexColor("#0F172A"), strokeColor=colors.HexColor("#64748B")))
        for idx in range(3):
            d.add(Circle(x+101+idx*5, y+23, 1.6, fillColor=GREEN, strokeColor=None))

    def equipment_card(x, y, width, height, title, subtitle, icon_fn, technologies, accent):
        d.add(Rect(x, y, width, height, rx=10, ry=10, fillColor=WHITE, strokeColor=accent, strokeWidth=1.5))
        d.add(Rect(x, y+height-30, width, 30, rx=10, ry=10, fillColor=accent, strokeColor=accent))
        label(x+10, y+height-20, title, 10, True, WHITE)
        label(x+10, y+height-42, subtitle, 7, True, MUTED)
        icon_fn(x+12, y+height-98)
        tx = x+106
        ty = y+height-57
        for name, role in technologies:
            d.add(Circle(tx, ty+2, 2.4, fillColor=accent, strokeColor=None))
            label(tx+7, ty, name, 7.3, True, NAVY)
            label(tx+7, ty-10, role, 6.3, False, MUTED)
            ty -= 27

    label(8, 611, "ARCHITECTURE GÉNÉRALE - ÉQUIPEMENTS, SERVICES ET FLUX", 12, True, NAVY)
    cloud_icon(240, 566)
    label(184, 522, "INTERNET + CLOUDFLARE", 9, True, NAVY)
    label(174, 510, "DNS public - HTTPS - Zero Trust", 7, False, MUTED)
    switch_icon(181, 458)
    label(199, 469, "PASSERELLE / RÉSEAU", 7.2, True, WHITE)
    arrow(240, 510, 240, 489, "HTTPS")

    equipment_card(8, 238, 225, 188, "srv-web - 192.168.50.10", "Serveur applicatif Ubuntu", server_icon, [
        ("cloudflared", "tunnel sortant Cloudflare"), ("Nginx", "reverse proxy HTTPS"),
        ("Docker", "conteneur secure-web-app-v2"), ("Gunicorn", "serveur WSGI"),
        ("Flask", "interface, routes et API"), ("Exporters", "Node Exporter + cAdvisor"),
    ], BLUE)
    equipment_card(247, 238, 225, 188, "srv-monitoring - 192.168.50.20", "Serveur d'observabilité Ubuntu", server_icon, [
        ("Prometheus", "collecte, PromQL et historique"), ("Grafana", "tableaux avancés"),
        ("Alertmanager", "routage des alertes Telegram"), ("Node Exporter", "métriques Linux"),
        ("Volumes Docker", "données persistantes"), ("Règles", "17 contrôles opérationnels"),
    ], GREEN)
    arrow(210, 458, 120, 426, "tunnel vers srv-web")
    arrow(270, 458, 360, 426, "accès monitoring")
    d.add(Line(233, 330, 247, 330, strokeColor=CYAN, strokeWidth=2))
    label(212, 338, "scrape 15 s", 6.5, True, CYAN)

    d.add(Rect(8, 62, 225, 150, rx=10, ry=10, fillColor=WHITE, strokeColor=AMBER, strokeWidth=1.5))
    d.add(Rect(8, 182, 225, 30, rx=10, ry=10, fillColor=AMBER, strokeColor=AMBER))
    label(18, 192, "PC Windows - 192.168.154.1", 10, True, WHITE)
    pc_icon(20, 83)
    for idx, (name, role) in enumerate([
        ("Navigateur + SSH", "administration"), ("Windows Exporter", "CPU, RAM, disque, réseau"),
        ("Collecteur batterie", "charge et secteur"), ("Tâche planifiée", "réplication des sauvegardes"),
    ]):
        yy=161-idx*27
        label(119, yy, name, 7.2, True, NAVY); label(119, yy-10, role, 6.2, False, MUTED)

    d.add(Rect(247, 62, 225, 150, rx=10, ry=10, fillColor=WHITE, strokeColor=AMBER, strokeWidth=1.5))
    d.add(Rect(247, 182, 225, 30, rx=10, ry=10, fillColor=AMBER, strokeColor=AMBER))
    label(257, 192, "Stockage de secours hors VM", 10, True, WHITE)
    nas_icon(260, 87)
    for idx, (name, role) in enumerate([
        ("Archives tar.gz", "srv-web + srv-monitoring"), ("SHA-256", "contrôle d'intégrité"),
        ("Copie SCP", "vers le PC Windows"), ("Journal", "preuve de réplication"),
    ]):
        yy=161-idx*27
        label(359, yy, name, 7.2, True, NAVY); label(359, yy-10, role, 6.2, False, MUTED)
    arrow(120, 238, 120, 212, "administration")
    arrow(360, 238, 360, 212, "copie SCP")
    label(8, 34, "Réseau services : 192.168.50.0/24    |    Réseau administration : 192.168.154.0/24", 7.5, True, NAVY)
    label(8, 19, "Chaque technologie est placée sur l'équipement où elle s'exécute réellement.", 7.2, False, MUTED)
    return d


def supervision_flow_diagram():
    d = Drawing(480, 315)
    nodes = [
        (8, 226, 104, 54, "EXPORTERS", ["Node Exporter", "cAdvisor", "Windows Exporter"]),
        (136, 226, 104, 54, "PROMETHEUS", ["scrape 15 s", "PromQL + historique"]),
        (264, 226, 104, 54, "RÈGLES", ["17 alertes", "pending -> firing"]),
        (392, 226, 80, 54, "ALERTMANAGER", ["groupement", "routage"]),
        (264, 105, 104, 54, "FLASK", ["API JSON", "normalisation"]),
        (136, 105, 104, 54, "INTERFACE", ["KPI + graphes", "Emma_IA"]),
        (392, 105, 80, 54, "TELEGRAM", ["firing", "resolved"]),
    ]
    for x, y, w, h, title, lines in nodes:
        d.add(Rect(x, y, w, h, rx=7, ry=7, fillColor=PALE, strokeColor=BLUE, strokeWidth=1.1))
        d.add(String(x + 7, y + h - 16, title, fontName="Helvetica-Bold", fontSize=8.5, fillColor=NAVY))
        for idx, line in enumerate(lines):
            d.add(String(x + 7, y + h - 31 - idx * 11, line, fontName="Helvetica", fontSize=6.8, fillColor=INK))
    for x1, y1, x2, y2, label in [
        (112,253,136,253,"métriques"),(240,253,264,253,"évalue"),(368,253,392,253,"envoie"),
        (316,226,316,159,"requêtes"),(264,132,240,132,"JSON"),(432,226,432,159,"notification")
    ]:
        d.add(Line(x1,y1,x2,y2,strokeColor=GREEN,strokeWidth=1.6))
        d.add(String((x1+x2)/2, (y1+y2)/2+4, label, fontName="Helvetica", fontSize=6.3, fillColor=MUTED))
    d.add(String(8, 74, "Principe essentiel : une métrique décrit un état chiffré ; une règle décide si cet état devient une alerte.", fontName="Helvetica-Bold", fontSize=8.5, fillColor=INK))
    d.add(String(8, 54, "L'interface lit Prometheus mais ne remplace ni le stockage temporel ni le moteur d'alertes.", fontName="Helvetica", fontSize=8, fillColor=MUTED))
    return d


def backup_flow_diagram():
    d = Drawing(480, 255)
    labels = [
        (5,150,88,"SERVICES",["application", "monitoring"]),
        (101,150,88,"ARCHIVE",["tar.gz", "contenu vérifié"]),
        (197,150,88,"INTÉGRITÉ",["SHA-256", "fichier adjacent"]),
        (293,150,88,"EXPORT VM",["backup-export", "permissions"]),
        (389,150,86,"PC WINDOWS",["copie SCP", "tâche planifiée"]),
    ]
    for x,y,w,title,lines in labels:
        d.add(Rect(x,y,w,62,rx=7,ry=7,fillColor=PALE,strokeColor=GREEN,strokeWidth=1.1))
        d.add(String(x+7,y+43,title,fontName="Helvetica-Bold",fontSize=8,fillColor=NAVY))
        for i,line in enumerate(lines):
            d.add(String(x+7,y+27-i*11,line,fontName="Helvetica",fontSize=6.7,fillColor=INK))
    for x in (93,189,285,381):
        d.add(Line(x,181,x+8,181,strokeColor=BLUE,strokeWidth=1.8))
    d.add(String(8,112,"SERVEURS",fontName="Helvetica-Bold",fontSize=8,fillColor=BLUE))
    d.add(String(389,112,"COPIE HORS VM",fontName="Helvetica-Bold",fontSize=8,fillColor=RED))
    d.add(String(8,78,"Restauration : sélectionner l'archive -> vérifier SHA-256 -> extraire sur machine de test -> recréer volumes -> démarrer -> valider.",fontName="Helvetica-Bold",fontSize=8,fillColor=INK))
    d.add(String(8,55,"Une sauvegarde non restaurée au moins une fois reste une hypothèse, pas une garantie.",fontName="Helvetica",fontSize=8,fillColor=MUTED))
    return d


def physical_architecture_plate():
    path = ROOT / "docs" / "diagrams" / "infrastructure-physical-annotated.png"
    image = RLImage(str(path), width=154 * mm, height=196.1 * mm)
    image.hAlign = "CENTER"
    return image


def build_audit(path: Path):
    story = []
    story += cover("Audit avant / après corrections", "Sécurité, fiabilité, supervision, interface et exploitation. Ce rapport explique les défauts observés, les corrections appliquées, les commandes de vérification et les preuves de validation.", "Rapport d’audit")
    story += toc()
    story += [p("1. Objet et périmètre", "h1"), p("L’audit couvre l’application Flask, Docker, Nginx, Cloudflare Tunnel, Prometheus, Grafana, Alertmanager, Emma_IA, les sauvegardes et le poste Windows supervisé. Il distingue les observations initiales des preuves obtenues après correction."), p("Limite : il s’agit d’un audit technique du projet et de sa configuration, pas d’un test d’intrusion externe certifié.", "callout")]
    story += [p("2. Architecture auditée", "h1"), p("Le périmètre ne se limite pas au code Flask. Il comprend les équipements physiques ou virtuels, les réseaux, le chemin HTTPS, la collecte des métriques, les volumes et la copie de secours hors VM."), p("Le schéma suivant localise chaque composant sur son équipement réel et distingue la production, l'observabilité, l'administration et la sauvegarde hors VM.", "callout"), PageBreak(), p("Architecture des équipements et services", "h1"), equipment_architecture_diagram(), PageBreak(), p("Lecture logique complémentaire", "h2"), full_architecture_diagram(), PageBreak()]
    story += [p("3. Situation initiale", "h1"), table(["Domaine", "Avant correction", "Risque"], [
        ("Emma_IA", "Intentions trop génériques, réponses répétées, confusion entre documentation et temps réel.", "Décisions fondées sur une réponse inadaptée."),
        ("Monitoring", "Historique figé, heures UTC affichées comme locales, KPI parfois vides.", "Lecture opérationnelle trompeuse."),
        ("Multi-équipement", "Seul srv-web était réellement présenté.", "srv-monitoring et le PC restaient invisibles."),
        ("Alertes", "Règles centrées sur Linux et couverture Windows incomplète.", "Incident PC ou batterie non signalé."),
        ("Sauvegardes", "Archives locales sans réplication PC automatisée.", "Perte simultanée de la VM et de ses sauvegardes."),
        ("Secrets", "Permissions et exclusions Git à renforcer.", "Publication ou lecture accidentelle."),
        ("PDF", "Texte de commandes peu contrasté et échappement incomplet.", "Rapport illisible ou contenu injecté."),
        ("Interface", "Doublons de navigation, mobile encombré, impression confuse.", "Expérience peu crédible et difficile à utiliser."),
    ], [31*mm, 94*mm, 45*mm])]
    story += [p("4. Corrections appliquées", "h1"), table(["Correction", "Résultat vérifié"], [
        ("Routage Emma_IA multi-équipement", "État ciblé, comparaison, équipement prioritaire, batterie et volumes persistants."),
        ("API et PromQL configurables", "srv-web, srv-monitoring et PC Windows interrogés par labels et instances configurables."),
        ("Interface multi-équipement", "Vue globale et onglets dédiés, KPI, historiques, services et stockage réel."),
        ("Collecteurs", "Node Exporter sur les deux serveurs, cAdvisor, Windows Exporter, batterie et volumes Docker."),
        ("Alertes Telegram", "17 règles chargées ; alerte RAM Windows reçue et résolution prise en charge."),
        ("Sauvegarde + réplication", "Archives serveur, empreintes SHA-256, copie automatique vérifiée sur Windows."),
        ("Durcissement", ".env en 600, credentials en 600, exclusions Git, Emma_IA en lecture seule."),
        ("Qualité", "Tests Python, tests interface, validation Docker Compose et contrôles HTTP."),
    ], [58*mm, 112*mm])]
    story += [p("5. Chaîne de supervision validée", "h1"), supervision_flow_diagram(), p("Les corrections ont été vérifiées à chaque niveau : exposition des exporters, targets Prometheus UP, requêtes PromQL, API Flask, graphiques, règles firing, réception Alertmanager et notification Telegram.", "callout")]
    story += [p("6. Commandes de contrôle", "h1"), p("Application et conteneur", "h2"), code("docker compose config --quiet\ndocker compose ps web\ndocker inspect secure-web-app-v2 --format 'État={{.State.Status}} Santé={{.State.Health.Status}}'\ncurl -k -I https://127.0.0.1\ndocker logs --tail 50 secure-web-app-v2"), p("Prometheus et Alertmanager", "h2"), code("promtool check rules /etc/prometheus/alerts.yml\namtool check-config /etc/alertmanager/alertmanager.yml\ncurl -fsS http://127.0.0.1:9090/api/v1/targets\ncurl -fsS http://127.0.0.1:9090/api/v1/alerts\ncurl -fsS http://127.0.0.1:9093/api/v2/alerts"), p("Sauvegardes", "h2"), code("systemctl list-timers --all | grep backup\nsha256sum -c ./*.tar.gz.sha256\n# Windows\nGet-ScheduledTaskInfo -TaskName 'Secure Local Cloud - Replication'\nGet-Content $env:USERPROFILE\\SecureLocalCloud-Backups\\logs\\replication.log -Tail 30")]
    story += [p("7. Preuves de validation", "h1"), table(["Preuve", "Résultat"], [
        ("Emma_IA Docker", "26 tests réussis."), ("Interface locale", "17 tests visuels réussis."),
        ("Syntaxe Python", "Compilation réussie."), ("Documentation", "0 lien relatif cassé."),
        ("Recherche de secrets", "Aucun motif sensible détecté dans le dépôt ni son historique local."),
        ("Production", "Conteneur running et healthy ; HTTPS local et URL publique répondent par redirection d’authentification."),
        ("Telegram", "Alerte WindowsMemoryCritical reçue par l’administrateur."),
        ("Métriques", "Trois équipements UP ; historiques et volumes persistants visibles."),
    ], [60*mm, 110*mm])]
    story += [p("8. État après audit", "h1"), p("La plateforme est exploitable comme laboratoire multi-équipement : les données temps réel sont distinguées de la documentation, l’interface affiche les trois sources, les alertes couvrent Linux et Windows, et les sauvegardes possèdent une copie hors VM."), p("Les améliorations ne suppriment pas le besoin de maintenance. Les dépendances, images, certificats, règles d’alerte et restaurations doivent être revérifiés périodiquement.", "callout")]
    story += [p("9. Risques résiduels et priorités", "h1")] + bullets([
        "Faire tourner tout secret ayant été exposé et reconstruire les exports publics avant publication.",
        "Tester une restauration complète sur une machine isolée au moins avant chaque migration.",
        "Épingler les images Docker par version ou digest au lieu d’utiliser latest.",
        "Ajouter une CI GitHub pour les tests, le scan de secrets et la validation des configurations.",
        "Prévoir une seconde destination de sauvegarde chiffrée hors du PC principal.",
    ])
    doc = NumberedDocTemplate(str(path), "Audit avant / après corrections", "AUDIT TECHNIQUE")
    doc.multiBuild(story)


def build_user(path: Path):
    story = []
    story += cover("Guide utilisateur de la plateforme", "Comprendre Secure Local Cloud, lire les indicateurs, naviguer dans les interfaces et réagir aux alertes sans connaissance préalable du code.", "Guide utilisateur")
    story += toc()
    story += [p("1. La plateforme en une phrase", "h1"), p("Secure Local Cloud est une console privée d’observabilité : elle centralise l’état de deux serveurs Ubuntu, du poste Windows, des conteneurs Docker, des ressources système, des alertes et des sauvegardes."), p("Le portail n’est pas Prometheus ni Grafana : il les utilise. Prometheus conserve et interroge les métriques, Grafana propose des tableaux avancés, Alertmanager distribue les alertes et Flask présente une vue simplifiée.", "callout"), table(["Bloc", "Fonction principale"], [("Production", "Publier et exécuter l'application Flask."), ("Observabilité", "Collecter, conserver, afficher et alerter."), ("Administration", "Consulter, maintenir et superviser Windows."), ("Secours", "Conserver une copie vérifiée hors des VM.")], [45*mm, 125*mm]), PageBreak(), p("2. Où se trouve chaque élément ?", "h1"), equipment_architecture_diagram(), PageBreak(), p("La même architecture sous forme logique", "h2"), full_architecture_diagram(), PageBreak()]
    story += [p("3. Les équipements", "h1"), table(["Équipement", "Rôle", "Données principales"], [
        ("srv-web", "Serveur applicatif", "Flask, Gunicorn, Nginx, cloudflared, Docker, cAdvisor, CPU, RAM, disque, réseau."),
        ("srv-monitoring", "Serveur d’observabilité", "Prometheus, Grafana, Alertmanager, volumes persistants, CPU, RAM, disque, réseau."),
        ("PC Emmanuel", "Poste d’administration", "Windows Exporter, CPU, RAM, disque C:, réseau, batterie, état secteur."),
    ], [35*mm, 45*mm, 90*mm])]
    story += [p("4. Comment les données circulent", "h1"), supervision_flow_diagram(), p("Un point affiché sur un graphique correspond à un échantillon daté. Le nombre de mesures chargées indique combien d'échantillons sont disponibles pour la période sélectionnée ; ce nombre augmente avec le temps et dépend du pas de collecte.", "callout")]
    story += [p("5. Comprendre les KPI", "h1"), table(["Indicateur", "Ce qu’il mesure", "Interprétation"], [
        ("CPU", "Part du temps processeur utilisée.", "Un pic court est normal ; une valeur durablement élevée exige une analyse."),
        ("RAM", "Mémoire physique occupée.", "Une RAM proche de 100 % peut provoquer lenteurs et pagination."),
        ("Disque", "Part utilisée de la partition principale.", "Au-delà des seuils, journaux et bases peuvent ne plus s’écrire."),
        ("Réseau", "Débit reçu ou envoyé au moment de la mesure.", "Une variation est normale ; un débit nul n’est pas forcément une panne."),
        ("Charge", "Travail en attente sur Linux.", "À comparer au nombre de CPU ; non applicable de la même façon à Windows."),
        ("Uptime", "Temps écoulé depuis le démarrage.", "Un changement soudain révèle un redémarrage."),
        ("Batterie", "Charge et alimentation du PC.", "Le collecteur indique secteur, décharge et fraîcheur de la donnée."),
        ("Mesures chargées", "Nombre d’échantillons affichés pour la période.", "Ce n’est ni un nombre d’incidents ni un score."),
    ], [30*mm, 62*mm, 78*mm])]
    story += [p("6. Page Monitoring", "h1"), p("La vue globale consolide les trois équipements. Les onglets srv-web, srv-monitoring et PC Emmanuel affichent ensuite les valeurs propres à une source."), table(["Zone", "Utilité"], [
        ("Sélecteur de période", "Choisir 1 h, 6 h, 24 h ou 7 jours."),
        ("Cartes KPI", "Valeurs les plus récentes."),
        ("Graphiques", "Historique CPU, RAM et disque avec minimum, moyenne et maximum."),
        ("Services supervisés", "État des composants rattachés à l’équipement."),
        ("Stockage persistant", "Racine système et, sur srv-monitoring, volumes Prometheus/Grafana/Alertmanager."),
        ("Informations système", "Rôle, OS, collecteur et dernière lecture."),
    ], [45*mm, 125*mm]), p("Une donnée absente est affichée comme indisponible, jamais transformée en zéro. Cela évite de faire croire qu’un équipement arrêté ne consomme aucune ressource.", "warning")]
    story += [p("7. Conteneurs Docker et journaux", "h1"), p("La page Conteneurs indique combien de conteneurs sont détectés et actifs, leur image, leur CPU, leur mémoire, leur uptime et leur état. Les onglets Images, Volumes et Réseaux décrivent les objets Docker associés."), p("Le journal d'audit enregistre qui a demandé une action, sur quelle ressource, à quelle heure, si l'action a réussi et le détail retourné. Il sert à reconstituer une opération ; ce n'est pas un graphique de performance."), p("Les boutons démarrer, arrêter et redémarrer sont des opérations administratives. Consulter les journaux est la première action recommandée avant toute modification.", "warning")]
    story += [p("8. Alertes Telegram", "h1"), p("Une alerte traverse trois états : inactive, pending, puis firing. La durée pending évite qu’un pic très court déclenche une notification. Alertmanager regroupe les événements et Telegram reçoit le message. Lorsque la condition disparaît, un message resolved peut être envoyé."), table(["Famille", "Exemples"], [
        ("Disponibilité", "Exporter ou service inaccessible."), ("Ressources", "CPU, RAM ou disque durablement trop élevés."),
        ("Application", "Conteneur Flask absent."), ("Batterie", "Charge faible, critique ou collecteur périmé."),
        ("Sauvegarde", "Échec, archive trop ancienne ou métrique absente."),
    ], [45*mm, 125*mm])]
    story += [p("9. Emma_IA", "h1"), p("Emma_IA est un assistant en lecture seule. Elle peut décrire la plateforme, afficher l’état réel d’un équipement, comparer les trois équipements, identifier la pression principale, expliquer la batterie et les volumes persistants."), p("Exemples de questions", "h2")] + bullets([
        "Quel est l’état actuel de srv-monitoring ?", "Compare les trois équipements.",
        "Quel équipement demande le plus d’attention ?", "Quel est l’état de la batterie de mon PC ?",
        "Explique les volumes persistants.", "Que vérifier si Grafana ne répond plus ?",
    ]) + [p("Emma_IA ne lance aucune commande et ne remplace pas une investigation complète.", "callout")]
    story += [p("10. Réagir à un incident", "h1")] + bullets([
        "Identifier l’équipement et l’heure de début.", "Vérifier si la valeur est instantanée ou durable dans l’historique.",
        "Contrôler l’état des services et des cibles Prometheus.", "Lire les journaux du service concerné.",
        "Éviter un redémarrage sans diagnostic, sauf urgence documentée.", "Après correction, confirmer le retour à la normale et la résolution Telegram.",
    ])
    doc = NumberedDocTemplate(str(path), "Guide utilisateur de la plateforme", "UTILISATEURS ET RECRUTEURS")
    doc.multiBuild(story)


def build_admin(path: Path):
    story = []
    story += cover("Manuel administrateur et dossier technique", "Reconstruction, exploitation, code, déploiement, alertes, sauvegardes, restauration et maintenance de Secure Local Cloud.", "Runbook administrateur")
    story += toc()
    story += [p("1. Architecture complète des équipements", "h1"), equipment_architecture_diagram(), PageBreak(), p("Architecture logique et flux", "h2"), full_architecture_diagram(), PageBreak(), p("Réseaux utilisés", "h2"), table(["Réseau", "Usage"], [
        ("192.168.50.0/24", "Services et collecte entre srv-web et srv-monitoring."),
        ("192.168.154.0/24", "Administration depuis Windows, SSH, réplication et Windows Exporter."),
        ("VMware NAT", "Sortie Internet des VM pour mises à jour et Cloudflare Tunnel."),
        ("Docker bridge", "Communication interne des conteneurs sur chaque hôte."),
    ], [48*mm, 122*mm])]
    story += [p("2. Inventaire détaillé par équipement", "h1"), table(["Équipement", "Composants internes", "Responsabilité"], [
        ("srv-web", "Ubuntu, cloudflared, Nginx, Docker, Gunicorn, Flask, Node Exporter, cAdvisor", "Publication HTTPS, application, API, conteneurs et métriques applicatives."),
        ("srv-monitoring", "Ubuntu, Docker Compose, Prometheus, Grafana, Alertmanager, Node Exporter", "Collecte, stockage temporel, visualisation, règles et notifications."),
        ("PC Emmanuel", "Windows, VMware, navigateur, SSH, Windows Exporter, collecteur batterie, tâche de réplication", "Administration, métriques Windows et copie hors VM."),
    ], [32*mm, 76*mm, 62*mm]), p("Ports et exposition", "h2"), table(["Port", "Service", "Exposition attendue"], [
        ("443", "Nginx / Cloudflare", "Accès applicatif HTTPS."), ("5001", "Gunicorn publié par Docker", "127.0.0.1 uniquement."),
        ("9090", "Prometheus", "Interfaces privées autorisées."), ("3000", "Grafana", "Interfaces privées ou tunnel contrôlé."),
        ("9093", "Alertmanager", "Réseau de monitoring."), ("9100", "Node Exporter", "Prometheus uniquement."),
        ("8080", "cAdvisor", "Prometheus uniquement."), ("9182", "Windows Exporter", "srv-monitoring uniquement."),
    ], [25*mm, 55*mm, 90*mm])]
    story += [p("3. Montage initial", "h1"), p("Préparer les machines", "h2")] + bullets([
        "Créer deux VM Ubuntu 24.04 avec trois interfaces selon le laboratoire.", "Attribuer les adresses privées fixes et conserver une route par défaut via l’interface NAT.",
        "Installer Docker Engine, Docker Compose, Nginx et les exporters nécessaires.", "Limiter les ports exporters aux réseaux d’administration et de services.",
    ]) + [code("hostnamectl\ncat /etc/os-release\nip -br address\nip route\ntimedatectl status\ndf -h\nfree -h\nsystemctl --failed --no-pager")]
    story += [p("4. Installation de l’application", "h1"), code("cd application\ncp .env.example .env\nchmod 600 .env\npython3 -c 'import secrets; print(secrets.token_urlsafe(48))'\ndocker compose config --quiet\ndocker compose up -d --build\ndocker compose ps\ndocker compose logs --tail 100 web"), p("Les secrets générés sont placés dans .env uniquement sur srv-web. Le fichier public .env.example ne contient que des noms de variables et des exemples neutres.", "warning")]
    story += [p("5. Installation du monitoring", "h1"), code("cd ~/monitoring\ndocker compose config\ndocker compose up -d\ndocker compose ps\ncurl -fsS http://127.0.0.1:9090/-/ready\ncurl -fsS http://127.0.0.1:9093/-/ready"), p("Prometheus collecte srv-web:9100, cAdvisor:8080, srv-monitoring:9100 et le PC Windows:9182. Les labels equipment, role et os permettent aux requêtes et alertes de rester génériques."), supervision_flow_diagram()]
    story += [p("6. Chemin HTTPS de bout en bout", "h1"), p("Cloudflare termine le HTTPS public et transmet la requête par un tunnel sortant cloudflared. Nginx reçoit l’origine sur srv-web et reverse-proxy vers Gunicorn exposé uniquement sur 127.0.0.1:5001. Gunicorn exécute Flask sur le port 5000 du conteneur."), table(["Étape", "Lieu", "Fonction"], [
        ("1", "Navigateur", "Demande https://app.emmanuelinfra.fr."), ("2", "Cloudflare", "DNS, certificat public, filtrage et terminaison TLS."),
        ("3", "cloudflared sur srv-web", "Tunnel sortant ; aucun port entrant à ouvrir sur la box."), ("4", "Nginx sur srv-web", "Reverse proxy et en-têtes HTTP."),
        ("5", "127.0.0.1:5001", "Port Docker local vers Gunicorn."), ("6", "Conteneur :5000", "Gunicorn distribue la requête à Flask."),
        ("7", "Flask", "Authentification, route, service, rendu HTML ou JSON."),
    ], [15*mm, 48*mm, 107*mm]), code("sudo nginx -t\nsudo systemctl reload nginx\nsystemctl status cloudflared --no-pager\ncurl -k -I https://127.0.0.1\ncurl -I https://app.emmanuelinfra.fr")]
    story += [p("7. Architecture du code", "h1"), code_map_diagram(), table(["Chemin", "Responsabilité"], [
        ("application/app.py", "Fabrique Flask, blueprints et initialisation."), ("application/config.py", "Variables d’environnement et paramètres."),
        ("application/routes/", "Pages, API, authentification, rapports et audit."), ("application/services/prometheus_service.py", "PromQL Linux/Windows et normalisation."),
        ("application/services/assistant_engine.py", "Routage général d’Emma_IA."), ("application/services/assistant_equipment.py", "Réponses multi-équipement temps réel."),
        ("application/templates/", "HTML Jinja."), ("application/static/", "CSS, JavaScript et ressources visuelles."),
        ("application/data/", "État local privé, non publié."), ("monitoring/", "Prometheus, alertes, Alertmanager et Compose."),
        ("docs/", "Documentation publique."), ("application/tests/", "Tests de non-régression."),
    ], [67*mm, 103*mm])]
    story += [p("8. API multi-équipement", "h1"), table(["Route", "Réponse"], [
        ("GET /api/equipment", "Inventaire et disponibilité des trois équipements."),
        ("GET /api/equipment/<nom>/metrics", "Valeurs instantanées, services, batterie et volumes."),
        ("GET /api/equipment/<nom>/history?hours=N", "Séries temporelles CPU, RAM et disque."),
        ("GET /api/metrics", "Compatibilité de l’ancien tableau de bord."),
        ("POST /api/assistant", "Question Emma_IA après authentification."),
        ("GET /export/pdf", "Rapport de supervision PDF authentifié."),
    ], [72*mm, 98*mm])]
    story += [p("9. Alertes et Telegram", "h1"), p("Les règles sont dans monitoring/alerts.yml. Prometheus les évalue puis envoie les alertes firing à Alertmanager. Le routage Telegram est défini dans alertmanager.yml, mais le jeton et l’identifiant de discussion doivent être injectés hors Git."), table(["État", "Signification", "Action"], [
        ("inactive", "Condition fausse.", "Aucune notification."), ("pending", "Condition vraie mais durée for non atteinte.", "Observer sans redémarrer précipitamment."),
        ("firing", "Condition maintenue.", "Alertmanager groupe et envoie Telegram."), ("resolved", "Condition revenue à la normale.", "Confirmer le service et documenter."),
    ], [28*mm, 76*mm, 66*mm]), code("docker compose exec -T prometheus promtool check rules /etc/prometheus/alerts.yml\ndocker compose exec -T alertmanager amtool check-config /etc/alertmanager/alertmanager.yml\ncurl -fsS http://127.0.0.1:9090/api/v1/alerts | python3 -m json.tool\ncurl -fsS http://127.0.0.1:9093/api/v2/alerts | python3 -m json.tool"), p("Ne jamais copier un fichier contenant un jeton réel vers GitHub, un PDF public, une archive partagée ou une conversation. En cas d’exposition, révoquer et recréer le jeton.", "warning")]
    story += [p("10. Sauvegardes et réplication", "h1"), backup_flow_diagram(), table(["Étape", "Destination"], [
        ("Sauvegarde srv-web", "/var/backups/... puis /home/emmanuel/backup-export/srv-web/"),
        ("Sauvegarde srv-monitoring", "/var/backups/... puis /home/emmanuel/backup-export/srv-monitoring/"),
        ("Empreinte", "Fichier .sha256 adjacent à chaque archive .tar.gz."),
        ("Réplication Windows", "C:\\Users\\Emman\\SecureLocalCloud-Backups\\srv-web et srv-monitoring"),
        ("Journal", "C:\\Users\\Emman\\SecureLocalCloud-Backups\\logs\\replication.log"),
        ("Tâche Windows", "Secure Local Cloud - Replication, déclenchée automatiquement."),
    ], [55*mm, 115*mm]), code("# Linux\nsystemctl list-timers --all | grep backup\nsha256sum -c ./*.tar.gz.sha256\n\n# Windows PowerShell\nGet-ScheduledTaskInfo -TaskName 'Secure Local Cloud - Replication'\nGet-ChildItem $env:USERPROFILE\\SecureLocalCloud-Backups -Recurse -File\nGet-Content $env:USERPROFILE\\SecureLocalCloud-Backups\\logs\\replication.log -Tail 30")]
    story += [p("11. Procédure de restauration", "h1")] + bullets([
        "Choisir une archive et vérifier son SHA-256.", "Copier l’archive sur une machine de test, jamais directement en production.",
        "Extraire dans un dossier vide et inventorier configurations, données et volumes.", "Recréer les volumes Docker avant les conteneurs.",
        "Restaurer les permissions restrictives des secrets.", "Démarrer le monitoring puis l’application.",
        "Tester authentification, métriques, historiques, alertes, PDF et sauvegardes.", "Documenter le test avant d’autoriser une restauration de production.",
    ])
    story += [p("12. Déploiement et retour arrière", "h1"), code("# Avant modification\ngit switch -c feature/nom-du-changement\ntar -czf ~/application-before-$(date -u +%Y%m%d-%H%M%S).tar.gz .\n\n# Image de test\ndocker build -t application-web:change-test .\ndocker run --rm application-web:change-test python -m unittest discover -s tests -p 'test_*.py' -q\n\n# Production\ndocker image tag application-web:latest application-web:before-change\ndocker image tag application-web:change-test application-web:latest\ndocker compose up -d --force-recreate --no-deps --no-build web"), p("Conserver le tag before-change jusqu’à validation de la santé, des logs, de l’URL publique et d’un parcours fonctionnel.", "callout")]
    story += [p("13. Maintenance périodique", "h1"), table(["Fréquence", "Actions"], [
        ("Chaque semaine", "Vérifier timers, archives, SHA-256, réplication et journal Windows."),
        ("Chaque mois", "Contrôler espace disque, volumes, cibles Prometheus et alertes Telegram."),
        ("Chaque trimestre", "Mettre à jour dépendances et images après sauvegarde et tests."),
        ("Avant changement", "Sauvegarde, branche Git, image de test et plan de retour arrière."),
        ("Avant migration", "Restauration complète sur une machine de test."),
    ], [43*mm, 127*mm])]
    story += [p("14. Publication GitHub", "h1"), code("git status --short\ngit diff --check\ngit add README.md application docs monitoring\ngit diff --cached --stat\ngit commit -m 'Documenter et finaliser le monitoring multi-équipement'\ngit push -u origin feature/multi-equipment-monitoring"), p("Avant git add, vérifier qu’aucun .env, credential, archive, base, clé privée, jeton ou fichier de données n’est suivi.", "warning")]
    story += [p("15. Checklist de reprise après plusieurs mois", "h1")] + bullets([
        "Lire README.md puis docs/ARCHITECTURE.md.", "Vérifier les trois équipements et les routes réseau.",
        "Contrôler docker compose ps sur les deux serveurs.", "Vérifier les targets et règles Prometheus.",
        "Lire les derniers journaux Nginx, Flask, Prometheus et Alertmanager.", "Contrôler la dernière sauvegarde serveur et sa copie Windows.",
        "Créer une branche et une sauvegarde avant toute correction.",
    ])
    doc = NumberedDocTemplate(str(path), "Manuel administrateur et dossier technique", "ADMINISTRATEUR")
    doc.multiBuild(story)


def main():
    targets = {
        "audit": OUTPUT / "audit-avant-apres-secure-local-cloud.pdf",
        "user": OUTPUT / "guide-utilisateur-secure-local-cloud.pdf",
        "admin": OUTPUT / "manuel-administrateur-secure-local-cloud.pdf",
    }
    build_audit(targets["audit"])
    build_user(targets["user"])
    build_admin(targets["admin"])
    for path in targets.values():
        print(path)


if __name__ == "__main__":
    main()
