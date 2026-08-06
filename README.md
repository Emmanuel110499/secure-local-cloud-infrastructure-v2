# Secure Local Cloud Infrastructure v2

Portail local de supervision et d'administration d'une infrastructure auto-hebergee. Le projet regroupe une application Flask, un proxy HTTPS Nginx et une pile de metriques Prometheus, Alertmanager, Grafana, Node Exporter et cAdvisor.

> Ce depot fournit une base de deploiement. Les adresses IP, noms d'hote, chemins de volumes et certificats doivent etre adaptes a votre environnement. Aucun secret reel ne doit etre versionne.

## Fonctionnalites

- tableau de bord web et vues de supervision ;
- etat des conteneurs Docker et metriques systeme ;
- integration Prometheus, Grafana et Alertmanager ;
- audit, consultation de journaux et export de rapports PDF ;
- authentification administrateur configuree par variables d'environnement ;
- terminaison TLS et reverse proxy avec Nginx.

## Architecture

```mermaid
flowchart LR
    U[Utilisateur] -->|HTTPS| N[Nginx]
    N --> F[Portail Flask / Gunicorn]
    F --> D[Docker Engine]
    F --> P[Prometheus]
    F --> G[Grafana]
    F --> A[Alertmanager]
    P --> E[Node Exporter]
    P --> C[cAdvisor]
```

Les composants peuvent etre repartis sur deux machines : un serveur web pour Nginx et Flask, et un serveur de monitoring pour Prometheus, Grafana et Alertmanager. Les adresses presentes dans les fichiers Compose sont des exemples issus du reseau local d'origine.

Une [architecture cible a grande echelle](docs/ARCHITECTURE.md#architecture-cible-a-grande-echelle) documente l'evolution possible vers plusieurs sites, des Prometheus regionaux, un stockage distribue, un cluster Alertmanager et une authentification centralisee.

## Arborescence utile

```text
application/          Application Flask et conteneur web
monitoring/           Prometheus, Alertmanager et Grafana
nginx/                Exemples de configuration du reverse proxy
services/             Unite systemd Node Exporter
systemd/              Services et timers d'export des journaux
scripts/              Scripts d'exploitation
docs/                 Installation, architecture et securite
docs/screenshots/     Captures d'ecran publiques
```

## Prerequis

- Linux avec Docker Engine et Docker Compose v2 ;
- Nginx si le reverse proxy est installe sur l'hote ;
- un certificat et une cle TLS ;
- connectivite entre les machines et ports strictement filtres par pare-feu.

## Demarrage rapide

1. Clonez le depot et placez-vous dans `application/`.
2. Copiez `.env.example` vers `.env`.
3. Generez une cle secrete et un mot de passe robuste.
4. Adaptez les URL, adresses IP et volumes dans les fichiers Compose.
5. Lancez les services.

```bash
git clone https://github.com/VOTRE_COMPTE/secure-local-cloud-infrastructure-v2.git
cd secure-local-cloud-infrastructure-v2/application
cp .env.example .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
docker compose config
docker compose up -d --build
```

Renseignez la valeur generee dans `SECRET_KEY` avant le lancement. Consultez [le guide d'installation](docs/INSTALLATION.md) pour le deploiement complet.

## Configuration

Les secrets sont lus depuis `application/.env`, fichier ignore par Git. Le modele `application/.env.example` ne contient aucune valeur confidentielle.

| Variable | Role |
|---|---|
| `SECRET_KEY` | Signature des sessions Flask, valeur longue et aleatoire |
| `ADMIN_USERNAME` | Identifiant administrateur |
| `ADMIN_PASSWORD` | Mot de passe initial ; preferer un secret injecte au deploiement |
| `ADMIN_PASSWORD_HASH` | Empreinte du mot de passe si cette option est utilisee |
| `PROMETHEUS_URL` | URL interne de Prometheus |
| `GRAFANA_URL` | URL interne de Grafana |
| `ALERTMANAGER_URL` | URL interne d'Alertmanager |

## Captures d'ecran

### Vue d'ensemble

![Accueil de Secure Local Cloud Infrastructure](docs/screenshots/accueil.png)

### Supervision des ressources

La vue de monitoring présente les mesures en temps réel et leur historique : CPU, mémoire vive, espace disque, seuils surveillés et export PDF.

![Monitoring CPU, mémoire et disque](docs/screenshots/monitoring.png)

### Conteneurs Docker

Cette vue centralise l'état, la consommation et les actions d'exploitation des conteneurs exécutés sur `srv-web`.

![Supervision des conteneurs Docker](docs/screenshots/conteneurs-docker.png)

### Architecture de l'infrastructure

La cartographie visualise le chemin d'accès externe, les réseaux privés, les deux serveurs et les principaux services de la plateforme.

![Architecture de Secure Local Cloud Infrastructure](docs/screenshots/architecture.png)

## Securite

Ce projet monte le socket Docker dans le conteneur web et cAdvisor utilise des acces privilegies. Ces droits sont tres puissants : ne rendez jamais ces services directement accessibles depuis Internet. Placez-les sur un reseau d'administration, limitez les ports avec un pare-feu et protegez le portail par TLS et authentification forte.

Avant chaque publication, consultez [SECURITY.md](SECURITY.md), verifiez l'historique Git et effectuez une recherche de secrets.

## Documentation

- [Installation](docs/INSTALLATION.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Securite et secrets](SECURITY.md)

## Etat du projet

Projet personnel d'infrastructure locale, a adapter et auditer avant tout usage en production.

Le depot public ne contient ni sauvegarde de production, ni base de donnees, ni fichier `.env`, ni jeton Telegram, ni cle Cloudflare, ni cle SSH. Les valeurs sensibles sont injectees uniquement sur les serveurs.
