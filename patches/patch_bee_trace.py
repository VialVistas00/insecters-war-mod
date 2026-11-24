import io
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

SRC = r"D:\游戏\Insecters War\iw-opensource\src"
DIS = r"D:\游戏\Insecters War\iw-opensource\src_disabled"

# ---------- 1. 再次停用技能分支 ----------
for f in ["HeroSkillBranch.cs", "SwordBranchBehaviour.cs",
          "SwordBranchEffect.cs", "RoomSkillBranchPanel.cs"]:
    srcf = os.path.join(SRC, f)
    dstf = os.path.join(DIS, f)
    if os.path.exists(srcf):
        shutil.move(srcf, dstf)
        print("disabled:", f)

hs = os.path.join(SRC, "HeroSetting.cs")
s = io.open(hs, encoding="utf-8-sig").read()
old = """		// 光剑战士（battleFrontHero）走技能分支系统：接管 U 键
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
new = """		// 技能分支系统暂停中（源码在 src_disabled/）"""
if old in s:
    s = s.replace(old, new, 1)
    io.open(hs, "w", encoding="utf-8", newline="\n").write(s)
    print("ok: HeroSetting attach removed")

nr = os.path.join(SRC, "NetworkRoomGUI2.cs")
s = io.open(nr, encoding="utf-8-sig").read()
old = """		// 房间界面挂「U 技能分支」切换按钮（IMGUI 叠加，不改预制体）
		RoomSkillBranchPanel.Ensure(this);"""
new = """		// 技能分支房间按钮暂停中（源码在 src_disabled/）"""
if old in s:
    s = s.replace(old, new, 1)
    io.open(nr, "w", encoding="utf-8", newline="\n").write(s)
    print("ok: NetworkRoomGUI2 Ensure removed")

# ---------- 2. 生化蜂链路日志 ----------
p = os.path.join(SRC, "SphereHarmByDetector.cs")
s = io.open(p, encoding="utf-8-sig").read()

# 2a. enableHarm 入口
old = """	public void enableHarm()
	{
		base.enabled = true;
	}"""
new = """	public void enableHarm()
	{
		base.enabled = true;
		if (Time.frameCount % 30 == 0)
		{
			Debug.Log(string.Concat("[SphereHarm] enableHarm on ",
				base.gameObject.name, " radius=", harmRadius,
				" dmg=", attackSetting._physicsAttack));
		}
	}"""
if old in s:
    s = s.replace(old, new, 1)
    print("ok: enableHarm log")

# 2b. Update 里的销毁前日志
old2 = """	private void Update()
	{
		if (base.enabled)
		{
			impHarm();
		}
		base.enabled = false;
		UnityEngine.Object.Destroy(base.gameObject);
	}"""
new2 = """	private void Update()
	{
		if (base.enabled)
		{
			impHarm();
		}
		else if (Time.frameCount % 120 == 0)
		{
			Debug.Log(string.Concat("[SphereHarm] idle-destroy ", base.gameObject.name,
				" radius=", harmRadius));
		}
		base.enabled = false;
		UnityEngine.Object.Destroy(base.gameObject);
	}"""
if old2 in s:
    s = s.replace(old2, new2, 1)
    print("ok: Update log")

# 2c. doHarm 入口日志（不管是否命中）
old3 = """		if (!(bool)pDetector || pData == null || pData.characterInfoObject == null)
		{
			return;
		}"""
new3 = """		if (!(bool)pDetector || pData == null || pData.characterInfoObject == null)
		{
			Debug.Log(string.Concat("[SphereHarm] doHarm ABORT detector=", (bool)pDetector,
				" data=", pData != null,
				" info=", pData != null && pData.characterInfoObject != null));
			return;
		}
		if (Time.frameCount % 30 == 0)
		{
			Debug.Log(string.Concat("[SphereHarm] doHarm entry src=",
				pData.characterInfoObject.name, " radius=", pData.harmRadius,
				" dmg=", pData.attackSetting._physicsAttack,
				" detector=", pDetector.GetType().Name));
		}"""
if old3 in s:
    s = s.replace(old3, new3, 1)
    print("ok: doHarm entry log")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
