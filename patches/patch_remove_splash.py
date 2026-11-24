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


# 1) 去掉自动结算调用（信号槽修好后由原版机制触发 impHarm）
must("""		// 攻击结算：不依赖下面那条「发现目标 → 发 Fire」的链路，
		// 只要范围内有敌人就按 attackInterval 节奏打一次。
		// （原版蜂身上那 3 个 SphereHarmByDetector 只在死亡时启用，攻击流程从不调用）
		DoAttackSplash(0);

""", """		// 攻击伤害由原版机制结算：
		// zzOnAction.addEventReceiver → SphereHarmByDetector.impHarm()
		// （此前信号槽因为签名不匹配绑不上，现已通过补无参 impHarm() 重载修好）
""", "remove auto splash")

# 2) 俯冲的额外结算也去掉（同样由原版 impHarm 负责）
must("""				actionCommandControl.setCommand(actionCommand);
				DoAttackSplash(2);""",
     """				actionCommandControl.setCommand(actionCommand);""",
     "remove swoop splash")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
