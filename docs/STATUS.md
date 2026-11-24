# 当前版本状态（2026-11-22）

## 一句话

游戏当前跑的是 **AI-only 版本**：原始游戏 + AI 相关改动。
技能分支系统已从构建中摘除，源码保留在 `src_disabled/`，随时可恢复。

---

## 三个版本文件

| 文件 | SHA-1 | 大小 | 说明 |
|---|---|---|---|
| `服务器\backup\Assembly-CSharp.dll.orig` | `866de55c50bf` | 1,546,752 | **原始零售版**，未做任何改动 |
| `服务器\backup\Assembly-CSharp.dll.ai-only` | `49d077d117a2` | 1,692,160 | **当前部署中**：原版 + AI 改动 |
| `服务器\backup\Assembly-CSharp.dll.modded-20261122` | `f50de02663a3` | 1,707,520 | 上一版全量改版（含技能分支），留档 |

`InsectersWar_Data\Managed\Assembly-CSharp.dll` = `ai-only`（哈希一致）。

---

## AI-only 版本包含的改动

### 1. AI 加点策略（`src/HeroSpawn.cs`）
- 原版：`pLevel % 3` 在 物理攻击 / 生命 / 能量攻击 之间轮转
- 现在：**优先点满物理攻击**，其余属性随机（受 `maxPoint` / `minLevel` 约束，与玩家同一套规则）

### 2. AI 行为扩展（`src/HeroAI.cs`、`src/PickupPointRegistry.cs`、`src/AwardHealth.cs`、`src/AwardSP.cs`）
决策优先级：

1. 血量 ≤ 25%，或 < 50% **且最近 2 秒掉过血** → 撤退
2. 附近 12 格内敌方小兵 ≥ 3 → **farmLane 清兵**
3. 附近有残血敌方英雄 → gank 追击
4. 脱战且有补给点（离己方出生点 ≥ 12 格）→ **contestPickup 抢点**
5. 否则 pushLane

配套修正：
- 已经在家（距出生点 < 9 格）时不再撤退，避免赖在家里
- 推线时若"前线"还在自家门口，改朝**敌方出生点**推进
- 找不到前线时的兜底从"自己家"改为"敌方出生点"
- 卡住判定只在 `pathAgent.pathing == true` 时生效（原来站着开火也会被判卡，一局误触发 400+ 次）
- 技能释放目标增加 `Physics.OverlapSphere` 兜底（原来只靠 4 方向射线，看不见侧面敌人）

### 3. 附带保留的其它改动
- 结算界面「返回大厅」按钮（`GameResultExitButton`）
- 范围伤害不再按命中数均摊（`SphereHarmByDetector.noDivide`）
- 等级上限 25 + 每级经验递增 + 25 技能点
- 生化蜂攻击半径放大、指挥官医疗包/轰炸/防御墙修复
- 买兵面板书签（`HeroCommandPanel` + `IwGuiSkin`）

> 以上都在 `src/` 里正常参与编译，属于已交付内容。

---

## 已摘除的技能分支（`src_disabled/`）

| 文件 | 作用 |
|---|---|
| `HeroSkillBranch.cs` | 分支数据层（蓄力剑气 / 双段环形斩击，写 config.cfg） |
| `SwordBranchBehaviour.cs` | 两套 U 技能实现、F8 切换 |
| `SwordBranchEffect.cs` | 程序生成的月牙 / 圆环特效 |
| `RoomSkillBranchPanel.cs` | 房间界面的分支切换按钮 |

摘除时同步注释掉两处挂载点：
- `src/HeroSetting.cs` → `SwordBranchBehaviour.Attach`
- `src/NetworkRoomGUI2.cs` → `RoomSkillBranchPanel.Ensure`

**恢复方法**：把四个文件移回 `src/`，取消上述两处注释，重新 `python build.py`。

---

## 实测数据（AI-only 版本，单局 64 秒自检）

```
[IWVERIFY] HeroAI 数量: 5
[IWVERIFY] 即时: 放技能=2 追击=0 游走=0 自救中=0
[IWVERIFY] 累计: 技能释放=32 进入追击=0 脱困自救=0
[IWVERIFY] 离家距离: 99 89 100 90 89 | 贴家(<9)=0/5
```

- `技能释放=32` —— AI 会放技能（修正前一直是 0）
- `脱困自救=0` —— 不再误判卡地形（修正前一局 422 次）
- `贴家(<9)=0/5` —— **5 只 AI 全部出门，没有赖在家里**
- 整局 `Exception 0`

---

## 回滚指令

```bat
:: 回到原始零售版
copy /y "服务器\backup\Assembly-CSharp.dll.orig" "InsectersWar_Data\Managed\Assembly-CSharp.dll"

:: 回到 AI-only 版
copy /y "服务器\backup\Assembly-CSharp.dll.ai-only" "InsectersWar_Data\Managed\Assembly-CSharp.dll"

:: 回到全量改版（含技能分支）
copy /y "服务器\backup\Assembly-CSharp.dll.modded-20261122" "InsectersWar_Data\Managed\Assembly-CSharp.dll"
```
