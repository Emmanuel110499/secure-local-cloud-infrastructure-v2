# Les métriques

Une métrique est une mesure chiffrée permettant de suivre l’état ou les performances d’un système.

Dans cette plateforme, les métriques permettent de surveiller l’utilisation du CPU, la mémoire RAM, l’espace disque, le trafic réseau, la consommation des conteneurs Docker et la disponibilité des services.

# CPU et RAM

La métrique CPU permet de détecter une surcharge, un processus trop gourmand ou un serveur manquant de puissance. La métrique RAM indique la quantité de mémoire utilisée et disponible.

Node Exporter expose les métriques du serveur. cAdvisor expose celles des conteneurs. Prometheus les collecte et Grafana les transforme en graphiques.

# Target Prometheus DOWN

Une cible Prometheus DOWN signifie que Prometheus ne parvient plus à récupérer les métriques du service. Les causes possibles sont un service arrêté, une mauvaise adresse IP, un port fermé, un problème réseau, un pare-feu ou une configuration Prometheus incorrecte.
