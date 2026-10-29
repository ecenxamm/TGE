# User flag

```bash
$ nmap 10.129.76.61 -sCV
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
80/tcp   open  http    nginx 1.24.0 (Ubuntu)
|_http-server-header: nginx/1.24.0 (Ubuntu)
|_http-title: Did not follow redirect to http://api.htb-airport.htb/
8081/tcp open  http    Uvicorn
|_http-title: "Site doesn't have a title (application/json)."
|_http-server-header: uvicorn
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```
On a le service SSH au port 22, un serveur HTTP nginx sur le port 80 et un serveur HTTP Uvicorn sur le port 8081 (serveur web Python).
D'abord le port 80 : il nous emmène sur `http://api.htb-airport.htb`, à enregistrer dans `/etc/hosts`. Voici ce qui nous est renvoyé sur la page racine :
```json
{
	"service":"terminal-edge-gateway",
	"status":"operational",
	"version":"1.0.0",
	"node":"tg-edge-01",
	"region":"eu-central-1",
	"uptime":"0d 0h 5m 37s",
	"upstreams": {
		"flight-data-service":"UP",
		"boarding-control":"UP",
		"gate-assignment":"UP",
		"passenger-manifest":"UP"
	},
	"message":"All terminal gateway systems are operational.",
	"timestamp":"2026-10-15T08:19:27.919495498Z"
}
```

Quant au port 8081, il nous renvoie sur la page racine :
```json
{
  "service": "AIDX flight-leg ingest",
  "what": "Accepts AIDX XML for processing",
  "how": {
    "method": "POST",
    "path": "/feeds/aidx",
    "content_type": "application/xml",
    "max_bytes": 262144
  },
  "required_elements": [
    "IATA_AIDX_FlightLegNotifRQ",
    "Originator",
    "FlightLeg",
    "LegIdentifier"
  ],
  "note": "Ingest does not parse. Full validation happens downstream.",
  "health": "GET /health"
}
```
On fait donc ce qui est écrit :
```json
// GET /health
{
	"status":"ok",
	"service":"AIDX flight-leg ingest",
	"raw_topic":"aidx.flightleg.raw.v1"
}

// Il reste la requête POST, trop vague pour l'instant
```

Après ces réponses, on scanne les deux sites obtenus à la recherche d'autres failles :
```bash
$ dirb http://api.htb-airport.htb -X .php,,.html
+ http://api.htb-airport.htb/error (CODE:500|SIZE:68)    # Error
+ http://api.htb-airport.htb/health (CODE:200|SIZE:15)   # {"status":"Up"}
+ http://api.htb-airport.htb/status (CODE:200|SIZE:362)  # Message ci-dessus

$ dirb http://10.129.76.61:8081 -X .php,,.html
+ http://10.129.76.61:8081/docs (CODE:200|SIZE:1021) # <-- Le site qu'on cherche
+ http://10.129.76.61:8081/health (CODE:200|SIZE:86)     # Message de statut
```

![](assets/Pasted%20image%2020261015104020.png)
Il y a un bouton "Try it out" pour chaque requête, ce qui nous permet d'envoyer nos requêtes aux URL proposées. Ce qui nous intéresse ici est la requête `POST /feeds/aidx`.
On a juste en-dessous du titre l'URL `/openapi.json`, qui renvoie les informations suivantes :
```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "AIDX flight-leg ingest",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "get": {
        "summary": "Root",
        "operationId": "root__get"
        }
      }
    },
    "/health": {
      "get": {
        "summary": "Health",
        "operationId": "health_health_get"
        }
      }
    },
    "/feeds/aidx": {
      "post": {
        "summary": "Ingest",
        "operationId": "ingest_feeds_aidx_post"
        }
      }
    }
  }
}    // Non exhaustif des paramètres pour des raisons de lisibilité
```

On essaie une attaque XXE.
```bash
curl -X 'POST' 'http://10.129.76.61:8081/feeds/aidx' \
	 -H 'accept: */*' \
	 -d ''
```



