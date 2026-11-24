import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\zzSignalSlot.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = """		MethodInfo method = slotComponent.GetType().GetMethod(slotMethodName, ParameterTypes);
		if (method == null || (method.ReturnType != ReturnType && !method.ReturnType.IsSubclassOf(ReturnType)))
		{
			Debug.LogError(base.gameObject.name + ":Slot Method isn't fit Signal,or it is not public");
		}"""

new = """		MethodInfo method = slotComponent.GetType().GetMethod(slotMethodName, ParameterTypes);
		if (method == null || (method.ReturnType != ReturnType && !method.ReturnType.IsSubclassOf(ReturnType)))
		{
			Debug.LogError(base.gameObject.name + ":Slot Method isn't fit Signal,or it is not public");
			// 诊断：把这个槽要求的确切签名打出来，才能知道该补什么方法。
			string ps = string.Empty;
			for (int pi = 0; pi < ParameterTypes.Length; pi++)
			{
				ps = ps + (pi > 0 ? "," : "") + ParameterTypes[pi].Name;
			}
			string have = string.Empty;
			MethodInfo[] ms = slotComponent.GetType().GetMethods();
			for (int mi = 0; mi < ms.Length; mi++)
			{
				MethodInfo m = ms[mi];
				if (m.DeclaringType != slotComponent.GetType())
				{
					continue;
				}
				string mps = string.Empty;
				ParameterInfo[] pis = m.GetParameters();
				for (int pj = 0; pj < pis.Length; pj++)
				{
					mps = mps + (pj > 0 ? "," : "") + pis[pj].ParameterType.Name;
				}
				have = have + " " + m.Name + "(" + mps + "):" + m.ReturnType.Name;
			}
			Debug.Log(string.Concat("[SlotDiag] obj=", base.gameObject.name,
				" signal=", (signalComponent != null ? signalComponent.GetType().Name : "null"),
				".", signalMethodName,
				" slot=", (slotComponent != null ? slotComponent.GetType().Name : "null"),
				".", slotMethodName,
				" need=(", ps, "):", ReturnType.Name,
				" have=[", have, " ]"));
		}"""

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("DONE")
