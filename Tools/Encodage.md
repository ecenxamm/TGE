# Base64
L'encodage en Base64 est généralement utilisé pour réduire le nombre de caractères spéciaux utilisés. Chaque caractère est passé en encodage binaire, puis est rassemblé afin de n'avoir que les caractères `a-z`, `A-Z`, `0-9`, `/` et `+`.
Quand il y a trop de bits par rapport au contenu à encoder, l'encodage rajoute un `=`.

Chaque caractère en base64 est encodé avec 6 bits. Ainsi, quand on encode un texte en ASCII (8 bits), on obtient cette conversion :
<table style="text-align:center; font-family:monospace; font-size:0.7em; border-collapse:collapse; table-layout:fixed; width:100%;">
  <tr>
    <td colspan="8" style="border:1px solid #888;"><strong>S</strong></td>
    <td colspan="8" style="border:1px solid #888;"><strong>a</strong></td>
    <td colspan="8" style="border:1px solid #888;"><strong>l</strong></td>
    <td colspan="8" style="border:1px solid #888;"><strong>u</strong></td>
    <td colspan="8" style="border:1px solid #888;"><strong>t</strong></td>
    <td style="border:1px solid #888;"></td>
  </tr>
  <tr>
    <td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td>
    <td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td>
    <td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">0</td>
    <td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td>
    <td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">1</td><td style="border:1px solid #888;">0</td><td style="border:1px solid #888;">0</td>
    <td style="border:1px solid #888;"></td>
  </tr>
  <tr>
    <td colspan="6" style="border:1px solid #888;"><strong>U</strong></td>
    <td colspan="6" style="border:1px solid #888;"><strong>2</strong></td>
    <td colspan="6" style="border:1px solid #888;"><strong>F</strong></td>
    <td colspan="6" style="border:1px solid #888;"><strong>s</strong></td>
    <td colspan="6" style="border:1px solid #888;"><strong>d</strong></td>
    <td colspan="6" style="border:1px solid #888;"><strong>X</strong></td>
    <td colspan="4" style="border:1px solid #888;"><strong>Q</strong></td>
    <td style="border:1px solid #888;"><strong>=</strong></td>
  </tr>
</table>
On voit que pour le dernier caractère, Q est encodé avec seulement 4 bits, il y a donc le `=` précisant la fin du message encodé.
```bash
# Encoder en base64
base64 [txt]
```

```bash
# Désencoder
base64 -d [encoded-txt]
```

# Hex
L'encodage en hexadécimal consiste à encoder chaque caractère en fonction de sa valeur hexédécimale dans la table ASCII, ainsi `a` devient `61`, `b` devient `62`...

```bash
# Encoder en hex
xxd -p [txt]
```

```bash
# Désencoder
xxd -p -r [hex-txt]
```

# RotX (Code César)
Consiste à décaler chaque lettre de l'alphabet d'un décalage fixe X. Le plus courant est le Rot13.

```bash
# Encoder en Rot13
echo [txt] | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

```bash
# Désencoder (2x 13 = 26, un tour complet)
echo [txt] | tr 'A-Za-z' 'N-ZA-Mn-za-m'
```

```bash
# Encoder/désencoder avec un autre décalage
echo [txt] | tr 'A-Za-z' 'E-ZA-De-za-d'
echo [txt] | tr 'E-ZA-De-za-d' 'A-Za-z'
```

