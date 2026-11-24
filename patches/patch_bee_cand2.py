import io
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 把刚插入的日志块换掉：不用 myLayer/enemyLayer 变量，全部内联求值
start = s.index("\t\tif (statAttacks <= 6)")
end = s.index("\t\tint myMask = (int)PlayerInfo.getRaceObjectValue(info.race);")

new = """\t\tif (statAttacks <= 6)
\t\t{
\t\t\tstring cand = string.Empty;
\t\t\tfor (int ci = 0; ci < hits.Length && ci < 6; ci++)
\t\t\t{
\t\t\t\tCollider cc = hits[ci];
\t\t\t\tif (!(bool)cc)
\t\t\t\t{
\t\t\t\t\tcontinue;
\t\t\t\t}
\t\t\t\tcand = cand + " [" + cc.name + ":L" + cc.gameObject.layer;
\t\t\t\tif ((bool)cc.transform.parent)
\t\t\t\t{
\t\t\t\t\tcand = cand + "/PL" + cc.transform.parent.gameObject.layer;
\t\t\t\t}
\t\t\t\tWMGameObject ww = WMGameObject.getFromTransform(cc.transform);
\t\t\t\tif ((bool)ww && (bool)ww.life && ww.life.characterInfo != null)
\t\t\t\t{
\t\t\t\t\tcand = cand + "/" + ww.life.characterInfo.race;
\t\t\t\t}
\t\t\t\tcand = cand + "]";
\t\t\t}
\t\t\tDebug.Log(string.Concat("[Bee] cand seed=", statAttacks,
\t\t\t\t" n=", hits.Length,
\t\t\t\t" selfLayer=", base.gameObject.layer,
\t\t\t\t" antLayer=", PlayerInfo.getRaceLayer(PlayerInfo.getAdversaryRace(info.race)),
\t\t\t\t" beeLayer=", PlayerInfo.getRaceLayer(info.race),
\t\t\t\t" mask=", mask, cand));
\t\t}

"""

s = s[:start] + new + s[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
