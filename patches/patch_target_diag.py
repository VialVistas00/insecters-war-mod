import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SwordBranchBehaviour.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 1) 把 IsSelfOrAlly 改成返回原因码（便于定位）
old_start = s.index("	private bool IsSelfOrAlly(WMGameObject pWm)")
old_end = s.index("	/// <summary>\n	/// F8 循环切换分支")
new_method = '''	// 跳过原因（诊断用）
	private const int SKIP_NONE = 0;
	private const int SKIP_SELF = 1;
	private const int SKIP_CHILD = 2;
	private const int SKIP_RACE = 3;
	private const int SKIP_LAYER = 4;
	private const int SKIP_UNKNOWN = 5;

	/// <summary>
	/// 判定目标是否可以打；返回 SKIP_NONE 表示"可以打"，其它值是跳过原因。
	/// </summary>
	private int CheckTarget(WMGameObject pWm)
	{
		if (!(bool)pWm)
		{
			return SKIP_UNKNOWN;
		}
		GameObject go = pWm.gameObject;
		if (!(bool)go)
		{
			return SKIP_UNKNOWN;
		}
		// 1) 自己
		if (go == base.gameObject)
		{
			return SKIP_SELF;
		}
		if ((bool)hero && (bool)hero.life && pWm.life == hero.life)
		{
			return SKIP_SELF;
		}
		// 2) 自己的子物体
		Transform t = go.transform;
		if (t == base.transform || t.IsChildOf(base.transform))
		{
			return SKIP_CHILD;
		}
		// 3) 有 characterInfo 时按 race 判（主判据）
		Race myRace = MyRace();
		Life other = pWm.life;
		if ((bool)other && other.characterInfo != null && myRace != Race.eNone)
		{
			return (other.characterInfo.race == myRace) ? SKIP_RACE : SKIP_NONE;
		}
		// 4) layer 兜底
		if (myRace == Race.eNone)
		{
			return SKIP_NONE;
		}
		int l = go.layer;
		int myLayer = PlayerInfo.getRaceLayer(myRace);
		if (l == myLayer)
		{
			return SKIP_LAYER;
		}
		if (myRace == Race.ePismire && l == layers.pismireBuilding)
		{
			return SKIP_LAYER;
		}
		if (myRace == Race.eBee && l == layers.beeBuilding)
		{
			return SKIP_LAYER;
		}
		// 判不出友方 → 当作敌人
		return SKIP_NONE;
	}

	private bool IsSelfOrAlly(WMGameObject pWm)
	{
		return CheckTarget(pWm) != SKIP_NONE;
	}

'''
s = s[:old_start] + new_method + s[old_end:]

# 2) ReleaseBlade：分类计数
s = s.replace(
    """		int count = 0;
		int skipped = 0;""",
    """		int count = 0;
		int skipped = 0;
		int skipSelf = 0;
		int skipChild = 0;
		int skipRace = 0;
		int skipLayer = 0;
		int skipUnknown = 0;""")

s = s.replace(
    """			if (IsSelfOrAlly(wm))
			{
				skipped++;
				continue;
			}
			// 只打向前方（避免背后的目标被误伤）""",
    """			int reason = CheckTarget(wm);
			if (reason != SKIP_NONE)
			{
				skipped++;
				if (reason == SKIP_SELF) { skipSelf++; }
				else if (reason == SKIP_CHILD) { skipChild++; }
				else if (reason == SKIP_RACE) { skipRace++; }
				else if (reason == SKIP_LAYER) { skipLayer++; }
				else { skipUnknown++; }
				continue;
			}
			// 只打向前方（避免背后的目标被误伤）""")

s = s.replace(
    '''" hits=", count, " skipped=", skipped, " colliders=", hits.Length));''',
    '''" hits=", count, " colliders=", hits.Length,
			" skip[self=", skipSelf, " child=", skipChild, " race=", skipRace,
			" layer=", skipLayer, " unk=", skipUnknown, "]",
			" myRace=", MyRace()));''')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok  CheckTarget:", s.count("CheckTarget"), " skipSelf:", s.count("skipSelf"))
