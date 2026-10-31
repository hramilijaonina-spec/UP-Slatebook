# Source unique : up-slatebook/index.html.
# Ce script en tire les trois copies, pour ne plus rien corriger en double :
#   1. UP Slatebook, site GitHub Pages  : index.html (la source elle-même) + sw.js à la bonne version
#   2. UP Slatebook, artefact Claude    : <ARTEFACT>/index.html (sans Firebase) + vendor/
#   3. Dydz Studio, site GitHub Pages   : <DYDZ>/index.html (nom, couleurs, assistant Dydz) + adapter.js, sw.js, vendor/
# Usage : python3 tools/build_all.py [--artifact DIR] [--dydz DIR]
import argparse, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
UP = os.path.dirname(HERE)
ap = argparse.ArgumentParser()
ap.add_argument("--artifact", default=os.path.join(os.path.dirname(UP), "slatebook"))
ap.add_argument("--dydz", default=os.path.join(os.path.dirname(UP), "ddc-breakdown"))
a = ap.parse_args()

src = open(os.path.join(UP, "index.html"), encoding="utf-8").read()
ver = re.search(r'const APP_VERSION="([^"]+)"', src).group(1)

def set_sw(path, prefix, version, name):
    t = open(path, encoding="utf-8").read()
    t = re.sub(r'const VERSION = APP \+ "-v[^"]*";', 'const VERSION = APP + "-v' + version + '";', t)
    t = re.sub(r'^/\* [^—\n]+ — service worker', '/* ' + name + ' — service worker', t)
    t = re.sub(r'^const APP = "[^"]*";', 'const APP = "' + prefix + '";', t, flags=re.M)
    open(path, "w", encoding="utf-8").write(t)

# 1. GitHub UP
set_sw(os.path.join(UP, "sw.js"), "up", ver, "UP Slatebook")
print("UP Slatebook", ver)

# 2. artefact : mêmes pages, sans Firebase ni fichiers du site (manifeste, icônes)
if a.artifact:
    art = src
    for pat in [r'<script src="https://www\.gstatic\.com[^"]*"></script>\n', r'<script src="config\.js"></script>\n',
                r'<script src="adapter\.js"></script>\n', r'<link rel="manifest"[^>]*>\n', r'<link rel="icon"[^>]*>\n',
                r'<link rel="apple-touch-icon"[^>]*>\n', r'<meta name="apple-mobile-web-app-[^>]*>\n']:
        art, n = re.subn(pat, "", art)
    assert "firebase" not in art.lower().split("<style>")[0] and "adapter.js" not in art
    os.makedirs(a.artifact, exist_ok=True)
    open(os.path.join(a.artifact, "index.html"), "w", encoding="utf-8").write(art)
    shutil.copytree(os.path.join(UP, "vendor"), os.path.join(a.artifact, "vendor"), dirs_exist_ok=True)
    print("artefact ->", a.artifact)

# 3. Dydz Studio
if a.dydz and os.path.isdir(a.dydz):
    b = os.path.join(a.dydz, "tools", "build_from_up.py")
    out = subprocess.run([sys.executable, b, os.path.join(UP, "index.html"), os.path.join(a.dydz, "index.html"), "gh"], capture_output=True, text=True)
    print(out.stdout.strip() or out.stderr.strip())
    if out.returncode: sys.exit(out.returncode)
    dv = re.search(r'const APP_VERSION="([^"]+)"', open(os.path.join(a.dydz, "index.html"), encoding="utf-8").read()).group(1)
    ad = open(os.path.join(UP, "adapter.js"), encoding="utf-8").read()
    ad = ad.replace("/* DDC Breakdown — couche autonome.", "/* Dydz Studio (ex-DDC Breakdown) — couche autonome.").replace('CFG.appName||"DDC Breakdown"', 'CFG.appName||"Dydz Studio"')
    open(os.path.join(a.dydz, "adapter.js"), "w", encoding="utf-8").write(ad)
    shutil.copy(os.path.join(UP, "sw.js"), os.path.join(a.dydz, "sw.js"))
    set_sw(os.path.join(a.dydz, "sw.js"), "ddc", dv, "Dydz Studio")
    shutil.copytree(os.path.join(UP, "vendor"), os.path.join(a.dydz, "vendor"), dirs_exist_ok=True)
    print("Dydz Studio", dv, "->", a.dydz)
