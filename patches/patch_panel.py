import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\HeroCommandPanel.cs"
s = io.open(p, encoding="utf-8-sig").read()

s = s.replace("private const float panelW = 660f;", "private const float panelW = 700f;")
s = s.replace("private const float panelH = 470f;", "private const float panelH = 560f;")
s = s.replace("float listH = Mathf.Max(rowH, pH * 0.44f);", "float listH = Mathf.Max(rowH, pH * 0.56f);")
s = s.replace('"Q/Tab 切页  Esc 关闭"', '"Q 切页  Esc 关闭"')
s = s.replace('"J/空格 确认"', '"J 确认"')

io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("panelH560:", s.count("panelH = 560f"), "| Q切页:", s.count("Q 切页"))
