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


# 1) 卡住判定放宽：0.12 -> 0.25
must("""	public float stuckDistance = 0.12f;""",
     """	// 0.6 秒必须位移超过这个值才算"没卡住"。
	// 原来 0.12 太敏感：起步、转向、被打退都会低于它，导致频繁误判自救。
	public float stuckDistance = 0.25f;""",
     "stuckDistance")

# 2) 绕行方向改成朝目标，不再随机反向
must("""			PausePath();
			if ((bool)hero && (bool)hero.tileCharacter)
			{
				int sign = (Random.value > 0.5f) ? 1 : -1;
				Vector2 p = base.transform.position;
				processAim(new IVector2(
					ifloat.ConvertToData(p.x + sign * 2.5f),
					ifloat.ConvertToData(p.y + 1.5f)));
			}""",
     """			PausePath();
			if ((bool)hero && (bool)hero.tileCharacter)
			{
				// 绕行方向要朝目标，不能随机反向 —— 随机反向有一半概率是往回走，
				// 会把 AI 带离战场，看起来就像"在原地来回转圈"。
				Transform aimTgt = ResolveMoveTarget();
				int sign = 1;
				if ((bool)aimTgt)
				{
					sign = (aimTgt.position.x >= base.transform.position.x) ? 1 : -1;
				}
				Vector2 p = base.transform.position;
				processAim(new IVector2(
					ifloat.ConvertToData(p.x + sign * 2.5f),
					ifloat.ConvertToData(p.y + 1.5f)));
			}""",
     "detour direction")

# 3) 拆塔门槛放宽，让它更愿意跟兵线推塔
must("""	public float siegeMinHealthRate = 0.72f;""",
     """	public float siegeMinHealthRate = 0.6f;""",
     "siege health")

must("""	public int siegeDangerAllies = 2;""",
     """	public int siegeDangerAllies = 1;""",
     "siege danger allies")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
