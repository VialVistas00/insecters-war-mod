import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\VariationBeeAI.cs"
s = io.open(p, encoding="utf-8-sig").read()

start = s.index("	/// <summary>把这只生化蜂身上所有球形攻击判定放大成群体攻击。</summary>")
end = s.index("	private bool swoopCheck()")

new_block = '''	/// <summary>把这只生化蜂身上所有球形攻击判定放大成群体攻击。</summary>
	private void WidenAttackRadius()
	{
		// Unity 陷阱：aoeRadius 是后加字段，预制体反序列化会把它冲成 0，
		// 那样 `h.harmRadius < aoeRadius` 永远为假，半径完全没被改。
		if (aoeRadius <= 0.05f)
		{
			aoeRadius = 3f;
		}

		SphereHarmByDetector[] harms = GetComponentsInChildren<SphereHarmByDetector>(true);
		BlastWave[] waves = GetComponentsInChildren<BlastWave>(true);

		string detail = string.Empty;
		for (int i = 0; i < harms.Length; i++)
		{
			SphereHarmByDetector h = harms[i];
			if (!(bool)h)
			{
				continue;
			}
			float before = h.harmRadius;
			if (h.harmRadius < aoeRadius)
			{
				h.harmRadius = aoeRadius;
			}
			detail = detail + " h" + i + ":r" + before.ToString("0.00") + "->"
				+ h.harmRadius.ToString("0.00") + "/dmg" + h.harmValueInCentre;
		}
		for (int j = 0; j < waves.Length; j++)
		{
			BlastWave w = waves[j];
			if (!(bool)w)
			{
				continue;
			}
			if (w.sphereCheckRadius < aoeRadius)
			{
				w.sphereCheckRadius = aoeRadius;
			}
			if (w.sphereCastRadius < aoeRadius)
			{
				w.sphereCastRadius = aoeRadius;
			}
			detail = detail + " w" + j + ":r" + w.sphereCheckRadius.ToString("0.00");
		}

		Debug.Log(string.Concat("[Bee] widen aoe=", aoeRadius,
			" harms=", harms.Length, " waves=", waves.Length,
			" obj=", base.name, detail));
	}

'''

s = s[:start] + new_block + s[end:]
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: WidenAttackRadius with diag")
