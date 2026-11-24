import io
import shutil
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = r"D:\游戏\Insecters War\iw-opensource\src"
DIS = r"D:\游戏\Insecters War\iw-opensource\src_disabled"

# ---------------- 1. SphereHarm 命中日志 ----------------
p = os.path.join(SRC, "SphereHarmByDetector.cs")
s = io.open(p, encoding="utf-8-sig").read()
old = """		float num3 = 1f;"""
new = """		float num3 = 1f;
		if (Time.frameCount % 45 == 0)
		{
			Debug.Log(string.Concat("[SphereHarm] hits=", dictionary.Count,
				" radius=", pData.harmRadius,
				" dmg=", pData.attackSetting._physicsAttack,
				" src=", (pData.characterInfoObject != null) ? pData.characterInfoObject.name : "-"));
		}"""
if old not in s:
    raise SystemExit("anchor missing: sphereharm")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: sphereharm diag")

# ---------------- 2. 恢复技能分支文件 ----------------
files = ["HeroSkillBranch.cs", "SwordBranchBehaviour.cs",
         "SwordBranchEffect.cs", "RoomSkillBranchPanel.cs"]
for f in files:
    srcf = os.path.join(DIS, f)
    dstf = os.path.join(SRC, f)
    if os.path.exists(srcf):
        shutil.copy2(srcf, dstf)
        print("restored:", f)
    else:
        print("missing (already restored?):", f)

# ---------------- 3. 取消两处挂载注释 ----------------
hs = os.path.join(SRC, "HeroSetting.cs")
s = io.open(hs, encoding="utf-8-sig").read()
old = """		// 技能分支系统已暂停（源码在 src_disabled/），此处不再挂载。
		// 恢复时把 src_disabled/SwordBranchBehaviour.cs 移回 src/ 并还原下面两行：
		//   Hero lHero = pObject.GetComponent<Hero>();
		//   if ((bool)lHero) SwordBranchBehaviour.Attach(lHero);"""
new = """		// 光剑战士（battleFrontHero）走技能分支系统：接管 U 键
		if (spawn != null && spawn.heroType == IWHeroType.battleFrontHero)
		{
			Hero lHero = pObject.GetComponent<Hero>();
			if ((bool)lHero)
			{
				SwordBranchBehaviour.Attach(lHero);
			}
			Debug.Log(string.Concat("[SwordBranch] attach onBirth heroType=",
				spawn.heroType, " hero=", (bool)lHero));
		}"""
if old in s:
    s = s.replace(old, new, 1)
    io.open(hs, "w", encoding="utf-8", newline="\n").write(s)
    print("ok: HeroSetting attach restored")
else:
    print("SKIP: HeroSetting already patched")

nr = os.path.join(SRC, "NetworkRoomGUI2.cs")
s = io.open(nr, encoding="utf-8-sig").read()
old = """		// 技能分支系统已暂停（源码在 src_disabled/RoomSkillBranchPanel.cs）。
		// 恢复时把该文件移回 src/ 并取消下一行注释：
		// RoomSkillBranchPanel.Ensure(this);"""
new = """		// 房间界面挂「U 技能分支」切换按钮（IMGUI 叠加，不改预制体）
		RoomSkillBranchPanel.Ensure(this);"""
if old in s:
    s = s.replace(old, new, 1)
    io.open(nr, "w", encoding="utf-8", newline="\n").write(s)
    print("ok: NetworkRoomGUI2 Ensure restored")
else:
    print("SKIP: NetworkRoomGUI2 already patched")

print("DONE")
