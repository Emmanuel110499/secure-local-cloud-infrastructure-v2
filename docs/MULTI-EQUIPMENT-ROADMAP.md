# État de la supervision multi-équipement

## Réalisé

- supervision de `srv-web`, `srv-monitoring` et `pc-emmanuel` ;
- métriques CPU, RAM, disque, réseau, uptime et batterie ;
- historiques de 1 heure à 7 jours et volumes persistants ;
- interface responsive et Emma_IA multi-équipement ;
- alertes Prometheus et Telegram ;
- sauvegardes Linux et réplication vérifiée vers le PC.

## Prochaines évolutions possibles

1. Exposer les métriques de sauvegarde de `srv-monitoring` comme celles de `srv-web`.
2. Alerter sur la croissance anormale des volumes persistants.
3. Automatiser un test périodique de restauration.
4. Actualiser les captures GitHub.
5. Ajouter les futurs serveurs avec le même modèle d’équipement.

## Règle de qualité

Aucune donnée fictive ne doit être affichée comme réelle. Une valeur absente reste `inconnue` et ne devient ni zéro ni panne sans preuve.
