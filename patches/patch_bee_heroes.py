import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = "\t\tHero[] allHeroes = Object.FindObjectsOfType<Hero>();"

new = (
    "\t\tHero[] allHeroes = Object.FindObjectsOfType<Hero>();\n"
    "\t\tif (statAttacks <= 6)\n"
    "\t\t{\n"
    "\t\t\tstring hd = string.Empty;\n"
    "\t\t\tfor (int hk = 0; hk < allHeroes.Length; hk++)\n"
    "\t\t\t{\n"
    "\t\t\t\tHero hh = allHeroes[hk];\n"
    "\t\t\t\tif (!(bool)hh)\n"
    "\t\t\t\t{\n"
    "\t\t\t\t\tcontinue;\n"
    "\t\t\t\t}\n"
    "\t\t\t\thd = hd + \" [\" + hh.name\n"
    "\t\t\t\t\t+ \":life=\" + ((bool)hh.life ? hh.life.lifeValue.ToString() : \"null\")\n"
    "\t\t\t\t\t+ \":race=\" + ((bool)hh.spawn ? hh.spawn.race.ToString() : \"nospawn\")\n"
    "\t\t\t\t\t+ \":d=\" + Vector3.Distance(hh.transform.position, center).ToString(\"0.0\") + \"]\";\n"
    "\t\t\t}\n"
    "\t\t\tDebug.Log(string.Concat(\"[Bee] heroes=\", allHeroes.Length, \" myRace=\", info.race, hd));\n"
    "\t\t}\n"
)

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
