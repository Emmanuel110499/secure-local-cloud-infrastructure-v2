(() => {
    "use strict";

    const state = { equipment: "global", hours: 24, inventory: [], charts: {} };
    const colors = { cpu: "#1769e8", memory: "#0aad78", disk: "#ec8700" };
    const $ = id => document.getElementById(id);
    const value = number => Number.isFinite(Number(number)) ? `${Number(number).toFixed(1)} %` : "—";
    const number = item => Number(item?.value);

    async function json(url) {
        const response = await fetch(`${url}${url.includes("?") ? "&" : "?"}t=${Date.now()}`, {
            headers: { Accept: "application/json" }, credentials: "same-origin"
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return response.json();
    }

    function setText(id, text) { const node = $(id); if (node) node.textContent = text; }
    function average(values) { return values.length ? values.reduce((a, b) => a + b, 0) / values.length : null; }

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
        setText("equipment-title", equipment.name);
        setText("breadcrumb-equipment", equipment.name);
        setText("equipment-role", equipment.role);
        setText("kpi-cpu", value(metrics.cpu));
        setText("kpi-memory", value(metrics.memory));
        setText("kpi-disk", value(metrics.disk));
        setText("kpi-network", metrics.network_receive_kbps == null ? "—" : `${metrics.network_receive_kbps.toFixed(1)} Ko/s`);
        setText("kpi-uptime", metrics.uptime || "—");
        setText("chart-cpu-current", value(metrics.cpu));
        setText("chart-memory-current", value(metrics.memory));
        setText("chart-disk-current", value(metrics.disk));
        setText("detail-title", equipment.name);
        setText("detail-subtitle", equipment.role);
        setText("detail-os", equipment.os === "windows" ? "Windows" : "Linux");
        setText("detail-state", item.state === "up" ? "Opérationnel" : item.state === "down" ? "Indisponible" : "Inconnu");
        setText("detail-source", equipment.id === "pc-emmanuel" ? "Windows Exporter → Prometheus" : "Node Exporter → Prometheus");
        setText("detail-updated", new Date(updatedAt).toLocaleTimeString("fr-FR"));
        const battery = metrics.battery;
        $("battery-kpi").hidden = !battery;
        if (battery) {
            setText("kpi-battery", value(battery.charge_percent));
            setText("battery-state", battery.on_ac_power ? "Branché au secteur" : "Sur batterie");
        }
    }

    function renderInventory(items) {
        $("equipment-list").innerHTML = items.map(item => `
            <div class="equipment-row ${item.state}">
                <i></i><div><b>${item.equipment.name}</b><small>${item.equipment.role}</small></div>
                <span>${item.state === "up" ? "OPÉRATIONNEL" : item.state.toUpperCase()}</span>
            </div>`).join("");
    }

    async function loadGlobal() {
        const payload = await json("/api/equipment");
        state.inventory = payload.equipment || [];
        renderInventory(state.inventory);
        const up = state.inventory.filter(item => item.state === "up").length;
        const metrics = key => average(state.inventory.map(item => Number(item.metrics?.[key])).filter(Number.isFinite));
        const representative = { equipment: { name: "Vue globale", role: `${up}/${state.inventory.length} équipements opérationnels`, os: "multi" }, state: up === state.inventory.length ? "up" : "unknown", metrics: { cpu: metrics("cpu"), memory: metrics("memory"), disk: metrics("disk"), network_receive_kbps: state.inventory.reduce((sum, item) => sum + (Number(item.metrics?.network_receive_kbps) || 0), 0), uptime: "Vue consolidée" } };
        updateDetails(representative, payload.updated_at);
        setText("detail-title", "Équipements supervisés");
        setText("detail-subtitle", `${up}/${state.inventory.length} disponibles`);
        $("battery-kpi").hidden = true;
        ["cpu", "memory", "disk"].forEach(name => updateChart(name, []));
        setText("sample-count", "Sélectionnez un équipement pour afficher son historique");
    }

    async function loadEquipment(id) {
        const [current, history] = await Promise.all([
            json(`/api/equipment/${id}/metrics`),
            json(`/api/equipment/${id}/history?hours=${state.hours}`)
        ]);
        updateDetails(current, current.updated_at);
        renderInventory(state.inventory.length ? state.inventory : [current]);
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

    refresh();
    setInterval(refresh, 60000);
})();
