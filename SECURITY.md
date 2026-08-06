# Politique de securite

## Signaler une vulnerabilite

N'ouvrez pas de ticket public contenant un secret, une adresse interne exploitable ou une preuve d'exploitation sensible. Contactez le mainteneur par un canal prive defini sur son profil GitHub.

## Secrets

Ne versionnez jamais `.env`, mots de passe, jetons, certificats, cles privees, fichiers `credentials.json`, bases de donnees ni journaux. Utilisez `application/.env.example` comme modele et injectez les valeurs reelles au deploiement.

Si un secret a deja ete publie : revoquez-le immediatement, retirez-le du code et de l'historique Git, puis controlez les journaux d'acces.

## Risques connus a maitriser

- le montage de `/var/run/docker.sock` equivaut a un acces tres privilegie a l'hote ;
- cAdvisor dispose de montages systeme et du mode `privileged` ;
- les ports 3000, 5001, 8080, 9090, 9093 et 9100 doivent etre filtres ;
- les images Docker doivent etre epinglees, mises a jour et analysees ;
- les certificats et cles TLS doivent rester hors du depot ;
- les sauvegardes et captures peuvent contenir des informations sensibles.

## Controle avant publication

```bash
git status --short
git diff --cached
git grep -nEi '(password|secret|token|api[_-]?key|private[_-]?key)'
git ls-files | grep -Ei '(^|/)(\.env|credentials\.json)|\.(pem|key|p12|pfx)$'
```

Analysez chaque resultat : les noms de variables et valeurs factices sont acceptables, les valeurs reelles ne le sont pas.
