# 改造路线（Roadmap）

从「能编译」到「能重做」的四个阶段。每阶段都给出**具体文件 + 具体切口**。

---

## 阶段 0：地基（已完成）

- [x] 源码重建（1236 文件，C# 5）
- [x] 一键编译 `build.cmd`
- [x] 实机验证（进房间 → 选英雄 → 进对局，零异常）
- [x] 原版 DLL 备份

---

## 阶段 1：小切口验证（1–2 天）

先做几处**小改动**确认整条「改源码 → 编译 → 进游戏」的链路顺畅。

### 1.1 结算界面加退出键

**文件**：`src/GameResultGUI.cs`

现象：`OnGUIDraw / OnGUIStart / OnGUIUpdateRect / OnGUIUpdateUV` 全是 `ret`，
真正绘制在预制体里。

改法：在 `OnGUIDraw` 里用 `GUI.Button` 画一个按钮（或复用 `backButton` 的 `visible`），
点击调 `GameScene.Singleton.Back()`：

```csharp
public override void OnGUIDraw()
{
    if (IsEndResult && GUI.Button(new Rect(Screen.width - 160, Screen.height - 60, 140, 44), "返回大厅"))
    {
        GameScene.Singleton.Back();      // 内部 LoadLevel("main.zzScene")
    }
}
```

### 1.2 详细结算

**文件**：`src/GameResultGUI.cs`、`src/ResultInfo.cs`

`ResultInfo` 已有 `indexInTeam / level / name / score / playerIndex`。
补充字段（击杀/死亡/伤害/加点）需要 `HeroSpawn` 侧埋点：

- `src/HeroSpawn.cs`：`AddExp` 附近加 `kill/death/damage` 累加
- `src/KillInfoSystem.cs`：`doKillInfo` 里把击杀写进对应 `ResultInfo`

### 1.3 范围伤害取消均摊

**文件**：`src/SphereHarmByDetector.cs`

```csharp
// 原逻辑
if (data.divideDamage)
{
    scale = 1.0f / targets.Count;
}
// 改为
if (data.divideDamage && !data.noDivide)   // 或直接删掉这段
```

`SphereHarmData.divideDamage` 来自 `map.obc.iw` 的 `sphereHarm`，**也可以只改地图**：
把 `"divideDamage": true` 去掉即可，不用重编译。

### 1.4 金币买兵

**文件**：`src/StrongholdBuilding.cs`

```csharp
public void _BuySoldier(int pIndex)
{
    // 现有：只换兵种
    // 加：
    if (lPurse != null && !lPurse.cost(price)) return;   // 钱不够直接退出
    ...
}
```

需要把 `HeroSpawn.purse` 传进据点建筑（`Stronghold.strongholdBuilding` 已持有 `spawn`）。

---

## 阶段 2：玩法改造（1–2 周）

### 2.1 英雄体系重构

现状：`Hero`(49 方法/73 字段) 是上帝类，三个英雄靠 `switch` 与不同 Action 组合。

建议：

1. 抽 `IHeroArchetype` 接口（`Skill1 / Skill2 / Passive / MoveProfile`）
2. `HeroConfigList`（已有）保留为数据容器，改为从 `map.obc.iw` 加载
3. 每个英雄一个类：`SwordWarrior : HeroArchetypeBase`
4. 技能用统一 `SkillBase`（现有 `SkillBarrier / SkillBoomerang / SkillInvisibility` 已具备雏形）

### 2.2 技能系统

现有技能类：`SkillBarrier`、`SkillBoomerang`、`SkillInvisibility`、`SkillAwardHealth`、`SkillState`。

建议统一：

```
SkillBase
 ├─ OnCast(Hero)
 ├─ OnUpdate(dt)
 ├─ OnEnd()
 └─ Cooldown / Cost / Targeting
```

再让 `map.obc.iw` 的 `skillPoint` / `turretSkillState` 驱动数值。

### 2.3 经济系统

现状：金币只进商店，据点出兵免费。

建议两条线打通：

| 线 | 入口 | 落点 |
|---|---|---|
| 击杀 → 金币 → 兵 | `WMPurse.add` | `StrongholdBuilding._BuySoldier(purse)` |
| 击杀 → 金币 → 装备 | `WMPurse.add` | `WMItemBag.buyOne`（已有） |

再加“经济追赶”：`WMPurse.addMoneyByTime` 的速率改成随局势浮动（落后方加速）。

### 2.4 兵线与据点

`Stronghold`(36/57) 已含占领进度、生长、兵种计数。
可加：

- 占领速度随“周围单位数量”变化（现在是固定速度）
- 据点提供**金币收入**而非直接给兵

---

## 阶段 3：UI 重做（2–4 周）

现状：`GameGUIBase`(88 方法) 是一套**自绘的即时模式 GUI**，配合预制体 + 图集。
它不是 uGUI，所以改造成本高。

两条路：

| 方案 | 说明 | 成本 |
|---|---|---|
| A. 继续用自绘 GUI | 沿用 `GameGUIRenderer`，只改布局与图集 | 低 |
| B. 迁移到 uGUI | `refs/UnityEngine.UI.dll` 已引用，可新建 Canvas | 中高，但后续维护性好 |

推荐：**结算/商店/加点等“静态复杂界面”迁 uGUI，局内 HUD 保留自绘**（性能与风格一致）。

---

## 阶段 4：网络与工具（并行）

- **权威服务器**：目前 `gameVerify=0`，客户端可改内存。要做公网匹配，
  把关键数值（伤害/金币/出兵）上移到服务器（`服务器/iw_server.py` 已有协议基础）。
- **地图编辑器**：`Urz` + `TileMapEditor` 已在源码内，可独立打包成编辑器工具。
- **UGC 分发**：`.iwm` 打包 + Workshop 订阅（`ResourcePacker/Unpacker` 已具备）。

---

## 附：改哪里不用重编译

| 目标 | 改这里 |
|---|---|
| 英雄/兵/据点数值 | `Scene/**/map.obc.iw` 的 `component` |
| 地图布局/据点位置 | `Scene/**/map.map.iw` 的 `objects` |
| 局外加点 | `config.cfg` 的 `"points"` |
| 服务器地址 | 客户端登录界面手动输入，或 `MainMenu` 预置项 |

改完地图记得**所有玩家用同一份文件**（客户端会比对地图哈希）。
