import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = '''		// —— SP 判断改为"按局势决定该不该花" ——
		ActionEnergyValue energy = hero.actionEnergyValue;'''

new = '''		// 诊断：为什么没放技能（节流 3 秒）
		if (Time.time >= nextSkillDiagTime)
		{
			nextSkillDiagTime = Time.time + 3f;
			ActionEnergyValue de = hero.actionEnergyValue;
			float dr = ((bool)de && de.fullValue > 0f) ? (de.nowValue / de.fullValue) : -1f;
			Debug.Log(string.Concat("[AI] skill probe dist=", dist.ToString("0.0"),
				" sp=", dr.ToString("0.00"),
				" a1can=", (bool)hero.action1 && hero.action1.canDo,
				" a2can=", (bool)hero.action2 && hero.action2.canDo,
				" a3can=", (bool)hero.action3 && hero.action3.canDo,
				" click1=", (bool)hero.action1 && hero.action1.needClick,
				" cmd1=", hero.action1CommandValue,
				" cmd2=", hero.action2CommandValue,
				" cmd3=", hero.action3CommandValue,
				" now=", (bool)hero.nowAction));
		}

		// —— SP 判断改为"按局势决定该不该花" ——
		ActionEnergyValue energy = hero.actionEnergyValue;'''

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: probe inserted")
