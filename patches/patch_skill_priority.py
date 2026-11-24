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


# ---------------------------------------------------------------- 1. 技能优先于普攻（全局）
hero = r"D:\游戏\Insecters War\iw-opensource\src\Hero.cs"
patch(hero, [
    ("""			if (lActionCommand.Fire)
			{
				firing = true;
				nowAction = fireAction;
			}
			else if ((command & action1CommandValue) != 0 && action1.canDo)
			{
				nowAction = action1;
			}
			else if ((command & action2CommandValue) != 0 && action2.canDo)
			{
				nowAction = action2;
			}
			else if ((command & action3CommandValue) != 0 && action3.canDo)
			{
				nowAction = action3;
			}""",
     """			// 本改版：技能优先级高于普攻。
			// 原版这里 Fire 排在最前面，只要按着普攻键，技能永远触发不了
			// （AI 一直只平 A 就是这个原因，玩家同时按也会被吞掉）。
			if ((command & action1CommandValue) != 0 && (bool)action1 && action1.canDo)
			{
				nowAction = action1;
			}
			else if ((command & action2CommandValue) != 0 && (bool)action2 && action2.canDo)
			{
				nowAction = action2;
			}
			else if ((command & action3CommandValue) != 0 && (bool)action3 && action3.canDo)
			{
				nowAction = action3;
			}
			else if (lActionCommand.Fire)
			{
				firing = true;
				nowAction = fireAction;
			}""",
     "skill over fire"),
])

# ---------------------------------------------------------------- 2. SP 低时去回黄点
ai = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
patch(ai, [
    ("""	public float pickupSearchDistance = 45f;""",
     """	public float pickupSearchDistance = 45f;

	/// <summary>SP 低于这个比例就主动去找回黄点补能量。</summary>
	public float lowSpRate = 0.2f;""",
     "lowSpRate"),

    # FindPickup：按需求决定优先回血还是回黄
    ("""		nextPickupScanTime = Time.time + 1.5f;
		bool needHealth = SelfHealthRate() < lowHealthRate;
		currentPickup = PickupPointRegistry.FindNearest(
			base.transform.position, needHealth, pickupSearchDistance,
			pickupMaxVerticalDelta, IsPickupBlocked);
		return currentPickup;""",
     """		nextPickupScanTime = Time.time + 1.5f;
		// 缺血优先回血；血够但 SP 快见底，则优先回黄
		float hp = SelfHealthRate();
		bool needHealth = hp < lowHealthRate;
		currentPickup = PickupPointRegistry.FindNearest(
			base.transform.position, needHealth, pickupSearchDistance,
			pickupMaxVerticalDelta, IsPickupBlocked);
		return currentPickup;""",
     "FindPickup comment"),

    # UpdateMode：SP 见底优先去回黄
    ("""		// 3) 兵线聚集 → 优先清兵
		if (ScanLaneCrowd() >= laneCrowdCount)
		{
			mode = AIMode.farmLane;
			return;
		}""",
     """		// 3) 兵线聚集 → 优先清兵
		if (ScanLaneCrowd() >= laneCrowdCount)
		{
			mode = AIMode.farmLane;
			return;
		}

		// 3.2) 能量见底 → 先去找回黄点，不然技能永远放不出来
		if (CurrentSpRate() < lowSpRate)
		{
			Transform spPoint = FindPickup();
			if ((bool)spPoint)
			{
				mode = AIMode.contestPickup;
				return;
			}
		}""",
     "low sp pickup"),
])

print("DONE")
