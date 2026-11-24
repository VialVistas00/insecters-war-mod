# 校验说明（VERIFY）

重建的 DLL 能不能替换进游戏，不能凭「编译通过」判断，必须证明**公共面等价**。
本工程提供两级校验。

---

## 1. 一键校验

```bat
python verify.py
```

输出示例：

```
类型数          原版 1554 / 重建 1555（已排除编译器生成类型 137 / 134）
缺失类型        0
多出类型        1
公有字段缺失    0 个类型
公有方法缺失    0 个类型
结论: 类型与公共面一致 ✔ 可替换
```

---

## 2. 判定标准（为什么是这三条）

Unity 在运行期对程序集只有三种依赖，任何重建都必须全部满足：

| 依赖 | 失败后果 | 校验项 |
|---|---|---|
| 类型存在 | 预制体/场景里的 MonoBehaviour 引用变成 `Missing (Mono Script)` | 「缺失类型 = 0」 |
| **公有字段**存在且类型兼容 | Unity 按「字段名 + 类型」反序列化 `.prefab` / `.unity` / `.iwm` 里的数值，字段丢了 → 该组件的所有调参归零 | 「公有字段缺失 = 0」 |
| 公有方法存在 | `SendMessage` / 协程 / RPC 反射调用失败 | 「公有方法缺失 = 0」 |

> 私有字段、方法体 IL 字节、元数据 token 编号**都不需要一致** ——
> 重建后它们必然不同，且不影响运行。

---

## 3. 为什么排除「编译器生成类型」

以下类型名在两次构建间会自然变化，且不承载任何游戏数据：

| 原版（Mono 2.0 编译器） | 重建（Roslyn） |
|---|---|
| `<>c__AnonStorey0` | `<>c__DisplayClass1` |
| `<X>c__Iterator0` | `<X>d__0` |
| `$ArrayType=16` | `__StaticArrayInitTypeSize=16` |
| `<PrivateImplementationDetails>` | `<PrivateImplementationDetails>{GUID}` |
| `<>f__mg$cache0`（字段） | `CS$<>9__CachedAnonymousMethodDelegate` |

这些在本工程的 `iw_verify.py` 里由 `CLOSURE` 正则统一排除，
**不参与类型集合比对**，否则会得到 137 条无意义的“缺失”。

---

## 4. 二级校验：REA 静态证据（可选）

[REA](https://github.com/NabilRFG12/Reverse-Engineer-anything) 的 `src/dotnet/`
提供**不加载程序集**的 PE/CLI 静态分析，适合把「重建产物是什么」固化成证据。

```bat
cd "服务器\tools\_rea\Reverse-Engineer-anything-main"
npm ci && npm run build
```

之后 `verify.py` 会自动追加：

```
## evidence_id
ev_8585425348bec93e8c111f2041435bde2499178be46945ae1e7aaa7fe29ad65b
## subject.digest
sha256 f176a881555e005955fa34da864859327e65e44b86a023e590772ba002f3e3d0
```

也可单独用它的跨构建比对：

```bat
node scripts\rea.mjs compare-managed-members <原版.dll> <重建.dll> --format md
```

它按「精确签名 → 精确 IL 签名 → 结构形状」三级匹配，输出
`unchanged / changed / added / removed` 统计。对本工程的参考意义：

- `unchanged: 172` —— 方法体字节都相同的（多为纯数据/简单属性）
- `changed: 5994` —— 签名相同但 IL 不同（正常的重编译差异）
- `removed/added` 大量出现 —— 主要来自上述编译器生成类型与 token 重编号

> REA 的定位是「**证据与限定条件**」，不是反编译器。反编译仍用 `ilspycmd -lv CSharp5`。

---

## 5. 实机校验（最终关口）

静态校验通过后，还必须实机跑一遍：

```bat
copy /y build\Assembly-CSharp.dll "D:\游戏\Insecters War\InsectersWar_Data\Managed\"
```

启动游戏，走完：**主菜单 → 联机 → 建房 → 选英雄 → 准备 → 开局 → 移动开火 → 结算**。

验收标准（本工程实测基线）：

| 项 | 期望 |
|---|---|
| `output_log.txt` 中 `Exception` | 0 |
| `TypeLoadException` / `MissingMethodException` / `InvalidProgramException` | 0 |
| 预制体引用 | 无 `Missing (Mono Script)` |
| 场景加载 | 无 `ArgumentException: extra characters in JSON input` |

**回滚**：`copy /y 服务器\backup\Assembly-CSharp.dll.vanilla-locked <Managed目录>`
