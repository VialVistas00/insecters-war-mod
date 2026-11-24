import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SoldierListFactory.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 1) 加计数字段
must(
    """	[System.NonSerialized]
	public int pendingNextWaveSoldierId = -1;""",
    """	[System.NonSerialized]
	public int pendingNextWaveSoldierId = -1;

	/// <summary>
	/// 同一兵种累计下单了几次 —— 买几次，下一波就多出几个。
	/// 之前只有 id 没有计数，所以连买多次只会生效最后一次。
	/// </summary>
	[System.NonSerialized]
	public int pendingNextWaveCount;""",
    "count field")

# 2) SetPendingNextWave 累加
must(
    """	/// <summary>登记一次"下一次出兵"的替换。</summary>
	public void SetPendingNextWave(int pSoldierId)
	{
		pendingNextWaveSoldierId = pSoldierId;
		// 关键：updateProduceInfo() 开头会检查这个标志，不置位的话
		// 下一波重建不会发生，待发兵种就永远消费不掉。
		needUpdateProduceInfo = true;
	}""",
    """	/// <summary>
	/// 登记一次"下一次出兵"的下单。
	/// 同兵种累加数量（买 3 次 = 下一波多 3 个），换兵种则重置为 1。
	/// </summary>
	public void SetPendingNextWave(int pSoldierId)
	{
		if (pendingNextWaveSoldierId == pSoldierId)
		{
			pendingNextWaveCount++;
		}
		else
		{
			pendingNextWaveSoldierId = pSoldierId;
			pendingNextWaveCount = 1;
		}
		// 关键：updateProduceInfo() 开头会检查这个标志，不置位的话
		// 下一波重建不会发生，待发兵种就永远消费不掉。
		needUpdateProduceInfo = true;
	}""",
    "accumulate")

# 3) 消费时返回数量
must(
    """	/// <summary>消耗并返回待发兵种 id（-1 表示没有）。</summary>
	public int ConsumePendingNextWave()
	{
		int result = pendingNextWaveSoldierId;
		pendingNextWaveSoldierId = -1;
		return result;
	}""",
    """	/// <summary>消耗并返回待发兵种 id（-1 表示没有）。</summary>
	public int ConsumePendingNextWave()
	{
		int result = pendingNextWaveSoldierId;
		pendingNextWaveSoldierId = -1;
		pendingNextWaveCount = 0;
		return result;
	}

	/// <summary>当前累计下单次数（UI / 日志用）。</summary>
	public int PendingNextWaveCount
	{
		get
		{
			return (pendingNextWaveSoldierId >= 0) ? pendingNextWaveCount : 0;
		}
	}""",
    "consume")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE part1")
