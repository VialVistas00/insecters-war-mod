import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\Life.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = """		float num = ArmorAndAttack.Singleton.getRate(pAttackInfo.attackTypeIndex, armorTypeIndex);
		CharacterInfo characterInfo = pAttackInfo.characterInfo;
		int totalPhysicsAttack = pAttackInfo.totalPhysicsAttack;"""

new = """		float num = ArmorAndAttack.Singleton.getRate(pAttackInfo.attackTypeIndex, armorTypeIndex);
		CharacterInfo characterInfo = pAttackInfo.characterInfo;
		int totalPhysicsAttack = pAttackInfo.totalPhysicsAttack;
		// 诊断：攻击类型 vs 护甲类型的伤害系数。
		// 系数为 0 时无论伤害多高都打不出血 —— "生化蜂完全没伤害"就可能是这个。
		if (Time.frameCount % 90 == 0 && totalPhysicsAttack > 0)
		{
			Debug.Log(string.Concat("[DmgRate] atkType=", pAttackInfo.attackTypeIndex,
				" armorType=", armorTypeIndex,
				" rate=", num.ToString("0.00"),
				" baseDmg=", totalPhysicsAttack,
				" armor=", physicsArmor,
				" target=", base.gameObject.name,
				" myRace=", (characterInfo != null) ? characterInfo.race.ToString() : "-"));
		}"""

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
