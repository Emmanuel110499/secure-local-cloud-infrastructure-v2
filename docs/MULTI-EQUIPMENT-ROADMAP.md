# Évolution vers la supervision multi-équipement

## Périmètre validé

La plateforme supervisera progressivement :

- `srv-web` (Linux, application, Nginx, Cloudflare Tunnel, Docker et cAdvisor) ;
- `srv-monitoring` (Linux, Prometheus, Grafana, Alertmanager et stockages persistants) ;
- `pc-emmanuel` (Windows, ressources système, réseau et batterie) ;
- les futurs serveurs ou VPS ajoutés à la configuration.

## Organisation de l’interface

La page Monitoring proposera un sélecteur commun :

`Vue globale | srv-web | srv-monitoring | PC Emmanuel`

La vue globale comparera la santé et les principaux indicateurs des équipements.
Chaque vue détaillée réutilisera le même gabarit, avec des panneaux adaptés au type
de machine et aux services réellement présents.

## Ordre de réalisation

1. Synchroniser le dépôt avec la version réellement déployée sur `srv-web`.
2. Ajouter une configuration centrale des équipements.
3. Créer les API de métriques actuelles, historiques et de disponibilité.
4. Construire l’interface Monitoring validée, sur ordinateur et téléphone.
5. Adapter l’accueil, l’infrastructure, l’audit et la documentation.
6. Étendre Emma_IA aux questions et comparaisons multi-équipement.
7. Étendre les alertes Prometheus et Telegram.
8. Tester, documenter et déployer avec une procédure de retour arrière.

## Règle de sécurité

Aucune donnée fictive ne doit être affichée comme une mesure réelle. Une donnée
absente doit rester `inconnue`, sans être transformée en panne ou en valeur nulle.
