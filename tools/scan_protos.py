import glob
import io
import json
import os
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\游戏\Insecters War"
use = Counter()
per_map = {}

# 1) 文件夹形式地图
for f in glob.glob(os.path.join(ROOT, "Scene", "*", "map.obc.iw")):
    mapname = os.path.basename(os.path.dirname(f))
    raw = io.open(f, encoding="utf-8", errors="replace").read()
    found = re.findall(r'"prototype"\s*:\s*"([^"]+)"', raw)
    per_map[mapname] = Counter(found)
    use.update(found)

# 2) 打包 .iwm
for f in glob.glob(os.path.join(ROOT, "Scene", "*.iwm")):
    mapname = os.path.basename(f)
    b = open(f, "rb").read()
    found = [m.decode("utf-8", "replace")
             for m in re.findall(rb'"prototype"\s*:\s*"([^"]+)"', b)]
    per_map[mapname] = Counter(found)
    use.update(found)

print("=== 地图数量:", len(per_map))
print("=== 出现过的原型总数:", len(use))
print()
print("=== 原型使用频次（全地图累计，前 60）")
for name, c in use.most_common(60):
    print("%-32s %d" % (name, c))

print()
print("=== 只在 1 张地图里出现过的原型")
rare = []
for name, c in use.items():
    maps = [m for m, cnt in per_map.items() if cnt.get(name)]
    if len(maps) == 1:
        rare.append((name, maps[0], c))
for name, mp, c in sorted(rare):
    print("%-32s x%-3d in %s" % (name, c, mp))
print("总计", len(rare), "个")

# 存成 json 供后续比对
out = os.path.join(ROOT, "服务器", "logs", "proto_usage.json")
io.open(out, "w", encoding="utf-8").write(
    json.dumps({"total": dict(use),
                "per_map": {k: dict(v) for k, v in per_map.items()}},
               ensure_ascii=False, indent=1))
print()
print("已写入", out)
