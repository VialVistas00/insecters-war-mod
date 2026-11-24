import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SoldierListFactoryUpdate.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 1) 波次与成长参数
must(
    """	public bool producing;""",
    """	public bool producing;

	/// <summary>
	/// 当前是第几波（每产完一轮 produceInfos 计一波）。
	/// 用来给新生成的兵按波次上浮生命值。
	/// </summary>
	public int waveIndex;

	/// <summary>
	/// 每波士兵生命值的成长比例。
	/// 0.06 表示第 n 波的血量 = 基础血量 × (1 + 0.06 × n)。
	/// </summary>
	public float waveHealthGrowth = 0.06f;

	/// <summary>成长上限倍率，防止后期血量失控。</summary>
	public float waveHealthMaxMultiplier = 3f;""",
    "wave fields")

# 2) 每波开始时递增
must(
    """	[RPC(rpcType = RPCType.hostToClient)]
	public void startPruduce()
	{
		soldierListFactory.updateProduceInfo();""",
    """	[RPC(rpcType = RPCType.hostToClient)]
	public void startPruduce()
	{
		// 每一轮出兵开始 = 新的一波，波次 +1（host 与 client 都走这里，计数一致）
		waveIndex++;
		soldierListFactory.updateProduceInfo();""",
    "wave increment")

# 3) 产兵时应用血量倍率
must(
    """		GameObject gameObject = GameNetwork.Instantiate(scenePrefab, position.x, position.y, 0f);
		gameObject.SetActive(true);
		gameObject.GetComponent<PathPointSearcher>().point = pathPointSearcher.point;""",
    """		GameObject gameObject = GameNetwork.Instantiate(scenePrefab, position.x, position.y, 0f);
		gameObject.SetActive(true);
		ApplyWaveHealth(gameObject);
		gameObject.GetComponent<PathPointSearcher>().point = pathPointSearcher.point;""",
    "apply health")

# 4) 应用方法
must(
    """	private void SoldierListFatoryProduce(byte pSoldierID)""",
    """	/// <summary>
	/// 按波次放大新兵的初始生命值。
	/// 只影响这一波新生成的单位，场上已有的兵不受影响。
	/// </summary>
	private void ApplyWaveHealth(GameObject pSoldier)
	{
		if (!(bool)pSoldier || waveIndex <= 0)
		{
			return;
		}
		if (waveHealthGrowth <= 0f)
		{
			return;
		}
		Life life = pSoldier.GetComponent<Life>();
		if (!(bool)life)
		{
			life = pSoldier.GetComponentInChildren<Life>();
		}
		if (!(bool)life)
		{
			return;
		}
		float mul = 1f + waveHealthGrowth * (float)waveIndex;
		if (waveHealthMaxMultiplier > 0f && mul > waveHealthMaxMultiplier)
		{
			mul = waveHealthMaxMultiplier;
		}
		if (mul <= 1.0001f)
		{
			return;
		}
		int baseFull = life.lifeFullValue;
		if (baseFull <= 0)
		{
			return;
		}
		int newFull = Mathf.RoundToInt((float)baseFull * mul);
		life.lifeFullValue = newFull;
		life.lifeValue = newFull;
		if (waveIndex % 5 == 0)
		{
			Debug.Log(string.Concat("[Wave] wave=", waveIndex,
				" mul=", mul.ToString("0.00"),
				" hp ", baseFull, " -> ", newFull,
				" unit=", pSoldier.name));
		}
	}

	private void SoldierListFatoryProduce(byte pSoldierID)""",
    "ApplyWaveHealth")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
