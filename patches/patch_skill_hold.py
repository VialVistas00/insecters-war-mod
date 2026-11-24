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


must(
    """	/// <summary>技能诊断节流（排查"AI 不放技能"用）。</summary>
	private float nextSkillDiagTime;""",
    """	/// <summary>技能诊断节流（排查"AI 不放技能"用）。</summary>
	private float nextSkillDiagTime;

	// ---- 技能按住窗口 ----
	// Hero.processAction 里当前动作不为空时不会立刻切新动作，
	// 只发一帧技能命令会被正在进行的普攻吃掉。这里记录"要按哪个技能"，
	// 在窗口内每帧都把它压进命令，才能可靠切进技能。

	private float skillHoldUntil;

	/// <summary>位掩码：1=action1, 2=action2, 4=action3。</summary>
	private int skillHoldSlot;""",
    "hold fields")

# 选中技能时记录窗口
must(
    """		// 依次尝试 action1 / action2 / action3
		SoldierAction chosen = null;
		if ((bool)hero.action1 && hero.action1.canDo)
		{
			chosen = hero.action1;
			actionCommand.Action1 = true;
			actionCommand.Action1Click = true;
		}
		else if ((bool)hero.action2 && hero.action2.canDo)
		{
			chosen = hero.action2;
			actionCommand.Action2 = true;
			actionCommand.Action2Click = true;
		}
		else if ((bool)hero.action3 && hero.action3.canDo)
		{
			chosen = hero.action3;
			actionCommand.Action3 = true;
			actionCommand.Action3Click = true;
		}""",
    """		// 依次尝试 action1 / action2 / action3
		SoldierAction chosen = null;
		int slot = 0;
		if ((bool)hero.action1 && hero.action1.canDo)
		{
			chosen = hero.action1;
			slot = 1;
		}
		else if ((bool)hero.action2 && hero.action2.canDo)
		{
			chosen = hero.action2;
			slot = 2;
		}
		else if ((bool)hero.action3 && hero.action3.canDo)
		{
			chosen = hero.action3;
			slot = 4;
		}
		if (slot != 0)
		{
			// 开一个 0.3 秒的"按住窗口"，期间每帧都压这个技能位
			skillHoldSlot = slot;
			skillHoldUntil = Time.time + 0.3f;
			actionCommand.Fire = false;
			ApplySkillHold();
		}""",
    "chosen slot")

# 追加 ApplySkillHold 方法
must(
    """	/// <summary>自己当前 SP 比例（0~1）。</summary>""",
    """	/// <summary>把"当前要按的技能"压进命令（窗口内每帧调用）。</summary>
	private void ApplySkillHold()
	{
		if (Time.time >= skillHoldUntil)
		{
			skillHoldSlot = 0;
			return;
		}
		// 技能优先：把普攻位清掉，否则 processAction 会先走普攻分支
		actionCommand.Fire = false;
		if ((skillHoldSlot & 1) != 0)
		{
			actionCommand.Action1 = true;
			actionCommand.Action1Click = true;
		}
		if ((skillHoldSlot & 2) != 0)
		{
			actionCommand.Action2 = true;
			actionCommand.Action2Click = true;
		}
		if ((skillHoldSlot & 4) != 0)
		{
			actionCommand.Action3 = true;
			actionCommand.Action3Click = true;
		}
	}

	/// <summary>自己当前 SP 比例（0~1）。</summary>""",
    "ApplySkillHold")

# Update 里每帧调用
must(
    """		// 吃补给点：补跳 / 超时放弃
		UpdatePickupProgress();""",
    """		// 技能按住窗口：窗口内每帧都把技能位压进命令
		ApplySkillHold();

		// 吃补给点：补跳 / 超时放弃
		UpdatePickupProgress();""",
    "call hold")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
