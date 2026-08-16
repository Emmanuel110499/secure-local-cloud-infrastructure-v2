(() => {
    "use strict";

    const state = { equipment: "global", hours: 24, inventory: [], charts: {} };
    const colors = { cpu: "#1769e8", memory: "#0aad78", disk: "#ec8700" };
    const $ = id => document.getElementById(id);
    const value = number => Number.isFinite(Number(number)) ? `${Number(number).toFixed(1)} %` : "—";
    const number = item => Number(item?.value);

    function configureMobileMenu() {
        const toggle = $("mobile-menu-toggle");
        const sidebar = $("monitoring-sidebar");
        const overlay = $("mobile-sidebar-overlay");
        if (!toggle || !sidebar || !overlay) return;

        const close = () => {
            sidebar.classList.remove("is-open");
            overlay.hidden = true;
            toggle.setAttribute("aria-expanded", "false");
            toggle.setAttribute("aria-label", "Ouvrir le menu");
            document.body.classList.remove("mobile-menu-open");
        };
        const open = () => {
            sidebar.classList.add("is-open");
            overlay.hidden = false;
            toggle.setAttribute("aria-expanded", "true");
            toggle.setAttribute("aria-label", "Fermer le menu");
            document.body.classList.add("mobile-menu-open");
        };

        toggle.addEventListener("click", () => {
            sidebar.classList.contains("is-open") ? close() : open();
        });
        overlay.addEventListener("click", close);
        sidebar.querySelectorAll("a").forEach(link => link.addEventListener("click", close));
        window.addEventListener("resize", () => {
            if (window.innerWidth > 720) close();
        });
    }

    async function json(url) {
        const response = await fetch(`${url}${url.includes("?") ? "&" : "?"}t=${Date.now()}`, {
            headers: { Accept: "application/json" }, credentials: "same-origin"
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }

    function setText(id, text) { const node = $(id); if (node) node.textContent = text; }
    function average(values) { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null; }

    function renderConnectionState(item) {
        const disconnected = item.state === "disconnected";
        const disconnectedPanel = $("disconnected-state");
        const sections = [
            $("kpi-grid"),
            document.querySelector(".content-grid"),
            document.querySelector(".bottom-grid"),
            document.querySelector(".scrape-footer"),
        ];

        if (disconnectedPanel) disconnectedPanel.hidden = !disconnected;
        sections.forEach(section => {
            if (section) section.hidden = disconnected;
        });
        document.body.classList.toggle("equipment-disconnected", disconnected);
        if (!disconnected) return;

        const isPc = item.equipment.id === "pc-emmanuel";
        setText("disconnected-title", isPc
            ? "PC Emmanuel est actuellement hors ligne"
            : "Laboratoire VMware en attente d’activation");
        setText("disconnected-description", isPc
            ? "Le poste d’administration n’envoie momentanément plus ses métriques. Le VPS et le portail public continuent de fonctionner normalement."
            : "Ce laboratoire est une extension facultative. Les anciennes VM ne sont pas nécessaires au fonctionnement de la plateforme hébergée sur le VPS.");
        setText("disconnected-action-title", isPc
            ? "Pour reprendre la supervision"
            : "Activation ultérieure");
        setText("disconnected-action-text", isPc
            ? "Démarrer le PC, Windows Exporter et la future liaison sécurisée vers le VPS."
            : "Démarrer les VM uniquement pour les exercices de laboratoire, puis établir leur liaison sécurisée avec Prometheus.");
    }

    function metricSummary(series) {
        const values = series.map(number).filter(Number.isFinite);
        return values.length ? { min: Math.min(...values), avg: average(values), max: Math.max(...values) } : null;
    }

    function updateChart(name, series) {
        const canvas = $(`chart-${name}`);
        const labels = series.map(point => new Date(point.timestamp * 1000).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }));
        const values = series.map(number);
        if (state.charts[name]) state.charts[name].destroy();
        state.charts[name] = new Chart(canvas, {
            type: "line",
            data: { labels, datasets: [{ data: values, borderColor: colors[name], backgroundColor: `${colors[name]}16`, fill: true, borderWidth: 2, pointRadius: 0, tension: .25 }] },
            options: { responsive: true, maintainAspectRatio: false, animation: false, plugins: { legend: { display: false } }, scales: { y: { min: 0, max: 100, ticks: { callback: v => `${v}%`, color: "#8090a8" }, grid: { color: "#e9eef5" } }, x: { ticks: { maxTicksLimit: 6, color: "#8090a8" }, grid: { display: false } } } }
        });
        const summary = metricSummary(series);
        setText(`stats-${name}`, summary ? `Min ${summary.min.toFixed(1)} % · Moy ${summary.avg.toFixed(1)} % · Max ${summary.max.toFixed(1)} %` : "Aucune donnée disponible");
    }

    function updateDetails(item, updatedAt) {
        const equipment = item.equipment;
        const metrics = item.metrics || {};
        renderConnectionState(item);
        setText("equipment-title", equipment.name);
        setText("breadcrumb-equipment", equipment.name);
        setText("equipment-role", equipment.role);
        setText("kpi-cpu", value(metrics.cpu));
        setText("kpi-memory", value(metrics.memory));
        setText("kpi-disk", value(metrics.disk));
        setText("kpi-network", metrics.network_receive_kbps == null ? "—" : `${metrics.network_receive_kbps.toFixed(1)} Ko/s`);
        setText("kpi-load", metrics.load_1m == null ? "—" : Number(metrics.load_1m).toFixed(2));
        setText("kpi-uptime", metrics.uptime || "—");
        setText("chart-cpu-current", value(metrics.cpu));
        setText("chart-memory-current", value(metrics.memory));
        setText("chart-disk-current", value(metrics.disk));
        setText("detail-title", equipment.name);
        setText("detail-subtitle", equipment.role);
        setText("detail-os", equipment.os === "windows" ? "Windows" : equipment.os === "multi" ? "Linux + Windows" : "Linux");
        const stateLabel = item.state === "up" ? "Opérationnel"
            : item.state === "down" ? "Indisponible"
                : item.state === "disconnected" ? "Non connecté" : "Inconnu";
        setText("detail-state", stateLabel);
        setText(
            "detail-source",
            equipment.id === "global"
                ? "Prometheus — vue consolidée"
                : equipment.id === "pc-emmanuel"
                    ? "Windows Exporter → Prometheus"
                    : equipment.id === "lab-vmware"
                        ? "Connexion à configurer"
                        : "Node Exporter → Prometheus"
        );
        const normalizedUpdatedAt = /(?:Z|[+-]\d{2}:?\d{2})$/.test(updatedAt)
            ? updatedAt
            : `${updatedAt}Z`;
        setText("detail-updated", new Date(normalizedUpdatedAt).toLocaleTimeString("fr-FR"));
        setText("os-badge", equipment.os === "windows" ? "Windows" : equipment.os === "multi" ? "Multi-équipement" : "Linux");
        setText("online-badge", item.state === "up" ? "● En ligne" : item.state === "disconnected" ? "○ Non connecté" : "● État partiel");
        $("online-badge")?.classList.toggle("is-disconnected", item.state === "disconnected");
        setText("system-name", equipment.name);
        setText("system-role", equipment.role);
        setText("system-os", equipment.os === "windows" ? "Windows" : equipment.os === "multi" ? "Linux + Windows" : "Linux");
        setText("system-exporter", equipment.id === "pc-emmanuel" ? "Windows Exporter" : equipment.os === "multi" ? "Prometheus" : "Node Exporter");
        renderStorage(equipment, metrics, item.state);
        const battery = metrics.battery;
        $("battery-kpi").hidden = !battery;
        if (battery) {
            setText("kpi-battery", value(battery.charge_percent));
            setText("battery-state", battery.on_ac_power ? "Branché au secteur" : "Sur batterie");
        }
    }

    function renderStorage(equipment, metrics, equipmentState) {
        const bytes = amount => Number.isFinite(Number(amount))
            ? `${(Number(amount) / 1073741824).toFixed(2)} Gio` : "—";
        const total = Number(metrics.disk_total_bytes);
        const available = Number(metrics.disk_available_bytes);
        const used = Number.isFinite(total) && Number.isFinite(available)
            ? total - available : null;
        if (equipmentState === "disconnected") {
            $("storage-rows").innerHTML = '<div class="storage-row"><b>Équipement non connecté</b><code>—</code><span>—</span><span>—</span><span>Connexion future</span></div>';
            return;
        }
        const rows = [{
            name: equipment.os === "windows" ? "Disque système" : equipment.os === "multi" ? "Stockage consolidé" : "Système racine",
            mountpoint: equipment.os === "windows" ? "C:" : equipment.os === "multi" ? "3 équipements" : "/",
            used_bytes: used,
            total_bytes: total,
            percent: metrics.disk,
        }];
        (metrics.volumes || []).forEach(volume => rows.push({
            name: volume.name,
            mountpoint: volume.mountpoint,
            used_bytes: volume.used_bytes,
            total_bytes: total,
            percent: Number.isFinite(total) && total > 0
                ? volume.used_bytes / total * 100 : null,
        }));
        $("storage-rows").innerHTML = rows.map(row => {
            const percent = Number(row.percent);
            const width = Number.isFinite(percent) ? Math.min(100, percent) : 0;
            return `<div class="storage-row">
                <b>${row.name || "Volume"}</b><code title="${row.mountpoint || ""}">${row.mountpoint || "—"}</code>
                <span>${bytes(row.used_bytes)}</span><span>${bytes(row.total_bytes)}</span>
                <span><i><em style="width:${width}%"></em></i><b>${Number.isFinite(percent) ? `${percent.toFixed(1)} %` : "—"}</b></span>
            </div>`;
        }).join("");
    }

    function renderInventory(items) {
        $("service-list").innerHTML = items.map(item => `
            <div class="equipment-row ${item.state}">
                <i></i><div><b>${item.equipment.name}</b><small>${item.equipment.role}</small></div>
                <span>${item.state === "up" ? "OPÉRATIONNEL" : item.state === "disconnected" ? "NON CONNECTÉ" : item.state.toUpperCase()}</span>
            </div>`).join("");
    }

    function renderServices(services) {
        const labels = {
            flask: "Application Flask", node_exporter: "Node Exporter",
            cadvisor: "cAdvisor", prometheus: "Prometheus", grafana: "Grafana",
            alertmanager: "Alertmanager", windows_exporter: "Windows Exporter",
            battery_collector: "Collecteur batterie"
        };
        $("service-list").innerHTML = Object.entries(services || {}).map(([name, status]) => `
            <div class="equipment-row ${status === false ? "down" : "up"}">
                <i></i><div><b>${labels[name] || name}</b><small>Service supervisé</small></div>
                <span>${status === true ? "OPÉRATIONNEL" : status === false ? "INDISPONIBLE" : "INCONNU"}</span>
            </div>`).join("");
    }

    async function loadGlobal() {
        const payload = await json("/api/equipment");
        state.inventory = payload.equipment || [];
        renderInventory(state.inventory);
        const monitored = state.inventory.filter(item => item.equipment?.monitored !== false);
        const optional = state.inventory.length - monitored.length;
        const up = monitored.filter(item => item.state === "up").length;
        const metrics = key => average(monitored.map(item => Number(item.metrics?.[key])).filter(Number.isFinite));
        const totalDisk = monitored.reduce((sum, item) => sum + (Number(item.metrics?.disk_total_bytes) || 0), 0);
        const availableDisk = monitored.reduce((sum, item) => sum + (Number(item.metrics?.disk_available_bytes) || 0), 0);
        const role = `${up}/${monitored.length} actif${monitored.length > 1 ? "s" : ""} · ${optional} extension${optional > 1 ? "s" : ""} en attente`;
        const representative = { equipment: { id: "global", name: "Vue globale", role, os: "multi" }, state: monitored.length > 0 && up === monitored.length ? "up" : "unknown", metrics: { cpu: metrics("cpu"), memory: metrics("memory"), disk: totalDisk > 0 ? (1 - availableDisk / totalDisk) * 100 : metrics("disk"), disk_total_bytes: totalDisk || null, disk_available_bytes: totalDisk ? availableDisk : null, network_receive_kbps: monitored.reduce((sum, item) => sum + (Number(item.metrics?.network_receive_kbps) || 0), 0), uptime: "VPS actif", load_1m: metrics("load_1m") } };
        updateDetails(representative, payload.updated_at);
        setText("detail-title", "Équipements supervisés");
        setText("detail-subtitle", role);
        $("battery-kpi").hidden = true;
        const history = await json(`/api/equipment/global/history?hours=${state.hours}`);
        ["cpu", "memory", "disk"].forEach(name => updateChart(name, history.series?.[name] || []));
        const count = Math.max(...["cpu", "memory", "disk"].map(name => history.series?.[name]?.length || 0));
        setText("sample-count", `${count} points consolidés`);
    }

    async function loadEquipment(id) {
        const [current, history] = await Promise.all([
            json(`/api/equipment/${id}/metrics`),
            json(`/api/equipment/${id}/history?hours=${state.hours}`)
        ]);
        updateDetails(current, current.updated_at);
        if (current.state === "disconnected") return;
        renderServices(current.services);
        ["cpu", "memory", "disk"].forEach(name => updateChart(name, history.series?.[name] || []));
        const count = Math.max(...["cpu", "memory", "disk"].map(name => history.series?.[name]?.length || 0));
        setText("sample-count", `${count} points sur ${state.hours === 168 ? "7 jours" : `${state.hours} h`}`);
    }

    async function refresh() {
        setText("refresh-state", "Actualisation…");
        try {
            if (state.equipment === "global") await loadGlobal(); else await loadEquipment(state.equipment);
            setText("refresh-state", `À jour à ${new Date().toLocaleTimeString("fr-FR")}`);
        } catch (error) {
            setText("refresh-state", `Données indisponibles (${error.message})`);
            $("refresh-state").classList.add("error");
        }
    }

    $("equipment-tabs").addEventListener("click", event => {
        const button = event.target.closest("button[data-equipment]");
        if (!button) return;
        document.querySelectorAll("[data-equipment]").forEach(item => item.classList.toggle("active", item === button));
        state.equipment = button.dataset.equipment;
        refresh();
    });
    document.querySelector(".period-tabs").addEventListener("click", event => {
        const button = event.target.closest("button[data-hours]");
        if (!button) return;
        document.querySelectorAll("[data-hours]").forEach(item => item.classList.toggle("active", item === button));
        state.hours = Number(button.dataset.hours);
        if (state.equipment !== "global") refresh();
    });

    configureMobileMenu();
    refresh();
    setInterval(refresh, 60000);
})();
