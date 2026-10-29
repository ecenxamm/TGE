
Pour se connecter à un service AWS, il faut des keys qui servent de creds.
Si besoin, voir [le guide d'installation](#installation).

# Utilisation

```shell
aws configure
```
Cet écran apparaît :
```shell
AWS Access Key ID [None]:
AWS Secret Access Key [None]:
Default region name [None]:
Default output format [None]: 
```
Si il y a un endpoint particulier, ajouter ce paramètre aux commandes d'après :
```shell
--endpoint-url [url-endpoint]
```

Une fois les credentials configurées, voici les requêtes possibles :
```shell
# Lister tes buckets
aws s3 ls

# Lister le contenu d'un bucket
aws s3 ls s3://nom-de-ton-bucket/
aws s3 ls s3://nom-de-ton-bucket/ --recursive

# Télécharger un fichier depuis S3 vers ta machine
aws s3 cp s3://nom-de-ton-bucket/fichier.txt ./fichier.txt

# --- Synchroniser un dossier entier ---
aws s3 sync ./mon-dossier/ s3://nom-de-ton-bucket/mon-dossier/

# Envoyer un fichier depuis ta machine vers S3
aws s3 cp ./mon-fichier.txt s3://nom-de-ton-bucket/

# Supprimer un fichier
aws s3 rm s3://nom-de-ton-bucket/fichier.txt
```

# Installation

```shell
sudo apt install awscli -y
```