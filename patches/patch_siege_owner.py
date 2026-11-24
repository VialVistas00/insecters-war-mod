import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroAI.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must_replace(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# ConsiderBuildingLife：种族优先从 CharacterInfoObject 读
must_replace(
    """	private void ConsiderBuildingLife(Life pLife, Transform pTransform, Race pMyRace, ref float pBest)
	{
		if (!(bool)pLife || !(bool)pTransform)
		{
			return;
		}
		if (pLife.characterInfo == null || pLife.characterInfo.race == pMyRace)
		{
			return;
		}
		if (pLife.lifeValue <= 0)
		{
			return;
		}""",
    """	private void ConsiderBuildingLife(Life pLife, Transform pTransform, Race pMyRace, ref float pBest)
	{
		if (!(bool)pLife || !(bool)pTransform)
		{
			return;
		}
		if (pLife.lifeValue <= 0)
		{
			return;
		}
		// 建筑的种族优先从 CharacterInfoObject 读 —— StrongholdBuilding 是在
		// characterInfoObject.characterInfo 上写 race，而 Life.characterInfo 常为 null，
		// 早先只读 Life 就一个建筑都找不到。
		Race owner = Race.eNone;
		CharacterInfoObject cio = pTransform.GetComponentInChildren<CharacterInfoObject>();
		if ((bool)cio && cio.characterInfo != null)
		{
			owner = cio.characterInfo.race;
		}
		if (owner == Race.eNone && pLife.characterInfo != null)
		{
			owner = pLife.characterInfo.race;
		}
		if (owner == Race.eNone)
		{
			// 判不出归属的建筑不打，避免打自己家
			return;
		}
		if (owner == pMyRace)
		{
			return;
		}""",
    "building race")

# StrongholdBuilding 直接传它自己的 characterInfoObject 语义
must_replace(
    """		StrongholdBuilding[] shs = Object.FindObjectsOfType<StrongholdBuilding>();
		for (int k = 0; k < shs.Length; k++)
		{
			StrongholdBuilding sb = shs[k];
			if ((bool)sb && (bool)sb.life)
			{
				ConsiderBuildingLife(sb.life, sb.transform, myRace, ref best);
			}
		}""",
    """		StrongholdBuilding[] shs = Object.FindObjectsOfType<StrongholdBuilding>();
		for (int k = 0; k < shs.Length; k++)
		{
			StrongholdBuilding sb = shs[k];
			if (!(bool)sb || !(bool)sb.life)
			{
				continue;
			}
			// 据点建筑上直接有 characterInfoObject，优先用它判归属
			Race owner = Race.eNone;
			if ((bool)sb.characterInfoObject && sb.characterInfoObject.characterInfo != null)
			{
				owner = sb.characterInfoObject.characterInfo.race;
			}
			if (owner == myRace || owner == Race.eNone)
			{
				continue;
			}
			float d = Vector3.Distance(base.transform.position, sb.transform.position);
			if (sb.life.lifeValue > 0 && d < best)
			{
				best = d;
				siegeTarget = sb.transform;
				siegeTargetLife = sb.life;
			}
		}""",
    "stronghold direct")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
