import io
import json
import os
import sys
import glob

sys.stdout.reconfigure(encoding="utf-8")

keys = ["DefenseTower", "ArmyBase", "AntBase", "BeeBase", "Stronghold",
        "AntSoldier", "BeeSoldier", "AntFactory", "BeeFactory", "AntHero1"]

for d in sorted(glob.glob(r"Scene/沙漠小镇*")):
    f = os.path.join(d, "map.map.iw")
    if not os.path.exists(f):
        print(d, "no map.map.iw")
        continue
    raw = io.open(f, encoding="utf-8", errors="replace").read()
    out = {}
    for k in keys:
        c = raw.count('"' + k + '"')
        if c:
            out[k] = c
    print(os.path.basename(d), "->", out)
