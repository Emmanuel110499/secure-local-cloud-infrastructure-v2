from pathlib import Path


ROOT = Path.cwd()
TEMPLATES = ROOT / "templates"

infra_path = TEMPLATES / "infrastructure.html"
assistant_path = TEMPLATES / "assistant.html"

infra_backup = (
    TEMPLATES
    / "backups"
    / "infrastructure-before-realism.html"
)

assistant_backup = (
    TEMPLATES
    / "backups"
    / "assistant-before-realism.html"
)

infra_backup.parent.mkdir(
    parents=True,
    exist_ok=True,
)

if infra_path.exists() and not infra_backup.exists():
    infra_backup.write_text(
        infra_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

if assistant_path.exists() and not assistant_backup.exists():
    assistant_backup.write_text(
        assistant_path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


css_link = """
<link
    rel="stylesheet"
    href="{{ url_for('static', filename='css/portal-realism.css', v='realism-8') }}"
>
""".strip()

js_link = """
<script
    src="{{ url_for('static', filename='js/portal-realism.js', v='realism-8') }}"
></script>
""".strip()


infra_block = r'''
<section
    id="real-infrastructure-map"
    class="real-infra-section"
>
    <header class="real-section-head">
        <div>
            <h2>Architecture opérationnelle en temps réel</h2>

            <p>
                Représentation des accès externes, du serveur applicatif,
                de Docker et de la chaîne de supervision.
            </p>
        </div>

        <span class="live-pill">
            Infrastructure connectée
        </span>
    </header>

    <div class="real-architecture">
        <article class="real-node">
            <div class="real-node-head">
                <span class="brand-logo large cloudflare">
                    <img
                        src="{{ url_for('static', filename='brand/cloudflare.svg') }}"
                        alt="Cloudflare"
                    >
                </span>

                <div>
                    <h3>Accès administrateur</h3>

                    <span class="real-node-subtitle">
                        Cloudflare Zero Trust
                    </span>
                </div>
            </div>

            <div class="real-node-details">
                <div class="real-node-detail">
                    <span>Entrée</span>
                    <strong>HTTPS public</strong>
                </div>

                <div class="real-node-detail">
                    <span>Protection</span>
                    <strong>Identité + tunnel</strong>
                </div>
            </div>

            <div class="real-services">
                <span class="real-service-chip">
                    TLS actif
                </span>

                <span class="real-service-chip">
                    Zero Trust
                </span>
            </div>
        </article>

        <div class="real-connector">
            <div class="real-connector-line">
                <span class="real-data-particle"></span>
                <span class="real-data-particle delay"></span>
            </div>

            <span class="real-connector-label">
                Requêtes HTTPS
            </span>
        </div>

        <article class="real-node">
            <div class="real-node-head">
                <span class="brand-logo large ubuntu">
                    <img
                        src="{{ url_for('static', filename='brand/ubuntu.svg') }}"
                        alt="Ubuntu"
                    >
                </span>

                <div>
                    <h3>srv-web</h3>

                    <span class="real-node-subtitle">
                        192.168.50.10
                    </span>
                </div>
            </div>

            <div class="real-monitoring-stack">
                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/nginx.svg') }}"
                        alt="Nginx"
                    >
                    <span>Nginx</span>
                </div>

                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/flask.svg') }}"
                        alt="Flask"
                    >
                    <span>Flask</span>
                </div>

                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/docker.svg') }}"
                        alt="Docker"
                    >
                    <span>Docker</span>
                </div>

                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/linux.svg') }}"
                        alt="Linux"
                    >
                    <span>Node Exporter</span>
                </div>
            </div>

            <div class="real-services">
                <span
                    class="real-service-chip"
                    data-real-service="flask"
                >
                    Flask
                </span>

                <span
                    class="real-service-chip"
                    data-real-service="node_exporter"
                >
                    Node Exporter
                </span>

                <span
                    class="real-service-chip"
                    data-real-service="cadvisor"
                >
                    cAdvisor
                </span>
            </div>
        </article>

        <div class="real-connector">
            <div class="real-connector-line">
                <span class="real-data-particle"></span>
                <span class="real-data-particle delay"></span>
            </div>

            <span class="real-connector-label">
                Scrape Prometheus
            </span>
        </div>

        <article class="real-node">
            <div class="real-node-head">
                <span class="brand-logo large prometheus">
                    <img
                        src="{{ url_for('static', filename='brand/prometheus.svg') }}"
                        alt="Prometheus"
                    >
                </span>

                <div>
                    <h3>srv-monitoring</h3>

                    <span class="real-node-subtitle">
                        192.168.50.20
                    </span>
                </div>
            </div>

            <div class="real-monitoring-stack">
                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/prometheus.svg') }}"
                        alt="Prometheus"
                    >
                    <span>Prometheus</span>
                </div>

                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/grafana.svg') }}"
                        alt="Grafana"
                    >
                    <span>Grafana</span>
                </div>

                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/alertmanager.svg') }}"
                        alt="Alertmanager"
                        onerror="this.style.display='none'"
                    >
                    <span>Alertmanager</span>
                </div>

                <div class="real-stack-item">
                    <img
                        src="{{ url_for('static', filename='brand/docker.svg') }}"
                        alt="Docker"
                    >
                    <span>Docker</span>
                </div>
            </div>

            <div class="real-services">
                <span
                    class="real-service-chip"
                    data-real-service="prometheus"
                >
                    Prometheus
                </span>

                <span
                    class="real-service-chip"
                    data-real-service="grafana"
                >
                    Grafana
                </span>
            </div>
        </article>
    </div>

    <div class="real-infra-bottom">
        <article class="real-flow-card">
            <h3>Flux technique</h3>

            <div class="real-flow-steps">
                <div class="real-flow-step">
                    <strong>1. Accès</strong>
                    L’administrateur passe par Cloudflare.
                </div>

                <div class="real-flow-step">
                    <strong>2. Application</strong>
                    Nginx transmet les requêtes à Flask.
                </div>

                <div class="real-flow-step">
                    <strong>3. Collecte</strong>
                    Prometheus interroge les exporters.
                </div>

                <div class="real-flow-step">
                    <strong>4. Visualisation</strong>
                    Grafana affiche les séries temporelles.
                </div>
            </div>
        </article>

        <article class="real-metrics-card">
            <h3>Métriques actuelles</h3>

            <div class="real-live-metrics">
                <div class="real-live-metric">
                    <span>CPU</span>
                    <strong id="real-infra-cpu">-- %</strong>
                </div>

                <div class="real-live-metric">
                    <span>Mémoire</span>
                    <strong id="real-infra-memory">-- %</strong>
                </div>

                <div class="real-live-metric">
                    <span>Disque</span>
                    <strong id="real-infra-disk">-- %</strong>
                </div>
            </div>
        </article>
    </div>
</section>
'''


emma_block = r'''
<section
    id="emma-command-center"
    class="emma-command-center"
>
    <header class="real-section-head">
        <div>
            <h2>Centre d’analyse Emma_IA</h2>

            <p>
                Emma_IA croise les métriques, l’état des services,
                Docker et la documentation du projet.
            </p>
        </div>

        <span class="live-pill">
            Lecture seule
        </span>
    </header>

    <div class="emma-command-grid">
        <article class="emma-brain-card">
            <div class="emma-brain-head">
                <span class="emma-core">
                    <svg viewBox="0 0 24 24">
                        <rect
                            x="4"
                            y="6"
                            width="16"
                            height="13"
                            rx="3"
                        />
                        <path d="M9 11h.01M15 11h.01M9 15h6"/>
                        <path d="M12 3v3"/>
                    </svg>
                </span>

                <div>
                    <h3>Moteur d’analyse local</h3>

                    <p>
                        Routage des intentions et données en temps réel.
                    </p>

                    <span class="emma-health-line">
                        Emma_IA opérationnelle
                    </span>
                </div>
            </div>

            <div class="emma-domain-grid">
                <div class="emma-domain">
                    <img
                        src="{{ url_for('static', filename='brand/docker.svg') }}"
                        alt="Docker"
                    >

                    <div>
                        <strong>Docker</strong>
                        <span>Conteneurs et ressources</span>
                    </div>
                </div>

                <div class="emma-domain">
                    <img
                        src="{{ url_for('static', filename='brand/prometheus.svg') }}"
                        alt="Prometheus"
                    >

                    <div>
                        <strong>Prometheus</strong>
                        <span>Métriques système</span>
                    </div>
                </div>

                <div class="emma-domain">
                    <img
                        src="{{ url_for('static', filename='brand/grafana.svg') }}"
                        alt="Grafana"
                    >

                    <div>
                        <strong>Grafana</strong>
                        <span>Visualisation</span>
                    </div>
                </div>

                <div class="emma-domain">
                    <img
                        src="{{ url_for('static', filename='brand/cloudflare.svg') }}"
                        alt="Cloudflare"
                    >

                    <div>
                        <strong>Sécurité</strong>
                        <span>Zero Trust et TLS</span>
                    </div>
                </div>
            </div>
        </article>

        <article class="emma-live-card">
            <h3>Observations actuelles</h3>

            <div class="emma-observation-list">
                <div class="emma-observation">
                    <span class="emma-observation-icon">
                        <svg viewBox="0 0 24 24">
                            <path d="M4 19V9M10 19V5M16 19v-7M22 19V3"/>
                        </svg>
                    </span>

                    <div>
                        <strong>CPU du serveur</strong>
                        <span>Mesure Prometheus actuelle</span>
                    </div>

                    <span
                        id="emma-live-cpu"
                        class="emma-observation-value"
                    >
                        -- %
                    </span>
                </div>

                <div class="emma-observation">
                    <span class="emma-observation-icon">
                        <svg viewBox="0 0 24 24">
                            <rect x="5" y="4" width="14" height="16" rx="2"/>
                            <path d="M9 8h6M9 12h6M9 16h3"/>
                        </svg>
                    </span>

                    <div>
                        <strong>Mémoire utilisée</strong>
                        <span>Occupation de la RAM</span>
                    </div>

                    <span
                        id="emma-live-memory"
                        class="emma-observation-value"
                    >
                        -- %
                    </span>
                </div>

                <div class="emma-observation">
                    <span class="emma-observation-icon">
                        <svg viewBox="0 0 24 24">
                            <ellipse cx="12" cy="6" rx="8" ry="3"/>
                            <path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>
                        </svg>
                    </span>

                    <div>
                        <strong>Stockage utilisé</strong>
                        <span>Espace disque consommé</span>
                    </div>

                    <span
                        id="emma-live-disk"
                        class="emma-observation-value"
                    >
                        -- %
                    </span>
                </div>

                <div class="emma-observation">
                    <span class="emma-observation-icon">
                        <svg viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="9"/>
                            <path d="m8 12 2.5 2.5L16 9"/>
                        </svg>
                    </span>

                    <div>
                        <strong>Services opérationnels</strong>
                        <span>État global supervisé</span>
                    </div>

                    <span
                        id="emma-live-services"
                        class="emma-observation-value"
                    >
                        --/--
                    </span>
                </div>
            </div>
        </article>
    </div>

    <div class="emma-command-suggestions">
        <button
            class="emma-command-chip"
            type="button"
            data-question="Analyse mon infrastructure et indique les risques actuels."
        >
            <code>SRE</code>
            Analyser les risques actuels
        </button>

        <button
            class="emma-command-chip"
            type="button"
            data-question="Quels conteneurs consomment le plus de ressources ?"
        >
            <code>Docker</code>
            Trouver les plus gros consommateurs
        </button>

        <button
            class="emma-command-chip"
            type="button"
            data-question="Vérifie l’état des services et explique les anomalies."
        >
            <code>Health</code>
            Diagnostiquer les services
        </button>
    </div>
</section>
'''


def inject_assets(text: str) -> str:
    if "portal-realism.css" not in text:
        text = text.replace(
            "</head>",
            css_link + "\n</head>",
            1,
        )

    if "portal-realism.js" not in text:
        text = text.replace(
            "</body>",
            js_link + "\n</body>",
            1,
        )

    return text


def inject_block(
    path: Path,
    block: str,
    marker: str,
) -> None:
    text = path.read_text(encoding="utf-8")
    text = inject_assets(text)

    if marker not in text:
        if "</main>" in text:
            text = text.replace(
                "</main>",
                block + "\n</main>",
                1,
            )
        elif "</body>" in text:
            text = text.replace(
                "</body>",
                block + "\n</body>",
                1,
            )
        elif "{% endblock %}" in text:
            index = text.rfind("{% endblock %}")

            text = (
                text[:index]
                + block
                + "\n"
                + text[index:]
            )
        else:
            raise RuntimeError(
                f"Point d’insertion introuvable : {path}"
            )

    path.write_text(text, encoding="utf-8")


inject_block(
    infra_path,
    infra_block,
    'id="real-infrastructure-map"',
)

inject_block(
    assistant_path,
    emma_block,
    'id="emma-command-center"',
)

print("Infrastructure améliorée.")
print("Emma_IA enrichie.")
