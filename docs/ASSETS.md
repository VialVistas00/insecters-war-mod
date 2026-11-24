# 游戏素材盘点：91 张地图里到底有什么，哪些没用起来

统计方式：解析 `Scene/` 下全部 91 张地图（13 个文件夹地图的 `map.obc.iw` + 78 个 `.iwm`），
提取所有 `"prototype"` 字段并汇总频次。

---

## 一、素材库总览

**共 55 种原型**，按用途分五类：

### 兵种（11 种）

| 原型 | 全地图使用次数 | 说明 |
|---|---|---|
| AntMarch | 1113 | 蚂蚁步兵，绝对主力 |
| AntShrapnel | 392 | 蚂蚁散弹兵 |
| AntArmoure | 289 | 蚂蚁重甲兵 |
| BeeVariation | 265 | 生化蜂（唯一在原版里坏的兵种，已修） |
| BeeInfantry | 224 | 蜜蜂步兵 |
| BeeFirepower | 193 | 蜜蜂火力支援 |
| AntShield | 177 | 蚂蚁盾兵 |
| BeeMedic | 121 | 蜜蜂医疗兵 |
| AntSoldier / BeeSoldier | 72 / 68 | 双方基础兵 |
| **AntFirebat** | **10** | **火焰兵，几乎没人用** |

### 建筑（10 种）

| 原型 | 次数 | 说明 |
|---|---|---|
| Stronghold | 981 | 据点（核心争夺点） |
| AntFactory / BeeFactory | 458 / 137 | 兵工厂 |
| StrongholdMachineGun | 304 | 据点机枪 |
| AntStronghold / BeeStronghold | 171 / 159 | 阵营据点 |
| AntBase / BeeBase | 148 / 139 | 主基地 |
| BeeSmallTurret / AntSmallTurret | 136 / 128 | 小防御塔 |
| **Manor** | **1** | **庄园：可占领的资源建筑，几乎没用过** |
| **Shop** | **11** | **商店：完整买卖系统，用得极少** |

### 地形与物件（7 种）

| 原型 | 次数 | 说明 |
|---|---|---|
| MetalPailRed | 467 | 红色铁桶（掩体） |
| DeadZone | 412 | 死亡区 |
| Scenery | 171 | 装饰 |
| IronBoard1 | 73 | 铁板平台 |
| Cube | 25 | 方块 |
| **MetalPailGrey** | **2** | **灰色铁桶，另一套配色，基本没用** |
| **PreventWay** | **1** | **禁行区：限制 AI/单位通行的区域** |

### 增益与拾取（4 种）

| 原型 | 次数 | 说明 |
|---|---|---|
| healthBuff | 547 | 回血点 |
| spBuff | 536 | 回蓝点 |
| FlameBuff | 76 | 火焰增益 |
| CheckPoint | 52 | 检查点 |

### 出生点与机制（5 种）

| 原型 | 次数 | 说明 |
|---|---|---|
| AntPlayerSpawn / BeePlayerSpawn | 69 / 77 | 玩家出生点 |
| AntHero1/2/3、BeeHero1/2/3 | 70~75 | 英雄出生点 |
| AntMechaSpawn / BeeMechaSpawn | 51 / 43 | 机甲出生点 |
| **TeleporterNode** | **1** | **传送点** |
| **VRuler** | **1** | **垂直标尺（编辑器用）** |

---

## 二、可以立刻拿来丰富内容的 7 项

按「投入产出比」排序：

### 1. Shop 商店系统（最值得用）

代码里是**完整的一套**：

- `ShopBuilding.cs` — 商店建筑本体
- `ShopGoodsGUI.cs` — 商品列表界面
- `ShopUI.cs` / `ShopGUI2.cs` — 购买界面
- `ShopFlowerControl.cs` — 商店的视觉（花朵）

**现状**：91 张地图里只有 11 处使用，绝大多数对局里玩家根本见不到商店。

**可以做的**：
- 在基地附近放一个商店，用金币买临时增益（护盾、加速、攻击力）
- 做「装备店」，攒钱买一件持续整局的强化
- 和现有的买兵系统打通：商店卖「下一次出兵 +3 个」

**成本**：只需在编辑器里放 ShopBuilding 原型并配商品，不用写代码。

### 2. Manor 庄园（资源争夺）

`Manor` 有 `owner` 种族字段和 `energyValue` 可恢复资源值，
占领方会切换材质（`pismireMaterial` / `beeMaterial`）。

**现状**：全游戏只有 1 张地图用过。

**可以做的**：
- 作为「中立资源点」，占领后持续产金币
- 多个庄园形成资源争夺线，逼玩家分兵
- 比现有据点更轻量（不用打建筑，站上去就占领）

### 3. AntFirebat 火焰兵（补全蚂蚁兵种树）

蚂蚁有 6 种兵，蜜蜂有 5 种。但火焰兵只被用了 10 次，
而 Bees 那边的 `BeeVariation` 用了 265 次。

**可以做的**：给蚂蚁的工厂加火焰兵选项，让它有「范围灼烧」这个战术位，
和蜜蜂的生化蜂形成对应。

### 4. PreventWay 禁行区（地图设计工具）

只在 `简单战争.iwm` 里出现过 1 次。

**可以做的**：
- 做「岩浆区」「毒雾区」，限制单位通行
- 配合传送点做迷宫式地图
- 强制兵线走特定路径，做出「咽喉要道」

### 5. TeleporterNode 传送点

同样只用过 1 次。

**可以做的**：
- 双向传送门，做「奇袭」玩法
- 配合 PreventWay 做立体地图

### 6. MetalPailGrey 灰色铁桶（美术资源浪费）

红色铁桶用了 467 次，灰色只用了 2 次。

**可以做的**：灰色版可以代表「不可破坏的铁桶」或「敌方阵营掩体」，
现在等于一套做好的美术资源闲置着。

### 7. VRuler 垂直标尺

编辑器辅助物件，做高空地图时用来对齐高度。开发时自用即可。

---

## 三、真正的死代码

### SonicWaveTower（声波塔）

`SonicWaveTower.cs` 有完整实现（继承 `WMBuilding`，有 `startTime` 逻辑），
但：

- 全代码库**只有它自己引用自己**
- 地图原型清单里**没有任何对应项**
- 说明预制体不存在，无法在地图里放置

**结论**：原版做了个开头就弃了。要用得先自己搭预制体，成本较高，优先级最低。

---

## 四、落地建议

如果目标是「让游戏内容更丰富」，按这个顺序做最划算：

| 优先级 | 做什么 | 工作量 | 效果 |
|---|---|---|---|
| 1 | 在 2~3 张图里放 **Shop 商店** | 编辑器操作，不改代码 | 立刻多一层经济/装备玩法 |
| 2 | 做一张 **Manor 资源争夺图** | 编辑器操作 | 新的胜负维度 |
| 3 | 给蚂蚁工厂加 **火焰兵** | 改一个工厂配置 | 补全兵种对抗 |
| 4 | 用 **PreventWay + Teleporter** 做一张立体图 | 编辑器操作 | 地图设计上限提升 |
| 5 | 灰色铁桶当「不可破坏掩体」 | 改一个属性 | 地图掩体有层次 |

前四项**都不需要改代码**，纯粹用编辑器摆原型 + 配数据，
这也符合「新内容尽量用游戏内已有素材」的原则。

---

## 附：完整原型清单（55 种，按使用次数降序）

```
AntMarch 1113          Stronghold 981         healthBuff 547
spBuff 536             MetalPailRed 467       AntFactory 458
DeadZone 412           AntShrapnel 392        StrongholdMachineGun 304
AntArmoure 289         BeeVariation 265       BeeInfantry 224
BeeFirepower 193       AntShield 177          AntStronghold 171
Scenery 171            BeeStronghold 159      AntBase 148
AntShrapnelBullet 147  BeeBase 139            BeeFactory 137
BeeSmallTurret 136     AntSmallTurret 128     BeeMedic 121
BeePlayerSpawn 77      FlameBuff 76           AntHero1 75
AntHero3 73            AntHero2 73            IronBoard1 73
ArmorAndAttack 72      AntSoldier 72          BeeHero1 71
BeeHero2 70            BeeHero3 70            AntPlayerSpawn 69
AntMulSoldierCube 68   BeeSoldier 68          AntHero1Blast 67
AntGrenade 67          BeeSoldierCube 67      AntSoldierCube 67
BeeGrenade 67          BeeMulSoldierCube 66   CheckPoint 52
AntMechaSpawn 51       BeeMechaSpawn 43       Cube 25
Shop 11                AntFirebat 10          MetalPailGrey 2
PreventWay 1           Manor 1                VRuler 1
TeleporterNode 1
```
