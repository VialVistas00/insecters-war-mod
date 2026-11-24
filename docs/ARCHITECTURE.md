# 架构说明（Architecture）

本文档描述重建工程 `src/` 的代码结构、核心类与主要调用链，作为后续改造的地图。

---

## 1. 分层总览

```
┌──────────────────────────────────────────────────────────────┐
│ 表现层   GUI / 输入 / 动画 / 特效                              │
│   GameGUIBase(88) GameGUIRenderer GameResultGUI ShopGUI2     │
│   GameInput mainInput Spine.* exSprite* Detonator*           │
├──────────────────────────────────────────────────────────────┤
│ 玩法层   英雄 / 载具 / 据点 / 兵线 / 道具 / 技能                │
│   Hero(49) HeroSpawn(70) Mecha(41) Stronghold(36)            │
│   SoldierFactory SoldierListFactory StrongholdBuilding(12)   │
│   IWItemSystem WMItemBag ShopBuilding                        │
├──────────────────────────────────────────────────────────────┤
│ 战斗结算  Life(61) Guard(18) Bullet(37) Emitter(32)           │
│   SphereHarmByDetector(19) AttackSetting ArmorAndAttack       │
│   SkillBarrier SkillBoomerang SkillInvisibility …             │
├──────────────────────────────────────────────────────────────┤
│ 引擎层   InsectersWarEngine（自研定点数 2D）                   │
│   AABB(33) GirdData(18) GirdAAABBQuadTree IwTileWorld(34)     │
│   IwCharacterController(23) IwTilePathAgent(20) GirdAAABBPathFind│
├──────────────────────────────────────────────────────────────┤
│ 网络层   自研 TCP + CzlProtobuf                               │
│   CbClientNet(13) CbServerHandler(47) CtServerLogic           │
│   CzlProtobuf.* (9 类)                                        │
├──────────────────────────────────────────────────────────────┤
│ 资源/序列化                                                    │
│   Urz(场景原型) GameResourceManager SerializeScene            │
│   zzNumerical* SceneModel*/SceneImage*                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. 核心类速查

方法数 / 字段数（来自原程序集元数据）：

| 类 | 方法 | 字段 | 职责 |
|---|---:|---:|---|
| `Hero` | 49 | 73 | 英雄主体：输入→动作、动画、开火、技能、上下半身混合 |
| `HeroSpawn` | 70 | 44 | 英雄的“玩家外壳”：复活、加点、商店、道具、载具请求、RPC 入口 |
| `Mecha` | 41 | 64 | 核心装甲：人形↔炮台双形态、冲击波、上下车、损伤分层 |
| `Stronghold` | 36 | 57 | 据点：占领进度、生长、切换建筑、兵种计数 |
| `StrongholdBuilding` | 12 | 12 | 据点建筑：买兵（**当前不扣钱**）、机枪塔、耐久 |
| `SoldierFactory` | 13 | 17 | 产兵：`produceIntervals` / `firstTimeOffset` 循环出兵 |
| `ShopBuilding` | 9 | 12 | 商店：把 `purse` / `priceList` / `itemBag` 绑到 UI |
| `IWItemSystem` | 13 | 14 | 全局道具表：按英雄/种族索引 |
| `WMItemBag` | 25 | 11 | 背包：买/卖/用、格位管理 |
| `GameScene` | 35 | 45 | 对局场景：出生点、路径、胜负、投降、结束流程 |
| `GameResultGUI` | 10 | 51 | 结算界面（**绘制在预制体里，代码只填数据**） |
| `Life` | 61 | 23 | 血量/护盾/伤害结算中心 |
| `Guard` | 18 | 26 | 护盾与格挡（`guardLife` / `recover` / `lostRecover`） |
| `Bullet` | 37 | 29 | 子弹：射线/球形检测、命中特效、击退 |
| `Emitter` | 32 | 17 | 发射器：单发/多角度、RPC 同步 |
| `SphereHarmByDetector` | 19 | 9 | **范围伤害核心**（均摊逻辑在这里） |
| `CbServerHandler` | 47 | 28 | 客户端房间协议处理（switch 分发所有 cat） |
| `CbClientNet` | 13 | 20 | 自研 TCP：4 字节大端帧头、2 秒心跳 |
| `NetworkRoom3` | 52 | 19 | 房间界面逻辑（准备/选人/开局/聊天） |
| `NetworkMenu3` | 25 | 21 | 大厅：服务器列表、房间列表、建房 |
| `GameGUIBase` | 88 | 32 | 自绘 GUI 基类（Rect/Color/UV/鼠标事件） |
| `HeroPointManager` | 19 | 30 | 局外加点（读 `config.cfg` 的 `points`） |

---

## 3. 三条主要调用链

### 3.1 一局的生命周期

```
MainMenu → NetworkMenu3.CreateRoom / JoinRoom
   → NetworkRoom3（选英雄 selectHero / 准备 makeReady）
   → GameScene.Start
        ├ pismirePlayerSpawns / beePlayerSpawns  → HeroSpawn.CreateHero
        ├ antPaths / beePaths                    → SoldierFactory 出兵
        └ mecha / stronghold 由地图原型生成
   → 对局中：Hero.Update → ActionCommandControl → 具体 Action（开火/技能/位移）
   → 满足 loseCondition → GameScene.GameSceneSetWiner
   → GameScene.endGameScene → GameResultGUI.UpdateResult（只填数据）
```

### 3.2 伤害结算链

```
Emitter.EmitBullet
   → Bullet.OnTriggerEnter / CheckRaycast
      → Bullet._touch → Life.injure(AttackInfo)
         → ArmorAndAttack.getRate(attackType, armorType)   // 攻击×护甲 倍率表
         → Life.changeHealth → Guard.guardValueChange       // 先扣护盾
            → HeroSetting.OnDead → HeroSpawn.OnDead → 复活计时

范围伤害：
SphereHarmByDetector.Update → impHarm(true)
   → doHarm(detector, data)
      ├ 收集命中目标到 Dictionary<Collider,float>
      ├ if (divideDamage) scale = 1.0f / dict.Count        ← 均摊点
      └ 逐目标 data.attackSetting.ScaleAttack(minHarmRate, scale, inScale) → Life.injure
```

### 3.3 经济链

```
WMPurse.addMoneyByTime（定时）
WMPurse.add（击杀 awardKiller.award）
   → ShopBuilding.operateThis(purse, priceList, itemBag)  → ShopUI 购买
   → WMItemBag.canBuy/buyOne/sellOne

据点出兵（不走金币）：
Stronghold.strongholdBuilding._BuySoldier(index)
   → factory.set_produceIntervals(...)   // 只换兵种，不扣钱
```

---

## 4. 网络协议（自研，非 Photon / 非 Unity Networking）

```
TCP 直连 :6020
帧格式：[int32 大端 bodyLen][body]
body  ：CzlProtobuf.ProtobufData
        int16 总长 | 重复( uint8 key=(fieldIndex<<4)|type + payload )
        type: 0=Int32 2=Byte 3=Int64 4=Bool 5=String 6=Object 7=Objects 8=Bytes
外层字段：f1=packHead  f2=objID  f3=roomID  f4=herosInfoList
          f5=roomsList/customMessage  f6=chatMessage
```

命令字（`CbProtocolCommand`）：

| 值 | 名称 | 用途 |
|---:|---|---|
| 1 | KEEP_ALIVE | 心跳（4 个 0 字节） |
| 3 | CLIENT_VERIFY_CONNECTION | 握手 |
| 30 | SYN_FRAME_DATA | 帧数据（全量/增量） |
| 60 | ROOM_MANAGER | 房间（建房/进房/选人/准备/开局/聊天） |
| 61–68 | ABLITY / MINOUS / STRONGPONT / BUY_MINOUS / CUSTOM | 局内事件 |

`CbServerHandler.ProecssRoomData` 里的 `switch (category)` 就是协议分发表，
改协议优先看这里。

---

## 5. 引擎层（InsectersWarEngine）

自研**定点数 2D 物理/网格**，不是 Unity 的 Rigidbody：

- `IVector2` / `ifloat`：Q12 定点数（`SHIFT_AMOUNT = 12`，`FACTOR = 4096`）
- `AABB` / `GirdAABB` / `GirdAAABBQuadTree`：格子 AABB + 四叉树
- `IwTileWorld` / `GirdData` / `IwTilePathAgent`：Tile 世界与寻路
- `IwCharacterController` / `IwPlatformTileCharacter`：平台角色控制（重力、斜坡、单向平台）

> 改玩法时若涉及移动/碰撞，改这里的成本远低于改 `Character2D` / `RigidBodyWalker`。

---

## 6. 资源与场景

- 地图 = 文件夹（`map.map.iw` + `map.obc.iw` + `map.path.iw` + `map.tile.iw` + 图集 PNG）
  或打包单文件 `.iwm`（`[int32 ver][int16 count][条目表][blob...]`）
- `map.map.iw`：场景对象 JSON（`{"objects":[{prototype, position, component...}]}`）
- `map.obc.iw`：原型定义 JSON（英雄/兵/据点/伤害表的**实际数值**）
- `Urz.loadPrototype` 读取 obc，`GameResourceManager.load` 组装场景
- `config.cfg`：音量、玩家名、**局外加点 `points`**

**关键数值都在 `map.obc.iw` 里**（如 `AntHero1` 的 life/attack/skillCost），
改平衡优先改这里，不必重编译。
