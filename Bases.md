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
$ ls
$ ls -r   # Pour voir à l'intérieur des dossiers
$ ls -a   # Montre les fichiers cachés
```
### Déplacement
```bash
# Quel utilisateur je suis ?
$ whoami

# Où je me trouve ?
$ pwd

# Se déplacer dans un dossier
$ cd nom-dossier
$ cd dossier/sous-dossier
$ cd ..    # Dossier parent

# Créer un dossier
$ mkdir nouveau-dossier
```
### Modifier les fichiers
```bash
# Pour modifier un fichier (prenez celui que vous préférez)
$ vim fichier.txt
$ nano fichier.txt     # Crée fichier.txt si il n'existe pas

# Déplacer un fichier
$ mv fichier /analyse/fichier   # Déplace fichier dans le dossier analyse
$ mv /tmp/mdp.txt /home/john.doe/mdp.txt

# Renommer un fichier
$ mv fichier nouveau-nom        # On déplace le même contenu dans un fichier avec un nouveau nom

# Supprimer un fichier
$ rm fichier
$ rm -rf dossier   # Supprime un dossier et tout ce qu'il contient (-f : force / -r : récursif)
```


