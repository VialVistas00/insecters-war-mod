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


# 1) 参数（预制体组件必须 NonSerialized，否则破坏旧地图序列化布局）
must("""	/// <summary>成长上限倍率，防止后期血量失控。</summary>
	[System.NonSerialized]
	public float waveHealthMaxMultiplier = 3f;""",
     """	/// <summary>成长上限倍率，防止后期血量失控。</summary>
	[System.NonSerialized]
	public float waveHealthMaxMultiplier = 3f;

	// ---- 蚂蚁方小兵强化 ----

	/// <summary>蚂蚁小兵血量倍率。</summary>
	[System.NonSerialized]
	public float antHealthScale = 1.6f;

	/// <summary>蚂蚁小兵物理攻击倍率。</summary>
	[System.NonSerialized]
	public float antAttackScale = 1.3f;

	/// <summary>累计强化过的蚂蚁小兵数（诊断用）。</summary>
	[System.NonSerialized]
	public int statAntBuffed;""",
     "ant fields")

# 2) 产兵时应用
must("""		ApplyWaveHealth(gameObject);""",
     """		ApplyWaveHealth(gameObject);
		ApplyAntBuff(gameObject);""",
     "call buff")

# 3) 实现
must("""	/// <summary>
	/// 按波次放大新兵的初始生命值。""",
     """	/// <summary>
	/// 蚂蚁方小兵强化：血量与物理攻击按倍率放大。
	///
	/// 背景：沙漠小镇这类 232 格宽的图，AI 推到中场就被敌方兵线压住，
	/// 一整局都摸不到塔（`siege none` 刷 91 次）。单纯改 AI 逻辑没用，
	/// 得让蚂蚁的兵线本身推得动。
	///
	/// 只强化蚂蚁（`Race.ePismire`），蜜蜂方不受影响。
	/// </summary>
	private void ApplyAntBuff(GameObject pSoldier)
	{
		if (!(bool)pSoldier || !(bool)soldierListFactory)
		{
			return;
		}
		if (soldierListFactory._race != Race.ePismire)
		{
			return;
		}
		// Unity 序列化陷阱：后加字段会被冲成 0，运行时兜底
		if (antHealthScale <= 0.05f)
		{
			antHealthScale = 1.6f;
		}
		if (antAttackScale <= 0.05f)
		{
			antAttackScale = 1.3f;
		}

		Life life = pSoldier.GetComponent<Life>();
		if (!(bool)life)
		{
			life = pSoldier.GetComponentInChildren<Life>();
		}
		int baseFull = 0;
		int newFull = 0;
		if ((bool)life && life.lifeFullValue > 0 && antHealthScale > 1.001f)
		{
			baseFull = life.lifeFullValue;
			newFull = Mathf.RoundToInt((float)baseFull * antHealthScale);
			life.lifeFullValue = newFull;
			life.lifeValue = newFull;
		}

		// 攻击力：写在 CharacterInfo 上（伤害结算读的是 characterInfo.physicsAttack）
		Soldier sd = pSoldier.GetComponent<Soldier>();
		if (!(bool)sd)
		{
			sd = pSoldier.GetComponentInChildren<Soldier>();
		}
		if ((bool)sd && (bool)sd.characterInfo && sd.characterInfo.characterInfo != null
			&& antAttackScale > 1.001f)
		{
			CharacterInfo ci = sd.characterInfo.characterInfo;
			ci.physicsAttack = Mathf.RoundToInt((float)ci.physicsAttack * antAttackScale);
		}

		statAntBuffed++;
		if (statAntBuffed % 20 == 1)
		{
			Debug.Log(string.Concat("[AntBuff] unit=", pSoldier.name,
				" hp ", baseFull, " -> ", newFull,
				" x", antHealthScale,
				" atk x", antAttackScale,
				" total=", statAntBuffed));
		}
	}

	/// <summary>
	/// 按波次放大新兵的初始生命值。""",
     "ApplyAntBuff")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
