import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SphereHarmByDetector.cs"
s = io.open(p, encoding="utf-8-sig").read()

# 找到 impHarm(float) 的声明位置，在它前面插入无参重载
anchor = None
for cand in ["\tpublic void impHarm(float pScale)",
             "\tpublic void impHarm(float scale)"]:
    if cand in s:
        anchor = cand
        break

if anchor is None:
    # 兜底：按名字定位
    idx = s.find("public void impHarm(")
    if idx < 0:
        raise SystemExit("impHarm not found")
    line_start = s.rfind("\n", 0, idx) + 1
    anchor = s[line_start:s.index("\n", idx)]

overload = (
    "\t/// <summary>\n"
    "\t/// 【原版缺陷修复】无参重载。\n"
    "\t///\n"
    "\t/// `zzSignalSlot` 用 `GetMethod(\"impHarm\", Type.EmptyTypes)` 找槽方法，\n"
    "\t/// 而原来的 `impHarm(float scale = 1f)` 编译后签名是 `impHarm(Single):Void`，\n"
    "\t/// 反射匹配不上无参签名，导致 bigAttack / smallAttack / swoopAttack\n"
    "\t/// 三个攻击组件的信号槽在 Awake 时就绑定失败：\n"
    "\t///   \"Slot Method isn't fit Signal,or it is not public\"\n"
    "\t/// 结果生化蜂的攻击动画永远触发不了伤害结算。\n"
    "\t/// 这里补一个真正的无参版本，让反射能绑上。\n"
    "\t/// </summary>\n"
    "\tpublic void impHarm()\n"
    "\t{\n"
    "\t\timpHarm(1f);\n"
    "\t}\n"
    "\n"
)

s = s.replace(anchor, overload + anchor, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: overload inserted before", anchor.strip())
