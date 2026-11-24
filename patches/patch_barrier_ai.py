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


# ============ 1. 防御墙基础生命值提高 ============
patch(r"D:\游戏\Insecters War\iw-opensource\src\SkillBarrier.cs", [
    ("""	[System.NonSerialized]
	public float enemyBreakDps = 260f;""",
     """	[System.NonSerialized]
	public float enemyBreakDps = 260f;

	/// <summary>
	/// 墙的基础生命值倍率（本改版）。
	/// 原版的血量在预制体里配得很低，敌人贴脸两三下就破，
	/// 指挥官的防守技能几乎没作用。这里在 Awake 里按倍率放大。
	/// </summary>
	[System.NonSerialized]
	public float barrierHealthScale = 3f;""",
     "scale field"),

    ("""	private void Awake()
	{
		startTime = (int)(_aliveTime * 1000f);""",
     """	private void Awake()
	{
		BoostBarrierHealth();
		startTime = (int)(_aliveTime * 1000f);""",
     "call boost"),

    ("""	private void deadAction(Life p)""",
     """	/// <summary>放大墙的总血量与当前血量。</summary>
	private void BoostBarrierHealth()
	{
		if (barrierHealthScale <= 0.05f)
		{
			barrierHealthScale = 3f;
		}
		if (!(bool)life || barrierHealthScale <= 1.001f)
		{
			return;
		}
		int baseFull = life.lifeFullValue;
		if (baseFull <= 0)
		{
			return;
		}
		int newFull = Mathf.RoundToInt((float)baseFull * barrierHealthScale);
		life.lifeFullValue = newFull;
		life.lifeValue = newFull;
		Debug.Log(string.Concat("[Barrier] hp ", baseFull, " -> ", newFull,
			" x", barrierHealthScale));
	}

	private void deadAction(Life p)""",
     "boost method"),
])

# ============ 2. AI 撤退后必须能重新出来 ============
patch(r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs", [
    ("""	/// <summary>在家停留超过这个秒数就强制外出。</summary>
	public float homeStayLimit = 4f;""",
     """	/// <summary>在家停留超过这个秒数就强制外出。</summary>
	public float homeStayLimit = 4f;

	/// <summary>
	/// 撤退状态最长持续多少秒。
	/// 原来的 bug：AI 血量一低就 retreat，跑到塔下之后没有任何出口条件，
	/// 血量回满了也还赖在塔下不参战（"总有一个 AI 缩在塔下"）。
	/// </summary>
	public float retreatMaxTime = 7f;

	/// <summary>血量回到这个比例以上就可以取消撤退。</summary>
	public float retreatRecoverRate = 0.7f;

	private float retreatStayTime;""",
     "retreat fields"),

    ("""		// 在家连续待太久 → 强制外出（兜住所有回家原因）""",
     """		// 撤退出口：血量回满 或 在塔下待太久 → 立刻回到战场
		if (mode == AIMode.retreat)
		{
			retreatStayTime += Time.deltaTime;
			bool recovered = SelfHealthRate() >= retreatRecoverRate;
			if (recovered || retreatStayTime >= retreatMaxTime)
			{
				retreatStayTime = 0f;
				Transform anchor = FindPushAnchor();
				if ((bool)anchor)
				{
					front = anchor;
				}
				mode = AIMode.pushLane;
			}
		}
		else
		{
			retreatStayTime = 0f;
		}

		// 在家连续待太久 → 强制外出（兜住所有回家原因）""",
     "retreat exit"),
])

print("DONE")
