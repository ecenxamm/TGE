```bash
# Envoie une requête GET à l'URL spécifiée
curl [url]

# Silent mode ; n'affiche pas le in-progress, les avertissements... Ne montre que la réponse du serveur
curl -s [url]
```

# POST
```bash
# Evnoie une requête POST
curl [url] -X POST

# Pour passer des paramètres avec la requête POST
curl [url] -X POST -d "param1=sample"
```
