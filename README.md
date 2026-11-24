# Insecters War — 逆向分析与改造记录

对 2016 年独立游戏 **Insecters War（昆虫战争）** 的逆向分析、源码重建与玩法改造记录。

> 本仓库只包含**分析文档、补丁脚本与自动化工具**，不包含游戏本体、美术资源或完整反编译源码。

---

## 一、起因

Insecters War 是 2016 年的一款 **2 人横版 MOBA** 独立游戏：

- Unity 5.6.7f1 引擎，32 位 Mono 运行时
- 双方选择英雄（光剑战士 / 工程师 / 战术指挥官），带兵线推塔
- 自定义 TCP 协议做联机，支持局域网与自建房间服务器

游戏本身有不少设计可惜的地方：某些兵种打不出伤害、范围技能体现不出群体效果、AI 不会放技能也不会推塔、结算界面没有退出按钮。原作者 2019 年之后再无更新。

**目标**：在不重做游戏的前提下，把这些问题修掉，并在原有素材基础上补充内容。

---

## 二、方法

没有工程文件、没有源码，只有打包后的资源和一个 `Assembly-CSharp.dll`。整条技术路线是：

### 1. 反编译与源码重建

```
ilspycmd -p -lv CSharp5 Assembly-CSharp.dll -o src/
```

关键点：**必须用 `-lv CSharp5`**。默认输出 C# 12 语法的代码，而游戏用的是旧版编译器，反编译结果无法回编。

重建出的 1243 个 `.cs` 文件，编译时有两个坑：

- **必须用游戏自带的 `mscorlib.dll`**，加 `/nostdlib+ /noconfig`。
  用系统 mscorlib 会在运行时抛 `TypeLoadException: Could not load type 'System.Action\`3'`。
- 编译产物要做**公共面等价性校验**：类型集合、公有字段、公有方法逐一比对，
  确保改完的 DLL 和原版对外接口一致（`tools/iw_verify.py`）。

### 2. 数据格式逆向

游戏的地图不是 Unity 场景，而是自定义格式：

| 文件 | 作用 |
|---|---|
| `map.map.iw` | 场景对象（JSON，含 `prototype` / `component` 字段） |
| `map.obc.iw` | 原型数据 |
| `map.path.iw` / `map.tile.iw` | 寻路与地形 |
| `*.iwm` | 上述文件的打包格式（自定义容器） |

对象的组件数据由一层叫 `UrzComponet` 的绑定系统写进 Unity 组件：

```
SerializeScene.deserializeUrzFromArray
  → UrzEditorObject.deserialize
    → UrzEditorComponent.serializeInName 匹配组件名
      → UrzEditorComponent.prototype.serialization.deserialize
```

### 3. 三个必须知道的技术陷阱

改造过程中踩到并解决的核心问题，也解释了原版游戏为什么有一堆"说不通"的 bug：

#### ① 给序列化组件加 public 字段会毁掉旧地图

Unity 组件实例随地图文件一起序列化。只要给这类组件新增 public 字段，
反序列化时字段布局对不上，**整个组件的数据全部作废**：

```
A script behaviour (probably SphereHarmByDetector?) has a different serialization layout when loading.
(Read 100 bytes but expected 104 bytes)
```

一个 `bool` 字段就多 4 字节，足以让整张地图的伤害归零。

**规则**：凡挂在预制体或地图对象上的组件，新增字段一律 `[System.NonSerialized]` + 运行时兜底赋值。
只有纯运行时 `AddComponent` 的组件才能用字段默认值。

#### ② 信号槽签名不匹配 —— 原版生化蜂打不出伤害的真因

`zzSignalSlot.Awake()` 用反射按「方法名 + 参数类型」绑定攻击事件：

```csharp
MethodInfo method = slotComponent.GetType().GetMethod(slotMethodName, ParameterTypes);
```

诊断输出：

```
need=( ):Void                     ← 槽要的是无参 void
have=[ ... impHarm(Single):Void ]  ← 实际签名是 impHarm(float scale = 1f)
```

`SphereHarmByDetector.impHarm` 带默认参数，编译后签名变成 `impHarm(float)`，
而 `GetMethod("impHarm", Type.EmptyTypes)` 找的是无参版本 → 绑定失败
→ 攻击动画永远触发不了伤害。

**修复**：补一个真正的无参重载，反射就能绑上。

用**原版 DLL** 验证过：原版同样报这三条错误，说明这是游戏自身的缺陷，不是改造引入的。

#### ③ 英雄是 CharacterController，物理查询搜不到

`Physics.OverlapSphere` 半径从 3 调到 9999，候选列表里始终只有地面、板子、补给点和同类：

```
[Bee] cand n=5 mask=-1 [AwardSP:L31] [Ground35:L21] [Ground36:L21] [variationBee:L9]
```

英雄用 `CharacterController` 移动，它不参与物理球形/胶囊查询。**必须用对象遍历**。

---

## 三、历程

完整改动记录见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md)（50+ 条，按时间顺序，每条都带实测日志）。

阶段概览：

| 阶段 | 内容 |
|---|---|
| **重建** | 反编译 1243 个源文件 → 可编译 → 公共面等价校验通过 |
| **基础修复** | 结算界面退出按钮、范围伤害不分摊、等级上限 25、技能点系统 |
| **UI** | 买兵面板与加点面板合并（Q 切换）、程序化 9-slice 皮肤 |
| **AI** | 加点策略、清兵/追击/抢点/拆塔决策、撤退出口、卡住自救 |
| **玩法** | 波次血量成长、买兵下单叠加、指挥官轰炸/防御墙、生化蜂群攻 |
| **引擎级修复** | 信号槽签名、序列化布局、英雄物理查询 |

---

## 四、目前结果

### 已修复的原版缺陷

| 缺陷 | 根因 | 状态 |
|---|---|---|
| 生化蜂完全打不出伤害 | `impHarm` 信号槽签名不匹配（原版就有） | 已修，实测 `life 230→0` 三下击杀 |
| 指挥官轰炸无伤害 | `minBlastRadius` 被反序列化冲成 0 | 已修，实测一次炸 18 个单位 |
| 防御墙拆不掉 | 同上，`enemyBreakDps` 被冲成 0 | 已修，墙血 20→300（可调） |
| 范围技能按命中数均摊 | 蚂蚁吃亏、蜜蜂不吃亏，两侧手感不一致 | 已改为恒不分摊 |
| 生化蜂群攻体现不出来 | 攻击半径只有 0.98 | 已放大，可打一片 |
| 结算界面无法退出 | 原版没有退出入口 | 已加 IMGUI 返回按钮 |
| 升级到 13 级崩溃 | `LevelConfigSkillState` 数组只有 12 级 | 已加越界保护 |
| AI 从不放技能 | `processAction` 里普攻优先级高于技能 | 已调整优先级 |

### 新增内容

- **等级上限 25** + 每级经验递增 + 25 技能点
- **买兵面板**：与加点面板融合，Q 键切换，支持连买叠加
- **每波兵线血量成长**：`基础 × min(1 + 0.06n, 3)`
- **AI 决策系统**：撤退 / 清兵 / 追击 / 拆塔 / 抢点 / 推线，六种模式
- **AI 撤退出口**：血量回 70% 或 7 秒封顶，解决"缩在塔下不出来"

### 实测数据

**AI 优化（沙漠小镇，三轮迭代）**：

| 指标 | 基线 | 优化后 |
|---|---|---|
| 脱困自救 / 秒 / AI | 0.090 | **0.033**（降低 63%） |
| 技能释放（局内） | 386 | 128 / 110 |
| 贴家（赖在家里） | 0 | 0 |

**生化蜂伤害（修复后）**：

```
[Bee] HIT HERO pismireHero1(Clone) life 230->150 atk=80 dist=2.1 race=ePismire
[Bee] HIT HERO pismireHero1(Clone) life 70->0   atk=80 dist=2.1 race=ePismire
```

**轰炸伤害（修复后）**：

```
[AirDrop] blast at 111.0,35.0 mask=262656 radius=5 colliders=18 hurt=18
[AirDrop] hit medicBee(Clone) life 350 -> 132 dmg=120
```

---

## 五、仓库内容

```
.
├── README.md                    本文件
├── docs/
│   ├── CHANGELOG.md             完整改动记录（50+ 条，带实测日志）
│   ├── ARCHITECTURE.md          引擎架构分析
│   ├── ASSETS.md                91 张地图的素材盘点
│   ├── PROJECT.md               工程搭建说明
│   ├── ROADMAP.md               后续计划
│   ├── STATUS.md                版本状态与回滚方式
│   └── VERIFY.md                等价性校验说明
├── patches/                     57 个补丁脚本（每个对应一处改动）
└── tools/                       自动化工具
    ├── ai_test.py               AI 行为测试（部署→开局→采日志）
    ├── iw_verify.py             公共面等价性校验
    ├── scan_protos.py           地图原型统计
    └── *.ps1                    窗口/键盘/鼠标操作辅助
```

---

## 六、说明

- 本项目仅用于**本地单人游戏与学习研究**。
- 不包含游戏本体、美术资源、音频或完整反编译源码。
- 所有改动均基于用户自己安装的游戏副本，不涉及分发。
- 游戏版权归原作者所有。

---

## 附：素材盘点发现

解析了 91 张地图，共 **55 种原型**。有些内容几乎没被用过（详见 `docs/ASSETS.md`）：

| 原型 | 使用次数 | 说明 |
|---|---|---|
| Shop | 11 | **完整的商店系统**（5 个类实现），绝大多数对局见不到 |
| Manor | 1 | 可占领的资源建筑 |
| AntFirebat | 10 | 蚂蚁火焰兵，对比蜜蜂生化蜂用了 265 次 |
| PreventWay | 1 | 禁行区，可做咽喉要道 |
| TeleporterNode | 1 | 传送点 |
| MetalPailGrey | 2 | 灰色铁桶（另一套配色） |

这些都是现成可用但未被充分利用的内容。
