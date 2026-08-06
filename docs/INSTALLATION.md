# Installation

## 1. Preparer les machines

Installez Docker Engine et le module Compose sur les hotes concernes. Configurez des adresses fixes ou des noms DNS internes. N'exposez publiquement que le port HTTPS du reverse proxy.

## 2. Configurer l'application

```bash
cd application
cp .env.example .env
chmod 600 .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Reportez la valeur generee dans `SECRET_KEY`, choisissez un identifiant et un mot de passe robustes, puis adaptez les URL du monitoring. Les chemins absolus de `application/docker-compose.yml` doivent egalement correspondre a l'hote cible.

Validez et demarrez :

```bash
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 web
```

## 3. Demarrer le monitoring

Adaptez les cibles de `monitoring/prometheus.yml`, puis :

```bash
cd monitoring
docker compose config
docker compose up -d
docker compose ps
```

Les images utilisent actuellement le tag `latest`. Pour un deploiement reproductible, remplacez-le par des versions testees et epinglees.

## 4. Configurer HTTPS

Installez le certificat et la cle hors du depot, avec des permissions restrictives. Adaptez `nginx/default-https`, testez la configuration puis rechargez Nginx :

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 5. Verification

- le portail repond uniquement en HTTPS ;
- la connexion administrateur fonctionne ;
- Prometheus voit ses cibles dans l'etat `UP` ;
- Grafana et Alertmanager ne sont pas exposes a Internet ;
- aucun secret n'apparait dans `git status` ou `git diff --cached`.

## Mise a jour

```bash
git pull --ff-only
cd application
docker compose up -d --build
```

Sauvegardez les volumes et bases de donnees avant toute mise a jour importante.
