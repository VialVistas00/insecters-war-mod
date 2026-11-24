import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = """			int cLayer = c.gameObject.layer;
			int pLayer = (bool)c.transform.parent ? c.transform.parent.gameObject.layer : cLayer;
			bool isFriend = (((myMask >> cLayer) & 1) != 0) || (((myMask >> pLayer) & 1) != 0);
			if (isFriend)
			{
				continue;
			}"""

new = """			int cLayer = c.gameObject.layer;
			int pLayer = (bool)c.transform.parent ? c.transform.parent.gameObject.layer : cLayer;
			// 直接用"自己所在层"作为友军判据：
			// PlayerInfo.getRaceObjectValue 返回的掩码范围太宽（131328），
			// 位运算会把所有单位都判成友军，导致一个都打不到。
			bool isFriend = (cLayer == myLayer) || (pLayer == myLayer);
			if (isFriend)
			{
				continue;
			}"""

if old not in s:
    raise SystemExit("ANCHOR MISSING friend")
s = s.replace(old, new, 1)

old2 = """		int myMask = (int)PlayerInfo.getRaceObjectValue(info.race);"""
new2 = """		int myMask = (int)PlayerInfo.getRaceObjectValue(info.race);
		int myLayer = base.gameObject.layer;
		int raceLayer = PlayerInfo.getRaceLayer(info.race);
		if (raceLayer > 0 && raceLayer < 32)
		{
			myLayer = raceLayer;
		}"""
if old2 not in s:
    raise SystemExit("ANCHOR MISSING myMask")
s = s.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
