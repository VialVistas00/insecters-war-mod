import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\AirDropAnimation.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = '''		Collider[] hits = Physics.OverlapSphere(center, minBlastRadius, damageMask);
		for (int j = 0; j < hits.Length; j++)
		{
			Collider c = hits[j];
			if (!(bool)c || c.isTrigger)
			{
				continue;
			}
			WMGameObject wm = WMGameObject.getFromTransform(c.transform);
			if (!(bool)wm)
			{
				continue;
			}
			float dist = Vector3.Distance(c.ClosestPointOnBounds(center), center);
			float rate = Mathf.Clamp01(1f - dist / minBlastRadius);
			float scale = 0.35f + 0.65f * rate;
			AttackSetting attack = new AttackSetting();
			attack._physicsAttack = (int)(forceDamage * scale);
			attack._magicAttack = (int)(forceDamage * scale);
			wm.injure(new AttackInfo
			{
				attackSetting = attack,
				attackTypeIndex = 0,
				characterInfo = characterInfo,
				harmType = Life.HarmType.explode
			});
		}
	}'''

new = '''		// 掩码兜底：damageMask 在预制体上没配（=0）时，OverlapSphere 一个都找不到，
		// 表现就是"轰炸完全没伤害"。用施法者种族的敌方掩码替代。
		int mask = damageMask;
		if (mask == 0)
		{
			if (characterInfo != null && characterInfo.race != Race.eNone)
			{
				Race enemyRace = PlayerInfo.getAdversaryRace(characterInfo.race);
				mask = (int)PlayerInfo.getRaceObjectValue(enemyRace);
			}
			else
			{
				mask = -1;
			}
		}

		Collider[] hits = Physics.OverlapSphere(center, minBlastRadius, mask);
		int hurt = 0;
		for (int j = 0; j < hits.Length; j++)
		{
			Collider c = hits[j];
			if (!(bool)c || c.isTrigger)
			{
				continue;
			}
			WMGameObject wm = WMGameObject.getFromTransform(c.transform);
			if (!(bool)wm)
			{
				continue;
			}
			// 不打自己人
			if ((bool)wm.life && characterInfo != null && wm.life.characterInfo != null
				&& wm.life.characterInfo.race == characterInfo.race)
			{
				continue;
			}
			float dist = Vector3.Distance(c.ClosestPointOnBounds(center), center);
			float rate = Mathf.Clamp01(1f - dist / minBlastRadius);
			float scale = 0.35f + 0.65f * rate;
			AttackSetting attack = new AttackSetting();
			attack._physicsAttack = (int)(forceDamage * scale);
			attack._magicAttack = (int)(forceDamage * scale);
			int before = (bool)wm.life ? wm.life.lifeValue : -1;
			wm.injure(new AttackInfo
			{
				attackSetting = attack,
				attackTypeIndex = 0,
				characterInfo = characterInfo,
				harmType = Life.HarmType.explode
			});
			int after = (bool)wm.life ? wm.life.lifeValue : -1;
			hurt++;
			if (hurt <= 3)
			{
				Debug.Log(string.Concat("[AirDrop] hit ", wm.name,
					" life ", before, " -> ", after,
					" dmg=", (int)(forceDamage * scale)));
			}
		}
		Debug.Log(string.Concat("[AirDrop] blast at ",
			center.x.ToString("0.0"), ",", center.y.ToString("0.0"),
			" mask=", mask, " radius=", minBlastRadius,
			" colliders=", hits.Length, " hurt=", hurt,
			" caster=", (characterInfo != null) ? characterInfo.race.ToString() : "null"));
	}'''

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: blast diag + mask fallback")
