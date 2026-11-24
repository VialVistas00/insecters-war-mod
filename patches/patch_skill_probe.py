import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


must(
    """	private float nextSkillCheckTime;""",
    """	private float nextSkillCheckTime;

	/// <summary>技能诊断节流。</summary>
	private float nextSkillDiagTime;""",
    "diag field")

# 在 TryUseSkill 里插入分支诊断
must(
    """		// SP 判断改为"按局势决定该不该花" ----""",
    """		// 诊断用
		if (Time.time >= nextSkillDiagTime)
		{
			nextSkillDiagTime = Time.time + 3f;
			Debug.Log(string.Concat("[AI] skill probe tgt=", (bool)fireTarget,
				" dist=", Vector2.Distance(base.transform.position, target.position).ToString("0.0"),
				" range=", (shootRange * 1.35f).ToString("0.0"),
				" a1=", (bool)hero.action1 && hero.action1.canDo,
				" a2=", (bool)hero.action2 && hero.action2.canDo,
				" a3=", (bool)hero.action3 && hero.action3.canDo,
				" needClick1=", (bool)hero.action1 && hero.action1.needClick,
				" cmd1=", hero.action1CommandValue,
				" cmd2=", hero.action2CommandValue,
				" cmd3=", hero.action3CommandValue));
		}

		// SP 判断改为"按局势决定该不该花" ----""",
    "probe")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
