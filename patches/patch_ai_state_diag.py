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


must_replace(
    """	private float nextAnchorScanTime;""",
    """	private float nextAnchorScanTime;

	/// <summary>状态诊断节流（排查"原地打转"用）。</summary>
	private float nextStateDiagTime;""",
    "state diag field")

# 在 Update 里 UpdateMode 之后打一条状态
must_replace(
    """		// 在家连续待太久 → 强制外出（兜住所有回家原因）""",
    """		// —— 状态诊断：每 4 秒打一次，用来判断"为什么不走" ——
		if (Time.time >= nextStateDiagTime)
		{
			nextStateDiagTime = Time.time + 4f;
			Transform probe = FindPushAnchor();
			Debug.Log(string.Concat("[AI] state mode=", mode,
				" pos=", base.transform.position.x.ToString("0"), ",", base.transform.position.y.ToString("0"),
				" spawn=", (bool)spawn ? spawn.position.x.ToString("0") : "-", ",",
				(bool)spawn ? spawn.position.y.ToString("0") : "-",
				" anchor=", (bool)probe ? probe.name : "none",
				" anchorPos=", (bool)probe ? probe.position.x.ToString("0") : "-", ",",
				(bool)probe ? probe.position.y.ToString("0") : "-",
				" pathing=", (bool)pathAgent && pathAgent.pathing,
				" stuck=", stuckCount, "/", stuckRetry,
				" crowd=", lastLaneCrowd,
				" siegeTgt=", (bool)siegeTarget ? siegeTarget.name : "none"));
		}

		// 在家连续待太久 → 强制外出（兜住所有回家原因）""",
    "state diag body")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
