import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 1) 去掉 fire 分支里的重复调用（保留 swoop 的 idx=2）
old1 = """				actionCommandControl.setCommand(actionCommand);
				// 补一次攻击结算：
				// 这张图里生化蜂身上那 3 个 SphereHarmByDetector 只在死亡时
				// （enableHarm 回调）才结算，攻击流程根本不会调用它们，
				// 表现就是"打到了但一点伤害都没有"。这里按攻击节奏直接结算。
				DoAttackSplash(0);"""
new1 = """				actionCommandControl.setCommand(actionCommand);"""
if old1 in s:
    s = s.replace(old1, new1, 1)
    print("ok: removed duplicate splash")

# 2) 在 actionCommandUpdate 开头统一结算
old2 = """		int lFireTaget = 0;
		Transform target;"""
new2 = """		// 攻击结算：不依赖下面那条「发现目标 → 发 Fire」的链路，
		// 只要范围内有敌人就按 attackInterval 节奏打一次。
		// （原版蜂身上那 3 个 SphereHarmByDetector 只在死亡时启用，攻击流程从不调用）
		DoAttackSplash(0);

		int lFireTaget = 0;
		Transform target;"""
if old2 in s:
    s = s.replace(old2, new2, 1)
    print("ok: auto splash")
else:
    raise SystemExit("ANCHOR MISSING: auto splash")

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
