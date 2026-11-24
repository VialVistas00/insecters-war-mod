import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = """			AttackSetting st = new AttackSetting();
			st._physicsAttack = dmg;
			st._magicAttack = 0;
			wm.injure(new AttackInfo
			{
				attackSetting = st,
				attackTypeIndex = src.attackTypeIndex,
				characterInfo = info,
				harmType = Life.HarmType.other
			});
			hurt++;"""

new = """			AttackSetting st = new AttackSetting();
			st._physicsAttack = dmg;
			st._magicAttack = 0;
			int bLife = (bool)wm.life ? wm.life.lifeValue : -1;
			int bGuard = (bool)wm.life ? wm.life.guardValue : -1;
			wm.injure(new AttackInfo
			{
				attackSetting = st,
				attackTypeIndex = src.attackTypeIndex,
				characterInfo = info,
				harmType = Life.HarmType.other
			});
			int aLife = (bool)wm.life ? wm.life.lifeValue : -1;
			int aGuard = (bool)wm.life ? wm.life.guardValue : -1;
			if (statAttacks % 3 == 1)
			{
				Debug.Log(string.Concat("[Bee] dmg-> ", wm.name,
					" life ", bLife, "->", aLife,
					" guard ", bGuard, "->", aGuard,
					" atk=", dmg, " type=", src.attackTypeIndex,
					" myRace=", info.race,
					" tgtRace=", (bool)wm.life && wm.life.characterInfo != null ? wm.life.characterInfo.race.ToString() : "-"));
			}
			hurt++;"""

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
