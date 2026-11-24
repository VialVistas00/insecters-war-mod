import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 1) 出生延迟字段
must("""	private float nextAttackTime;""",
     """	private float nextAttackTime;

	/// <summary>出生后多久才开始结算攻击（秒）。</summary>
	[System.NonSerialized]
	public float spawnAttackDelay = 0.8f;

	/// <summary>出生时刻。</summary>
	private float spawnTime;""",
     "delay fields")

# 2) AIStart 里记录出生时间并推迟第一次出手
must("""		soldier.character2D.canBeatBack = false;
		WidenAttackRadius();""",
     """		soldier.character2D.canBeatBack = false;
		WidenAttackRadius();
		// 出生保护：新建/新刷出的蜂先不要立刻结算伤害。
		// 否则在编辑器里点一次「创建」，新建的蜂当场就打 80 点，
		// 看起来像是"点按钮扣血"。
		spawnTime = Time.time;
		nextAttackTime = Time.time + 1f;""",
     "spawn delay")

# 3) DoAttackSplash 里再兜一层
must("""		if (Time.time < nextAttackTime)
		{
			return;
		}""",
     """		if (Time.time - spawnTime < spawnAttackDelay)
		{
			return;
		}
		if (Time.time < nextAttackTime)
		{
			return;
		}""",
     "guard")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
