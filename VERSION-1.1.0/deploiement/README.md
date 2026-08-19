# Déploiement VPS

Ce dossier décrit la pile réellement utilisée sur le VPS de production : portail Flask, Prometheus, Grafana, Alertmanager, Node Exporter et cAdvisor.

## Préparation

1. Copier `secrets/application.env.example` vers `secrets/application.env`.
2. Copier `secrets/grafana.env.example` vers `secrets/grafana.env`.
3. Remplacer toutes les valeurs d'exemple et conserver les deux fichiers avec des permissions strictes.
4. Créer le certificat interne attendu par l'application :

```bash
openssl req -x509 -newkey rsa:2048 -nodes \
  -keyout secrets/internal-status.key \
  -out config/internal-status.crt \
  -days 365 -subj '/CN=secure-local-cloud-internal'
chmod 600 secrets/*.env secrets/internal-status.key
```

## Lancement

```bash
docker compose config --quiet
docker compose up -d --build
curl -fsS http://127.0.0.1:5001/health
```

Les services d'administration écoutent uniquement sur `127.0.0.1`. L'accès public au portail passe par Nginx et Cloudflare Tunnel. Les équipements distants sont joints par Tailscale.

## Sécurité

Ne jamais ajouter dans Git : fichiers `.env`, clés privées, jeton Cloudflare, état Tailscale, données applicatives ou volumes Docker.

## Politique d’alertes livrée

Le fichier `config/alerts.yml` reflète la politique finale : production critique, laboratoire en avertissement seulement lorsque le PC hôte est joignable. Les adresses et secrets réels ne sont pas inclus.
