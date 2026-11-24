import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 1) 掩码改成敌方种族层（与 DefenseTower.Init 一致）
old = """		Vector3 center = base.transform.position;
		// 掩码必须放宽：实测 PlayerInfo.getRaceObjectValue(敌方) 在这个场景里
		// 一个碰撞体都搜不到（日志 colliders=0），所以直接搜全部层，
		// 靠下面的 CharacterInfo.race 判断敌我。
		int rawMask = (int)PlayerInfo.getRaceObjectValue(PlayerInfo.getAdversaryRace(info.race));
		int mask = -1;"""
new = """		Vector3 center = base.transform.position;
		// 用引擎自己的「敌方种族层」做掩码 —— DefenseTower.Init 里就是这么算的：
		//   1 << PlayerInfo.getRaceLayer(adversaryRace)
		// 之前用 getRaceObjectValue 搜出来的是自己人，改成这个才对准敌人。
		Race beeEnemyRace = PlayerInfo.getAdversaryRace(info.race);
		int enemyLayer = PlayerInfo.getRaceLayer(beeEnemyRace);
		int rawMask = (int)PlayerInfo.getRaceObjectValue(beeEnemyRace);
		int mask = -1;
		if (enemyLayer > 0 && enemyLayer < 32)
		{
			mask = 1 << enemyLayer;
		}"""
if old not in s:
    raise SystemExit("ANCHOR MISSING mask")
s = s.replace(old, new, 1)

# 2) 友军过滤只保留「排除自身」，不再按层判种族（掩码已经限定了敌方层）
old2 = """			int cLayer = c.gameObject.layer;
			int pLayer = (bool)c.transform.parent ? c.transform.parent.gameObject.layer : cLayer;
			// 己方建筑层也要排除，否则会打自己家的基地/塔
			int myBuildingLayer = PlayerInfo.getBuildingLayer(info.race);
			bool isFriend = (cLayer == myLayer) || (pLayer == myLayer)
				|| (myBuildingLayer > 0 && (cLayer == myBuildingLayer || pLayer == myBuildingLayer));
			if (isFriend)
			{
				continue;
			}"""
new2 = """			int cLayer = c.gameObject.layer;
			// 掩码已经限定在敌方种族层内，这里只额外排除"自己所在层"，
			// 防止把同族单位当成敌人。
			if (cLayer == myLayer)
			{
				continue;
			}"""
if old2 not in s:
    raise SystemExit("ANCHOR MISSING friend")
s = s.replace(old2, new2, 1)

# 3) 日志里带上敌方层号
old3 = """				" race=", info.race, " rawMask=", rawMask,"""
new3 = """				" race=", info.race, " enemyLayer=", enemyLayer, " mask=", mask,"""
if old3 in s:
    s = s.replace(old3, new3, 1)
    print("ok: log")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
