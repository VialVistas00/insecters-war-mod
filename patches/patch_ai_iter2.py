import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 有己方小兵掩护时，允许更低的血量继续顶线（这是"跟兵线推塔"的关键）
must("""		float hurtRecently = (Time.time - lastDamageTime) < 2f;
		if (myRate <= 0.25f || (myRate < lowHealthRate && hurtRecently))""",
     """		float hurtRecently = (Time.time - lastDamageTime) < 2f;
		// 有己方小兵在前面顶着时，敢打敢推；没有掩护才按原来的阈值撤。
		// 实测没这条时，AI 一到中场遇到敌方兵线就撤，永远推不到塔下。
		int coverAllies = CountAlliesInRange(9f);
		float retreatHp = (coverAllies >= 2) ? (lowHealthRate * 0.7f) : lowHealthRate;
		if (myRate <= 0.2f || (myRate < retreatHp && hurtRecently))""",
     "cover retreat")

# 拆塔搜索半径略放宽
must("""	public float siegeSearchRange = 22f;""",
     """	public float siegeSearchRange = 26f;""",
     "siege range")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
