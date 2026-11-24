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


# ---------------------------------------------------------------- 1. 枚举加 siege
must_replace(
    """		/// <summary>没兵线压力时去抢地图上的回血 / 回黄点。</summary>
		contestPickup
	}""",
    """		/// <summary>没兵线压力时去抢地图上的回血 / 回黄点。</summary>
		contestPickup,
		/// <summary>配合兵线拆塔：己方小兵顶在前面时，推掉敌方建筑。</summary>
		siege
	}""",
    "enum siege")

# ---------------------------------------------------------------- 2. 新增字段
must_replace(
    """	private int lastLaneCrowd;""",
    """	private int lastLaneCrowd;

	// ---- 拆塔 ----

	/// <summary>拆塔搜索半径。</summary>
	public float siegeSearchRange = 14f;

	/// <summary>附近己方小兵至少这么多，才敢跟着兵线拆塔（有肉盾）。</summary>
	public int siegeMinAllies = 2;

	/// <summary>血量低于该比例不拆塔（先撤）。</summary>
	public float siegeMinHealthRate = 0.55f;

	/// <summary>对建筑的出手间隔（秒）。</summary>
	public float siegeAttackInterval = 0.65f;

	/// <summary>对建筑的每次伤害占自身物攻的比例。</summary>
	public float siegeDamageRate = 0.85f;

	private Transform siegeTarget;

	private Life siegeTargetLife;

	private float nextSiegeScanTime;

	private float nextSiegeAttackTime;

	/// <summary>累计拆除建筑次数（自检用）。</summary>
	public int statSiegeHits;""",
    "siege fields")

# ---------------------------------------------------------------- 3. 拆塔目标查找
must_replace(
    """	/// <summary>自己是否在己方出生点附近（=赖在家里）。</summary>""",
    """	/// <summary>统计半径内的己方小兵数量（判断"有没有肉盾顶着"）。</summary>
	private int CountAlliesInRange(float pRange)
	{
		Race myRace = (bool)hero && (bool)hero.spawn ? hero.spawn.race : GameNetwork.self.race;
		if (myRace == Race.eNone)
		{
			return 0;
		}
		int mask = (int)PlayerInfo.getRaceObjectValue(myRace);
		Collider[] hits = Physics.OverlapSphere(base.transform.position, pRange, mask);
		int count = 0;
		for (int i = 0; i < hits.Length; i++)
		{
			Collider c = hits[i];
			if (!(bool)c || c.isTrigger)
			{
				continue;
			}
			if ((bool)c.GetComponentInParent<Soldier>())
			{
				count++;
			}
		}
		return count;
	}

	/// <summary>
	/// 找最近的敌方建筑（防御塔 / 主基地 / 据点建筑），带缓存。
	/// 建筑的种族从它自己的 Life.characterInfo 读，避免用 layer 猜。
	/// </summary>
	private void ScanSiegeTarget()
	{
		if (Time.time < nextSiegeScanTime)
		{
			return;
		}
		nextSiegeScanTime = Time.time + 1.5f;
		siegeTarget = null;
		siegeTargetLife = null;
		Race myRace = (bool)hero && (bool)hero.spawn ? hero.spawn.race : GameNetwork.self.race;
		if (myRace == Race.eNone)
		{
			return;
		}
		float best = siegeSearchRange;
		// 防御塔
		DefenseTower[] towers = Object.FindObjectsOfType<DefenseTower>();
		for (int i = 0; i < towers.Length; i++)
		{
			ConsiderBuilding(towers[i] ? towers[i].transform : null, myRace, ref best);
		}
		// 主基地
		ArmyBase[] bases = Object.FindObjectsOfType<ArmyBase>();
		for (int j = 0; j < bases.Length; j++)
		{
			ArmyBase ab = bases[j];
			if ((bool)ab)
			{
				ConsiderBuildingLife(ab.life, ab.transform, myRace, ref best);
			}
		}
		// 据点建筑
		StrongholdBuilding[] shs = Object.FindObjectsOfType<StrongholdBuilding>();
		for (int k = 0; k < shs.Length; k++)
		{
			StrongholdBuilding sb = shs[k];
			if ((bool)sb && (bool)sb.life)
			{
				ConsiderBuildingLife(sb.life, sb.transform, myRace, ref best);
			}
		}
	}

	private void ConsiderBuilding(Transform pTransform, Race pMyRace, ref float pBest)
	{
		if (!(bool)pTransform)
		{
			return;
		}
		Life l = pTransform.GetComponentInChildren<Life>();
		ConsiderBuildingLife(l, pTransform, pMyRace, ref pBest);
	}

	private void ConsiderBuildingLife(Life pLife, Transform pTransform, Race pMyRace, ref float pBest)
	{
		if (!(bool)pLife || !(bool)pTransform)
		{
			return;
		}
		if (pLife.characterInfo == null || pLife.characterInfo.race == pMyRace)
		{
			return;
		}
		if (pLife.lifeValue <= 0)
		{
			return;
		}
		float d = Vector3.Distance(base.transform.position, pTransform.position);
		if (d < pBest)
		{
			pBest = d;
			siegeTarget = pTransform;
			siegeTargetLife = pLife;
		}
	}

	/// <summary>自己是否在己方出生点附近（=赖在家里）。</summary>""",
    "siege scan")

# ---------------------------------------------------------------- 4. UpdateMode 插入 siege
must_replace(
    """		// 4) 没战斗 → 抢点，但排除"家门口的补给点"，避免在家附近打转""",
    """		// 3.5) 配合兵线拆塔：有己方小兵顶着 + 血量健康 + 敌方建筑在附近
		ScanSiegeTarget();
		if ((bool)siegeTarget && (bool)siegeTargetLife
			&& SelfHealthRate() >= siegeMinHealthRate
			&& CountAlliesInRange(siegeSearchRange) >= siegeMinAllies)
		{
			mode = AIMode.siege;
			return;
		}

		// 4) 没战斗 → 抢点，但排除"家门口的补给点"，避免在家附近打转""",
    "UpdateMode siege")

# ---------------------------------------------------------------- 5. ResolveMoveTarget 加 siege
must_replace(
    """		case AIMode.contestPickup:""",
    """		case AIMode.siege:
			return (bool)siegeTarget ? siegeTarget : front;
		case AIMode.contestPickup:""",
    "ResolveMoveTarget siege")

# ---------------------------------------------------------------- 6. TryUseSkill 优化
must_replace(
    """		// SP 不足 → 留着
		ActionEnergyValue energy = hero.actionEnergyValue;
		if ((bool)energy)
		{
			float rate = (energy.fullValue > 0f) ? (energy.nowValue / energy.fullValue) : 0f;
			if (rate < skillSpThreshold)
			{
				return;
			}
		}""",
    """		// —— SP 判断改为"按局势决定该不该花" ——
		ActionEnergyValue energy = hero.actionEnergyValue;
		float spRate = 1f;
		if ((bool)energy && energy.fullValue > 0f)
		{
			spRate = energy.nowValue / energy.fullValue;
		}

		// 局势评估：目标数量 / 有没有残血可收
		int nearCount = CountEnemiesInRange(shootRange * 1.2f);
		bool hasLowHpTarget = IsTargetLowHealth(target, 0.35f);
		bool spOverflow = spRate >= 0.92f;      // SP 快满了，不用白不用

		// 阈值动态调整：
		//   多个目标（范围技能收益高） 或 能收残血 或 SP 溢出 → 放宽
		//   只有一个满血目标                          → 保持原阈值，别浪费
		float need = skillSpThreshold;
		if (spOverflow)
		{
			need = 0f;
		}
		else if (nearCount >= 2 || hasLowHpTarget)
		{
			need = skillSpThreshold * 0.6f;
		}
		if (spRate < need)
		{
			return;
		}""",
    "TryUseSkill sp logic")

# ---------------------------------------------------------------- 7. 辅助方法
must_replace(
    """	/// <summary>统计半径内的己方小兵数量（判断"有没有肉盾顶着"）。</summary>""",
    """	/// <summary>统计半径内的敌方单位数量（用于判断技能是否值得放）。</summary>
	private int CountEnemiesInRange(float pRange)
	{
		Collider[] hits = Physics.OverlapSphere(base.transform.position, pRange, (int)enemy);
		int count = 0;
		for (int i = 0; i < hits.Length; i++)
		{
			Collider c = hits[i];
			if (!(bool)c || c.isTrigger)
			{
				continue;
			}
			WMGameObject wm = WMGameObject.getFromTransform(c.transform);
			if ((bool)wm)
			{
				count++;
			}
		}
		return count;
	}

	/// <summary>目标血量比例是否低于阈值（收人头判断）。</summary>
	private bool IsTargetLowHealth(Transform pTarget, float pRate)
	{
		if (!(bool)pTarget)
		{
			return false;
		}
		WMGameObject wm = WMGameObject.getFromTransform(pTarget);
		if (!(bool)wm || !(bool)wm.life)
		{
			return false;
		}
		Life l = wm.life;
		if (l.lifeFullValue <= 0)
		{
			return false;
		}
		return (float)l.lifeValue / (float)l.lifeFullValue <= pRate;
	}

	/// <summary>统计半径内的己方小兵数量（判断"有没有肉盾顶着"）。</summary>""",
    "helpers")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
