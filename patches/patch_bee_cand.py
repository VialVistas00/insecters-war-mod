import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = """		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);"""

new = """		Collider[] hits = Physics.OverlapSphere(center, aoeRadius, mask);
		if (statAttacks <= 6)
		{
			string cand = string.Empty;
			for (int ci = 0; ci < hits.Length && ci < 6; ci++)
			{
				Collider cc = hits[ci];
				cand = cand + " [" + (cc != null ? cc.name : "-") + ":L"
					+ (cc != null ? cc.gameObject.layer.ToString() : "?");
				if (cc != null && cc.transform.parent != null)
				{
					cand = cand + "/PL" + cc.transform.parent.gameObject.layer;
				}
				WMGameObject ww = (cc != null) ? WMGameObject.getFromTransform(cc.transform) : null;
				if (ww != null && ww.life != null && ww.life.characterInfo != null)
				{
					cand = cand + "/" + ww.life.characterInfo.race;
				}
				cand = cand + "]";
			}
			Debug.Log(string.Concat("[Bee] cand seed=", statAttacks,
				" n=", hits.Length, " myLayer=", myLayer,
				" enemyLayer=", enemyLayer, " mask=", mask, cand));
		}"""

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
