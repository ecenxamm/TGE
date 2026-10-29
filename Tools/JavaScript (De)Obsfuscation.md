# Definition
* **Obfuscation :** Le fait de rendre un code (par exemple JavaScript) illisible ou difficilement compréhensible pour l'homme. Le but étant de protéger les codes qui s'exécutent en clair côté client, ou de détourner des protections analysant des codes. Le code offusqué aura exactement la même fonction, mais peut devenir plus lent.
* **Deobfuscation :** Le fait d'inverser le processus d'offusquation, afin d'analyser plus simplement un code.
# Links
## Obsfuscation

| Site                                                                 | Remarques                                                                                   |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [Obfuscator.io](https://obfuscator.io/)                              | Plus d'options, à préférer                                                                  |
| [Toptal](https://www.toptal.com/developers/javascript-minifier)      | Minifier, le code sera comprimé en une seule ligne, sans modification autre.                |
| [BeautifyTools](https://beautifytools.com/javascript-obfuscator.php) | Basique, pour des besoins simples                                                           |
| [JSFuck](https://jsfuck.com/)                                        | `[]]][([][[]]+[])[+!+[]]+(![]+[])[+!+[]]+((+)`<br>Exécution de code plus lente              |
| [JJEncode](https://utf-8.jp/public/jjencode.html)                    | `$=~[];$={___:++$,$$$$:(![]+"")[$]`<br>Exécution de code encore plus lente                  |
| [AAEncode](https://utf-8.jp/public/aaencode.html)                    | `ﾟωﾟﾉ= /｀ｍ´）ﾉ ~┻━┻   //*´∇｀*/ ['_']; o=(ﾟｰﾟ)  =_=3;`<br>Exécution de code encore plus lente |
## Deobfuscation
Les outils du navigateur (inspecter) ont déjà de bons outils pour embellir le code minifié.

| Site                                            | Remarques                                                                 |
| ----------------------------------------------- | ------------------------------------------------------------------------- |
| [UnPacker](https://matthewfl.com/unPacker.html) | Déminifie, et rassemble des morceaux de codes pour le rendre plus lisible |
| [Prettier](https://prettier.io/playground/)     | Pour code minifié, présente quelques options                              |
| [Beautifier](https://beautifier.io/)            | Pour code minifié, présente quelques options                              |
