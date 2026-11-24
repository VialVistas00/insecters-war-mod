import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = (
    "\t\t\tCollider c = hits[i];\n"
    "\t\t\tif (!(bool)c || c.isTrigger)\n"
    "\t\t\t{\n"
    "\t\t\t\tcontinue;\n"
    "\t\t\t}\n"
)
new = (
    "\t\t\tCollider c = hits[i];\n"
    "\t\t\t// 不能因为 isTrigger 就跳过 —— 英雄单位的碰撞体正是 trigger，\n"
    "\t\t\t// 之前这一句把玩家整个过滤掉了，表现就是「贴脸却完全打不到」。\n"
    "\t\t\tif (!(bool)c)\n"
    "\t\t\t{\n"
    "\t\t\t\tcontinue;\n"
    "\t\t\t}\n"
)

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
