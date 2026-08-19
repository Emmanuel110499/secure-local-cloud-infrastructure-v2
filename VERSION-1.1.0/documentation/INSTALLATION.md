# Guide complet d'installation et de reconstruction

> Secure Local Cloud Infrastructure v1.0.0 — du poste vierge à la plateforme publique.
>
> Ce document ne contient aucun secret réel. Remplacez toutes les valeurs entre `<...>` et conservez les jetons, mots de passe et clés hors de Git.

## 1. Résultat à obtenir

L'installation finale repose sur trois équipements :

| Équipement | Adresse | Rôle | Technologies principales |
|---|---:|---|---|
| PC Emmanuel | `192.168.154.1` | Administration et hôte VMware | Windows 11, VMware Workstation, SSH, Windows Exporter, collecteur batterie, réplication |
| `srv-web` | `192.168.50.10` / `192.168.154.10` | Serveur applicatif | Ubuntu, Docker, Flask, Gunicorn, Nginx, cloudflared, Node Exporter, cAdvisor |
| `srv-monitoring` | `192.168.50.20` / `192.168.154.20` | Serveur d'observabilité | Ubuntu, Docker, Prometheus, Grafana, Alertmanager, Node Exporter |

Flux public :

```text
Internet -> Cloudflare (DNS, HTTPS, Zero Trust)
         -> tunnel cloudflared sortant sur srv-web
         -> Nginx
         -> 127.0.0.1:5001
         -> Gunicorn / Flask dans Docker :5000
```

Flux de supervision :

```text
Node Exporter srv-web :9100 ---------+
cAdvisor srv-web :8080 --------------+--> Prometheus :9090
Node Exporter srv-monitoring :9100 ---+        |--> Grafana :3000
Windows Exporter PC :9182 ------------+        +--> Alertmanager :9093 --> Telegram
```

## 2. Prérequis

- un PC Windows 11 avec virtualisation activée dans l'UEFI ;
- VMware Workstation ;
- une image ISO Ubuntu Server 24.04 LTS ;
- au moins 4 cœurs CPU, 12 Gio de RAM et 40 Gio libres pour le laboratoire ;
- un nom de domaine géré dans Cloudflare ;
- un compte GitHub et Git ;
- un bot Telegram dédié aux alertes, facultatif pendant l'installation initiale.

Conservez les secrets dans un gestionnaire de mots de passe. Ne placez jamais `.env`, une clé privée SSH, un jeton Telegram ou un fichier d'identifiants dans le dépôt public.

## 3. Créer les réseaux VMware

Dans **Virtual Network Editor**, préparez :

| Réseau VMware | Sous-réseau | Usage |
|---|---|---|
| NAT | réseau attribué par VMware | mises à jour Ubuntu et tunnel Cloudflare |
| VMnet service | `192.168.50.0/24` | échanges entre les deux VM et scraping Prometheus |
| VMnet administration | `192.168.154.0/24` | SSH depuis Windows, Windows Exporter et réplication |

Le PC porte `192.168.154.1` sur l'adaptateur VMware d'administration. Ne configurez qu'une seule route par défaut dans chaque VM : celle de l'interface NAT.

## 4. Créer les machines virtuelles

### 4.1 `srv-web`

- nom : `srv-web` ;
- 2 vCPU ;
- 4 Gio de RAM ;
- disque dynamique de 20 Gio minimum ;
- carte 1 : NAT ;
- carte 2 : réseau services ;
- carte 3 : réseau administration ;
- Ubuntu Server 24.04 LTS, installation minimale avec OpenSSH Server.

### 4.2 `srv-monitoring`

- nom : `srv-monitoring` ;
- 2 vCPU ;
- 4 Gio de RAM ;
- disque dynamique de 30 Gio minimum ;
- mêmes trois cartes réseau ;
- Ubuntu Server 24.04 LTS avec OpenSSH Server.

Un disque de 10 Gio fonctionne pour une démonstration, mais laisse peu de marge à Grafana, Prometheus, Docker et aux sauvegardes. Pour une exploitation durable, utilisez 30 Gio ou plus sur `srv-monitoring`.

## 5. Configurer Ubuntu et le réseau

Sur chaque VM :

```bash
sudo apt update
sudo apt full-upgrade -y
sudo apt install -y ca-certificates curl gnupg git jq unzip nginx ufw
sudo hostnamectl set-hostname srv-web             # ou srv-monitoring
sudo timedatectl set-timezone Europe/Paris
```

Identifiez les interfaces :

```bash
ip -br address
ip route
```

Exemple Netplan à adapter à vos noms d'interfaces :

```yaml
network:
  version: 2
  ethernets:
    ens33:
      dhcp4: true
    ens37:
      addresses: [192.168.50.10/24]
    ens38:
      addresses: [192.168.154.10/24]
```

Sur `srv-monitoring`, remplacez `.10` par `.20`. Appliquez prudemment :

```bash
sudo netplan generate
sudo netplan try
sudo netplan apply
```

Validez depuis le PC :

```powershell
ssh emmanuel@192.168.154.10
ssh emmanuel@192.168.154.20
```

## 6. Durcir l'accès SSH et le pare-feu

Créez une clé distincte pour l'administration et installez sa clé publique avec `ssh-copy-id` ou dans `~/.ssh/authorized_keys`. Conservez provisoirement une session ouverte avant de désactiver l'authentification par mot de passe.

Sur `srv-web` :

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.154.1 to any port 22 proto tcp
sudo ufw allow from 192.168.50.20 to any port 9100 proto tcp
sudo ufw allow from 192.168.50.20 to any port 8080 proto tcp
sudo ufw enable
```

Sur `srv-monitoring`, autorisez SSH depuis le PC et les interfaces privées nécessaires pour `3000`, `9090`, `9093` et `9100`. Aucun de ces ports ne doit être ouvert directement sur Internet.

## 7. Installer Docker Engine et Compose

Sur les deux VM :

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg |
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo $VERSION_CODENAME) stable" |
  sudo tee /etc/apt/sources.list.d/docker.list >/dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
```

Reconnectez la session, puis contrôlez :

```bash
docker version
docker compose version
docker run --rm hello-world
```

## 8. Déployer le serveur d'observabilité

Sur `srv-monitoring` :

```bash
git clone https://github.com/Emmanuel110499/secure-local-cloud-infrastructure-v2.git
cd secure-local-cloud-infrastructure-v2/monitoring
```

Le fichier `prometheus.yml` doit déclarer les quatre cibles :

```yaml
scrape_configs:
  - job_name: srv-web
    static_configs:
      - targets: ["192.168.50.10:9100"]
        labels:
          equipment: srv-web
          role: application
          os: linux

  - job_name: cadvisor
    static_configs:
      - targets: ["192.168.50.10:8080"]

  - job_name: srv-monitoring
    static_configs:
      - targets: ["192.168.50.20:9100"]
        labels:
          equipment: srv-monitoring
          role: monitoring
          os: linux

  - job_name: pc-windows
    static_configs:
      - targets: ["192.168.154.1:9182"]
        labels:
          equipment: pc-emmanuel
          role: administration
          os: windows
          alert_on_down: "false"
```

Validez et démarrez :

```bash
docker compose config --quiet
docker compose up -d
docker compose ps
curl -fsS http://127.0.0.1:9090/-/ready
curl -fsS http://127.0.0.1:9093/-/ready
```

Les volumes `monitoring_prometheus-data`, `monitoring_grafana-data` et `monitoring_alertmanager-data` conservent respectivement les séries temporelles, les tableaux Grafana et l'état d'Alertmanager. Un volume persistant n'est pas une sauvegarde.

## 9. Installer Node Exporter sur les deux VM

Téléchargez une version vérifiée depuis le dépôt officiel Prometheus, installez le binaire dans `/usr/local/bin/node_exporter`, puis copiez et activez l'unité fournie dans `services/node_exporter.service`.

```bash
sudo cp services/node_exporter.service /etc/systemd/system/node_exporter.service
sudo systemctl daemon-reload
sudo systemctl enable --now node_exporter
curl -fsS http://127.0.0.1:9100/metrics | head
```

Sur `srv-monitoring`, le collecteur de volumes écrit également des métriques texte pour afficher l'occupation réelle de Prometheus, Grafana et Alertmanager :

```bash
sudo install -m 0755 scripts/collect-monitoring-volumes.sh /usr/local/sbin/collect-monitoring-volumes.sh
sudo cp systemd/monitoring-volume-metrics.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now monitoring-volume-metrics.timer
sudo systemctl start monitoring-volume-metrics.service
curl -fsS http://192.168.50.20:9100/metrics | grep '^secure_docker_volume_'
```

## 10. Déployer l'application Flask sur `srv-web`

```bash
git clone https://github.com/Emmanuel110499/secure-local-cloud-infrastructure-v2.git
cd secure-local-cloud-infrastructure-v2/application
cp .env.example .env
chmod 600 .env
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

Renseignez `.env` avec des valeurs privées. Les variables multi-équipement importantes sont :

```dotenv
PROMETHEUS_URL=http://192.168.50.20:9090
MONITORING_NODE_JOB=srv-monitoring
MONITORING_NODE_INSTANCE=192.168.50.20:9100
WINDOWS_EXPORTER_JOB=pc-windows
WINDOWS_EXPORTER_INSTANCE=192.168.154.1:9182
WINDOWS_EQUIPMENT=pc-emmanuel
```

Validez, testez et démarrez :

```bash
python3 -m py_compile app.py config.py extensions.py services/prometheus_service.py
docker compose config --quiet
docker build -t application-web:v1.0.0 .
docker run --rm --env-file .env --network host \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  application-web:v1.0.0 \
  python -m unittest discover -s /app/tests -p 'test_*.py' -q
docker image tag application-web:v1.0.0 application-web:latest
docker compose up -d --force-recreate --no-build web
docker compose ps web
```

Le socket Docker est monté en lecture seule. Emma_IA et l'interface n'exécutent aucune commande système en réponse à une question.

## 11. Installer Windows Exporter et la batterie

Téléchargez le MSI Windows Exporter depuis la release GitHub officielle, comparez son SHA-256 avec l'empreinte publiée puis installez les collecteurs CPU, mémoire, disque, réseau, système et service.

Limitez le pare-feu au serveur Prometheus :

```powershell
New-NetFirewallRule `
  -DisplayName "Secure Cloud - Windows Exporter" `
  -Direction Inbound -Action Allow -Protocol TCP `
  -LocalAddress 192.168.154.1 -LocalPort 9182 `
  -RemoteAddress 192.168.154.20 -Profile Any
```

Contrôlez :

```powershell
Invoke-WebRequest -UseBasicParsing http://192.168.154.1:9182/health
(Invoke-WebRequest -UseBasicParsing http://192.168.154.1:9182/metrics).Content
```

Le collecteur batterie écrit périodiquement des métriques dans le répertoire textfile de Windows Exporter. Sa tâche planifiée doit s'exécuter sous `SYSTEM`, environ toutes les minutes, et publier la charge, l'alimentation secteur, la décharge et l'heure de dernière collecte.

## 12. Configurer les alertes et Telegram

Validez d'abord les 17 règles publiques :

```bash
cd ~/monitoring
docker compose exec -T prometheus promtool check rules /etc/prometheus/alerts.yml
```

Dans la configuration privée d'Alertmanager, injectez le jeton et l'identifiant de discussion depuis un fichier protégé ou des variables non suivies. Le dépôt public ne doit contenir que des placeholders.

```bash
docker compose exec -T alertmanager amtool check-config /etc/alertmanager/alertmanager.yml
docker compose restart prometheus alertmanager
curl -fsS http://127.0.0.1:9090/api/v1/alerts | python3 -m json.tool
curl -fsS http://127.0.0.1:9093/api/v2/alerts | python3 -m json.tool
```

Une alerte passe de `inactive` à `pending`, puis `firing` après la durée de confirmation. Le message `resolved` confirme le retour à la normale.

## 13. Configurer Nginx et Cloudflare Tunnel

Sur `srv-web`, adaptez `nginx/default-https`, puis :

```bash
sudo cp nginx/default-https /etc/nginx/sites-available/secure-local-cloud
sudo ln -sfn /etc/nginx/sites-available/secure-local-cloud /etc/nginx/sites-enabled/secure-local-cloud
sudo nginx -t
sudo systemctl reload nginx
curl -k -I https://127.0.0.1
```

Dans Cloudflare Zero Trust :

1. créez un tunnel ;
2. installez `cloudflared` sur `srv-web` ;
3. créez le nom public `app.emmanuelinfra.fr` ;
4. envoyez l'origine vers l'adresse Nginx locale ;
5. protégez éventuellement l'accès avec une politique d'identité ;
6. activez et contrôlez le service `cloudflared`.

```bash
systemctl status cloudflared --no-pager
journalctl -u cloudflared -n 100 --no-pager
curl -I https://app.emmanuelinfra.fr
```

Une erreur Cloudflare 1033 signifie généralement que le tunnel n'est plus connecté. Vérifiez d'abord la route NAT, le DNS et le service `cloudflared`.

## 14. Mettre en place les sauvegardes et la réplication

Chaque serveur crée une archive `.tar.gz` accompagnée de son `.sha256` :

```text
/var/backups/secure-local-cloud/automatic/srv-web/
/var/backups/secure-local-cloud/automatic/srv-monitoring/
```

Une copie exportable est déposée dans :

```text
/home/emmanuel/backup-export/srv-web/
/home/emmanuel/backup-export/srv-monitoring/
```

Vérifiez les timers Linux :

```bash
systemctl list-timers --all | grep backup
sha256sum -c /home/emmanuel/backup-export/srv-web/*.sha256
```

Sur Windows, créez la clé SSH dédiée puis la tâche quotidienne **Secure Local Cloud - Replication**. Elle exécute :

```text
C:\Users\Emman\SecureLocalCloud-Backups\sync-secure-cloud-backups.ps1
```

et copie vers :

```text
C:\Users\Emman\SecureLocalCloud-Backups\srv-web\
C:\Users\Emman\SecureLocalCloud-Backups\srv-monitoring\
C:\Users\Emman\SecureLocalCloud-Backups\logs\replication.log
```

La tâche actuelle est prévue chaque jour à 20:00, avec `StartWhenAvailable`. Après une veille ou un arrêt, Windows la lance dès que possible.

```powershell
Get-ScheduledTaskInfo -TaskName "Secure Local Cloud - Replication"
Start-ScheduledTask -TaskName "Secure Local Cloud - Replication"
Get-Content "$env:USERPROFILE\SecureLocalCloud-Backups\logs\replication.log" -Tail 30
```

## 15. Recette complète

### Sur `srv-monitoring`

```bash
docker compose ps
curl -fsS http://127.0.0.1:9090/api/v1/targets | python3 -m json.tool
curl -fsS http://127.0.0.1:9090/api/v1/rules | python3 -m json.tool
```

Les quatre cibles doivent être `up` lorsque le PC est allumé.

### Sur `srv-web`

```bash
docker compose ps web
docker inspect secure-web-app-v2 --format 'Etat={{.State.Status}} Sante={{.State.Health.Status}}'
curl -sS http://127.0.0.1:5001/health
curl -k -I https://127.0.0.1
docker logs --tail 100 secure-web-app-v2
```

### Dans le navigateur

- connexion à `https://app.emmanuelinfra.fr` ;
- vue globale puis vues `srv-web`, `srv-monitoring` et `PC Emmanuel` ;
- graphiques CPU, RAM et disque ;
- volumes Prometheus, Grafana et Alertmanager ;
- conteneurs Docker ;
- architecture multi-équipement ;
- questions Emma_IA ;
- téléchargement du rapport PDF ;
- affichage mobile à 390 × 645.

## 16. Restauration, mise à jour et maintenance

Avant toute modification :

```bash
git switch -c feature/nom-du-changement
tar -czf "$HOME/application-before-$(date -u +%Y%m%d-%H%M%S).tar.gz" .
```

Pour restaurer :

1. choisissez une archive copiée sur le PC ;
2. vérifiez son SHA-256 ;
3. restaurez d'abord sur une machine de test ;
4. recréez les volumes avant les conteneurs ;
5. remettez les secrets avec des permissions `600` ;
6. testez l'authentification, les métriques, les alertes et les PDF ;
7. seulement ensuite, planifiez la restauration de production.

Rythme conseillé :

| Fréquence | Contrôle |
|---|---|
| Hebdomadaire | sauvegardes, empreintes, réplication Windows |
| Mensuelle | disque, volumes, cibles Prometheus, alertes Telegram |
| Trimestrielle | dépendances, images Docker et correctifs Ubuntu |
| Avant changement | archive, branche Git, tests et retour arrière |
| Avant migration | restauration complète sur une machine de test |

## Dépannage rapide

| Symptôme | Vérification prioritaire |
|---|---|
| URL publique en erreur 1033 | réseau NAT, DNS, `systemctl status cloudflared` |
| KPI vides | cibles Prometheus, labels `equipment`, console du navigateur |
| Graphiques absents | historique Prometheus et chargement de Chart.js |
| PC indisponible | Windows Exporter, pare-feu, veille du PC |
| Telegram silencieux | règle encore `pending`, Alertmanager, jeton privé |
| disque élevé | `df -h`, `docker system df`, journaux et anciennes sauvegardes |
| sauvegarde non copiée | tâche Windows, SSH, journal `replication.log` |

La plateforme est considérée installée uniquement lorsque les services sont sains, les données réelles sont visibles, une alerte de test arrive, une sauvegarde est vérifiée sur le PC et une restauration de test a réussi.
