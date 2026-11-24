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


# 1) 攻击结算字段
must(
    """	[System.NonSerialized]
	public float aoeRadius = 3.0f;""",
    """	[System.NonSerialized]
	public float aoeRadius = 3.0f;

	/// <summary>两次攻击结算之间的最小间隔（秒），避免同一次挥击重复扣血。</summary>
	[System.NonSerialized]
	public float attackInterval = 0.55f;

	private float nextAttackTime;

	/// <summary>累计攻击结算次数（诊断用）。</summary>
	[System.NonSerialized]
	public int statAttacks;""",
    "attack fields")

# 2) 在发出攻击命令处补结算
must(
    """			else if (lFireTaget != 0)
			{
				if (overaweCheck())
				{
					actionCommand.Action2 = true;
				}
				else
				{
					actionCommand.Fire = true;
					setFaceCommand(actionCommand, lFireTaget);
				}
				PausePath();
				actionCommandControl.setCommand(actionCommand);
			}""",
    """			else if (lFireTaget != 0)
			{
				if (overaweCheck())
				{
					actionCommand.Action2 = true;
				}
				else
				{
					actionCommand.Fire = true;
					setFaceCommand(actionCommand, lFireTaget);
				}
				PausePath();
				actionCommandControl.setCommand(actionCommand);
				// 补一次攻击结算：
				// 这张图里生化蜂身上那 3 个 SphereHarmByDetector 只在死亡时
				// （enableHarm 回调）才结算，攻击流程根本不会调用它们，
				// 表现就是"打到了但一点伤害都没有"。这里按攻击节奏直接结算。
				DoAttackSplash(0);
			}""",
    "fire splash")

# 3) swoop 也结算
must(
    """				PausePath();
				actionCommandControl.setCommand(actionCommand);
			}
			else if (lFireTaget != 0)""",
    """				PausePath();
				actionCommandControl.setCommand(actionCommand);
				DoAttackSplash(2);
			}
			else if (lFireTaget != 0)""",
    "swoop splash")

# 4) 结算实现
must(
    """	private bool swoopCheck()""",
    """	/// <summary>
	/// 对自身前方一圈敌人结算一次伤害。
	/// 伤害值取自身上对应攻击组件的 attackSetting（弹药数据来自地图 obc），
	/// 半径用 aoeRadius，保证"范围群体攻击"能体现出来。
	/// </summary>
	private void DoAttackSplash(int pHarmIndex)
	{
		if (Time.time < nextAttackTime)
		{
			return;
		}
		if (aoeRadius <= 0.05f)
		{
			aoeRadius = 3f;
		}
		if (attackInterval <= 0.01f)
		{
			attackInterval = 0.55f;
		}

		SphereHarmByDetector[] harms = GetComponentsInChildren<SphereHarmByDetector>(true);
		if (harms.Length == 0)
		{
			return;
		}
		SphereHarmByDetector src = harms[Mathf.Clamp(pHarmIndex, 0, harms.Length - 1)];
		if (!(bool)src)
		{
			return;
		}

		nextAttackTime = Time.time + attackInterval;

		int dmg = src.attackSetting._physicsAttack;
		if (dmg <= 0)
		{
			dmg = src.attackSetting._magicAttack;
		}
		if (dmg <= 0)
		{
			dmg = 50;
		}

		CharacterInfo info = null;
		if ((bool)soldier && (bool)soldier.life)
		{
			info = soldier.life.characterInfo;
		}
		if (info == null)
		{
			return;
		}

		Vector3 center = base.transform.position;
		int mask = (int)PlayerInfo.getRaceObjectValue(PlayerInfo.getAdversaryRace(info.race));
		if (mask == 0)
		{
			mask = -1;
		}

		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);
		int hurt = 0;
		for (int i = 0; i < hits.Length; i++)
		{
			Collider c = hits[i];
			if (!(bool)c || c.isTrigger)
			{
				continue;
			}
			WMGameObject wm = WMGameObject.getFromTransform(c.transform);
			if (!(bool)wm || !(bool)wm.life)
			{
				continue;
			}
			if (wm.life.characterInfo != null && wm.life.characterInfo.race == info.race)
			{
				continue;
			}
			AttackSetting st = new AttackSetting();
			st._physicsAttack = dmg;
			st._magicAttack = 0;
			wm.injure(new AttackInfo
			{
				attackSetting = st,
				attackTypeIndex = src.attackTypeIndex,
				characterInfo = info,
				harmType = Life.HarmType.other
			});
			hurt++;
		}
		statAttacks++;
		if (statAttacks % 5 == 1)
		{
			Debug.Log(string.Concat("[Bee] attack idx=", pHarmIndex,
				" dmg=", dmg, " radius=", aoeRadius,
				" colliders=", hits.Length, " hurt=", hurt,
				" race=", info.race));
		}
	}

	private bool swoopCheck()""",
    "DoAttackSplash")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
