import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 1) 半径兜底放大到 5
must("""		if (aoeRadius <= 0.05f)
		{
			aoeRadius = 3f;
		}""",
     """		if (aoeRadius <= 0.05f)
		{
			aoeRadius = 5f;
		}""",
     "radius 5")

# 2) 敌我判断：排除自己 + CharacterInfoObject 兜底 + 判不出就不打
must("""			WMGameObject wm = WMGameObject.getFromTransform(c.transform);
			if (!(bool)wm || !(bool)wm.life)
			{
				continue;
			}
			if (wm.life.characterInfo != null && wm.life.characterInfo.race == info.race)
			{
				continue;
			}""",
     """			WMGameObject wm = WMGameObject.getFromTransform(c.transform);
			if (!(bool)wm || !(bool)wm.life)
			{
				continue;
			}
			// 绝不打自己：自身与子物体直接跳过
			if (wm.transform == base.transform || wm.transform.IsChildOf(base.transform))
			{
				continue;
			}
			// 敌我判断：Life.characterInfo 常常是 null（蜂自己就是），
			// 退化到 CharacterInfoObject；两个都判不出来就不打，避免同族互殴。
			Race tgtRace = Race.eNone;
			if (wm.life.characterInfo != null)
			{
				tgtRace = wm.life.characterInfo.race;
			}
			else
			{
				CharacterInfoObject cio = wm.GetComponent<CharacterInfoObject>();
				if (!(bool)cio)
				{
					cio = wm.GetComponentInChildren<CharacterInfoObject>();
				}
				if ((bool)cio && cio.characterInfo != null)
				{
					tgtRace = cio.characterInfo.race;
				}
			}
			if (tgtRace == Race.eNone)
			{
				continue;
			}
			if (tgtRace == info.race)
			{
				continue;
			}""",
     "friend filter")

# 3) 日志改用已算好的 tgtRace
must("""					" myRace=", info.race,
					" tgtRace=", (bool)wm.life && wm.life.characterInfo != null ? wm.life.characterInfo.race.ToString() : "-"));""",
     """					" myRace=", info.race,
					" tgtRace=", tgtRace));""",
     "log race")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
