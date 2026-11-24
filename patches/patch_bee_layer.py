import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old_start = "			// 敌我判断：Life.characterInfo 常常是 null（蜂自己就是），"
old_end = "			AttackSetting st = new AttackSetting();"

i = s.index(old_start)
j = s.index(old_end)

new_block = """			// 敌我判断改用 layer：
			// 这个游戏里 Life.characterInfo 普遍是 null（实测 tgtRace=- 满屏），
			// CharacterInfoObject 也不在同一物体上，只有 layer 是可靠的。
			// 我方种族掩码覆盖到的层 = 友军，直接跳过。
			int cLayer = c.gameObject.layer;
			int pLayer = (bool)c.transform.parent ? c.transform.parent.gameObject.layer : cLayer;
			bool isFriend = (((myMask >> cLayer) & 1) != 0) || (((myMask >> pLayer) & 1) != 0);
			if (isFriend)
			{
				continue;
			}
			Race tgtRace = Race.eNone;

"""

s = s[:i] + new_block + s[j:]

# myMask 在循环外算好
old2 = """		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);"""
new2 = """		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);
		int myMask = (int)PlayerInfo.getRaceObjectValue(info.race);"""
if old2 not in s:
    raise SystemExit("ANCHOR MISSING myMask")
s = s.replace(old2, new2, 1)

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
