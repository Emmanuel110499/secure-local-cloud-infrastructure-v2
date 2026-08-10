(() => {
    "use strict";

    const icons = {
        home: '<path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5"/><path d="M9.5 20v-6h5v6"/>',
        monitoring: '<path d="M4 18V9"/><path d="M10 18V5"/><path d="M16 18v-7"/><path d="M22 18H2"/>',
        containers: '<rect x="3" y="4" width="8" height="7" rx="1"/><rect x="13" y="4" width="8" height="7" rx="1"/><rect x="3" y="13" width="8" height="7" rx="1"/><rect x="13" y="13" width="8" height="7" rx="1"/>',
        infrastructure: '<rect x="4" y="3" width="16" height="6" rx="1"/><rect x="4" y="15" width="16" height="6" rx="1"/><path d="M8 6h.01M8 18h.01M12 9v6"/>',
        grafana: '<path d="M5 19V9h3v10M11 19V4h3v15M17 19v-7h3v7"/>',
        prometheus: '<path d="M12 3c1 4-2 5-2 8 0 1.7 1 3 2 3s2-1.3 2-3c0-1-.3-2-.8-3 2.5 2 4.3 4.6 4.3 7.2A5.5 5.5 0 0 1 12 21a5.5 5.5 0 0 1-5.5-5.8C6.5 11 9.6 8.5 12 3Z"/>',
        security: '<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3M12 14v3"/>',
        audit: '<path d="M6 3h9l3 3v15H6z"/><path d="M14 3v4h4M9 11h6M9 15h6"/>',
        documentation: '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H11v17H6.5A2.5 2.5 0 0 0 4 22Z"/><path d="M20 5.5A2.5 2.5 0 0 0 17.5 3H13v17h4.5A2.5 2.5 0 0 1 20 22Z"/>',
        brand: '<rect x="9" y="9" width="6" height="6" rx="1.5"/><rect x="3" y="3" width="4" height="4" rx="1"/><rect x="17" y="3" width="4" height="4" rx="1"/><rect x="3" y="17" width="4" height="4" rx="1"/><rect x="17" y="17" width="4" height="4" rx="1"/><path d="m7 7 2.5 2.5M17 7l-2.5 2.5M7 17l2.5-2.5M17 17l-2.5-2.5"/>',
    };

    function svg(name) {
        return `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name]}</svg>`;
    }

    const brand = document.querySelector(".sidebar .brand-icon");
    if (brand) {
        brand.innerHTML = svg("brand");
    }

    document.querySelectorAll(".sidebar .nav-item").forEach(link => {
        const href = String(link.getAttribute("href") || "");
        let name = "home";

        if (href.includes("monitoring")) name = "monitoring";
        else if (href.includes("containers")) name = "containers";
        else if (href.includes("infrastructure")) name = "infrastructure";
        else if (href.includes("grafana")) name = "grafana";
        else if (href.includes("prometheus")) name = "prometheus";
        else if (href.includes("security")) name = "security";
        else if (href.includes("audit")) name = "audit";
        else if (href.includes("documentation")) name = "documentation";

        const icon = link.querySelector(".sidebar-colored-icon");
        if (icon) {
            icon.innerHTML = svg(name);
        }
    });
})();
