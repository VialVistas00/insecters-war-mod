import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must_replace(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 在 siege 判断处加诊断输出
must_replace(
    """		// 3.5) 配合兵线拆塔：有己方小兵顶着 + 血量健康 + 敌方建筑在附近
		ScanSiegeTarget();
		if ((bool)siegeTarget && (bool)siegeTargetLife
			&& SelfHealthRate() >= siegeMinHealthRate
			&& CountAlliesInRange(siegeSearchRange) >= siegeMinAllies)
		{
			mode = AIMode.siege;
			return;
		}""",
    """		// 3.5) 配合兵线拆塔：有己方小兵顶着 + 血量健康 + 敌方建筑在附近
		ScanSiegeTarget();
		int lSiegeAllies = 0;
		if ((bool)siegeTarget && (bool)siegeTargetLife)
		{
			lSiegeAllies = CountAlliesInRange(siegeSearchRange);
			if (SelfHealthRate() >= siegeMinHealthRate && lSiegeAllies >= siegeMinAllies)
			{
				mode = AIMode.siege;
				return;
			}
			// 诊断：每 3 秒打一次，说明"看到建筑但条件不满足"
			if (Time.time >= nextSiegeDiagTime)
			{
				nextSiegeDiagTime = Time.time + 3f;
				Debug.Log(string.Concat("[AI] siege blocked hp=", SelfHealthRate().ToString("0.00"),
					" need>=", siegeMinHealthRate,
					" allies=", lSiegeAllies, " need>=", siegeMinAllies,
					" target=", siegeTarget.name,
					" dist=", Vector3.Distance(base.transform.position, siegeTarget.position).ToString("0.0")));
			}
		}
		else if (Time.time >= nextSiegeDiagTime)
		{
			nextSiegeDiagTime = Time.time + 5f;
			Debug.Log("[AI] siege none: no enemy building within " + siegeSearchRange);
		}""",
    "siege diag")

must_replace(
    """	private float nextSiegeAttackTime;""",
    """	private float nextSiegeAttackTime;

	private float nextSiegeDiagTime;""",
    "diag field")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
