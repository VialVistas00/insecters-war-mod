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


# 1) 提高拆塔门槛
must("""	public int siegeMinAllies = 1;""",
     """	public int siegeMinAllies = 2;""",
     "siegeMinAllies 2")

must("""	public float siegeMinHealthRate = 0.55f;""",
     """	public float siegeMinHealthRate = 0.72f;

	/// <summary>贴到敌方建筑这么近就算进入"塔下危险区"。</summary>
	public float siegeDangerRange = 7f;

	/// <summary>危险区里己方小兵少于这个数就撤。</summary>
	public int siegeDangerAllies = 2;""",
     "danger fields")

# 2) 危险区判定：贴脸敌方建筑又没兵顶着 → 先撤，别送
must("""		// 3.5) 配合兵线拆塔：有己方小兵顶着 + 血量健康 + 敌方建筑在附近
		ScanSiegeTarget();""",
     """		// 3.5) 配合兵线拆塔：有己方小兵顶着 + 血量健康 + 敌方建筑在附近
		ScanSiegeTarget();

		// 3.4) 危险区：贴到敌方建筑跟前、又没有小兵顶着、还在挨打 → 立刻撤
		//      （之前 AI 会一路顶到基地前被打死，就是缺这条）
		if ((bool)siegeTarget)
		{
			float dB = Vector3.Distance(base.transform.position, siegeTarget.position);
			if (dB <= siegeDangerRange)
			{
				int alliesNear = CountAlliesInRange(siegeDangerRange + 2f);
				bool takingHit = (Time.time - lastDamageTime) < 1.2f;
				if (alliesNear < siegeDangerAllies && (takingHit || SelfHealthRate() < 0.85f))
				{
					if (!IsAtHome())
					{
						mode = AIMode.retreat;
						return;
					}
				}
			}
		}""",
     "danger check")

# 3) 拆塔途中掉到 60% 血就撤
must("""		nextSiegeAttackTime = Time.time + siegeAttackInterval;""",
     """		// 拆塔途中血量掉到 60% 以下、而且还在挨打 → 放弃，别送
		if (SelfHealthRate() < 0.6f && (Time.time - lastDamageTime) < 1.5f)
		{
			siegeTarget = null;
			siegeTargetLife = null;
			return;
		}
		nextSiegeAttackTime = Time.time + siegeAttackInterval;""",
     "abort when low")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
