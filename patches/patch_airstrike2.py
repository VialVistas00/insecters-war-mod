import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\AirDropAnimation.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = '''	private void ApplyBlast(GameObject pObject, Vector3 pCenter)
	{
		Vector3 center = pCenter;'''

new = '''	private void ApplyBlast(GameObject pObject, Vector3 pCenter)
	{
		// Unity 陷阱：这几个字段是后加的，预制体里没有对应的序列化数据，
		// 反序列化时会用类型默认值 0 覆盖掉代码里写的初始值。
		// 所以运行时必须在这里兜底，否则半径 0 = 一颗炸弹都炸不到。
		if (minBlastRadius <= 0.05f)
		{
			minBlastRadius = 3.2f;
		}
		if (forceDamage <= 0.05f)
		{
			forceDamage = 45f;
		}

		Vector3 center = pCenter;'''

if old not in s:
    raise SystemExit("ANCHOR MISSING")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: runtime fallback for radius/damage")
