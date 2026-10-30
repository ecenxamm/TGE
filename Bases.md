# Linux
## Structure
```
|- bin
|- etc
  |- passwd : Liste des utilisateurs
  |- shadow : Liste des utilisateurs et leurs mdp hashés
|- home
  |- jean.d : L'emplacement de la session de jean.d
  |- john.doe
|- root : L'emplacement de la session du compte root
|- sys
|- tmp : Dossier de fichiers temporaires ; bien aimé des hackers, parfois des choses intéressantes
|- usr
```
## Commandes
### Exploration des fichiers
```bash
# Enumération des fichiers
ls
ls -r   # Pour voir à l'intérieur des dossiers
ls -a   # Montre les fichiers cachés
ls -l   # Donne les détails de permissions

# Quel utilisateur je suis ?
whoami

# Où je me trouve ?
pwd

# Se déplacer dans un dossier
cd nom-dossier
cd dossier/sous-dossier
cd ..    # Dossier parent

# Créer un dossier
mkdir nouveau-dossier

# Parcourir une arborescence de fichier
find /home/kali -name "*.txt"   # Cherche tous les fichiers .txt
find /home/kali -name "mdp"     # Cherche tous les fichiers qui s'appellent mdp
find /home/kali -name "*mdp*"   # Cherche tous les fichiers qui contiennent mdp dans leur nom
find . -size +10M               # Plus de 10 Mo (-10M = moins de 10 Mo)
find / -user root               # Appartenant à root

# Trouver un terme dans un texte
grep root mdp.txt           # Cherche dans mdp.txt le terme root
grep root mdp.txt -a2 -b5   # Affiche les 2 lignes précédents root et les 5 lignes après
```
### Interagir avec les fichiers
```bash
# Afficher le contenu d'un fichier
cat fichier.txt

# Affiche les premières lignes d'un fichier
head fichier.txt

# Pour modifier un fichier (prenez la commande que vous préférez)
vim fichier.txt
nano fichier.txt     # Crée fichier.txt si il n'existe pas

# Déplacer un fichier
mv fichier /analyse/fichier   # Déplace fichier dans le dossier analyse
mv /tmp/mdp.txt /home/john.doe/mdp.txt

# Renommer un fichier
mv fichier nouveau-nom        # On déplace le même contenu dans un fichier avec un nouveau nom

# Supprimer un fichier
rm fichier
rm -rf dossier   # Supprime un dossier et tout ce qu'il contient (-f : force / -r : récursif)

# Connaître le type d'un fichier et de son contenu
file fichier
```
### Connexions à distance
```bash
# Ouvrir un terminal à distance
ssh [utilisateur]@[adresse] -p 22   # Le port SS par défaut est 22
# Exemple
ssh user1@10.10.15.158 -p 2220

# Terminer une connexion à distance
exit

# Télécharger / téléverser un fichier
scp [fichier] [destination]
# Exemple - On rentre l'addresse avec user@adresse, puis on mets : et le chemin vers le fichier à télécharger / téléverser
scp user1@10.10.15.158:/home/user1/mdps.txt mdps.txt  # Du serveur à notre machine
scp virus user1@10.10.15.158:/tmp/virus               # De notre machine au serveur
```
### Sudo
Sudo est une commande réservée à un certain groupe d'utilisateurs, appelés les **sudoers**. Mise au début d'une commande, elle permet au sudoer de lancer la commande avec les droits administrateurs.
Il y a des utilisateurs qui peuvent utiliser sudo sur toutes les commandes, et parfois seulement sur certaines commandes. Lorsque les droits sont mal gérés, on peut utiliser ces commandes en root pour escalader nos privilèges, et donc obtenir des droits complets sur la machine à partir d'une session utilisateur.
```bash
sudo cat /etc/shadow

# La commande su permet d'ouvrir une autre session sur la même machine
su user2       # Nécessite le mot de passe de user2
sudo su user2  # Nécessite le mot de passe de la session actuelle, qui est sudoer
sudo su        # Ouvre un terminal root
```
### Commandes complexes
```bash
# Renvoie (fais un écho) le texte écrit
echo texte

# Pour rentrer une sortie d'une commande 1 en tant qu'entrée d'une commande 2, on fait
command1 | command2
# Par exemple
echo "avion bateau char" | grep char    # Cherche le mot char dans la chaîne passée en entrée
cat /etc/shadow | grep user             # Renvoie la ligne du hash correspondant à user

# Enregistrer la sortie d'une commande dans un fichier
nmap 10.10.15.158 > sortie-nmap    # Ecrase les données initiales
nmap 10.10.15.158 >> sortie-nmap   # Ajoute à la suite

# xargs - Effectue une commande avec plusieurs arguments
echo fichier1 fichier2 | xargs cat   # Affiche le contenu de fichier1 et fichier2
find . | xargs file                  # Donne le type de tous les fichiers du dossier actuel
```
### Aller plus loin
```bash
# Pour obtenir l'aide d'une commande, la plupart du temps
command --help
# ou
command -h

# Pour obtenir le manuel complet d'une commande
man command
```