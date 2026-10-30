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
### Enumération des fichiers
```bash
ls
ls -r   # Pour voir à l'intérieur des dossiers
ls -a   # Montre les fichiers cachés
ls -l   # Donne les détails de permissions
```
### Déplacement
```bash
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
```
### Interagir avec les fichiers
```bash
# Afficher le contenu d'un fichier
cat fichier.txt

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
### Aller plus loin
```bash
# Pour obtenir l'aide d'une commande, la plupart du temps
command --help
# ou
command -h

# Pour obtenir le manuel complet d'une commande
man command
```

