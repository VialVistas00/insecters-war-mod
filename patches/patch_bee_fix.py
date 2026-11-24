import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SphereHarmByDetector.cs"
s = io.open(p, encoding="utf-8-sig").read()


def must(old, new, label):
    global s
    if old not in s:
        raise SystemExit("ANCHOR MISSING: " + label)
    s = s.replace(old, new, 1)
    print("ok:", label)


# 1) SphereHarmData 增加自身 Life，用于 characterInfo 兜底
must(
    """		public CharacterInfoObject characterInfoObject;

		public bool divideDamage;""",
    """		public CharacterInfoObject characterInfoObject;

		/// <summary>自身 Life，characterInfoObject 没配时用它取 characterInfo。</summary>
		public Life selfLife;

		public bool divideDamage;""",
    "data field")

# 2) nowData 填充
must(
    """			sphereHarmData.characterInfoObject = characterInfoObject;""",
    """			sphereHarmData.characterInfoObject = characterInfoObject;
			sphereHarmData.selfLife = life;""",
    "nowData")

# 3) doHarm 入口：不再因为 characterInfoObject 为空就放弃
must(
    """		if (!(bool)pDetector || pData == null || pData.characterInfoObject == null)
		{
			Debug.Log(string.Concat("[SphereHarm] doHarm ABORT detector=", (bool)pDetector,
				" data=", pData != null,
				" info=", pData != null && pData.characterInfoObject != null));
			return;
		}""",
    """		if (!(bool)pDetector || pData == null)
		{
			return;
		}
		// 关键修复：很多攻击（生化蜂的 smallAttack / bigAttack / swoopAttack）
		// 身上根本没配 characterInfoObject，原版这里直接 return，
		// 表现就是"这个兵种完全打不出伤害"。
		// 这里退化到用组件自己的 Life.characterInfo。
		CharacterInfo attackInfo = null;
		if (pData.characterInfoObject != null)
		{
			attackInfo = pData.characterInfoObject.characterInfo;
		}
		if (attackInfo == null && pData.selfLife != null)
		{
			attackInfo = pData.selfLife.characterInfo;
		}
		if (attackInfo == null)
		{
			return;
		}""",
    "doHarm guard")

# 4) 伤害结算改用兜底后的 characterInfo
must(
    """				characterInfo = pData.characterInfoObject.characterInfo,""",
    """				characterInfo = attackInfo,""",
    "attack info use")

# 5) 诊断日志改用兜底后的信息来源
must(
    """			Debug.Log(string.Concat("[SphereHarm] doHarm entry src=",
				pData.characterInfoObject.name, " radius=", pData.harmRadius,
				" dmg=", pData.attackSetting._physicsAttack,
				" detector=", pDetector.GetType().Name));""",
    """			Debug.Log(string.Concat("[SphereHarm] doHarm entry src=",
				(pData.characterInfoObject != null) ? pData.characterInfoObject.name
					: ((pData.selfLife != null) ? pData.selfLife.name : "-"),
				" radius=", pData.harmRadius,
				" dmg=", pData.attackSetting._physicsAttack,
				" race=", attackInfo.race,
				" detector=", pDetector.GetType().Name));""",
    "diag use")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
