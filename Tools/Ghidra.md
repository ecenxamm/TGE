
> [!Installation]
> Pour l'installation, il suffit d'aller sur https://github.com/NationalSecurityAgency/ghidra/releases et télécharger la dernière version, puis la dézipper. Et voilà !

# Qu'est-ce que c'est ?
Logiciel de reverse engineering publié en 2019 par la NSA pour :
- Analyse de malware - Comprendre leur fonctionnement sans les exécuter
- Vulnérabilités - Analyse de logiciels pour y trouver des failles
- Décompilation - Reconstruction d'un pseudo code C à partir du binaire
Le logiciel est gratuit, contrairement à IDA Pro auquel on doit acheter une licence à 5000€ (malgré le fait que aç soit plus complet).
De plus, la collaboration multi utilisateurs apporte une multitude de add-ons qui font de Ghidra un logiciel tout de même très complet.

# Installation
1. Aller sur github.com/NationalSecurityAgency/ghidra/releases et télécharger la dernière version du fichier ZIP.
2. Le mettre dans le dossier souhaité, et dézipper le fichier.
3. Aller dedans, et lancer le script `ghidraRun`.

Si la version de JDK (Java) n'est pas trouvée, lancer dans un autre terminal :
```shell
sudo apt update
sudo apt install openjdk-25-jdk
```
Pour obtenir un accès conforme à l'ensemble des outils proposés par Ghidra, il faut également installer :
```shell
# PyGhidra


# Debugger
sudo apt install gdb
sudo dpkg --add-architecture i386
sudo apt update
sudo apt install gcc-multilib libc6:i386
```

# Reverse engineering
## Transformation de la source au binaire
1. **Préprocesseur :** Le préprocesseur traite toutes les directives commençant par # : #include, #define, #ifdef. Il substitue les macros et inclut le contenu des headers. Le résultat est encore du C, mais dépouillé de ses directives
2. **Compilation :** Le compilateur proprement dit transforme le C en assembleur. C'est ici que se produisent les optimisations qui rendent le reverse plus difficile : inlining de fonctions, déroulage de boucles, élimination de code mort, réorganisation des instructions.
3. **Assemblage :** L'assembleur transforme le code assembleur textuel en code objet — un fichier `.o` contenant des instructions binaires mais avec des références symboliques non encore résolues.
4. **Édition de liens :** Le linker combine plusieurs fichiers objets, résout les références entre eux et avec les bibliothèques (libc, libpthread...), et produit l'exécutable final.
## Architecture du processeur
Pour comprendre l'assembleur, il faut comprendre comment le code communique en son sein.
- Les données multi-octets sont stockés en *little-endian* (à l'envers) ; l'octet de poids faible arrive en premier.

# Avant Ghidra
Soit un binaire à analyser `kanye`. Avant de l'analyser sur Ghidra, on fait :
```shell
file ./kanye
strings ./kanye     # Cherche pour des strings lisibles
```

# Où trouver des binaires ?
- [crackmes.one](https://crackmes.one)
- [Reversing.Kr](https://reversing.kr)
- [picoCTF](https://picoctf.org)
- [pwn.college](https://pwn.college)
- [HackTheBox](https://app.hackthebox.com/home)
- [Root-Me](https://root-me.org)