
# Avec un fichier `id_rsa`
Si l'on possède ce fichier, c'est que l'on a la clé privée du serveur distant auquel l'on souhaiterait se connecter.

Si une passphrase est nécessaire à l'utilisation de la clé, on la récupère comme suit :
```shell
ssh2john id_rsa > hash.txt
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```
Et on l'ajoute au fichier :
```shell
ssh-add id_rsa
```

# Création d'un tunnel SSH
Pour créer un tunnel, on peut faire :
```bash
# -L pour le tunnel | -N pour pas ouvrir de shell
ssh -N -L [port-local]:localhost:[port-serveur] user@10.10.14.158
```
Ainsi, tout ce qui est écouté au `[port-serveur]` sur `10.10.14.158` sera renvoyé sur le `[port-local]` à l'adresse `localhost`.
On peut le faire dans un sens (attaquant > serveur) ou depuis le serveur pour écouter un port local du serveur (serveur > attaquant).