import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\AirDropAnimation.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


must(
    """		if (minBlastRadius <= 0.05f)
		{
			minBlastRadius = 3.2f;
		}
		if (forceDamage <= 0.05f)
		{
			forceDamage = 45f;
		}""",
    """		if (minBlastRadius <= 0.05f)
		{
			minBlastRadius = 5f;
		}
		if (forceDamage <= 0.05f)
		{
			forceDamage = 120f;
		}""",
    "defaults")

must(
    """		int mask = damageMask;
		if (mask == 0)
		{
			if (characterInfo != null && characterInfo.race != Race.eNone)
			{
				Race enemyRace = PlayerInfo.getAdversaryRace(characterInfo.race);
				mask = (int)PlayerInfo.getRaceObjectValue(enemyRace);
			}
			else
			{
				mask = -1;
			}
		}""",
    """		// 掩码：把预制体配的 damageMask 和"敌方单位+建筑"掩码合并。
		// 之前只用 damageMask（=512，仅一层），敌人站在另一层就完全打不到。
		int mask = damageMask;
		if (characterInfo != null && characterInfo.race != Race.eNone)
		{
			Race enemyRace = PlayerInfo.getAdversaryRace(characterInfo.race);
			mask |= (int)PlayerInfo.getRaceObjectValue(enemyRace);
		}
		if (mask == 0)
		{
			mask = -1;
		}""",
    "mask merge")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
