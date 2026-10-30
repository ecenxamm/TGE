# Bandit0
```bash
$ ssh bandit0@bandit.labs.overthewire.org -p 2220
bandit0

$ ls
readme

$ cat readme
Congratulations on your first steps into the bandit game!!
Please make sure you have read the rules at https://overthewire.org/rules/
If you are following a course, workshop, walkthrough or other educational activity,
please inform the instructor about the rules as well and encourage them to
contribute to the OverTheWire community so we can keep these games free!

The password you are looking for is: 6y2kwnwK6grgvwvpvLaa2T1cpFEKOhNR
```
# Bandit1
```bash
$ ssh bandit1@bandit.labs.overthewire.org -p 2220
6y2kwnwK6grgvwvpvLaa2T1cpFEKOhNR

$ ls
-

$ cat "./-"
PK8fYLZg2hnHSz83plBL1iEPKdD3QToB
```
# Bandit2
```bash
$ ssh bandit2@bandit.labs.overthewire.org -p 2220
PK8fYLZg2hnHSz83plBL1iEPKdD3QToB

$ ls
--spaces in this filename--

$ cat "./--spaces in this filename--"
7ZZ2LFrykP2zEyvBl4m3clcL7tGYJPME
```
# Bandit3
```bash
$ ssh bandit3@bandit.labs.overthewire.org -p 2220
7ZZ2LFrykP2zEyvBl4m3clcL7tGYJPME

$ ls
inhere

$ cd inhere
$ ls -a
.  ..  ...Hiding-From-You

$ cat ...Hiding-From-You 
xzTXq1rDJQVVAzdv5cHq1TQytTWufAMq
```
# Bandit4
```bash
$ ssh bandit4@bandit.labs.overthewire.org -p 2220
xzTXq1rDJQVVAzdv5cHq1TQytTWufAMq

# Renvoie une liste des fichiers
$ find .
.
./-file06
./-file05
./-file09
./-file02
./-file08
./-file00
./-file07
./-file03
./-file01
./-file04

# Le symbole | prend la sortie de la commande à gauche, et l'injecte comme argument dans la commande à droite
# Ici, xargs file fait la commande file sur tous les fichiers renvoyés par find .
$ find . | xargs file
.:         directory
./-file06: data
./-file05: data
./-file09: Non-ISO extended-ASCII text, with no line terminators
./-file02: Non-ISO extended-ASCII text, with NEL line terminators, with escape sequences
./-file08: data
./-file00: data
./-file07: ASCII text
./-file03: data
./-file01: data
./-file04: data

$ cat "./-file07"
6C7h9GD8M6ai5nr7wo1RonrzFjj9yIrG

# On aurait pu les tester un par un, mais c'est loin d'être optimal...
```




