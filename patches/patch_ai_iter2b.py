import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = (
    "\t\tbool hurtRecently = (Time.time - lastDamageTime) < 2f;\n"
    "\t\tif (myRate <= 0.25f || (myRate < lowHealthRate && hurtRecently))\n"
)
new = (
    "\t\tbool hurtRecently = (Time.time - lastDamageTime) < 2f;\n"
    "\t\t// 有己方小兵在前面顶着时敢打敢推；没掩护才按原阈值撤。\n"
    "\t\t// 实测缺这条时，AI 到中场遇到敌方兵线就撤，永远推不到塔下。\n"
    "\t\tint coverAllies = CountAlliesInRange(9f);\n"
    "\t\tfloat retreatHp = (coverAllies >= 2) ? (lowHealthRate * 0.7f) : lowHealthRate;\n"
    "\t\tif (myRate <= 0.2f || (myRate < retreatHp && hurtRecently))\n"
)

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)

# 拆塔搜索半径
s = s.replace("public float siegeSearchRange = 22f;",
              "public float siegeSearchRange = 26f;", 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
