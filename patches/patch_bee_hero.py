import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 在 DoAttackSplash 里，OverlapSphere 之后追加"对象遍历"补充命中
old = """		int hurt = 0;
		for (int i = 0; i < hits.Length; i++)"""

new = """		int hurt = 0;

		// 关键：英雄用的是 CharacterController，Physics.OverlapSphere 搜不到它
		// （实测半径 3/5 下候选列表里永远只有地面和同类）。
		// 所以额外用对象遍历补一遍英雄与小兵。
		Hero[] allHeroes = Object.FindObjectsOfType<Hero>();
		for (int hi = 0; hi < allHeroes.Length; hi++)
		{
			Hero h = allHeroes[hi];
			if (!(bool)h || !(bool)h.life || h.life.lifeValue <= 0)
			{
				continue;
			}
			if (!(bool)h.spawn || h.spawn.race == info.race)
			{
				continue;
			}
			if (Vector3.Distance(h.transform.position, center) > aoeRadius)
			{
				continue;
			}
			AttackSetting hst = new AttackSetting();
			hst._physicsAttack = dmg;
			int hb = h.life.lifeValue;
			h.life.injure(new AttackInfo
			{
				attackSetting = hst,
				attackTypeIndex = src.attackTypeIndex,
				characterInfo = info,
				harmType = Life.HarmType.other
			}, out int hpa, out int hma);
			int ha = h.life.lifeValue;
			if (hurt <= 2)
			{
				Debug.Log(string.Concat("[Bee] HIT HERO ", h.name,
					" life ", hb, "->", ha,
					" atk=", dmg, " dist=",
					Vector3.Distance(h.transform.position, center).ToString("0.0"),
					" race=", h.spawn.race));
			}
			hurt++;
		}

		for (int i = 0; i < hits.Length; i++)"""

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
