import io
import sys

sys.stdout.reconfigure(encoding="utf-8")


def patch(path, pairs):
    s = io.open(path, encoding="utf-8-sig").read()
    ok = True
    for old, new, label in pairs:
        if old not in s:
            print("SKIP (anchor missing):", label)
            ok = False
            continue
        s = s.replace(old, new, 1)
        print("ok:", label)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    return ok


# 1) SkillBarrier：新增字段被预制体反序列化成 0 → 墙拆不掉
patch(r"D:\游戏\Insecters War\iw-opensource\src\SkillBarrier.cs", [
    ("""	private void ApplyEnemyBreak()
	{""",
     """	private void ApplyEnemyBreak()
	{
		// Unity 陷阱：这几个字段是后加的，预制体里没有序列化数据，
		// 运行时会被填成 0（radius 0 = 查不到敌人，dps 0 = 不掉血）。
		if (enemyBreakDps <= 0.05f)
		{
			enemyBreakDps = 260f;
		}
		if (breakCheckRadius <= 0.05f)
		{
			breakCheckRadius = 1.6f;
		}
		if (breakCheckInterval <= 0.005f)
		{
			breakCheckInterval = 0.2f;
		}""",
     "barrier fallback"),
])

# 2) SphereHarmByDetector：noDivide 被反序列化成 false → 又变回均摊
patch(r"D:\游戏\Insecters War\iw-opensource\src\SphereHarmByDetector.cs", [
    ("""		float num3 = ((!pData.divideDamage) ? 1f : (1f / (float)dictionary.Count));""",
     """		// 本改版：移除"按命中数均摊"。
		// noDivide 是后加字段，预制体反序列化会把它冲成 false，
		// 所以这里不再依赖该字段，直接让每个目标都吃满按距离衰减后的伤害
		// （原版蚂蚁光剑 U 打 3 个目标每个只吃 1/3、蜜蜂却不分摊，手感不一致）。
		float num3 = 1f;""",
     "no divide"),
])

print("DONE")
