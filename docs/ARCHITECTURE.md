# Architecture technique réelle

Ce document décrit l’installation multi-équipement actuellement exploitée. Les adresses sont celles du laboratoire ; elles doivent être adaptées lors d’une migration.

## État validé au 10 août 2026

| Équipement | Fonction | Composants réellement présents |
|---|---|---|
| PC Emmanuel | Administration, hébergement VMware et supervision Windows | Windows 11, VMware Workstation, Windows Exporter, collecteur batterie, SSH et réplication des sauvegardes |
| `srv-web` | Serveur applicatif et collecte locale | Cloudflare Tunnel, Nginx, Flask/Gunicorn, Docker Engine, Node Exporter et cAdvisor |
| `srv-monitoring` | Collecte, stockage, visualisation et alertes | Prometheus, Grafana, Alertmanager, Node Exporter, Docker Engine et volumes persistants |

Les vues publiques `/monitoring` et `/infrastructure` utilisent cette topologie. Les mesures affichées proviennent de Prometheus et les états absents ne sont pas remplacés artificiellement par zéro.

## Vue physique et réseau

```mermaid
flowchart TB
    Internet((Internet))
    CF["Cloudflare Edge<br/>DNS, HTTPS public, Zero Trust"]
    PC["PC Emmanuel — Windows<br/>192.168.154.1<br/>Navigateur, SSH, Windows Exporter :9182<br/>collecteur batterie et réplication"]

    subgraph WEB["srv-web — Ubuntu — 192.168.50.10 / 192.168.154.10"]
        Tunnel["cloudflared<br/>tunnel sortant"]
        Nginx["Nginx<br/>HTTPS local et reverse proxy"]
        Flask["Flask + Gunicorn<br/>port conteneur 5000<br/>port hôte 127.0.0.1:5001"]
        Docker["Docker Engine"]
        NEWeb["Node Exporter :9100"]
        CAdvisor["cAdvisor :8080"]
        AppData["Données applicatives<br/>authentification, historique, audit"]
    end

    subgraph MON["srv-monitoring — Ubuntu — 192.168.50.20 / 192.168.154.20"]
        Prom["Prometheus :9090<br/>collecte et historique"]
        Graf["Grafana :3000<br/>visualisation"]
        AM["Alertmanager :9093<br/>routage des alertes"]
        NEMon["Node Exporter :9100<br/>métriques hôte et volumes"]
        Volumes["Volumes Docker persistants<br/>prometheus-data<br/>grafana-data<br/>alertmanager-data"]
    end

    TG["Telegram<br/>notifications firing et resolved"]
    Backup["PC Windows<br/>SecureLocalCloud-Backups<br/>archives vérifiées SHA-256"]

    Internet -->|HTTPS 443| CF
    CF -->|Tunnel chiffré sortant| Tunnel
    Tunnel --> Nginx
    PC -->|HTTPS / interface| Nginx
    Nginx -->|HTTP local| Flask
    Flask -->|API Prometheus| Prom
    Flask --> Docker
    Flask --> AppData
    Prom -->|scrape 15 s| NEWeb
    Prom -->|scrape 15 s| CAdvisor
    Prom -->|scrape 15 s| NEMon
    Prom -->|scrape 15 s| PC
    Prom -->|alertes| AM
    AM -->|API Telegram| TG
    Prom --> Volumes
    Graf --> Prom
    WEB -. archives .-> Backup
    MON -. archives .-> Backup
```

## Rôle de chaque zone

| Zone | Rôle | Éléments importants |
|---|---|---|
| Accès public | Publier sans port entrant sur la box | Cloudflare DNS, HTTPS et Tunnel |
| `srv-web` | Servir la plateforme | Nginx, Flask, Gunicorn, Docker, cAdvisor, Node Exporter |
| `srv-monitoring` | Observer et alerter | Prometheus, Grafana, Alertmanager, Node Exporter |
| PC Emmanuel | Administrer et être supervisé | navigateur, SSH, Windows Exporter, batterie, réplication |
| Telegram | Prévenir l’administrateur | alertes critiques, avertissements et résolutions |

## Chemin d’une requête utilisateur

```mermaid
sequenceDiagram
    actor U as Utilisateur
    participant C as Cloudflare
    participant T as cloudflared
    participant N as Nginx
    participant F as Flask/Gunicorn
    participant P as Prometheus

    U->>C: HTTPS app.emmanuelinfra.fr
    C->>T: tunnel chiffré
    T->>N: requête vers l’origine
    N->>F: proxy HTTP local
    F->>P: requête PromQL si données temps réel
    P-->>F: métriques des équipements
    F-->>N: page HTML ou réponse JSON
    N-->>U: réponse HTTPS
```

Le certificat public est géré côté Cloudflare. Nginx protège et distribue le trafic sur `srv-web`. Gunicorn exécute l’application Flask ; il ne doit pas être exposé directement à Internet.

## Chaîne de supervision

```mermaid
flowchart LR
    NW["Node Exporter srv-web"] --> P[Prometheus]
    CA[cAdvisor] --> P
    NM["Node Exporter srv-monitoring"] --> P
    WE["Windows Exporter"] --> P
    BAT["Collecteur batterie"] --> WE
    VM["Collecteur volumes Docker"] --> NM
    P --> UI["Portail Flask"]
    P --> G[Grafana]
    P --> R["Règles d’alerte"]
    R --> A[Alertmanager]
    A --> T[Telegram]
```

Prometheus interroge périodiquement les exporters. Une valeur absente reste inconnue : elle ne doit jamais être transformée artificiellement en zéro. Le portail interroge Prometheus pour afficher les valeurs actuelles et les historiques.

## Données persistantes

| Donnée | Emplacement logique | Emplacement sur l’hôte |
|---|---|---|
| Séries Prometheus | `prometheus-data` | `/var/lib/docker/volumes/monitoring_prometheus-data/_data` |
| Tableaux Grafana | `grafana-data` | `/var/lib/docker/volumes/monitoring_grafana-data/_data` |
| État Alertmanager | `alertmanager-data` | `/var/lib/docker/volumes/monitoring_alertmanager-data/_data` |
| Données Flask | `application/data/` | volume ou dossier de `srv-web` |
| Configuration sensible | `application/.env` | uniquement sur `srv-web`, permission `600` |

Un volume Docker conserve ses données après la recréation d’un conteneur, mais ce n’est pas une sauvegarde. Les volumes doivent être inclus dans les archives de restauration.

## Frontières de sécurité

- seul le point d’entrée HTTPS est public ;
- Prometheus, Grafana, Alertmanager, exporters et socket Docker restent privés ;
- le PC Windows autorise le port `9182` uniquement depuis `srv-monitoring` ;
- le PC peut être en veille sans générer une alerte d’indisponibilité générale ;
- les secrets, bases, archives et clés sont exclus de Git ;
- Emma_IA est en lecture seule et ne lance aucune commande système.

## Extension future

Pour ajouter un nouvel équipement : installer un exporter, filtrer son port, déclarer la cible dans `monitoring/prometheus.yml`, ajouter ses labels (`equipment`, `role`, `os`), adapter les requêtes et règles, puis créer sa vue en réutilisant le gabarit multi-équipement.
