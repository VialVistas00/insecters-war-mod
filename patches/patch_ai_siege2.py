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


# 1) 拆塔伤害结算方法
must_replace(
    """	/// <summary>统计半径内的敌方单位数量（用于判断技能是否值得放）。</summary>""",
    """	/// <summary>
	/// 拆塔：按固定间隔对建筑结算一次伤害。
	///
	/// 建筑的受击不走射线/子弹那套（AI 的 DetectFire 只找单位），
	/// 所以这里直接对建筑的 Life 调 injure，并同时按开火键让英雄做出攻击动作。
	/// </summary>
	private void DoSiegeAttack()
	{
		if (!(bool)siegeTarget || !(bool)siegeTargetLife)
		{
			return;
		}
		if (siegeTargetLife.lifeValue <= 0)
		{
			siegeTargetLife = null;
			siegeTarget = null;
			return;
		}
		if (Time.time < nextSiegeAttackTime)
		{
			return;
		}
		float d = Vector3.Distance(base.transform.position, siegeTarget.position);
		if (d > siegeSearchRange * 1.15f)
		{
			return;
		}
		nextSiegeAttackTime = Time.time + siegeAttackInterval;

		int atk = 20;
		if ((bool)hero && (bool)hero.spawn && (bool)hero.spawn.heroSetting)
		{
			atk = hero.spawn.heroSetting._totalPhysicsAttack;
		}
		if (atk < 5)
		{
			atk = 5;
		}
		atk = Mathf.Max(5, (int)(atk * siegeDamageRate));

		AttackSetting setting = new AttackSetting();
		setting._physicsAttack = atk;
		setting._magicAttack = 0;

		int before = siegeTargetLife.lifeValue;
		int pa;
		int ma;
		try
		{
			siegeTargetLife.injure(new AttackInfo
			{
				attackSetting = setting,
				attackTypeIndex = 0,
				characterInfo = (bool)hero ? hero.characterInfo : null,
				harmType = Life.HarmType.other
			}, out pa, out ma);
		}
		catch (System.Exception ex)
		{
			Debug.Log("[AI] siege injure failed: " + ex.Message);
			return;
		}
		int after = siegeTargetLife.lifeValue;
		statSiegeHits++;
		if (statSiegeHits % 8 == 1)
		{
			Debug.Log(string.Concat("[AI] siege dmg=", atk,
				" life ", before, " -> ", after,
				" (applied=", before - after, ") target=", siegeTarget.name));
		}
		// 面向建筑并按开火，让动作看起来是在打塔
		actionCommand.Fire = true;
		float dx = siegeTarget.position.x - base.transform.position.x;
		actionCommand.FaceRight = dx > 0f;
		actionCommand.FaceLeft = dx < 0f;
	}

	/// <summary>统计半径内的敌方单位数量（用于判断技能是否值得放）。</summary>""",
    "DoSiegeAttack")

# 2) Update 里调用
must_replace(
    """		// 技能：推线/gank/游走途中都愿意放（游走时遇到人更容易先手）
		if (mode != AIMode.retreat)
		{
			TryUseSkill();
		}""",
    """		// 技能：推线/gank/游走途中都愿意放（游走时遇到人更容易先手）
		if (mode != AIMode.retreat)
		{
			TryUseSkill();
		}
		// 拆塔：单独结算建筑伤害
		if (mode == AIMode.siege)
		{
			DoSiegeAttack();
		}""",
    "Update call siege")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
