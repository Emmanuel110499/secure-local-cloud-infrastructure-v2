from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
TEMPLATES = ROOT / "templates"
STATIC_CSS = ROOT / "static" / "css"
STATIC_JS = ROOT / "static" / "js"

BACKUP = (
    ROOT
    / "backups"
    / f"remaining-v3-{datetime.now():%Y%m%d-%H%M%S}"
)

STATIC_CSS.mkdir(parents=True, exist_ok=True)
STATIC_JS.mkdir(parents=True, exist_ok=True)
BACKUP.mkdir(parents=True, exist_ok=True)


def backup(filename: str) -> None:
    source = TEMPLATES / filename

    if source.is_file():
        shutil.copy2(
            source,
            BACKUP / filename,
        )


def write_template(filename: str, content: str) -> None:
    path = TEMPLATES / filename

    path.write_text(
        content.strip() + "\n",
        encoding="utf-8",
    )

    print(f"Template installé : {filename}")


for filename in (
    "images.html",
    "volumes.html",
    "networks.html",
    "logs.html",
    "prometheus.html",
    "help_center.html",
    "getting_started.html",
    "faq.html",
):
    backup(filename)


layout = r'''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>
        {% block title %}Secure Local Cloud{% endblock %}
    </title>

    <link
        rel="stylesheet"
        href="{{ url_for('static', filename='css/portal-v3.css', v='remaining-v3-4') }}"
    >

    {% block head %}{% endblock %}
</head>

<body class="v3-body">
    <div class="v3-background-orb v3-background-orb-one"></div>
    <div class="v3-background-orb v3-background-orb-two"></div>

    <main class="v3-page">
        <header class="v3-topbar">
            <a
                class="v3-brand"
                href="/"
                aria-label="Retour au tableau de bord"
            >
                <span class="v3-brand-mark">
                    <svg viewBox="0 0 24 24">
                        <path d="M12 3 5 6v5c0 4.8 2.8 8.3 7 10 4.2-1.7 7-5.2 7-10V6Z"/>
                        <path d="m9 12 2 2 4-4"/>
                    </svg>
                </span>

                <span>
                    <strong>Secure Local</strong>
                    <small>Cloud Infrastructure</small>
                </span>
            </a>

            <nav class="v3-top-actions">
                {% block top_actions %}{% endblock %}

                <a
                    class="v3-dashboard-link"
                    href="/"
                >
                    <svg viewBox="0 0 24 24">
                        <path d="M3 11 12 3l9 8"/>
                        <path d="M5 10v10h14V10"/>
                        <path d="M9 20v-6h6v6"/>
                    </svg>

                    <span>Tableau de bord</span>
                </a>
            </nav>
        </header>

        <section class="v3-page-heading">
            <div class="v3-heading-identity">
                <span class="v3-page-icon">
                    {% block page_icon %}
                        <svg viewBox="0 0 24 24">
                            <path d="M4 5h16v14H4Z"/>
                        </svg>
                    {% endblock %}
                </span>

                <div>
                    <div class="v3-breadcrumb">
                        Secure Local Cloud
                        <span>/</span>
                        {% block breadcrumb %}Portail{% endblock %}
                    </div>

                    <h1>{% block page_title %}Portail{% endblock %}</h1>

                    <p>
                        {% block page_description %}
                            Gestion de l’infrastructure locale sécurisée.
                        {% endblock %}
                    </p>
                </div>
            </div>

            {% block heading_actions %}{% endblock %}
        </section>

        {% block content %}{% endblock %}
    </main>

    <div
        id="v3-toast-container"
        class="v3-toast-container"
        aria-live="polite"
    ></div>

    <script
        src="{{ url_for('static', filename='js/portal-v3.js', v='remaining-v3-4') }}"
    ></script>

    {% block scripts %}{% endblock %}
</body>
</html>
'''

write_template(
    "portal_v3_base.html",
    layout,
)


css = r'''
:root {
    --v3-background: #f3f6fb;
    --v3-surface: #ffffff;
    --v3-surface-soft: #f7f9fd;
    --v3-text: #17233a;
    --v3-text-soft: #67778f;
    --v3-border: #e1e8f2;
    --v3-primary: #315fd8;
    --v3-primary-dark: #244bb4;
    --v3-primary-soft: #e9f0ff;
    --v3-purple: #7c3aed;
    --v3-purple-soft: #f3e8ff;
    --v3-green: #059669;
    --v3-green-soft: #ecfdf5;
    --v3-orange: #d97706;
    --v3-orange-soft: #fff7e8;
    --v3-red: #dc2626;
    --v3-red-soft: #fff1f2;
    --v3-cyan: #0891b2;
    --v3-cyan-soft: #ecfeff;
    --v3-shadow:
        0 12px 34px rgba(30, 48, 82, 0.08);
    --v3-shadow-hover:
        0 20px 48px rgba(30, 48, 82, 0.13);
}

* {
    box-sizing: border-box;
}

html {
    min-height: 100%;
    background: var(--v3-background);
}

body.v3-body {
    min-height: 100vh;
    margin: 0;
    color: var(--v3-text);
    background:
        linear-gradient(
            145deg,
            #f7f9fd 0%,
            #f1f5fb 48%,
            #f6f7fc 100%
        );
    font-family:
        Inter,
        "Segoe UI",
        Arial,
        sans-serif;
    -webkit-font-smoothing: antialiased;
}

button,
input,
select {
    font: inherit;
}

button,
a {
    -webkit-tap-highlight-color: transparent;
}

.v3-background-orb {
    position: fixed;
    z-index: 0;
    border-radius: 50%;
    pointer-events: none;
    filter: blur(1px);
}

.v3-background-orb-one {
    top: -180px;
    left: -150px;
    width: 450px;
    height: 450px;
    background:
        radial-gradient(
            circle,
            rgba(49, 95, 216, 0.10),
            transparent 70%
        );
}

.v3-background-orb-two {
    top: -210px;
    right: -170px;
    width: 480px;
    height: 480px;
    background:
        radial-gradient(
            circle,
            rgba(124, 58, 237, 0.08),
            transparent 70%
        );
}

.v3-page {
    position: relative;
    z-index: 1;
    width: min(1440px, 100%);
    margin: auto;
    padding: 20px 28px 40px;
}

.v3-topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    min-height: 68px;
    margin-bottom: 24px;
    padding: 10px 14px;
    background: rgba(255, 255, 255, 0.78);
    border: 1px solid rgba(225, 232, 242, 0.90);
    border-radius: 19px;
    box-shadow:
        0 8px 30px rgba(30, 48, 82, 0.055);
    backdrop-filter: blur(18px);
}

.v3-brand {
    display: flex;
    align-items: center;
    gap: 11px;
    min-width: 0;
    color: var(--v3-text);
    text-decoration: none;
}

.v3-brand-mark {
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    width: 42px;
    height: 42px;
    color: #ffffff;
    background:
        linear-gradient(
            145deg,
            var(--v3-primary-dark),
            var(--v3-primary) 58%,
            #7256dd
        );
    border-radius: 13px;
    box-shadow:
        0 10px 23px rgba(49, 95, 216, 0.25);
}

.v3-brand-mark svg,
.v3-page-icon svg,
.v3-dashboard-link svg,
.v3-icon svg,
.v3-button svg,
.v3-search svg,
.v3-empty-icon svg {
    width: 21px;
    height: 21px;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
}

.v3-brand strong,
.v3-brand small {
    display: block;
}

.v3-brand strong {
    font-size: 0.88rem;
    letter-spacing: -0.015em;
}

.v3-brand small {
    margin-top: 2px;
    color: var(--v3-text-soft);
    font-size: 0.59rem;
}

.v3-top-actions {
    display: flex;
    align-items: center;
    gap: 9px;
}

.v3-dashboard-link,
.v3-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    min-height: 42px;
    padding: 0 14px;
    color: var(--v3-primary);
    background: #ffffff;
    border: 1px solid var(--v3-border);
    border-radius: 12px;
    box-shadow:
        0 6px 16px rgba(30, 48, 82, 0.05);
    cursor: pointer;
    text-decoration: none;
    font-size: 0.71rem;
    font-weight: 800;
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease;
}

.v3-dashboard-link:hover,
.v3-button:hover {
    transform: translateY(-2px);
    border-color: #cbd9f3;
    box-shadow:
        0 12px 25px rgba(30, 48, 82, 0.09);
}

.v3-button.primary {
    color: #ffffff;
    background:
        linear-gradient(
            145deg,
            var(--v3-primary-dark),
            #4e76e6
        );
    border-color: transparent;
}

.v3-page-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 22px;
}

.v3-heading-identity {
    display: flex;
    align-items: center;
    gap: 16px;
    min-width: 0;
}

.v3-page-icon {
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    width: 58px;
    height: 58px;
    color: #ffffff;
    background:
        linear-gradient(
            145deg,
            #234dbb,
            #4c74e2 58%,
            #7456dc
        );
    border-radius: 18px;
    box-shadow:
        0 15px 32px rgba(49, 95, 216, 0.24);
}

.v3-page-icon svg {
    width: 29px;
    height: 29px;
}

.v3-breadcrumb {
    margin-bottom: 5px;
    color: #8a97a9;
    font-size: 0.61rem;
    font-weight: 700;
}

.v3-breadcrumb span {
    margin: 0 5px;
    color: #b6c0ce;
}

.v3-page-heading h1 {
    margin: 0;
    color: var(--v3-text);
    font-size: clamp(1.55rem, 2.6vw, 2.05rem);
    font-weight: 860;
    letter-spacing: -0.035em;
}

.v3-page-heading p {
    max-width: 760px;
    margin: 7px 0 0;
    color: var(--v3-text-soft);
    font-size: 0.82rem;
    line-height: 1.55;
}

.v3-toolbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 13px;
    margin-bottom: 16px;
    padding: 13px;
    background: rgba(255, 255, 255, 0.90);
    border: 1px solid var(--v3-border);
    border-radius: 17px;
    box-shadow: var(--v3-shadow);
    backdrop-filter: blur(12px);
}

.v3-search {
    display: flex;
    align-items: center;
    gap: 10px;
    width: min(520px, 100%);
    min-height: 44px;
    padding: 0 13px;
    color: #8290a3;
    background: var(--v3-surface-soft);
    border: 1px solid var(--v3-border);
    border-radius: 12px;
}

.v3-search:focus-within {
    color: var(--v3-primary);
    background: #ffffff;
    border-color: #9eb4ee;
    box-shadow:
        0 0 0 4px rgba(49, 95, 216, 0.08);
}

.v3-search input {
    width: 100%;
    padding: 0;
    color: var(--v3-text);
    background: transparent;
    border: 0;
    outline: 0;
    font-size: 0.74rem;
}

.v3-tabs {
    display: flex;
    align-items: center;
    gap: 7px;
    overflow-x: auto;
    scrollbar-width: none;
}

.v3-tabs::-webkit-scrollbar {
    display: none;
}

.v3-tab {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    min-height: 37px;
    padding: 0 12px;
    color: #5f6f85;
    background: #f7f9fc;
    border: 1px solid var(--v3-border);
    border-radius: 10px;
    text-decoration: none;
    font-size: 0.63rem;
    font-weight: 800;
}

.v3-tab.active {
    color: #ffffff;
    background:
        linear-gradient(
            145deg,
            var(--v3-primary-dark),
            #5278e5
        );
    border-color: transparent;
    box-shadow:
        0 8px 18px rgba(49, 95, 216, 0.20);
}

.v3-stat-grid {
    display: grid;
    grid-template-columns:
        repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 16px;
}

.v3-stat-card {
    position: relative;
    min-width: 0;
    padding: 17px;
    overflow: hidden;
    background:
        linear-gradient(
            180deg,
            #ffffff,
            #fdfefe
        );
    border: 1px solid var(--v3-border);
    border-radius: 17px;
    box-shadow: var(--v3-shadow);
}

.v3-stat-card::after {
    position: absolute;
    top: -35px;
    right: -35px;
    width: 100px;
    height: 100px;
    content: "";
    background:
        radial-gradient(
            circle,
            rgba(49, 95, 216, 0.08),
            transparent 68%
        );
    border-radius: 50%;
}

.v3-stat-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 10px;
}

.v3-stat-card span,
.v3-stat-card strong,
.v3-stat-card small {
    display: block;
}

.v3-stat-card > span,
.v3-stat-top > span:first-child {
    color: var(--v3-text-soft);
    font-size: 0.63rem;
    font-weight: 750;
}

.v3-stat-card strong {
    margin-top: 8px;
    color: var(--v3-text);
    font-size: 1.45rem;
    font-weight: 900;
    letter-spacing: -0.04em;
}

.v3-stat-card small {
    margin-top: 5px;
    color: #909cad;
    font-size: 0.53rem;
}

.v3-icon {
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    width: 39px;
    height: 39px;
    color: var(--v3-primary);
    background: var(--v3-primary-soft);
    border: 1px solid #d6e2f8;
    border-radius: 12px;
}

.v3-icon.purple {
    color: var(--v3-purple);
    background: var(--v3-purple-soft);
    border-color: #e9d5ff;
}

.v3-icon.green {
    color: var(--v3-green);
    background: var(--v3-green-soft);
    border-color: #d1fae5;
}

.v3-icon.orange {
    color: var(--v3-orange);
    background: var(--v3-orange-soft);
    border-color: #fde8bd;
}

.v3-icon.cyan {
    color: var(--v3-cyan);
    background: var(--v3-cyan-soft);
    border-color: #cffafe;
}

.v3-panel {
    padding: 20px;
    background:
        linear-gradient(
            180deg,
            #ffffff,
            #fdfefe
        );
    border: 1px solid var(--v3-border);
    border-radius: 19px;
    box-shadow: var(--v3-shadow);
}

.v3-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 17px;
}

.v3-panel-header h2 {
    margin: 0;
    color: var(--v3-text);
    font-size: 0.89rem;
    font-weight: 850;
}

.v3-panel-header p,
.v3-panel-header span {
    margin: 4px 0 0;
    color: var(--v3-text-soft);
    font-size: 0.61rem;
}

.v3-card-grid {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 12px;
}

.v3-resource-card {
    min-width: 0;
    padding: 16px;
    background: #ffffff;
    border: 1px solid var(--v3-border);
    border-radius: 16px;
    box-shadow:
        0 7px 22px rgba(30, 48, 82, 0.055);
    transition:
        transform 0.18s ease,
        box-shadow 0.18s ease,
        border-color 0.18s ease;
}

.v3-resource-card:hover {
    transform: translateY(-3px);
    border-color: #ccd8ee;
    box-shadow: var(--v3-shadow-hover);
}

.v3-resource-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 11px;
    margin-bottom: 13px;
}

.v3-resource-identity {
    display: flex;
    align-items: center;
    gap: 10px;
    min-width: 0;
}

.v3-resource-identity strong,
.v3-resource-identity span {
    display: block;
    min-width: 0;
}

.v3-resource-identity strong {
    overflow: hidden;
    color: var(--v3-text);
    font-size: 0.74rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.v3-resource-identity span {
    margin-top: 4px;
    overflow: hidden;
    color: var(--v3-text-soft);
    font-size: 0.56rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.v3-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 auto;
    min-height: 27px;
    padding: 0 9px;
    color: var(--v3-primary);
    background: var(--v3-primary-soft);
    border: 1px solid #d6e2f8;
    border-radius: 999px;
    font-size: 0.54rem;
    font-weight: 900;
}

.v3-badge.success {
    color: #047857;
    background: #dcfce7;
    border-color: #bbf7d0;
}

.v3-badge.warning {
    color: #b45309;
    background: #fef3c7;
    border-color: #fde68a;
}

.v3-badge.danger {
    color: #b91c1c;
    background: #fee2e2;
    border-color: #fecaca;
}

.v3-detail-grid {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 8px;
}

.v3-detail {
    min-width: 0;
    padding: 10px;
    background: var(--v3-surface-soft);
    border: 1px solid #e9eef5;
    border-radius: 10px;
}

.v3-detail span,
.v3-detail strong {
    display: block;
}

.v3-detail span {
    color: var(--v3-text-soft);
    font-size: 0.51rem;
    font-weight: 700;
}

.v3-detail strong {
    margin-top: 5px;
    overflow: hidden;
    color: #344258;
    font-size: 0.62rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.v3-list {
    display: grid;
    gap: 10px;
}

.v3-list-item {
    display: grid;
    grid-template-columns:
        auto minmax(150px, 1fr)
        repeat(3, minmax(100px, 0.55fr));
    align-items: center;
    gap: 13px;
    min-width: 0;
    padding: 14px;
    background: #ffffff;
    border: 1px solid var(--v3-border);
    border-radius: 14px;
    box-shadow:
        0 7px 22px rgba(30, 48, 82, 0.045);
}

.v3-list-field {
    min-width: 0;
}

.v3-list-field span,
.v3-list-field strong {
    display: block;
}

.v3-list-field span {
    color: var(--v3-text-soft);
    font-size: 0.51rem;
    font-weight: 700;
}

.v3-list-field strong {
    margin-top: 4px;
    overflow: hidden;
    color: #344258;
    font-size: 0.64rem;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.v3-empty {
    display: grid;
    place-items: center;
    padding: 45px 20px;
    color: var(--v3-text-soft);
    text-align: center;
    background:
        linear-gradient(
            180deg,
            #ffffff,
            #fafcff
        );
    border: 1px dashed #ced8e8;
    border-radius: 17px;
}

.v3-empty[hidden] {
    display: none;
}

.v3-empty-icon {
    display: grid;
    place-items: center;
    width: 58px;
    height: 58px;
    margin-bottom: 13px;
    color: var(--v3-primary);
    background: var(--v3-primary-soft);
    border-radius: 17px;
}

.v3-empty h3 {
    margin: 0;
    color: var(--v3-text);
    font-size: 0.81rem;
}

.v3-empty p {
    max-width: 480px;
    margin: 7px 0 0;
    font-size: 0.64rem;
    line-height: 1.55;
}

.v3-code-panel {
    min-height: 420px;
    margin: 0;
    padding: 17px;
    overflow: auto;
    color: #d8e8f6;
    background:
        linear-gradient(
            145deg,
            #0c1728,
            #111f34
        );
    border: 1px solid #22344d;
    border-radius: 15px;
    font-family:
        Consolas,
        "Courier New",
        monospace;
    font-size: 0.67rem;
    line-height: 1.65;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
}

.v3-guide-grid {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 13px;
}

.v3-guide-card {
    min-width: 0;
    padding: 18px;
    background: #ffffff;
    border: 1px solid var(--v3-border);
    border-radius: 17px;
    box-shadow: var(--v3-shadow);
}

.v3-guide-card h2,
.v3-guide-card h3 {
    margin: 12px 0 0;
    color: var(--v3-text);
    font-size: 0.82rem;
}

.v3-guide-card p {
    margin: 8px 0 0;
    color: var(--v3-text-soft);
    font-size: 0.65rem;
    line-height: 1.6;
}

.v3-guide-card ul,
.v3-guide-card ol {
    margin: 13px 0 0;
    padding-left: 18px;
    color: #526178;
    font-size: 0.63rem;
    line-height: 1.7;
}

.v3-guide-card a {
    display: inline-flex;
    margin-top: 14px;
    color: var(--v3-primary);
    text-decoration: none;
    font-size: 0.63rem;
    font-weight: 850;
}

.v3-accordion {
    display: grid;
    gap: 10px;
}

.v3-accordion-item {
    background: #ffffff;
    border: 1px solid var(--v3-border);
    border-radius: 14px;
    box-shadow:
        0 7px 22px rgba(30, 48, 82, 0.045);
}

.v3-accordion-button {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    width: 100%;
    min-height: 58px;
    padding: 13px 15px;
    color: var(--v3-text);
    background: transparent;
    border: 0;
    cursor: pointer;
    text-align: left;
    font-size: 0.69rem;
    font-weight: 820;
}

.v3-accordion-button::after {
    flex: 0 0 auto;
    width: 9px;
    height: 9px;
    content: "";
    border-right: 2px solid #8492a6;
    border-bottom: 2px solid #8492a6;
    transform: rotate(45deg);
    transition: transform 0.18s ease;
}

.v3-accordion-item.open
.v3-accordion-button::after {
    transform: rotate(225deg);
}

.v3-accordion-content {
    display: none;
    padding: 0 15px 15px;
    color: var(--v3-text-soft);
    font-size: 0.64rem;
    line-height: 1.65;
}

.v3-accordion-item.open
.v3-accordion-content {
    display: block;
}

.v3-updated {
    margin-top: 12px;
    color: #8a97a9;
    font-size: 0.56rem;
}

.v3-toast-container {
    position: fixed;
    z-index: 4000;
    right: 18px;
    bottom: 18px;
    display: grid;
    gap: 9px;
}

.v3-toast {
    min-width: 240px;
    max-width: 380px;
    padding: 12px 14px;
    color: #344258;
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid var(--v3-border);
    border-radius: 13px;
    box-shadow: var(--v3-shadow-hover);
    font-size: 0.64rem;
    animation: v3-toast-in 0.2s ease;
}

.v3-toast.error {
    color: #991b1b;
    background: #fff5f5;
    border-color: #fecaca;
}

@keyframes v3-toast-in {
    from {
        opacity: 0;
        transform: translateY(8px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 1050px) {
    .v3-stat-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .v3-card-grid,
    .v3-guide-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .v3-list-item {
        grid-template-columns:
            auto minmax(150px, 1fr)
            repeat(2, minmax(100px, 0.55fr));
    }

    .v3-list-field.optional {
        display: none;
    }
}

@media (max-width: 720px) {
    .v3-page {
        padding: 10px 12px 28px;
    }

    .v3-topbar {
        min-height: 57px;
        margin-bottom: 16px;
        padding: 7px 9px;
        border-radius: 15px;
    }

    .v3-brand-mark {
        width: 39px;
        height: 39px;
        border-radius: 12px;
    }

    .v3-brand strong {
        font-size: 0.75rem;
    }

    .v3-brand small {
        font-size: 0.51rem;
    }

    .v3-dashboard-link {
        width: 39px;
        min-height: 39px;
        padding: 0;
    }

    .v3-dashboard-link span {
        display: none;
    }

    .v3-page-heading {
        align-items: flex-start;
        margin-bottom: 17px;
    }

    .v3-page-icon {
        width: 47px;
        height: 47px;
        border-radius: 15px;
    }

    .v3-page-icon svg {
        width: 24px;
        height: 24px;
    }

    .v3-breadcrumb {
        display: none;
    }

    .v3-page-heading h1 {
        font-size: 1.25rem;
    }

    .v3-page-heading p {
        margin-top: 5px;
        font-size: 0.68rem;
    }

    .v3-toolbar {
        align-items: stretch;
        flex-direction: column;
        padding: 10px;
    }

    .v3-stat-grid {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        scrollbar-width: none;
    }

    .v3-stat-grid::-webkit-scrollbar {
        display: none;
    }

    .v3-stat-card {
        flex: 0 0 145px;
        padding: 13px;
    }

    .v3-stat-card strong {
        font-size: 1.18rem;
    }

    .v3-panel {
        padding: 14px;
        border-radius: 16px;
    }

    .v3-card-grid,
    .v3-guide-grid {
        grid-template-columns: 1fr;
    }

    .v3-list-item {
        grid-template-columns:
            auto minmax(0, 1fr)
            auto;
        padding: 12px;
    }

    .v3-list-field.mobile-full {
        grid-column: 2 / -1;
    }

    .v3-list-field.optional {
        display: none;
    }

    .v3-detail-grid {
        grid-template-columns: 1fr;
    }

    .v3-code-panel {
        min-height: 360px;
        font-size: 0.61rem;
    }

    .v3-toast-container {
        right: 10px;
        bottom: 10px;
        left: 10px;
    }

    .v3-toast {
        min-width: 0;
        max-width: none;
    }
}
'''

(STATIC_CSS / "portal-v3.css").write_text(
    css.strip() + "\n",
    encoding="utf-8",
)

print("CSS installé : static/css/portal-v3.css")


js = r'''
window.PortalV3 = (() => {
    function escapeHtml(value) {
        const element = document.createElement("div");
        element.textContent = String(value ?? "");
        return element.innerHTML;
    }

    function number(value, digits = 1) {
        const parsed = Number(value);

        return Number.isFinite(parsed)
            ? parsed.toFixed(digits)
            : "0.0";
    }

    function showToast(message, type = "success") {
        const container = document.getElementById(
            "v3-toast-container"
        );

        if (!container) {
            return;
        }

        const toast = document.createElement("div");

        toast.className = `v3-toast ${
            type === "error"
                ? "error"
                : ""
        }`;

        toast.textContent = message;
        container.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3500);
    }

    function bindSearch({
        input,
        selector,
        getText,
        empty,
    }) {
        const field = document.querySelector(input);

        if (!field) {
            return;
        }

        function filter() {
            const query = field.value
                .trim()
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "");

            let visible = 0;

            document
                .querySelectorAll(selector)
                .forEach((element) => {
                    const text = (
                        getText
                            ? getText(element)
                            : element.textContent
                    )
                        .toLowerCase()
                        .normalize("NFD")
                        .replace(/[\u0300-\u036f]/g, "");

                    const matches =
                        !query
                        || text.includes(query);

                    element.hidden = !matches;

                    if (matches) {
                        visible += 1;
                    }
                });

            if (empty) {
                const emptyElement =
                    document.querySelector(empty);

                if (emptyElement) {
                    emptyElement.hidden =
                        visible !== 0;
                }
            }
        }

        field.addEventListener("input", filter);
    }

    function bindAccordions() {
        document
            .querySelectorAll(".v3-accordion-button")
            .forEach((button) => {
                button.addEventListener(
                    "click",
                    () => {
                        button.closest(
                            ".v3-accordion-item"
                        )?.classList.toggle("open");
                    }
                );
            });
    }

    document.addEventListener(
        "DOMContentLoaded",
        bindAccordions
    );

    return {
        escapeHtml,
        number,
        showToast,
        bindSearch,
    };
})();
'''

(STATIC_JS / "portal-v3.js").write_text(
    js.strip() + "\n",
    encoding="utf-8",
)

print("JavaScript installé : static/js/portal-v3.js")


docker_tabs = r'''
<div class="v3-tabs">
    <a class="v3-tab {{ 'active' if active_docker_page == 'containers' else '' }}" href="/containers">
        Conteneurs
    </a>

    <a class="v3-tab {{ 'active' if active_docker_page == 'images' else '' }}" href="/images">
        Images
    </a>

    <a class="v3-tab {{ 'active' if active_docker_page == 'volumes' else '' }}" href="/volumes">
        Volumes
    </a>

    <a class="v3-tab {{ 'active' if active_docker_page == 'networks' else '' }}" href="/networks">
        Réseaux
    </a>
</div>
'''

write_template(
    "_docker_tabs.html",
    docker_tabs,
)


images = r'''
{% extends "portal_v3_base.html" %}

{% set active_docker_page = "images" %}

{% block title %}Images Docker — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Docker / Images{% endblock %}
{% block page_title %}Images Docker{% endblock %}

{% block page_description %}
Inventaire des images disponibles sur srv-web, avec leur taille,
leur tag et leur état d’utilisation.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <rect x="3" y="5" width="18" height="14" rx="2"/>
    <circle cx="8" cy="10" r="1.5"/>
    <path d="m4 17 5-5 3 3 2-2 6 6"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="image-search"
            type="search"
            placeholder="Rechercher un repository, un tag ou un identifiant…"
        >
    </label>

    {% include "_docker_tabs.html" %}
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Images détectées</span>

            <span class="v3-icon">
                <svg viewBox="0 0 24 24">
                    <rect x="3" y="5" width="18" height="14" rx="2"/>
                    <path d="m4 17 5-5 3 3 2-2 6 6"/>
                </svg>
            </span>
        </div>

        <strong id="images-total">{{ images | length }}</strong>
        <small>Images présentes localement</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Images utilisées</span>

            <span class="v3-icon green">
                <svg viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="m8 12 2.5 2.5L16 9"/>
                </svg>
            </span>
        </div>

        <strong id="images-used">
            {{ images | selectattr("used") | list | length }}
        </strong>

        <small>Référencées par un conteneur</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Taille totale</span>

            <span class="v3-icon purple">
                <svg viewBox="0 0 24 24">
                    <path d="M5 4h14v16H5Z"/>
                    <path d="M9 4v16M15 4v16"/>
                </svg>
            </span>
        </div>

        <strong id="images-size">--</strong>
        <small>Espace occupé approximatif</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Repository principal</span>

            <span class="v3-icon cyan">
                <svg viewBox="0 0 24 24">
                    <path d="M4 7h16v13H4Z"/>
                    <path d="M7 4h10v3H7Z"/>
                </svg>
            </span>
        </div>

        <strong id="images-main" style="font-size:.82rem">
            {% if images %}
                {{ images[0].repository }}
            {% else %}
                Aucun
            {% endif %}
        </strong>

        <small>Première image inventoriée</small>
    </article>
</section>

<section class="v3-panel">
    <header class="v3-panel-header">
        <div>
            <h2>Catalogue des images</h2>
            <p>Actualisation automatique toutes les 10 secondes.</p>
        </div>

        <span id="images-updated">Chargement…</span>
    </header>

    <div
        id="images-grid"
        class="v3-card-grid"
    >
        {% for image in images %}
            <article class="v3-resource-card image-card">
                <header class="v3-resource-header">
                    <div class="v3-resource-identity">
                        <span class="v3-icon">
                            <svg viewBox="0 0 24 24">
                                <rect x="3" y="5" width="18" height="14" rx="2"/>
                                <path d="m4 17 5-5 3 3 2-2 6 6"/>
                            </svg>
                        </span>

                        <div style="min-width:0">
                            <strong>{{ image.repository }}</strong>
                            <span>{{ image.id }}</span>
                        </div>
                    </div>

                    <span class="v3-badge {% if image.used %}success{% endif %}">
                        {% if image.used %}Utilisée{% else %}Disponible{% endif %}
                    </span>
                </header>

                <div class="v3-detail-grid">
                    <div class="v3-detail">
                        <span>Tag</span>
                        <strong>{{ image.tag }}</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Taille</span>
                        <strong>{{ image.size_mb }} Mo</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Créée le</span>
                        <strong>{{ image.created }}</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Identifiant</span>
                        <strong>{{ image.id }}</strong>
                    </div>
                </div>
            </article>
        {% endfor %}
    </div>

    <div
        id="images-empty"
        class="v3-empty"
        {% if images %}hidden{% endif %}
    >
        <span class="v3-empty-icon">
            <svg viewBox="0 0 24 24">
                <rect x="3" y="5" width="18" height="14" rx="2"/>
                <path d="M8 9h.01M5 17l4-4 3 3"/>
            </svg>
        </span>

        <h3>Aucune image Docker trouvée</h3>

        <p>
            Les images téléchargées ou construites apparaîtront
            automatiquement dans cette page.
        </p>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("images-grid");
    const empty = document.getElementById("images-empty");
    let images = {{ images | tojson }};

    function render(items) {
        const escape = PortalV3.escapeHtml;

        if (!items.length) {
            grid.innerHTML = "";
            empty.hidden = false;
        } else {
            empty.hidden = true;

            grid.innerHTML = items.map((image) => `
                <article class="v3-resource-card image-card">
                    <header class="v3-resource-header">
                        <div class="v3-resource-identity">
                            <span class="v3-icon">
                                <svg viewBox="0 0 24 24">
                                    <rect x="3" y="5" width="18" height="14" rx="2"/>
                                    <path d="m4 17 5-5 3 3 2-2 6 6"/>
                                </svg>
                            </span>

                            <div style="min-width:0">
                                <strong>${escape(image.repository)}</strong>
                                <span>${escape(image.id)}</span>
                            </div>
                        </div>

                        <span class="v3-badge ${image.used ? "success" : ""}">
                            ${image.used ? "Utilisée" : "Disponible"}
                        </span>
                    </header>

                    <div class="v3-detail-grid">
                        <div class="v3-detail">
                            <span>Tag</span>
                            <strong>${escape(image.tag)}</strong>
                        </div>

                        <div class="v3-detail">
                            <span>Taille</span>
                            <strong>${PortalV3.number(image.size_mb)} Mo</strong>
                        </div>

                        <div class="v3-detail">
                            <span>Créée le</span>
                            <strong>${escape(image.created)}</strong>
                        </div>

                        <div class="v3-detail">
                            <span>Identifiant</span>
                            <strong>${escape(image.id)}</strong>
                        </div>
                    </div>
                </article>
            `).join("");
        }

        const totalSize = items.reduce(
            (total, image) =>
                total + Number(image.size_mb || 0),
            0
        );

        document.getElementById("images-total").textContent =
            items.length;

        document.getElementById("images-used").textContent =
            items.filter((image) => image.used).length;

        document.getElementById("images-size").textContent =
            `${totalSize.toFixed(1)} Mo`;

        document.getElementById("images-main").textContent =
            items[0]?.repository || "Aucun";
    }

    async function refresh() {
        try {
            const response = await fetch(
                `/api/docker/images?t=${Date.now()}`,
                { cache: "no-store" }
            );

            if (!response.ok) {
                throw new Error("API Docker indisponible");
            }

            const payload = await response.json();

            images = Array.isArray(payload.images)
                ? payload.images
                : [];

            render(images);

            document.getElementById(
                "images-updated"
            ).textContent =
                `Actualisé à ${
                    new Date(
                        payload.updated_at
                    ).toLocaleTimeString("fr-FR")
                }`;
        } catch (error) {
            console.error(error);
            PortalV3.showToast(
                "Impossible d’actualiser les images Docker.",
                "error"
            );
        }
    }

    PortalV3.bindSearch({
        input: "#image-search",
        selector: ".image-card",
        empty: "#images-empty",
    });

    render(images);
    window.setInterval(refresh, 10000);
});
</script>
{% endblock %}
'''

write_template(
    "images.html",
    images,
)


volumes = r'''
{% extends "portal_v3_base.html" %}

{% set active_docker_page = "volumes" %}

{% block title %}Volumes Docker — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Docker / Volumes{% endblock %}
{% block page_title %}Volumes Docker{% endblock %}

{% block page_description %}
Inventaire des espaces de stockage persistants utilisés
par les conteneurs Docker.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <ellipse cx="12" cy="6" rx="8" ry="3"/>
    <path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>
    <path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="volume-search"
            type="search"
            placeholder="Rechercher un volume, un driver ou un point de montage…"
        >
    </label>

    {% include "_docker_tabs.html" %}
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Volumes détectés</span>

            <span class="v3-icon purple">
                <svg viewBox="0 0 24 24">
                    <ellipse cx="12" cy="6" rx="8" ry="3"/>
                    <path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>
                </svg>
            </span>
        </div>

        <strong id="volumes-total">{{ volumes | length }}</strong>
        <small>Stockages Docker persistants</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Driver principal</span>

            <span class="v3-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M5 4h14v16H5Z"/>
                    <path d="M8 8h8M8 12h8"/>
                </svg>
            </span>
        </div>

        <strong id="volumes-driver" style="font-size:.88rem">
            {% if volumes %}
                {{ volumes[0].driver }}
            {% else %}
                Aucun
            {% endif %}
        </strong>

        <small>Premier driver détecté</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Points de montage</span>

            <span class="v3-icon cyan">
                <svg viewBox="0 0 24 24">
                    <path d="M4 6h6l2 2h8v10H4Z"/>
                </svg>
            </span>
        </div>

        <strong id="volumes-mounts">{{ volumes | length }}</strong>
        <small>Emplacements disponibles</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>État du stockage</span>

            <span class="v3-icon green">
                <svg viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="m8 12 2.5 2.5L16 9"/>
                </svg>
            </span>
        </div>

        <strong style="font-size:.88rem">
            {% if volumes %}Disponible{% else %}Aucun volume{% endif %}
        </strong>

        <small>Inventaire Docker local</small>
    </article>
</section>

<section class="v3-panel">
    <header class="v3-panel-header">
        <div>
            <h2>Espaces persistants</h2>
            <p>Actualisation automatique toutes les 10 secondes.</p>
        </div>

        <span id="volumes-updated">Chargement…</span>
    </header>

    <div
        id="volumes-grid"
        class="v3-card-grid"
    ></div>

    <div
        id="volumes-empty"
        class="v3-empty"
        {% if volumes %}hidden{% endif %}
    >
        <span class="v3-empty-icon">
            <svg viewBox="0 0 24 24">
                <ellipse cx="12" cy="6" rx="8" ry="3"/>
                <path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>
            </svg>
        </span>

        <h3>Aucun volume Docker présent</h3>

        <p>
            La plateforme fonctionne actuellement sans volume Docker
            nommé. Les futurs volumes apparaîtront automatiquement ici.
        </p>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("volumes-grid");
    const empty = document.getElementById("volumes-empty");
    let volumes = {{ volumes | tojson }};

    function render(items) {
        const escape = PortalV3.escapeHtml;

        grid.innerHTML = items.map((volume) => `
            <article class="v3-resource-card volume-card">
                <header class="v3-resource-header">
                    <div class="v3-resource-identity">
                        <span class="v3-icon purple">
                            <svg viewBox="0 0 24 24">
                                <ellipse cx="12" cy="6" rx="8" ry="3"/>
                                <path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>
                            </svg>
                        </span>

                        <div style="min-width:0">
                            <strong>${escape(volume.name)}</strong>
                            <span>${escape(volume.driver)}</span>
                        </div>
                    </div>

                    <span class="v3-badge success">
                        Disponible
                    </span>
                </header>

                <div class="v3-detail-grid">
                    <div class="v3-detail">
                        <span>Driver</span>
                        <strong>${escape(volume.driver)}</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Créé le</span>
                        <strong>${escape(volume.created || "--")}</strong>
                    </div>

                    <div class="v3-detail" style="grid-column:1/-1">
                        <span>Point de montage</span>
                        <strong>${escape(volume.mountpoint || "--")}</strong>
                    </div>
                </div>
            </article>
        `).join("");

        empty.hidden = items.length !== 0;

        document.getElementById(
            "volumes-total"
        ).textContent = items.length;

        document.getElementById(
            "volumes-mounts"
        ).textContent = items.length;

        document.getElementById(
            "volumes-driver"
        ).textContent =
            items[0]?.driver || "Aucun";
    }

    async function refresh() {
        try {
            const response = await fetch(
                `/api/docker/volumes?t=${Date.now()}`,
                { cache: "no-store" }
            );

            if (!response.ok) {
                throw new Error("API Docker indisponible");
            }

            const payload = await response.json();

            volumes = Array.isArray(payload.volumes)
                ? payload.volumes
                : [];

            render(volumes);

            document.getElementById(
                "volumes-updated"
            ).textContent =
                `Actualisé à ${
                    new Date(
                        payload.updated_at
                    ).toLocaleTimeString("fr-FR")
                }`;
        } catch (error) {
            console.error(error);

            PortalV3.showToast(
                "Impossible d’actualiser les volumes.",
                "error"
            );
        }
    }

    PortalV3.bindSearch({
        input: "#volume-search",
        selector: ".volume-card",
        empty: "#volumes-empty",
    });

    render(volumes);
    window.setInterval(refresh, 10000);
});
</script>
{% endblock %}
'''

write_template(
    "volumes.html",
    volumes,
)


networks = r'''
{% extends "portal_v3_base.html" %}

{% set active_docker_page = "networks" %}

{% block title %}Réseaux Docker — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Docker / Réseaux{% endblock %}
{% block page_title %}Réseaux Docker{% endblock %}

{% block page_description %}
Topologie des réseaux Docker locaux et nombre de conteneurs
connectés à chaque segment.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <circle cx="6" cy="12" r="2.5"/>
    <circle cx="18" cy="6" r="2.5"/>
    <circle cx="18" cy="18" r="2.5"/>
    <path d="m8.2 10.9 7.5-3.8M8.2 13.1l7.5 3.8"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="network-search"
            type="search"
            placeholder="Rechercher un réseau, un driver ou un scope…"
        >
    </label>

    {% include "_docker_tabs.html" %}
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Réseaux détectés</span>

            <span class="v3-icon cyan">
                <svg viewBox="0 0 24 24">
                    <circle cx="6" cy="12" r="2.5"/>
                    <circle cx="18" cy="6" r="2.5"/>
                    <circle cx="18" cy="18" r="2.5"/>
                    <path d="m8.2 10.9 7.5-3.8M8.2 13.1l7.5 3.8"/>
                </svg>
            </span>
        </div>

        <strong id="networks-total">{{ networks | length }}</strong>
        <small>Réseaux Docker disponibles</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Conteneurs connectés</span>

            <span class="v3-icon green">
                <svg viewBox="0 0 24 24">
                    <rect x="4" y="6" width="16" height="12" rx="2"/>
                    <path d="M8 10h8M8 14h5"/>
                </svg>
            </span>
        </div>

        <strong id="networks-containers">
            {{ networks | sum(attribute="containers") }}
        </strong>

        <small>Connexions réseau recensées</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Réseaux bridge</span>

            <span class="v3-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M4 18h16M6 18V9M18 18V9M6 9c3-4 9-4 12 0"/>
                </svg>
            </span>
        </div>

        <strong id="networks-bridge">
            {{ networks | selectattr("driver", "equalto", "bridge") | list | length }}
        </strong>

        <small>Segments utilisant le driver bridge</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Scope principal</span>

            <span class="v3-icon purple">
                <svg viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="M3 12h18M12 3a15 15 0 0 1 0 18"/>
                </svg>
            </span>
        </div>

        <strong id="networks-scope" style="font-size:.88rem">
            {% if networks %}
                {{ networks[0].scope }}
            {% else %}
                Aucun
            {% endif %}
        </strong>

        <small>Portée réseau dominante</small>
    </article>
</section>

<section class="v3-panel">
    <header class="v3-panel-header">
        <div>
            <h2>Segments réseau Docker</h2>
            <p>Actualisation automatique toutes les 10 secondes.</p>
        </div>

        <span id="networks-updated">Chargement…</span>
    </header>

    <div
        id="networks-grid"
        class="v3-card-grid"
    ></div>

    <div
        id="networks-empty"
        class="v3-empty"
        {% if networks %}hidden{% endif %}
    >
        <span class="v3-empty-icon">
            <svg viewBox="0 0 24 24">
                <circle cx="6" cy="12" r="2.5"/>
                <circle cx="18" cy="6" r="2.5"/>
                <circle cx="18" cy="18" r="2.5"/>
                <path d="m8.2 10.9 7.5-3.8M8.2 13.1l7.5 3.8"/>
            </svg>
        </span>

        <h3>Aucun réseau Docker détecté</h3>
        <p>Les réseaux créés par Docker apparaîtront ici.</p>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    const grid = document.getElementById("networks-grid");
    const empty = document.getElementById("networks-empty");
    let networks = {{ networks | tojson }};

    function render(items) {
        const escape = PortalV3.escapeHtml;

        grid.innerHTML = items.map((network) => `
            <article class="v3-resource-card network-card">
                <header class="v3-resource-header">
                    <div class="v3-resource-identity">
                        <span class="v3-icon cyan">
                            <svg viewBox="0 0 24 24">
                                <circle cx="6" cy="12" r="2.5"/>
                                <circle cx="18" cy="6" r="2.5"/>
                                <circle cx="18" cy="18" r="2.5"/>
                                <path d="m8.2 10.9 7.5-3.8M8.2 13.1l7.5 3.8"/>
                            </svg>
                        </span>

                        <div style="min-width:0">
                            <strong>${escape(network.name)}</strong>
                            <span>${escape(network.id || "Réseau Docker")}</span>
                        </div>
                    </div>

                    <span class="v3-badge ${
                        Number(network.containers || 0) > 0
                            ? "success"
                            : ""
                    }">
                        ${Number(network.containers || 0)} conteneur(s)
                    </span>
                </header>

                <div class="v3-detail-grid">
                    <div class="v3-detail">
                        <span>Driver</span>
                        <strong>${escape(network.driver)}</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Scope</span>
                        <strong>${escape(network.scope)}</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Conteneurs</span>
                        <strong>${Number(network.containers || 0)}</strong>
                    </div>

                    <div class="v3-detail">
                        <span>Type</span>
                        <strong>
                            ${
                                network.name === "application_default"
                                    ? "Applicatif"
                                    : "Système"
                            }
                        </strong>
                    </div>
                </div>
            </article>
        `).join("");

        empty.hidden = items.length !== 0;

        document.getElementById(
            "networks-total"
        ).textContent = items.length;

        document.getElementById(
            "networks-containers"
        ).textContent = items.reduce(
            (total, network) =>
                total + Number(network.containers || 0),
            0
        );

        document.getElementById(
            "networks-bridge"
        ).textContent = items.filter(
            (network) => network.driver === "bridge"
        ).length;

        document.getElementById(
            "networks-scope"
        ).textContent =
            items[0]?.scope || "Aucun";
    }

    async function refresh() {
        try {
            const response = await fetch(
                `/api/docker/networks?t=${Date.now()}`,
                { cache: "no-store" }
            );

            if (!response.ok) {
                throw new Error("API Docker indisponible");
            }

            const payload = await response.json();

            networks = Array.isArray(payload.networks)
                ? payload.networks
                : [];

            render(networks);

            document.getElementById(
                "networks-updated"
            ).textContent =
                `Actualisé à ${
                    new Date(
                        payload.updated_at
                    ).toLocaleTimeString("fr-FR")
                }`;
        } catch (error) {
            console.error(error);

            PortalV3.showToast(
                "Impossible d’actualiser les réseaux.",
                "error"
            );
        }
    }

    PortalV3.bindSearch({
        input: "#network-search",
        selector: ".network-card",
        empty: "#networks-empty",
    });

    render(networks);
    window.setInterval(refresh, 10000);
});
</script>
{% endblock %}
'''

write_template(
    "networks.html",
    networks,
)


prometheus = r'''
{% extends "portal_v3_base.html" %}

{% block title %}Prometheus — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Monitoring / Prometheus{% endblock %}
{% block page_title %}Targets Prometheus{% endblock %}

{% block page_description %}
État en temps réel des sources de métriques supervisées
par Prometheus.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <path d="M12 3c2.5 3 4.5 5.3 4.5 8.2A4.5 4.5 0 0 1 12 16a4.5 4.5 0 0 1-4.5-4.8C7.5 8.3 9.5 6 12 3Z"/>
    <path d="M5 20h14M8 16.5 6.5 20M16 16.5l1.5 3.5"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="target-search"
            type="search"
            placeholder="Rechercher une target, une instance ou un job…"
        >
    </label>

    <div class="v3-tabs">
        <a class="v3-tab" href="/monitoring">Monitoring</a>
        <a class="v3-tab active" href="/prometheus">Prometheus</a>

        <a
            class="v3-tab"
            href="https://grafana.emmanuelinfra.fr"
            target="_blank"
            rel="noopener noreferrer"
        >
            Grafana
        </a>
    </div>
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Targets détectées</span>
            <span class="v3-icon">{{ "" }}</span>
        </div>

        <strong id="targets-total">--</strong>
        <small>Sources configurées</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Targets disponibles</span>

            <span class="v3-icon green">
                <svg viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="9"/>
                    <path d="m8 12 2.5 2.5L16 9"/>
                </svg>
            </span>
        </div>

        <strong id="targets-up">--</strong>
        <small>État UP</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Targets indisponibles</span>

            <span class="v3-icon orange">
                <svg viewBox="0 0 24 24">
                    <path d="M12 4 3 20h18Z"/>
                    <path d="M12 9v5M12 17h.01"/>
                </svg>
            </span>
        </div>

        <strong id="targets-down">--</strong>
        <small>État DOWN ou inconnu</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>État Prometheus</span>

            <span class="v3-icon purple">
                <svg viewBox="0 0 24 24">
                    <path d="M4 12h3l2-5 4 10 2-5h5"/>
                </svg>
            </span>
        </div>

        <strong id="prometheus-state" style="font-size:.88rem">
            Analyse…
        </strong>

        <small>Collecteur central</small>
    </article>
</section>

<section class="v3-panel">
    <header class="v3-panel-header">
        <div>
            <h2>Sources supervisées</h2>
            <p>Actualisation automatique toutes les 10 secondes.</p>
        </div>

        <span id="targets-updated">Chargement…</span>
    </header>

    <div
        id="targets-list"
        class="v3-list"
    ></div>

    <div
        id="targets-empty"
        class="v3-empty"
        hidden
    >
        <span class="v3-empty-icon">
            <svg viewBox="0 0 24 24">
                <path d="M4 12h3l2-5 4 10 2-5h5"/>
            </svg>
        </span>

        <h3>Aucune target Prometheus trouvée</h3>
        <p>Vérifiez la configuration et la disponibilité de Prometheus.</p>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    const list = document.getElementById("targets-list");
    const empty = document.getElementById("targets-empty");

    function getTargets(payload) {
        if (Array.isArray(payload)) {
            return payload;
        }

        if (Array.isArray(payload.targets)) {
            return payload.targets;
        }

        if (Array.isArray(payload.data)) {
            return payload.data;
        }

        if (Array.isArray(payload.activeTargets)) {
            return payload.activeTargets;
        }

        return [];
    }

    function isUp(target) {
        const state = String(
            target.health
            || target.status
            || target.state
            || ""
        ).toLowerCase();

        return [
            "up",
            "healthy",
            "active",
            "true",
        ].includes(state);
    }

    function render(targets) {
        const escape = PortalV3.escapeHtml;

        list.innerHTML = targets.map((target) => {
            const up = isUp(target);

            const name =
                target.job
                || target.labels?.job
                || target.name
                || "Target Prometheus";

            const instance =
                target.instance
                || target.labels?.instance
                || target.scrapeUrl
                || target.url
                || "--";

            const error =
                target.lastError
                || target.error
                || "";

            return `
                <article class="v3-list-item target-item">
                    <span class="v3-icon ${up ? "green" : "orange"}">
                        <svg viewBox="0 0 24 24">
                            ${
                                up
                                    ? `
                                        <circle cx="12" cy="12" r="9"/>
                                        <path d="m8 12 2.5 2.5L16 9"/>
                                    `
                                    : `
                                        <path d="M12 4 3 20h18Z"/>
                                        <path d="M12 9v5M12 17h.01"/>
                                    `
                            }
                        </svg>
                    </span>

                    <div class="v3-list-field mobile-full">
                        <span>Job</span>
                        <strong>${escape(name)}</strong>
                    </div>

                    <div class="v3-list-field">
                        <span>Instance</span>
                        <strong>${escape(instance)}</strong>
                    </div>

                    <div class="v3-list-field optional">
                        <span>Dernier scrape</span>
                        <strong>
                            ${escape(
                                target.lastScrape
                                || target.last_scrape
                                || "--"
                            )}
                        </strong>
                    </div>

                    <div class="v3-list-field">
                        <span>État</span>
                        <strong>
                            <span class="v3-badge ${
                                up ? "success" : "danger"
                            }">
                                ${up ? "UP" : "DOWN"}
                            </span>
                        </strong>
                    </div>

                    ${
                        error
                            ? `
                                <div class="v3-list-field optional">
                                    <span>Erreur</span>
                                    <strong>${escape(error)}</strong>
                                </div>
                            `
                            : ""
                    }
                </article>
            `;
        }).join("");

        empty.hidden = targets.length !== 0;

        const upCount = targets.filter(isUp).length;

        document.getElementById(
            "targets-total"
        ).textContent = targets.length;

        document.getElementById(
            "targets-up"
        ).textContent = upCount;

        document.getElementById(
            "targets-down"
        ).textContent = targets.length - upCount;

        document.getElementById(
            "prometheus-state"
        ).textContent =
            targets.length > 0
            && upCount === targets.length
                ? "Opérationnel"
                : targets.length
                    ? "Dégradé"
                    : "Indisponible";
    }

    async function refresh() {
        try {
            const response = await fetch(
                `/api/prometheus/targets?t=${Date.now()}`,
                { cache: "no-store" }
            );

            if (!response.ok) {
                throw new Error("Prometheus indisponible");
            }

            const payload = await response.json();
            const targets = getTargets(payload);

            render(targets);

            document.getElementById(
                "targets-updated"
            ).textContent =
                `Actualisé à ${
                    new Date().toLocaleTimeString("fr-FR")
                }`;
        } catch (error) {
            console.error(error);
            render([]);

            PortalV3.showToast(
                "Impossible d’actualiser les targets Prometheus.",
                "error"
            );
        }
    }

    PortalV3.bindSearch({
        input: "#target-search",
        selector: ".target-item",
        empty: "#targets-empty",
    });

    refresh();
    window.setInterval(refresh, 10000);
});
</script>
{% endblock %}
'''

write_template(
    "prometheus.html",
    prometheus,
)


logs = r'''
{% extends "portal_v3_base.html" %}

{% block title %}Journaux — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Observabilité / Journaux{% endblock %}
{% block page_title %}Journaux système{% endblock %}

{% block page_description %}
Consultation des journaux applicatifs et techniques
exportés par la plateforme.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <path d="M6 3h12v18H6Z"/>
    <path d="M9 8h6M9 12h6M9 16h4"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="log-search"
            type="search"
            placeholder="Rechercher dans le journal affiché…"
        >
    </label>

    <div class="v3-tabs">
        <a class="v3-tab" href="/audit">Audit</a>
        <a class="v3-tab active" href="/logs">Journaux</a>
        <a class="v3-tab" href="/monitoring">Monitoring</a>
    </div>
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Journal sélectionné</span>

            <span class="v3-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M6 3h12v18H6Z"/>
                    <path d="M9 8h6M9 12h6"/>
                </svg>
            </span>
        </div>

        <strong
            id="selected-log-name"
            style="font-size:.83rem"
        >
            {{ selected_log or "application" }}
        </strong>

        <small>Source actuellement affichée</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Lignes chargées</span>

            <span class="v3-icon cyan">
                <svg viewBox="0 0 24 24">
                    <path d="M5 7h14M5 12h14M5 17h9"/>
                </svg>
            </span>
        </div>

        <strong id="log-lines-count">{{ log_lines | length }}</strong>
        <small>Entrées affichées</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Filtrage</span>

            <span class="v3-icon purple">
                <svg viewBox="0 0 24 24">
                    <path d="M4 5h16l-6 7v6l-4 2v-8Z"/>
                </svg>
            </span>
        </div>

        <strong
            id="log-filter-state"
            style="font-size:.83rem"
        >
            Aucun
        </strong>

        <small>Recherche locale instantanée</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Mode d’accès</span>

            <span class="v3-icon green">
                <svg viewBox="0 0 24 24">
                    <path d="M7 11V8a5 5 0 0 1 10 0v3"/>
                    <rect x="5" y="11" width="14" height="10" rx="2"/>
                </svg>
            </span>
        </div>

        <strong style="font-size:.83rem">
            Lecture seule
        </strong>

        <small>Aucune modification des fichiers</small>
    </article>
</section>

<section class="v3-panel">
    <header class="v3-panel-header">
        <div>
            <h2>Contenu du journal</h2>
            <p>
                Les lignes sont affichées dans l’ordre fourni
                par le service de journaux.
            </p>
        </div>

        <div style="display:flex;gap:7px">
            <button
                id="copy-logs"
                class="v3-button"
                type="button"
            >
                Copier
            </button>

            <button
                id="refresh-logs"
                class="v3-button primary"
                type="button"
            >
                Actualiser
            </button>
        </div>
    </header>

    <pre
        id="log-content"
        class="v3-code-panel"
    >{% for line in log_lines %}{{ line }}
{% endfor %}</pre>

    <div
        id="logs-updated"
        class="v3-updated"
    >
        Journal chargé depuis le serveur.
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    const content = document.getElementById("log-content");
    const search = document.getElementById("log-search");
    const selectedLog =
        {{ (selected_log or "application") | tojson }};

    let originalText = content.textContent;

    function applySearch() {
        const query = search.value.trim().toLowerCase();

        document.getElementById(
            "log-filter-state"
        ).textContent = query || "Aucun";

        if (!query) {
            content.textContent = originalText;
            return;
        }

        content.textContent = originalText
            .split("\n")
            .filter((line) =>
                line.toLowerCase().includes(query)
            )
            .join("\n");
    }

    async function refresh() {
        try {
            const response = await fetch(
                `/api/logs/${
                    encodeURIComponent(selectedLog)
                }?t=${Date.now()}`,
                { cache: "no-store" }
            );

            if (!response.ok) {
                throw new Error("Journal indisponible");
            }

            const payload = await response.json();

            if (Array.isArray(payload.lines)) {
                originalText = payload.lines.join("\n");
            } else if (typeof payload.content === "string") {
                originalText = payload.content;
            } else if (typeof payload.logs === "string") {
                originalText = payload.logs;
            } else if (Array.isArray(payload)) {
                originalText = payload.join("\n");
            } else {
                originalText = JSON.stringify(
                    payload,
                    null,
                    2
                );
            }

            document.getElementById(
                "log-lines-count"
            ).textContent =
                originalText.split("\n").filter(Boolean).length;

            applySearch();

            document.getElementById(
                "logs-updated"
            ).textContent =
                `Actualisé à ${
                    new Date().toLocaleTimeString("fr-FR")
                }`;
        } catch (error) {
            console.error(error);

            PortalV3.showToast(
                "Impossible d’actualiser le journal.",
                "error"
            );
        }
    }

    search.addEventListener("input", applySearch);

    document.getElementById(
        "refresh-logs"
    ).addEventListener("click", refresh);

    document.getElementById(
        "copy-logs"
    ).addEventListener("click", async () => {
        try {
            await navigator.clipboard.writeText(
                content.textContent
            );

            PortalV3.showToast(
                "Journal copié dans le presse-papiers."
            );
        } catch (error) {
            PortalV3.showToast(
                "Impossible de copier le journal.",
                "error"
            );
        }
    });
});
</script>
{% endblock %}
'''

write_template(
    "logs.html",
    logs,
)


help_center = r'''
{% extends "portal_v3_base.html" %}

{% block title %}Centre d’aide — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Aide{% endblock %}
{% block page_title %}Centre d’aide{% endblock %}

{% block page_description %}
Guides, documentation, diagnostic et assistance technique
pour exploiter Secure Local Cloud Infrastructure.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="9"/>
    <path d="M9.8 9a2.4 2.4 0 1 1 3.4 2.2c-.8.4-1.2.9-1.2 1.8"/>
    <path d="M12 17h.01"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="help-search"
            type="search"
            placeholder="Rechercher une rubrique d’aide…"
        >
    </label>

    <div class="v3-tabs">
        <a class="v3-tab active" href="/help">Centre d’aide</a>
        <a class="v3-tab" href="/documentation">Documentation</a>
        <a class="v3-tab" href="/faq">FAQ</a>
        <a class="v3-tab" href="/assistant">Emma_IA</a>
    </div>
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Guides principaux</span>

            <span class="v3-icon">
                <svg viewBox="0 0 24 24">
                    <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v16H6.5A2.5 2.5 0 0 0 4 21.5Z"/>
                    <path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H13v16h4.5a2.5 2.5 0 0 1 2.5 2.5Z"/>
                </svg>
            </span>
        </div>

        <strong>6</strong>
        <small>Rubriques techniques disponibles</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Assistant technique</span>

            <span class="v3-icon purple">
                <svg viewBox="0 0 24 24">
                    <rect x="4" y="6" width="16" height="13" rx="3"/>
                    <path d="M9 11h.01M15 11h.01M9 15h6M12 3v3"/>
                </svg>
            </span>
        </div>

        <strong style="font-size:.86rem">Emma_IA</strong>
        <small>Réponses basées sur les données réelles</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>État des ressources</span>

            <span class="v3-icon green">
                <svg viewBox="0 0 24 24">
                    <path d="M4 12h3l2-5 4 10 2-5h5"/>
                </svg>
            </span>
        </div>

        <strong style="font-size:.86rem">Temps réel</strong>
        <small>Métriques et services consultables</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Niveau d’accès</span>

            <span class="v3-icon cyan">
                <svg viewBox="0 0 24 24">
                    <path d="M7 11V8a5 5 0 0 1 10 0v3"/>
                    <rect x="5" y="11" width="14" height="10" rx="2"/>
                </svg>
            </span>
        </div>

        <strong style="font-size:.86rem">Sécurisé</strong>
        <small>Accès authentifié au portail</small>
    </article>
</section>

<section class="v3-guide-grid">
    <article class="v3-guide-card help-card">
        <span class="v3-icon">
            <svg viewBox="0 0 24 24">
                <path d="M12 3v12"/>
                <path d="m7 10 5 5 5-5"/>
                <path d="M5 21h14"/>
            </svg>
        </span>

        <h2>Prise en main</h2>

        <p>
            Découvrez les composants essentiels et le fonctionnement
            général de la plateforme.
        </p>

        <a href="/getting-started">
            Commencer le guide →
        </a>
    </article>

    <article class="v3-guide-card help-card">
        <span class="v3-icon purple">
            <svg viewBox="0 0 24 24">
                <path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v16H6.5A2.5 2.5 0 0 0 4 21.5Z"/>
                <path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H13v16h4.5a2.5 2.5 0 0 1 2.5 2.5Z"/>
            </svg>
        </span>

        <h2>Documentation technique</h2>

        <p>
            Consultez les guides Docker, Prometheus, Grafana,
            sécurité et architecture.
        </p>

        <a href="/documentation">
            Ouvrir la documentation →
        </a>
    </article>

    <article class="v3-guide-card help-card">
        <span class="v3-icon green">
            <svg viewBox="0 0 24 24">
                <rect x="4" y="6" width="16" height="13" rx="3"/>
                <path d="M9 11h.01M15 11h.01M9 15h6M12 3v3"/>
            </svg>
        </span>

        <h2>Emma_IA</h2>

        <p>
            Interrogez les données réelles de l’infrastructure
            et obtenez un diagnostic.
        </p>

        <a href="/assistant">
            Discuter avec Emma_IA →
        </a>
    </article>

    <article class="v3-guide-card help-card">
        <span class="v3-icon orange">
            <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="9"/>
                <path d="M9.8 9a2.4 2.4 0 1 1 3.4 2.2c-.8.4-1.2.9-1.2 1.8"/>
                <path d="M12 17h.01"/>
            </svg>
        </span>

        <h2>Questions fréquentes</h2>

        <p>
            Retrouvez les réponses rapides aux difficultés
            les plus courantes.
        </p>

        <a href="/faq">
            Consulter la FAQ →
        </a>
    </article>

    <article class="v3-guide-card help-card">
        <span class="v3-icon cyan">
            <svg viewBox="0 0 24 24">
                <path d="M4 12h3l2-5 4 10 2-5h5"/>
            </svg>
        </span>

        <h2>Monitoring</h2>

        <p>
            Analysez le CPU, la mémoire, le disque et
            l’historique des métriques.
        </p>

        <a href="/monitoring">
            Ouvrir le monitoring →
        </a>
    </article>

    <article class="v3-guide-card help-card">
        <span class="v3-icon purple">
            <svg viewBox="0 0 24 24">
                <path d="M12 3 5 6v5c0 4.8 2.8 8.3 7 10 4.2-1.7 7-5.2 7-10V6Z"/>
                <path d="m9 12 2 2 4-4"/>
            </svg>
        </span>

        <h2>Sécurité</h2>

        <p>
            Vérifiez le certificat TLS, UFW, Fail2ban,
            Nginx et Alertmanager.
        </p>

        <a href="/security">
            Consulter la sécurité →
        </a>
    </article>
</section>

<div
    id="help-empty"
    class="v3-empty"
    hidden
>
    <span class="v3-empty-icon">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>
    </span>

    <h3>Aucune rubrique trouvée</h3>
    <p>Essayez une recherche plus générale.</p>
</div>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    PortalV3.bindSearch({
        input: "#help-search",
        selector: ".help-card",
        empty: "#help-empty",
    });
});
</script>
{% endblock %}
'''

write_template(
    "help_center.html",
    help_center,
)


getting_started = r'''
{% extends "portal_v3_base.html" %}

{% block title %}Prise en main — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Aide / Prise en main{% endblock %}
{% block page_title %}Prise en main{% endblock %}

{% block page_description %}
Comprendre rapidement l’architecture, les services
et les principales fonctions du portail.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <path d="M12 3v12"/>
    <path d="m7 10 5 5 5-5"/>
    <path d="M5 21h14"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <div class="v3-tabs">
        <a class="v3-tab" href="/help">Centre d’aide</a>
        <a class="v3-tab active" href="/getting-started">Prise en main</a>
        <a class="v3-tab" href="/documentation">Documentation</a>
        <a class="v3-tab" href="/faq">FAQ</a>
    </div>

    <a class="v3-button primary" href="/assistant">
        Demander à Emma_IA
    </a>
</section>

<section class="v3-guide-grid">
    <article class="v3-guide-card">
        <span class="v3-icon">
            <svg viewBox="0 0 24 24">
                <rect x="4" y="3" width="16" height="7" rx="2"/>
                <rect x="4" y="14" width="16" height="7" rx="2"/>
                <path d="M8 6.5h.01M8 17.5h.01M12 6.5h5M12 17.5h5"/>
            </svg>
        </span>

        <h2>1. Comprendre les serveurs</h2>

        <p>
            La plateforme repose sur deux machines virtuelles
            Ubuntu Server.
        </p>

        <ul>
            <li>srv-web : 192.168.50.10</li>
            <li>srv-monitoring : 192.168.50.20</li>
            <li>Réseau privé : 192.168.50.0/24</li>
        </ul>
    </article>

    <article class="v3-guide-card">
        <span class="v3-icon purple">
            <svg viewBox="0 0 24 24">
                <rect x="3" y="7" width="5" height="5" rx="1"/>
                <rect x="9.5" y="7" width="5" height="5" rx="1"/>
                <rect x="16" y="7" width="5" height="5" rx="1"/>
                <path d="M4 15h16"/>
            </svg>
        </span>

        <h2>2. Identifier les services</h2>

        <ul>
            <li>Flask et Gunicorn</li>
            <li>Docker et cAdvisor</li>
            <li>Node Exporter</li>
            <li>Prometheus et Grafana</li>
            <li>Nginx et Cloudflare</li>
        </ul>
    </article>

    <article class="v3-guide-card">
        <span class="v3-icon green">
            <svg viewBox="0 0 24 24">
                <path d="M4 19V9M10 19V5M16 19v-7M22 19V3"/>
            </svg>
        </span>

        <h2>3. Consulter les métriques</h2>

        <p>
            Le tableau de bord et la page Monitoring affichent
            les valeurs réelles collectées par Prometheus.
        </p>

        <ul>
            <li>CPU et charge système</li>
            <li>Mémoire vive</li>
            <li>Espace disque</li>
            <li>Réseau et uptime</li>
        </ul>
    </article>

    <article class="v3-guide-card">
        <span class="v3-icon cyan">
            <svg viewBox="0 0 24 24">
                <path d="M12 3 5 6v5c0 4.8 2.8 8.3 7 10 4.2-1.7 7-5.2 7-10V6Z"/>
                <path d="m9 12 2 2 4-4"/>
            </svg>
        </span>

        <h2>4. Vérifier la sécurité</h2>

        <ul>
            <li>Authentification Flask</li>
            <li>Certificat HTTPS</li>
            <li>Cloudflare Zero Trust</li>
            <li>UFW et Fail2ban</li>
            <li>Journal d’audit</li>
        </ul>
    </article>

    <article class="v3-guide-card">
        <span class="v3-icon orange">
            <svg viewBox="0 0 24 24">
                <path d="M6 3h12v18H6Z"/>
                <path d="M9 8h6M9 12h6M9 16h4"/>
            </svg>
        </span>

        <h2>5. Diagnostiquer</h2>

        <p>
            Utilisez les pages Docker, Journaux, Prometheus
            et Audit pour identifier une anomalie.
        </p>

        <ul>
            <li>Vérifier les services DOWN</li>
            <li>Analyser les consommations Docker</li>
            <li>Consulter les logs</li>
            <li>Contrôler les actions administratives</li>
        </ul>
    </article>

    <article class="v3-guide-card">
        <span class="v3-icon purple">
            <svg viewBox="0 0 24 24">
                <rect x="4" y="6" width="16" height="13" rx="3"/>
                <path d="M9 11h.01M15 11h.01M9 15h6M12 3v3"/>
            </svg>
        </span>

        <h2>6. Utiliser Emma_IA</h2>

        <p>
            Posez des questions sur l’état de la plateforme
            ou demandez un diagnostic et des commandes.
        </p>

        <a href="/assistant">
            Ouvrir Emma_IA →
        </a>
    </article>
</section>

<section class="v3-panel" style="margin-top:16px">
    <header class="v3-panel-header">
        <div>
            <h2>Parcours recommandé</h2>
            <p>Ordre conseillé pour découvrir la plateforme.</p>
        </div>
    </header>

    <div class="v3-list">
        <article class="v3-list-item">
            <span class="v3-icon">1</span>
            <div class="v3-list-field mobile-full">
                <span>Étape</span>
                <strong>Consulter le tableau de bord</strong>
            </div>
            <div class="v3-list-field">
                <span>Objectif</span>
                <strong>Voir l’état global</strong>
            </div>
            <div class="v3-list-field optional">
                <span>Page</span>
                <strong>/</strong>
            </div>
        </article>

        <article class="v3-list-item">
            <span class="v3-icon purple">2</span>
            <div class="v3-list-field mobile-full">
                <span>Étape</span>
                <strong>Explorer l’infrastructure</strong>
            </div>
            <div class="v3-list-field">
                <span>Objectif</span>
                <strong>Comprendre les flux</strong>
            </div>
            <div class="v3-list-field optional">
                <span>Page</span>
                <strong>/infrastructure</strong>
            </div>
        </article>

        <article class="v3-list-item">
            <span class="v3-icon green">3</span>
            <div class="v3-list-field mobile-full">
                <span>Étape</span>
                <strong>Analyser le monitoring</strong>
            </div>
            <div class="v3-list-field">
                <span>Objectif</span>
                <strong>Étudier les métriques</strong>
            </div>
            <div class="v3-list-field optional">
                <span>Page</span>
                <strong>/monitoring</strong>
            </div>
        </article>
    </div>
</section>
{% endblock %}
'''

write_template(
    "getting_started.html",
    getting_started,
)


faq = r'''
{% extends "portal_v3_base.html" %}

{% block title %}FAQ — Secure Local Cloud{% endblock %}
{% block breadcrumb %}Aide / FAQ{% endblock %}
{% block page_title %}Questions fréquentes{% endblock %}

{% block page_description %}
Réponses rapides aux questions les plus courantes
sur la plateforme et son infrastructure.
{% endblock %}

{% block page_icon %}
<svg viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="9"/>
    <path d="M9.8 9a2.4 2.4 0 1 1 3.4 2.2c-.8.4-1.2.9-1.2 1.8"/>
    <path d="M12 17h.01"/>
</svg>
{% endblock %}

{% block content %}
<section class="v3-toolbar">
    <label class="v3-search">
        <svg viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="7"/>
            <path d="m20 20-4-4"/>
        </svg>

        <input
            id="faq-search"
            type="search"
            placeholder="Rechercher une question ou un mot-clé…"
        >
    </label>

    <div class="v3-tabs">
        <a class="v3-tab" href="/help">Centre d’aide</a>
        <a class="v3-tab" href="/documentation">Documentation</a>
        <a class="v3-tab active" href="/faq">FAQ</a>
        <a class="v3-tab" href="/assistant">Emma_IA</a>
    </div>
</section>

<section class="v3-stat-grid">
    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Questions disponibles</span>
            <span class="v3-icon">?</span>
        </div>

        <strong>10</strong>
        <small>Réponses techniques rapides</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Thèmes Docker</span>
            <span class="v3-icon purple">D</span>
        </div>

        <strong>3</strong>
        <small>Conteneurs et ressources</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Thèmes Monitoring</span>
            <span class="v3-icon green">M</span>
        </div>

        <strong>4</strong>
        <small>Prometheus, Grafana et métriques</small>
    </article>

    <article class="v3-stat-card">
        <div class="v3-stat-top">
            <span>Thèmes Sécurité</span>
            <span class="v3-icon cyan">S</span>
        </div>

        <strong>3</strong>
        <small>Accès et protections</small>
    </article>
</section>

<section class="v3-panel">
    <header class="v3-panel-header">
        <div>
            <h2>Réponses techniques</h2>
            <p>Cliquez sur une question pour afficher sa réponse.</p>
        </div>
    </header>

    <div class="v3-accordion">
        <article class="v3-accordion-item faq-item open">
            <button class="v3-accordion-button" type="button">
                À quoi sert Secure Local Cloud Infrastructure ?
            </button>

            <div class="v3-accordion-content">
                La plateforme centralise la supervision, la gestion
                Docker, l’état de sécurité, les journaux, l’audit
                et la documentation d’une infrastructure locale.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Quelle est la différence entre Prometheus et Grafana ?
            </button>

            <div class="v3-accordion-content">
                Prometheus collecte et conserve les métriques.
                Grafana interroge Prometheus et transforme les données
                en graphiques et tableaux de bord.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Pourquoi une target Prometheus peut-elle être DOWN ?
            </button>

            <div class="v3-accordion-content">
                Le service cible peut être arrêté, inaccessible,
                mal configuré ou bloqué par le réseau ou le pare-feu.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Comment vérifier les conteneurs Docker actifs ?
            </button>

            <div class="v3-accordion-content">
                Ouvrez la page Conteneurs Docker. Elle affiche
                l’état, le CPU, la mémoire, l’image et l’uptime
                de chaque conteneur détecté.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Pourquoi le conteneur de l’application est-il protégé ?
            </button>

            <div class="v3-accordion-content">
                Arrêter le conteneur Flask depuis l’interface couperait
                immédiatement le portail. Les actions dangereuses sont
                donc désactivées pour ce conteneur.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                À quoi sert Cloudflare Zero Trust ?
            </button>

            <div class="v3-accordion-content">
                Zero Trust protège l’accès externe en imposant
                des contrôles d’identité avant d’autoriser l’accès
                aux services publiés.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Comment les échanges sont-ils sécurisés ?
            </button>

            <div class="v3-accordion-content">
                Les échanges sont chiffrés par HTTPS. Nginx agit
                comme reverse proxy et les accès externes passent
                par Cloudflare.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                À quoi servent UFW et Fail2ban ?
            </button>

            <div class="v3-accordion-content">
                UFW limite les ports et connexions autorisés.
                Fail2ban bloque automatiquement les adresses générant
                trop de tentatives de connexion échouées.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Emma_IA peut-elle modifier l’infrastructure ?
            </button>

            <div class="v3-accordion-content">
                Non. Emma_IA travaille en lecture seule. Elle analyse
                les données et propose des recommandations sans
                exécuter d’action système.
            </div>
        </article>

        <article class="v3-accordion-item faq-item">
            <button class="v3-accordion-button" type="button">
                Où consulter les actions administratives ?
            </button>

            <div class="v3-accordion-content">
                La page Audit enregistre les actions Docker,
                l’utilisateur, la ressource, le résultat et les détails.
            </div>
        </article>
    </div>

    <div
        id="faq-empty"
        class="v3-empty"
        hidden
        style="margin-top:12px"
    >
        <span class="v3-empty-icon">?</span>
        <h3>Aucune question trouvée</h3>
        <p>Essayez un autre mot-clé ou interrogez Emma_IA.</p>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
document.addEventListener("DOMContentLoaded", () => {
    PortalV3.bindSearch({
        input: "#faq-search",
        selector: ".faq-item",
        empty: "#faq-empty",
    });
});
</script>
{% endblock %}
'''

write_template(
    "faq.html",
    faq,
)


print()
print("Installation V3 terminée.")
print(f"Sauvegardes disponibles dans : {BACKUP}")
