SMB (Server Message Block) est un protocole très répandu sur les machines Windows qui offre de nombreux vecteurs pour le mouvement vertical et latéral. Parfois, des données sensibles peuvent se trouver sur ce réseau.

# `smbclient`
Cet outil permet de se connecter au réseau SMB, 

# SMB & `smbclient`

Fiche de référence : comprendre le protocole SMB et utiliser `smbclient` pour énumérer et manipuler des partages réseau (contexte CTF / pentest).

---

## 1. Qu'est-ce que SMB ?

**SMB** (_Server Message Block_) est un protocole réseau de partage de ressources. Il permet à une machine cliente de lire/écrire des fichiers, d'accéder à des imprimantes et de communiquer avec des services situés sur une machine distante, comme si ces ressources étaient locales. C'est le mécanisme historique du partage de fichiers dans le monde Windows (« Voisinage réseau », lecteurs réseau `\\serveur\partage`), mais il est aussi parlé côté Linux/Unix grâce à **Samba**, l'implémentation open source du protocole.

On croise souvent le sigle **CIFS** (_Common Internet File System_) : c'est simplement un ancien nom d'un dialecte de SMB (SMBv1). Aujourd'hui on dit « SMB », et CIFS ne désigne plus qu'une vieille version.

### Fonctionnement général

SMB suit un modèle **client-serveur** orienté requête/réponse :

1. Le client ouvre une connexion TCP vers le serveur.
2. Il négocie une **session** (authentification : utilisateur/mot de passe, ou session anonyme dite _null session_).
3. Il se connecte à un **partage** (_share_) : un dossier ou une ressource exposée par le serveur, identifié par un nom (ex. `Documents`, `IPC$`, `C$`).
4. Il envoie des opérations sur les fichiers (lister, lire, écrire, supprimer…).

### Notion de partage (_share_)

Un partage est un point d'accès nommé sur le serveur. Quelques partages ont un rôle particulier :

|Partage|Rôle|
|---|---|
|`IPC$`|Canal de communication inter-processus. Sert notamment à l'énumération (utilisateurs, autres partages) via les _null sessions_. Ne contient pas de fichiers.|
|`ADMIN$`|Accès administratif au dossier système Windows (`C:\Windows`). Nécessite des droits admin.|
|`C$`, `D$`…|Partages administratifs cachés donnant accès à la racine des disques.|
|Partages « custom »|Créés par l'administrateur (ex. `Share`, `Backups`, `Users`). C'est souvent là que se trouvent les données intéressantes en CTF.|

Le `$` à la fin d'un nom signifie que le partage est **caché** (il n'apparaît pas dans une navigation classique), mais il reste accessible si on connaît son nom.

### Ports & protocoles associés

|Port|Usage|
|---|---|
|**445/tcp**|SMB « moderne », directement sur TCP/IP. C'est le port principal aujourd'hui.|
|**139/tcp**|SMB via **NetBIOS** (ancienne pile). Encore présent sur des systèmes plus anciens.|
|137-138/udp|Services NetBIOS (résolution de noms, datagrammes).|

### Versions de SMB

- **SMBv1 / CIFS** : historique, obsolète et dangereux (vulnérabilité _EternalBlue_ → WannaCry). Désactivé par défaut sur les systèmes récents, mais encore rencontré sur de vieilles machines.
- **SMBv2** : introduit avec Windows Vista/2008, bien plus performant et sûr.
- **SMBv3** : à partir de Windows 8/2012, ajoute le chiffrement de bout en bout, l'intégrité, etc.

### Pourquoi SMB est important en pentest / CTF

SMB est une **mine d'informations** et une surface d'attaque fréquente :

- **Énumération** : lister les partages, les utilisateurs, la politique de mots de passe, souvent sans authentification (null session).
- **Fuite de données** : des partages mal configurés laissent lire des fichiers sensibles (configs, scripts avec mots de passe, sauvegardes, clés).
- **Point d'entrée** : dépôt de fichiers (webshell sur un partage relié à un serveur web), exécution de code (via `psexec`, `wmiexec`…), mouvements latéraux.
- **Vulnérabilités** : SMBv1 et diverses failles d'implémentation.

`smbclient` est l'outil de base pour la première étape : **explorer et manipuler les partages**.

---

## 2. `smbclient` : présentation

`smbclient` est un client SMB en ligne de commande, fourni par la suite **Samba**. Il se comporte un peu comme un client **FTP** : on se connecte à un partage, puis on navigue et on transfère des fichiers via un shell interactif.

### Installation

Sur Kali / Debian / Ubuntu :

```bash
sudo apt update && sudo apt install smbclient
```

Vérifier :

```bash
smbclient --version
```

---

## 3. Lister les partages disponibles

C'est presque toujours la première commande à lancer contre une cible.

```bash
# -L : lister les partages ; -N : pas de mot de passe (session anonyme)
smbclient -L //10.10.10.10 -N
```

- `//10.10.10.10` : l'adresse de la cible (double slash).
- `-L` (ou `--list`) : demande la liste des partages plutôt que de se connecter à l'un d'eux.
- `-N` (ou `--no-pass`) : ne demande pas de mot de passe → tente une **session null / anonyme**.

Avec un utilisateur :

```bash
smbclient -L //10.10.10.10 -U administrateur
```

Le mot de passe sera demandé de façon interactive. Exemple de sortie typique :

```
        Sharename       Type      Comment
        ---------       ----      -------
        ADMIN$          Disk      Remote Admin
        C$              Disk      Default share
        IPC$            IPC       Remote IPC
        Backups         Disk
        Users           Disk
```

Ici, `Backups` et `Users` sont des partages custom à explorer en priorité.

---

## 4. Se connecter à un partage

Une fois un partage repéré, on s'y connecte :

```bash
# Session anonyme
smbclient //10.10.10.10/Backups -N

# Avec un utilisateur
smbclient //10.10.10.10/Backups -U htb-student
```

En cas de succès, tu obtiens un prompt interactif :

```
smb: \>
```

À partir de là, tu es « dans » le partage et tu utilises des commandes internes.

---

## 5. Commandes internes (mode interactif)

Une fois connecté (`smb: \>`), les commandes ressemblent à un mélange de shell Unix et de client FTP :

|Commande|Effet|
|---|---|
|`ls` ou `dir`|Lister le contenu du répertoire courant|
|`cd <dossier>`|Changer de répertoire (`cd ..` pour remonter)|
|`pwd`|Afficher le répertoire courant|
|`get <fichier>`|Télécharger un fichier vers ta machine|
|`mget <motif>`|Télécharger plusieurs fichiers (ex. `mget *.txt`)|
|`put <fichier>`|Envoyer un fichier local vers le partage|
|`mput <motif>`|Envoyer plusieurs fichiers|
|`lcd <dossier>`|Changer le répertoire **local** (où atterrissent les `get`)|
|`recurse ON`|Activer la récursivité (pour parcourir/télécharger les sous-dossiers)|
|`prompt OFF`|Désactiver la confirmation fichier par fichier (utile avec `mget`)|
|`mask ""`|Réinitialiser le filtre de fichiers avant un `mget` récursif|
|`!<commande>`|Exécuter une commande sur ta machine locale (ex. `!ls`, `!pwd`)|
|`more <fichier>`|Afficher le contenu d'un fichier sans le télécharger|
|`help`|Lister toutes les commandes disponibles|
|`exit` ou `quit`|Quitter|

### Exemple : récupérer un fichier

```
smb: \> ls
  .                    D        0  ...
  ..                   D        0  ...
  note.txt             A      142  ...
  config               D        0  ...

smb: \> get note.txt
getting file \note.txt of size 142 as note.txt (0.1 KiloBytes/sec)

smb: \> exit
```

Le fichier `note.txt` se retrouve dans le répertoire depuis lequel tu as lancé `smbclient`.

### Exemple : tout télécharger récursivement

```
smb: \> recurse ON
smb: \> prompt OFF
smb: \> mget *
```

Cela télécharge l'intégralité de l'arborescence du partage en conservant la structure des dossiers. Très pratique pour rapatrier un partage entier et le fouiller tranquillement en local.

---

## 6. Exécuter des commandes sans mode interactif (`-c`)

L'option `-c` permet d'enchaîner des commandes internes en une seule ligne, sans entrer dans le shell interactif. Idéal pour scripter ou aller vite.

```bash
# Lister le contenu d'un partage en une commande
smbclient //10.10.10.10/Backups -N -c 'ls'

# Récupérer directement un fichier
smbclient //10.10.10.10/Backups -N -c 'get flag.txt'

# Enchaîner plusieurs commandes (séparées par ;)
smbclient //10.10.10.10/Users -U htb-student -c 'cd Administrator; cd Desktop; get flag.txt'

# Tout télécharger récursivement, sans interaction
smbclient //10.10.10.10/Backups -N -c 'recurse ON; prompt OFF; mget *'
```

---

## 7. Options utiles en ligne de commande

|Option|Rôle|
|---|---|
|`-U user`|Nom d'utilisateur|
|`-U 'DOMAINE\user'`|Utilisateur avec domaine (Active Directory)|
|`-U 'user%motdepasse'`|Utilisateur **et** mot de passe en une fois (pratique en script, mais le mot de passe apparaît dans l'historique/`ps`)|
|`-N`|Aucune authentification (session anonyme)|
|`-p <port>`|Port non standard (si SMB n'écoute pas sur 445)|
|`-W <domaine>`|Spécifier le domaine / workgroup|
|`--pw-nt-hash`|Interpréter le « mot de passe » fourni comme un **hash NT** → _pass-the-hash_|
|`-m SMB2` / `-m SMB3`|Forcer une version max du protocole|
|`-d <niveau>`|Niveau de verbosité (debug), utile pour diagnostiquer|

### Exemple : authentification avec domaine

```bash
smbclient //10.10.10.10/Share -U 'CORP\jdoe'
```

### Exemple : pass-the-hash

Si tu as récupéré le hash NT d'un utilisateur (sans connaître le mot de passe en clair) :

```bash
smbclient //10.10.10.10/C$ -U administrateur --pw-nt-hash -U 'administrateur%<HASH_NT>'
```

> Le pass-the-hash permet de s'authentifier avec l'empreinte du mot de passe plutôt que le mot de passe lui-même. Selon les versions de `smbclient`, la prise en charge peut varier ; des outils comme **impacket** ou **netexec** sont souvent plus fiables pour cet usage.

---

## 8. Cas d'usage typiques en CTF

Une séquence classique d'énumération SMB :

```bash
# 1. Quels partages existent ? (anonyme)
smbclient -L //10.10.10.10 -N

# 2. Explorer un partage prometteur
smbclient //10.10.10.10/Share -N -c 'recurse ON; ls'

# 3. Rapatrier tout le partage pour l'analyser en local
mkdir loot && cd loot
smbclient //10.10.10.10/Share -N -c 'recurse ON; prompt OFF; mget *'

# 4. Fouiller le butin
grep -riE 'password|passwd|secret|api[_-]?key' .
```

Objectifs recherchés : fichiers de configuration, scripts contenant des identifiants en dur, sauvegardes, clés SSH, notes, bases de données, etc.

---

## 9. Erreurs courantes (`NT_STATUS_*`)

`smbclient` renvoie des codes d'erreur Windows préfixés `NT_STATUS_`. Les plus fréquents :

|Message|Signification|Piste|
|---|---|---|
|`NT_STATUS_LOGON_FAILURE`|Identifiants incorrects|Vérifier user/mot de passe/domaine|
|`NT_STATUS_ACCESS_DENIED`|Authentifié mais sans droit sur cette ressource|Essayer un autre partage ou d'autres identifiants|
|`NT_STATUS_BAD_NETWORK_NAME`|Le partage demandé n'existe pas|Relancer `-L` pour le nom exact|
|`NT_STATUS_ACCOUNT_LOCKED_OUT`|Compte verrouillé (trop d'essais)|Attendre / éviter le bruteforce agressif|
|`NT_STATUS_CONNECTION_REFUSED`|Port SMB fermé / service absent|Vérifier que 445 est ouvert (`nmap`)|
|`NT_STATUS_PASSWORD_EXPIRED`|Mot de passe expiré|Le changer si possible|
|`NT_STATUS_NOT_SUPPORTED`|Négociation de protocole échouée|Forcer une version (`-m SMB2`) ou activer SMBv1 en legacy|

### Cas particulier : cible en SMBv1

Contre une vieille machine qui n'accepte que SMBv1, il faut parfois autoriser explicitement l'ancien dialecte :

```bash
smbclient -L //10.10.10.10 -N --option='client min protocol=NT1'
```

---

## 10. Outils complémentaires

`smbclient` est parfait pour explorer et transférer, mais d'autres outils vont plus loin dans l'énumération :

- **`smbmap`** : cartographie rapide des partages **et de tes permissions** (lecture/écriture) sur chacun.
    
    ```bash
    smbmap -H 10.10.10.10 -u '' -p ''
    ```
    
- **`netexec`** (ex-`crackmapexec`, commande `nxc`) : énumération et attaques SMB à grande échelle (spray d'identifiants, exécution de commandes, dump de secrets).
    
    ```bash
    nxc smb 10.10.10.10 -u user -p password --shares
    ```
    
- **`enum4linux-ng`** : énumération complète (utilisateurs, groupes, partages, politique de mot de passe) via SMB/RPC.
- **`rpcclient`** : requêtes RPC bas niveau (énumération d'utilisateurs, de domaines).

Un workflow courant : `nmap` pour repérer le port 445 → `smbmap`/`enum4linux-ng` pour l'énumération large → `smbclient` pour aller chercher précisément les fichiers.

---

## Récapitulatif express

```bash
# Lister les partages en anonyme
smbclient -L //IP -N

# Se connecter
smbclient //IP/PARTAGE -U user

# En une ligne : télécharger un fichier
smbclient //IP/PARTAGE -N -c 'get fichier.txt'

# Aspirer tout un partage
smbclient //IP/PARTAGE -N -c 'recurse ON; prompt OFF; mget *'
```

Commandes internes clés : `ls`, `cd`, `get`, `mget`, `put`, `recurse ON`, `prompt OFF`, `!cmd`, `exit`.