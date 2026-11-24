import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = "\t\t\tif (statAttacks % 3 == 1)\n\t\t\t{\n\t\t\t\tDebug.Log(string.Concat(\"[Bee] dmg-> \", wm.name,"
new = "\t\t\tif (hurt <= 2)\n\t\t\t{\n\t\t\t\tDebug.Log(string.Concat(\"[Bee] dmg-> \", wm.name,"

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
