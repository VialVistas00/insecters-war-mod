import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

start = s.index("			// 敌我判断改用 layer：")
end = s.index("			Race tgtRace = Race.eNone;")

new = """			// 掩码已经限定在「敌方种族层」内，这里只额外排除自己所在层，
			// 防止把同族单位误当成敌人（之前的写法把敌方建筑层也排除掉，
			// 结果连敌人都打不到了）。
			int cLayer = c.gameObject.layer;
			if (cLayer == myLayer)
			{
				continue;
			}
"""

s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: friend filter simplified")
