import io
import sys

sys.stdout.reconfigure(encoding="utf-8")


def patch(path, pairs):
    s = io.open(path, encoding="utf-8-sig").read()
    for old, new, label in pairs:
        if old not in s:
            raise SystemExit("ANCHOR MISSING in " + path + ": " + label)
        s = s.replace(old, new, 1)
        print("ok:", label)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)


# ---------- 1. 轰炸伤害调低 ----------
patch(r"D:\游戏\Insecters War\iw-opensource\src\AirDropAnimation.cs", [
    ("""		if (minBlastRadius <= 0.05f)
		{
			minBlastRadius = 5f;
		}
		if (forceDamage <= 0.05f)
		{
			forceDamage = 120f;
		}""",
     """		if (minBlastRadius <= 0.05f)
		{
			minBlastRadius = 4f;
		}
		if (forceDamage <= 0.05f)
		{
			// 120 实测过强（一发能清一片），按原版节奏压到 45
			forceDamage = 45f;
		}""",
     "forceDamage 45"),
])

# ---------- 2. 生化蜂：打印目标血量/护盾变化，确认伤害去处 ----------
patch(r"D:\游戏\Insecters War\iw-opensource\src\SphereHarmByDetector.cs", [
    ("""			key.injure(new AttackInfo""",
     """			int beforeLife = (bool)key.life ? key.life.lifeValue : -1;
			int beforeGuard = (bool)key.life ? key.life.guardValue : -1;
			key.injure(new AttackInfo""",
     "before snapshot"),
    ("""		}
	}

	/// <summary>关闭"按命中目标数均摊"。</summary>""",
     """			int afterLife = (bool)key.life ? key.life.lifeValue : -1;
			int afterGuard = (bool)key.life ? key.life.guardValue : -1;
			if (Time.frameCount % 20 == 0 && (beforeLife != afterLife || beforeGuard != afterGuard))
			{
				Debug.Log(string.Concat("[SphereHarm] hit ", key.name,
					" life ", beforeLife, "->", afterLife,
					" guard ", beforeGuard, "->", afterGuard));
			}
		}
	}

	/// <summary>关闭"按命中目标数均摊"。</summary>""",
     "after log"),
])

print("DONE")
