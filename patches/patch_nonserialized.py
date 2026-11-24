import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = r"D:\游戏\Insecters War\iw-opensource\src"

# (文件, 原字段声明片段, 替换后)
JOBS = [
    # 1. SphereHarmByDetector: noDivide 已不再使用，直接删掉，恢复序列化布局
    ("SphereHarmByDetector.cs",
     """	/// <summary>
	/// 关闭"按命中目标数均摊"。
	/// 原版 divideDamage=true 时，范围内每个单位只吃到 base/N（N=命中数），
	/// 而蜜蜂同类技能不分摊 —— 同一招两边手感完全不同。
	/// 本改版默认关闭均摊：每个目标都吃满按距离衰减后的伤害。
	/// </summary>
	public bool noDivide = true;""",
     """	// 注意：这里不能加新的 public 字段。
	// SphereHarmByDetector 的实例是随地图文件序列化保存的，
	// 一旦多出字段，Unity 反序列化时会报
	// "different serialization layout when loading"，
	// 整个组件的 attackSetting / characterInfoObject 都会失效 → 伤害归零。"""),

    # 2. AirDropAnimation
    ("AirDropAnimation.cs",
     """	public float minBlastRadius = 3.2f;""",
     """	[System.NonSerialized]
	public float minBlastRadius = 3.2f;"""),
    ("AirDropAnimation.cs",
     """	public float forceDamage = 45f;""",
     """	[System.NonSerialized]
	public float forceDamage = 45f;"""),

    # 3. SkillBarrier
    ("SkillBarrier.cs",
     """	public float enemyBreakDps = 260f;""",
     """	[System.NonSerialized]
	public float enemyBreakDps = 260f;"""),
    ("SkillBarrier.cs",
     """	public float breakCheckRadius = 1.6f;""",
     """	[System.NonSerialized]
	public float breakCheckRadius = 1.6f;"""),
    ("SkillBarrier.cs",
     """	public float breakCheckInterval = 0.2f;""",
     """	[System.NonSerialized]
	public float breakCheckInterval = 0.2f;"""),

    # 4. SoldierListFactoryUpdate
    ("SoldierListFactoryUpdate.cs",
     """	public int waveIndex;""",
     """	[System.NonSerialized]
	public int waveIndex;"""),
    ("SoldierListFactoryUpdate.cs",
     """	public float waveHealthGrowth = 0.06f;""",
     """	[System.NonSerialized]
	public float waveHealthGrowth = 0.06f;"""),
    ("SoldierListFactoryUpdate.cs",
     """	public float waveHealthMaxMultiplier = 3f;""",
     """	[System.NonSerialized]
	public float waveHealthMaxMultiplier = 3f;"""),

    # 5. VariationBeeAI
    ("VariationBeeAI.cs",
     """	public float aoeRadius = 3.0f;""",
     """	[System.NonSerialized]
	public float aoeRadius = 3.0f;"""),
]

for fname, old, new in JOBS:
    p = SRC + "\\" + fname
    s = io.open(p, encoding="utf-8-sig").read()
    # 已经加过标记就跳过
    if "[System.NonSerialized]" in s and old.replace("\t", "")[:40] in s.replace("\t", ""):
        marker = "[System.NonSerialized]\n\t" + old.lstrip("\t")
        if marker.strip() in s:
            print("skip (already):", fname, old.strip().split("=")[0].strip())
            continue
    if old not in s:
        print("MISS:", fname, old.strip().split("=")[0].strip())
        continue
    s = s.replace(old, new, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok:", fname, new.strip().split("=")[0].strip())

print("DONE")
