import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\IwSelfCheck.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must_replace(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


must_replace(
    """		int totalSkill = 0;
		int totalGank = 0;
		int totalStuck = 0;""",
    """		int totalSkill = 0;
		int totalGank = 0;
		int totalStuck = 0;
		int siegeNow = 0;
		int totalSiege = 0;""",
    "counters")

must_replace(
    """			if (ai.mode == HeroAI.AIMode.roam)
			{
				roamNow++;
			}""",
    """			if (ai.mode == HeroAI.AIMode.roam)
			{
				roamNow++;
			}
			if (ai.mode == HeroAI.AIMode.siege)
			{
				siegeNow++;
			}
			totalSiege += ai.statSiegeHits;""",
    "collect siege")

must_replace(
    """		pSb.AppendLine(string.Concat(TAG, " 即时: 放技能=", skillNow, " 追击=", gankNow,
			" 游走=", roamNow, " 自救中=", stuckNow));""",
    """		pSb.AppendLine(string.Concat(TAG, " 即时: 放技能=", skillNow, " 追击=", gankNow,
			" 游走=", roamNow, " 拆塔中=", siegeNow, " 自救中=", stuckNow));""",
    "instant line")

must_replace(
    """		pSb.AppendLine(string.Concat(TAG, " 累计: 技能释放=", totalSkill,
			" 进入追击=", totalGank, " 脱困自救=", totalStuck));""",
    """		pSb.AppendLine(string.Concat(TAG, " 累计: 技能释放=", totalSkill,
			" 进入追击=", totalGank, " 拆塔出手=", totalSiege, " 脱困自救=", totalStuck));""",
    "total line")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
