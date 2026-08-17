# Secure Local Cloud — dossier complet de la version 1.1.0

Ce dossier regroupe en un seul endroit tout ce qui permet de comprendre la version 1.1.0 sans parcourir l'ensemble du dépôt.

## Parcours conseillé

1. [Lire les notes de version](documentation/NOTES-DE-VERSION.md) pour comprendre ce qui a changé depuis la version 1.0.0.
2. [Lire l'architecture](documentation/ARCHITECTURE.md) pour comprendre les rôles du VPS, du PC et des deux VM.
3. [Consulter les schémas](schemas/) pour visualiser les flux publics et privés.
4. [Consulter les captures](captures/) pour voir les données réellement remontées par les équipements.
5. [Consulter le déploiement](deploiement/README.md) pour retrouver les modèles de configuration sans secrets.

## Contenu du dossier

```text
VERSION-1.1.0/
├── README.md
├── documentation/
│   ├── ARCHITECTURE.md
│   ├── INSTALLATION.md
│   ├── NOTES-DE-VERSION.md
│   └── SAUVEGARDES-RESTAURATION.md
├── schemas/
│   ├── architecture-production.svg
│   └── evolution-v1.0-vers-v1.1.svg
├── captures/
│   ├── monitoring-pc-emmanuel.png
│   ├── monitoring-vm-srv-web.png
│   └── monitoring-vm-srv-monitoring.png
└── deploiement/
    ├── README.md
    ├── docker-compose.yml
    ├── config/
    ├── nginx/
    ├── scripts/
    ├── secrets/*.example
    └── systemd/
```

## Architecture résumée

![Architecture de production](schemas/architecture-production.svg)

- **VPS Production** : héberge en permanence le portail, Prometheus, Grafana, Alertmanager, Nginx et les sauvegardes.
- **PC Emmanuel** : poste Windows d'administration, supervisé avec Windows Exporter et le collecteur batterie.
- **VM srv-web** : serveur applicatif du laboratoire VMware, supervisé par Node Exporter.
- **VM srv-monitoring** : serveur d'observabilité du laboratoire VMware, supervisé par Node Exporter.
- **Cloudflare Tunnel** : publie les services web sans exposer directement Flask.
- **Tailscale** : relie de façon privée le VPS, le PC et les deux VM.

## Sécurité

Ce dossier ne contient aucun mot de passe, jeton, fichier `.env` réel, clé privée ni adresse privée réelle. Les fichiers `*.example` doivent être copiés et adaptés hors de Git avant un déploiement.
