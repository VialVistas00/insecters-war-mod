import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

start = s.index("	/// <summary>\n	/// 找最近的敌方建筑（防御塔 / 主基地 / 据点建筑），带缓存。")
end = s.index("	/// <summary>\n	/// 推线锚点：找不到敌方出生点时")

new_block = '''	/// <summary>
	/// 找最近的敌方建筑，带缓存。
	///
	/// 实现改用 **敌方建筑 layer** 来做球形查询，而不是逐个 FindObjectsOfType：
	///   · 地图里的建筑类型五花八门（DefenseTower / ArmyBase / AntBase / BeeBase / 据点建筑…），
	///     按类名枚举必然漏；
	///   · 而建筑的 layer 一定是对应阵营的 building layer（DefenseTower.Init 里就是这么设的），
	///     一次 OverlapSphere 就能把所有敌方建筑捞出来。
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
		Race enemyRace = PlayerInfo.getAdversaryRace(myRace);
		int enemyBuildingLayer = PlayerInfo.getBuildingLayer(enemyRace);
		if (enemyBuildingLayer <= 0)
		{
			return;
		}

		Collider[] hits = Physics.OverlapSphere(base.transform.position, siegeSearchRange,
			(1 << enemyBuildingLayer) | (int)PlayerInfo.getRaceObjectValue(enemyRace));
		float best = float.MaxValue;
		for (int i = 0; i < hits.Length; i++)
		{
			Collider c = hits[i];
			if (!(bool)c || c.isTrigger)
			{
				continue;
			}
			Life l = c.GetComponentInParent<Life>();
			if (!(bool)l || l.lifeValue <= 0)
			{
				continue;
			}
			// 单位（小兵/英雄）不算建筑：只认 layer 是建筑层的
			if (c.gameObject.layer != enemyBuildingLayer
				&& (!c.transform.parent || c.transform.parent.gameObject.layer != enemyBuildingLayer))
			{
				continue;
			}
			Transform t = (bool)l ? l.transform : c.transform;
			float d = Vector3.Distance(base.transform.position, t.position);
			if (d < best)
			{
				best = d;
				siegeTarget = t;
				siegeTargetLife = l;
			}
		}
	}

'''
s = s[:start] + new_block + s[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ScanSiegeTarget replaced")
