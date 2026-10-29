Permet de scanner les ports d'une adresse IP.

# Usage

```
nmap [IP]
```

# Paramètres

- `-sU` Scan des ports UDP
- `-sV` Identifie les versions des services
- `-sC` Scanne avec le script Nmap par défaut
- `-A` Tente de détecter la version de l'OS et des services
- `-p-` Scan des 65 535 ports
- `-oN nmap.log` Enregistre dans un log