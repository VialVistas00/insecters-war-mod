import io
import sys

sys.stdout.reconfigure(encoding="utf-8")


def patch(path, pairs):
    s = io.open(path, encoding="utf-8-sig").read()
    for old, new, label in pairs:
        if old not in s:
            raise SystemExit("ANCHOR MISSING in " + path + ": " + label)
        s = s.replace(old, new, 1)
        print("ok:", label)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)


# ---------------------------------------------------------------- 1. 注册表加高度过滤 + 黑名单
reg = r"D:\游戏\Insecters War\iw-opensource\src\PickupPointRegistry.cs"
patch(reg, [
    ("""	public static Transform FindNearest(Vector3 pFrom, bool pPreferHealth, float pMaxDistance)
	{
		Prune();""",
     """	/// <param name="pMaxVerticalDelta">
	/// 允许的最大高度差。超过这个值说明补给点在高台/下层，AI 跳不上去，
	/// 直接跳过不选（原来的 bug：AI 会对高台上的血包反复寻路，卡在下面不动）。
	/// </param>
	/// <param name="pIsBlocked">黑名单判定，返回 true 表示这个点当前不可选。</param>
	public static Transform FindNearest(Vector3 pFrom, bool pPreferHealth, float pMaxDistance,
		float pMaxVerticalDelta = 999f, System.Func<Transform, bool> pIsBlocked = null)
	{
		Prune();""",
     "signature"),
    ("""			if (e.available != null && !e.available())
			{
				continue;
			}
			float d = Vector3.Distance(pFrom, e.transform.position);""",
     """			if (e.available != null && !e.available())
			{
				continue;
			}
			if (pIsBlocked != null && pIsBlocked(e.transform))
			{
				continue;
			}
			// 高度差过滤：跳不上去的点不选
			if (Mathf.Abs(e.transform.position.y - pFrom.y) > pMaxVerticalDelta)
			{
				continue;
			}
			float d = Vector3.Distance(pFrom, e.transform.position);""",
     "vertical filter"),
])

# ---------------------------------------------------------------- 2. HeroAI 超时/黑名单/补跳
ai = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
patch(ai, [
    ("""	private float nextPickupScanTime;""",
     """	private float nextPickupScanTime;

	// ---- 吃补给点的可达性处理 ----

	/// <summary>允许的最大高度差：超过就当"跳不上去"，不选。</summary>
	public float pickupMaxVerticalDelta = 2.0f;

	/// <summary>去某个补给点超过这个时间仍未拿到就放弃。</summary>
	public float pickupGiveUpTime = 6f;

	/// <summary>放弃后拉黑多久（秒）。</summary>
	public float pickupBlockSeconds = 25f;

	/// <summary>被拉黑的补给点 → 解禁时间。</summary>
	private readonly System.Collections.Generic.Dictionary<Transform, float> pickupBlockedUntil
		= new System.Collections.Generic.Dictionary<Transform, float>();

	/// <summary>当前正在前往的补给点与起始时间（用于超时判定）。</summary>
	private Transform pickupInProgress;

	private float pickupStartTime;""",
     "fields"),
    ("""		nextPickupScanTime = Time.time + 1.5f;
		bool needHealth = SelfHealthRate() < lowHealthRate;
		currentPickup = PickupPointRegistry.FindNearest(
			base.transform.position, needHealth, pickupSearchDistance);
		return currentPickup;
	}""",
     """		nextPickupScanTime = Time.time + 1.5f;
		bool needHealth = SelfHealthRate() < lowHealthRate;
		currentPickup = PickupPointRegistry.FindNearest(
			base.transform.position, needHealth, pickupSearchDistance,
			pickupMaxVerticalDelta, IsPickupBlocked);
		return currentPickup;
	}

	/// <summary>这个补给点是否在拉黑期内。</summary>
	private bool IsPickupBlocked(Transform pPoint)
	{
		if (!(bool)pPoint)
		{
			return true;
		}
		float until;
		if (pickupBlockedUntil.TryGetValue(pPoint, out until))
		{
			if (Time.time < until)
			{
				return true;
			}
			pickupBlockedUntil.Remove(pPoint);
		}
		return false;
	}

	/// <summary>拉黑一个拿不到的补给点。</summary>
	private void BlockPickup(Transform pPoint, string pReason)
	{
		if (!(bool)pPoint)
		{
			return;
		}
		pickupBlockedUntil[pPoint] = Time.time + pickupBlockSeconds;
		if (pickupInProgress == pPoint)
		{
			pickupInProgress = null;
		}
		if (currentPickup == pPoint)
		{
			currentPickup = null;
		}
		nextPickupScanTime = 0f;
		Debug.Log(string.Concat("[AI] pickup give up (", pReason, ") at ",
			pPoint.position.x.ToString("0"), ",", pPoint.position.y.ToString("0")));
	}

	/// <summary>
	/// 抢点过程中的可达性处理：
	///   · 目标贴脸但高度差一点 → 补一次跳跃，能跳上去就吃到；
	///   · 去了太久还没拿到 → 放弃并拉黑，避免一直卡在台子下面。
	/// </summary>
	private void UpdatePickupProgress()
	{
		if (mode != AIMode.contestPickup && mode != AIMode.retreat)
		{
			pickupInProgress = null;
			return;
		}
		Transform pk = currentPickup;
		if (!(bool)pk)
		{
			pickupInProgress = null;
			return;
		}
		if (pickupInProgress != pk)
		{
			pickupInProgress = pk;
			pickupStartTime = Time.time;
			return;
		}

		Vector3 me = base.transform.position;
		float dx = Mathf.Abs(pk.position.x - me.x);
		float dy = pk.position.y - me.y;

		// 已经贴到点了但吃不到（多半高度差），先跳一下
		if (dx <= 1.6f && dy > 0.6f && dy <= 3.2f)
		{
			actionCommand.Jump = true;
		}

		// 超时放弃
		if (Time.time - pickupStartTime > pickupGiveUpTime)
		{
			BlockPickup(pk, "timeout");
		}
	}""",
     "FindPickup+progress"),
    ("""		// 拆塔：单独结算建筑伤害
		if (mode == AIMode.siege)
		{
			DoSiegeAttack();
		}""",
     """		// 拆塔：单独结算建筑伤害
		if (mode == AIMode.siege)
		{
			DoSiegeAttack();
		}
		// 吃补给点：补跳 / 超时放弃
		UpdatePickupProgress();""",
     "call progress"),
])

print("DONE")
