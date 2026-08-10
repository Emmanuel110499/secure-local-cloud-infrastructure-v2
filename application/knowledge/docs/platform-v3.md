# Vue d'ensemble de Secure Local Cloud Infrastructure

La plateforme est un laboratoire personnel de supervision, d'administration et de sécurité construit autour de deux serveurs Ubuntu. Elle permet d'observer l'état du système, les conteneurs Docker, les métriques, les alertes et les mécanismes de protection depuis une interface Flask.

Le serveur srv-web héberge l'application Flask exécutée par Gunicorn, le proxy Nginx, Cloudflare Tunnel, Node Exporter et cAdvisor. Le serveur srv-monitoring héberge Prometheus, Grafana et Alertmanager. Le réseau privé 192.168.50.0/24 transporte les échanges de supervision. Le réseau 192.168.154.0/24 sert à l'administration depuis le poste personnel.

# Chemin d'une visite publique

Un visiteur ouvre un domaine emmanuelinfra.fr. Cloudflare reçoit la connexion publique et la transmet au tunnel cloudflared exécuté sur srv-web. Pour l'application principale, cloudflared contacte Flask sur le port local 5001. Pour Grafana ou Prometheus, srv-web traverse le réseau privé vers srv-monitoring. Les règles DOCKER-USER n'autorisent que les sources internes prévues.

# Collecte et visualisation

Node Exporter expose les métriques du système srv-web. cAdvisor expose les métriques des conteneurs. Prometheus collecte ces deux cibles, conserve les séries temporelles pendant au maximum quinze jours ou un gigaoctet, et évalue les règles d'alerte. Grafana interroge Prometheus et transforme les métriques en tableaux de bord.

# Alertes

Quand une règle Prometheus devient vraie pendant la durée définie, Prometheus transmet l'alerte à Alertmanager. Alertmanager regroupe les événements et utilise le récepteur Telegram. Les alertes surveillent notamment l'indisponibilité des cibles, le CPU, la mémoire, le disque, le conteneur Flask et les sauvegardes automatiques.

# Sauvegardes

srv-web et srv-monitoring disposent chacun d'un timer systemd hebdomadaire. Les scripts arrêtent brièvement les services concernés, créent une archive protégée, vérifient son contenu, calculent une empreinte SHA-256 et redémarrent les conteneurs. Les archives automatiques anciennes sont supprimées uniquement dans leur dossier dédié.

# Emma_IA

Emma_IA est l'assistant d'exploitation intégré à Flask. Elle ne doit jamais exécuter automatiquement une commande système. Elle combine les métriques réelles, l'inventaire Docker et la documentation locale. Elle indique si sa réponse vient de données temps réel ou de la documentation, fournit un niveau de confiance et propose des questions de suivi.
