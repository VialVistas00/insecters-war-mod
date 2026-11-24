import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SwordBranchBehaviour.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 1) 月牙：加 skipped 统计
s = s.replace(
    """			new Vector3(length * 0.5f, bladeWidth * 0.5f, 2f), Quaternion.identity);
		int count = 0;""",
    """			new Vector3(length * 0.5f, bladeWidth * 0.5f, 2f), Quaternion.identity);
		int count = 0;
		int skipped = 0;""")

s = s.replace(
    """			if (IsSelfOrAlly(wm))
			{
				continue;
			}
			// 只打向前方（避免背后的目标被误伤）""",
    """			if (IsSelfOrAlly(wm))
			{
				skipped++;
				continue;
			}
			// 只打向前方（避免背后的目标被误伤）""")

s = s.replace(
    '''" bonus=", bonus, " length=", length.ToString("0.0"), " hits=", count));''',
    '''" bonus=", bonus, " length=", length.ToString("0.0"),
			" hits=", count, " skipped=", skipped, " colliders=", hits.Length));''')

# 2) 环形：加 skipped 统计
s = s.replace(
    """		Collider[] hits = Physics.OverlapSphere(center, ringRadius);
		int count = 0;""",
    """		Collider[] hits = Physics.OverlapSphere(center, ringRadius);
		int count = 0;
		int ringSkipped = 0;""")

s = s.replace(
    """			if (IsSelfOrAlly(wm))
			{
				continue;
			}
			AttackSetting setting = new AttackSetting();
			setting._physicsAttack = (int)(baseAttack._physicsAttack * 1.2f);""",
    """			if (IsSelfOrAlly(wm))
			{
				ringSkipped++;
				continue;
			}
			AttackSetting setting = new AttackSetting();
			setting._physicsAttack = (int)(baseAttack._physicsAttack * 1.2f);""")

s = s.replace(
    '''" bulletsCleared=", cleared));''',
    '''" bulletsCleared=", cleared, " skipped=", ringSkipped,
			" colliders=", hits.Length));''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("skipped:", s.count("skipped"), "ringSkipped:", s.count("ringSkipped"))
