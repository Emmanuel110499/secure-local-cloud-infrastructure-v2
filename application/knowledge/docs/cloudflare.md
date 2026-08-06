# Cloudflare Tunnel

Cloudflare Tunnel permet de publier la plateforme sur Internet sans ouvrir de port entrant sur la box ou le routeur.

Le service cloudflared fonctionne automatiquement sur srv-web. Il établit une connexion sortante sécurisée vers Cloudflare.

L’application principale est accessible à l’adresse app.emmanuelinfra.fr.

# Cloudflare Zero Trust

Grafana et Prometheus contiennent des informations techniques sensibles. Ils sont donc protégés par Cloudflare Zero Trust.

Lorsqu’un utilisateur ouvre Grafana ou Prometheus, Cloudflare lui demande son adresse e-mail. Seules les adresses autorisées reçoivent un code temporaire de connexion.

Les adresses protégées sont :

- grafana.emmanuelinfra.fr ;
- prometheus.emmanuelinfra.fr.
