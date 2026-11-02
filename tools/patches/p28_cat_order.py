# Fiche de dépouillement : ordre des catégories demandé par l'équipe (Animaux, non cité, à la fin).
import re, sys
p = sys.argv[1]; t = open(p, encoding="utf-8").read()
m = re.search(r'const CATS=\[\n(.*?)\n\];', t, re.S); assert m
rows = {re.search(r'id:"(\w+)"', l).group(1): l for l in m.group(1).split("\n")}
order = ["cast","extras","props","wardrobe","makeup","setdress","vehicles","stunts","sfx","vfx","sound","equipment","animals"]
assert sorted(order) == sorted(rows)
t = t[:m.start(1)] + "\n".join(rows[k] for k in order) + t[m.end(1):]
t = re.sub(r'const APP_VERSION="1\.22\.\d";', 'const APP_VERSION="1.22.1";', t)
open(p, "w", encoding="utf-8").write(t); print("ok", p)
