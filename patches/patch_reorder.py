import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
lines = io.open(p, encoding="utf-8-sig").read().splitlines()

# 取出第 194-201 行（myMask/myLayer/enemyLayer 的计算），挪到 OverlapSphere 之前
# 先定位这段
start = next(i for i, l in enumerate(lines) if "int myMask = (int)PlayerInfo.getRaceObjectValue" in l)
# 向上找 enemyLayer 定义（在之前已被替换成 beeEnemyRace 那一段）
guard_start = None
for i in range(start - 1, max(0, start - 40), -1):
    if "Race beeEnemyRace" in lines[i]:
        guard_start = i
        break
if guard_start is None:
    raise SystemExit("cannot locate enemyLayer block")

# 找到这段结束（myLayer = raceLayer; 之后的花括号）
end = start
while end < len(lines) and "}" not in lines[end].strip() or lines[end].strip() == "":
    end += 1
# 更稳：找最后一个 myLayer 赋值相关的闭括号
while end < len(lines) and not lines[end].strip().startswith("}"):
    end += 1
end += 1

block = lines[guard_start:end]

# 从原位置删除
rest = lines[:guard_start] + lines[end:]

# 插入到 OverlapSphere 之前
idx = next(i for i, l in enumerate(rest) if "Collider[] hits = Physics.OverlapSphere" in l)
new_lines = rest[:idx] + block + [""] + rest[idx:]

io.open(p, "w", encoding="utf-8", newline="\n").write("\n".join(new_lines) + "\n")
print("moved block of", len(block), "lines before OverlapSphere")
