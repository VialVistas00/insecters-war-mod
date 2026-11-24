import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = """		Vector3 center = base.transform.position;
		int mask = (int)PlayerInfo.getRaceObjectValue(PlayerInfo.getAdversaryRace(info.race));
		if (mask == 0)
		{
			mask = -1;
		}

		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);"""

new = """		Vector3 center = base.transform.position;
		// 掩码必须放宽：实测 PlayerInfo.getRaceObjectValue(敌方) 在这个场景里
		// 一个碰撞体都搜不到（日志 colliders=0），所以直接搜全部层，
		// 靠下面的 CharacterInfo.race 判断敌我。
		int rawMask = (int)PlayerInfo.getRaceObjectValue(PlayerInfo.getAdversaryRace(info.race));
		int mask = -1;

		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);"""

if old not in s:
    raise SystemExit("ANCHOR MISSING mask")
s = s.replace(old, new, 1)

# 诊断里带上两种掩码值
old2 = """			Debug.Log(string.Concat("[Bee] attack idx=", pHarmIndex,
				" dmg=", dmg, " radius=", aoeRadius,
				" colliders=", hits.Length, " hurt=", hurt,
				" race=", info.race));"""
new2 = """			Debug.Log(string.Concat("[Bee] attack idx=", pHarmIndex,
				" dmg=", dmg, " radius=", aoeRadius,
				" colliders=", hits.Length, " hurt=", hurt,
				" race=", info.race, " rawMask=", rawMask,
				" pos=", center.x.ToString("0.0"), ",", center.y.ToString("0.0")));"""
if old2 not in s:
    raise SystemExit("ANCHOR MISSING diag")
s = s.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
