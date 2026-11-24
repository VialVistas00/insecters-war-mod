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
    """		// 3) 有残血敌人 → 追击
		if (FindGankTarget() != null)""",
    """		// 2.5) 能量见底 → 先去找回黄点，不然技能永远放不出来
		if (CurrentSpRate() < lowSpRate)
		{
			Transform spPoint = FindPickup();
			if ((bool)spPoint)
			{
				mode = AIMode.contestPickup;
				return;
			}
		}

		// 3) 有残血敌人 → 追击
		if (FindGankTarget() != null)""",
    "low sp branch")

# CurrentSpRate 辅助
must(
    """	/// <summary>自己血量比例。</summary>""",
    """	/// <summary>自己当前 SP 比例（0~1）。</summary>
	private float CurrentSpRate()
	{
		if (!(bool)hero || !(bool)hero.actionEnergyValue)
		{
			return 1f;
		}
		ActionEnergyValue e = hero.actionEnergyValue;
		if (e.fullValue <= 0f)
		{
			return 1f;
		}
		return Mathf.Clamp01(e.nowValue / e.fullValue);
	}

	/// <summary>自己血量比例。</summary>""",
    "CurrentSpRate")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
