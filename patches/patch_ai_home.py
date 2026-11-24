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


# 1) 新增：推进锚点 + 在家停留计时
must_replace(
    """	private float nextSiegeDiagTime;""",
    """	private float nextSiegeDiagTime;

	// ---- 防赖家（第二版）----

	/// <summary>在己方出生点附近连续停留了多久。</summary>
	private float homeStayTime;

	/// <summary>在家停留超过这个秒数就强制外出。</summary>
	public float homeStayLimit = 4f;

	/// <summary>推进锚点缓存（敌方出生点 / 最远据点）。</summary>
	private Transform pushAnchor;

	private float nextAnchorScanTime;""",
    "anchor fields")

# 2) 推进锚点查找
must_replace(
    """	/// <summary>自己是否在己方出生点附近（=赖在家里）。</summary>""",
    """	/// <summary>
	/// 推线锚点：找不到敌方出生点时（比如对面全是同族 AI），
	/// 退化为"离自己最远的据点"，绝不再回自己家。
	/// </summary>
	private Transform FindPushAnchor()
	{
		if ((bool)pushAnchor && Time.time < nextAnchorScanTime)
		{
			return pushAnchor;
		}
		nextAnchorScanTime = Time.time + 4f;

		Transform es = FindEnemySpawn();
		if ((bool)es)
		{
			pushAnchor = es;
			return pushAnchor;
		}

		// 退化：最远的据点
		Transform best = null;
		float bestDist = 0f;
		System.Collections.Generic.IList<Stronghold> all = StrongholdRegistry.All;
		for (int i = 0; i < all.Count; i++)
		{
			Stronghold sh = all[i];
			if (!(bool)sh)
			{
				continue;
			}
			float d = Vector3.Distance(base.transform.position, sh.transform.position);
			if (d > bestDist)
			{
				bestDist = d;
				best = sh.transform;
			}
		}
		pushAnchor = best;
		return pushAnchor;
	}

	/// <summary>自己是否在己方出生点附近（=赖在家里）。</summary>""",
    "FindPushAnchor")

# 3) Update：在家停留计时 + 强制外出
must_replace(
    """		UpdateMode();
		TrackModeChange();""",
    """		UpdateMode();
		TrackModeChange();

		// 在家连续待太久 → 强制外出（兜住所有回家原因）
		if (IsAtHome())
		{
			homeStayTime += Time.deltaTime;
			if (homeStayTime > homeStayLimit)
			{
				Transform anchor = FindPushAnchor();
				if ((bool)anchor)
				{
					front = anchor;
					mode = AIMode.pushLane;
					homeStayTime = 0f;
				}
			}
		}
		else
		{
			homeStayTime = 0f;
		}""",
    "home stay force out")

# 4) front 为空的兜底：不再回自己家
must_replace(
    """			if (!(bool)front)
			{
				// 找不到"前线"时，朝敌方出生点推进，而不是回自己家
				front = FindEnemySpawn();
			}
			if (!(bool)front && (bool)spawn)
			{
				front = spawn;
			}""",
    """			if (!(bool)front)
			{
				// 找不到"前线"时朝推进锚点走；绝不回自己家
				front = FindPushAnchor();
			}""",
    "front fallback")

# 5) 推线/清兵：用锚点替换"家门口的 front"
must_replace(
    """				if ((bool)front && (bool)spawn)
				{
					float dHome = Vector3.Distance(front.position, spawn.position);
					if (dHome < homeRadius)
					{
						Transform es = FindEnemySpawn();
						if ((bool)es)
						{
							return es;
						}
					}
				}
				return front;""",
    """				if ((bool)front && (bool)spawn)
				{
					float dHome = Vector3.Distance(front.position, spawn.position);
					if (dHome < homeRadius)
					{
						Transform anchor = FindPushAnchor();
						if ((bool)anchor)
						{
							return anchor;
						}
					}
				}
				return front;""",
    "pushLane anchor")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
