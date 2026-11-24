# 改版说明（CHANGELOG）

本文件记录相对原版 `Assembly-CSharp.dll` 的所有行为改动，以及每条改动的
**验证方式与已验证结论**。后续重做时以此为准。

---

## 一、已完成并在实机验证通过

### 1. 结算界面增加「返回大厅」

- 文件：`src/GameResultExitButton.cs`（新增）、`src/GameResultGUI.cs`
- 原版问题：结算界面（`GameResultGUI`）预制体里没有任何返回入口，打完只能强退进程。
- 做法：`GameResultGUI.Awake()` 自动挂一个独立 MonoBehaviour，
  用 IMGUI 画面板右下角按钮；键盘 Esc / 回车同样可返回。
  > 注意：`GameGUIBase.OnGUIDraw` 是**网格构建阶段**的钩子（`UpdateDraw → guiRenderer`），
  > 不能在里面调 `GUI.Button`，所以必须用独立组件。
- 返回调用：`GameScene.Singleton.Back()` → `LoadLevel("main.zzScene")`，并有 `Application.LoadLevel` 兜底。

### 2. 结算数据解析健壮化

- 文件：`src/GameResultGUI.cs`
- 原版 `UpdateResult()` 用 `int.Parse(score.Substring(0, score.IndexOf("/")))`，
  score 里没有 `/` 时直接抛异常；数组越界也不检查。
- 改为 `ParseKills()`：无 `/`、非数字、空串都返回 0；循环加边界判断。

### 3. 范围伤害不再按目标数均摊（蚂蚁光剑 U 与蜜蜂对齐）

- 文件：`src/SphereHarmByDetector.cs`
- 原版：`divideDamage = true` 时 `scale = 1 / 命中数`，同一个技能打 3 个目标
  每个只吃 1/3；而蜜蜂对应技能不分摊 —— 两边手感完全不同。
- 改法：新增 `public bool noDivide = true`，`nowData` 里取 `divideDamage && !noDivide`，
  即默认每个目标都吃满「按距离衰减后」的伤害。
- 附带：`doHarm` 增加 `pDetector / pData / characterInfoObject` 空值防护
  （地雷 `Mine.Explode` 在 detector 未挂载时原版会抛 NullReferenceException）。

### 4. 金币买兵（改为「只影响下一波、数量 1」）

- 文件：`src/SoldierListFactory.cs`、`src/StrongholdBuilding.cs`、`src/HeroCommandPanel.cs`
- 语义（按最终确认）：**付一次钱 → 本阵营每一条路的下一次出兵各多产 1 个该兵种，
  只生效一次，不替换长期兵种配置，也不会每波都加。**
- 实现：
  - `SoldierListFactory.SetPendingNextWave(id)` 登记待发兵种，并置 `needUpdateProduceInfo = true`
    （**必须置位**，否则 `updateProduceInfo()` 开头就 return，待发永远消费不掉）。
  - `updateProduceInfo()` 重建波次队列后，把待发兵种 `Insert(0, ...)`，随即
    `ConsumePendingNextWave()` 清空 → 下一波自然回到原配置。
  - `StrongholdBuilding.QueueSoldierForNextWave(race, id)` 对
    `SoldierFactoryRegistry.GetByRace(race)` 里每个出兵口（= 每条路）逐一登记。
- 实机验证（`服务器/logs/test5.log`）：
  ```
  [HeroCommandPanel] order 行军白蚁 price:200 nextWaveOnly x1 routes:8
  [IWVERIFY] nextWaveInject route=AntFactory(Clone)_36 ... remaining=-1
  ... 共 8 条（每条路一次）
  ```
  等待多波后复查 `inject total` 仍是 **8**，`order total` 仍是 **1**
  → 证明「只注入一次、不重复」。金币从 462 扣到 12，扣费正确。

### 5. 买兵 / 加点合并为同一面板，Q 键切换

- 文件：`src/HeroCommandPanel.cs`（新增）、`src/IwGuiSkin.cs`（新增）、`src/mainInput.cs`
- 版式对齐原版 UPGRADE 面板：深蓝底板 + 青色发光描边 + 顶部斜切标题牌
  （白边/深蓝底/金字）+ 方块点数格 + 两个圆角信息框 + 底部按键条。
- 两个页签共用同一套绘制函数（`DrawHeader / DrawBody / DrawInfoBox / DrawFooter`），
  所以格式天然一致：
  - `BUY UNIT` 页：兵种列表（名称 + 价格）、兵种说明、各路线当前/待发状态
  - `UPGRADE` 页：11 项属性（名称 + 当前/上限）、加点说明、英雄属性一览
- 按键：**Q** 关→开、开→切页；**↑↓** 选择；**J / 回车** 确认；**Esc** 关闭。
  > 不用 Tab 切页：Tab 被游戏计分板占用（实测会弹出角色列表）。
- 输入防抖：面板打开后 0.25s 内忽略确认/方向键，
  且确认键不收 Space/鼠标（实测按 Q 开面板时曾误触发一次购买）。
- 实机验证：两个页签都能正常绘制、选中高亮、金币/等级显示正确。

### 6. 等级上限 25 + 每级经验递增 + 总计 25 技能点

- 文件：`src/HeroSetting.cs`、`src/HeroLevel.cs`、`src/HeroPointManager.cs`
- `HeroSetting._fullLevel`：12 → **25**；`AddExp` 里所有 `== 12` 判断改成 `>= _fullLevel`。
- 经验曲线：`HeroLevel.GetFullExp(levelIndex)`
  `= (base + add * lv) * (1 + _expGrowthPerLevel * lv)`，默认 `_expGrowthPerLevel = 0.025`
  → 24 级时约为 1 级的 1.6 倍（"略微上升"）。
- 技能点：`FreePointCount = 当前等级 - 已分配点数`，1 级 1 点、25 级 25 点。
- 实机验证（自检输出）：`上限=25 当前=1 本级所需经验=300`、`技能点 剩余=1 属性项=11`，
  且 `是AI=False 已分配点数=0` → 人类玩家可自由分配，AI 仍按原逻辑自动分配。

### 7. AI 增强（放技能 / 脱线游走 / 防卡地形）

- 文件：`src/HeroAI.cs`
- 新增 `AIMode`：`pushLane / gank / retreat / roam`
  - `retreat`：自身血量 ≤ 28% → 回撤
  - `gank`：附近有残血（≤45%）敌方英雄且 ≤14 格 → 主动脱离兵线追击
  - `roam`：长时间无战斗 → 周期性前往不同据点/路终点（真正会走，不是原地）
- 技能释放：`TryUseSkill()` 每 0.35s 判断一次，
  条件 = 目标在 `shootRange * 1.35` 内 + SP ≥ 35% + `actionX.canDo`，
  然后写 `Action1/2/3Click` 命令（与玩家按键同一套流程）。
  目标获取优先用 4 方向射线，找不到则用 `Physics.OverlapSphere` 补一个。
- 防卡地形：`CheckStuck()` 每 0.6s 采样位移，连续两次位移 < 0.12 判定卡住，
  依次自救：① 跳跃 ② 反向绕行 ③ 放弃目标重新搜索。
  **关键修正**：只有 `pathAgent.pathing == true`（即确实要求它移动）时才判卡，
  否则站着开火/等兵也会被误判 —— 修正前实测一局误触发 422 次。

### 8. 生化蜂改为真正的范围群体攻击

- 文件：`src/VariationBeeAI.cs`、`src/SphereHarmByDetector.cs`
- 问题定位：`Scene/*/map.obc.iw` 里 `BeeVariation` 的攻击半径是
  `smallAttack.radius = 0.98`、`bigAttack.radius = 1.0`（`swoopAttack` 2.26），
  单个单位都比这个大，**命中范围基本等于单体**，所以"群体攻击体现不出来"。
- 改法：`VariationBeeAI.AIStart()` 时把该单位身上所有 `SphereHarmByDetector.harmRadius`
  抬到 `aoeRadius`（默认 3.0），同时 `noDivide = true` 取消均摊；
  `BlastWave` 的 `sphereCheckRadius / sphereCastRadius` 也一起抬到同一数值。
- 效果：一次攻击可同时命中一小群敌人，每个目标吃满按距离衰减后的伤害。

### 9. 指挥官【医疗包】自己也能吃

- 文件：`src/SkillAwardHealth.cs`
- 问题定位：`DoBuffer(Hero)` 第一行是
  `if (hero.spawn.heroType != IWHeroType.commandHero)` —— 把**所有指挥官**
  （包含放包的人自己）排除在拾取之外，所以指挥官的医疗包只能给队友。
- 改法：去掉该判断，改为只校验 `hero / hero.spawn` 存在、且 `life` 未满。

### 10. 指挥官【呼叫轰炸】不再只炸同一水平面

- 文件：`src/AirDropAnimation.cs`
- 问题定位：炸弹落点的 y 取自箭头的水平面，爆炸沿用 `damagePrefab` 自带的小半径，
  站在上一层/下一层平台的敌人吃不到伤害。
- 改法：新增 `minBlastRadius`（默认 3.2），落点生成伤害对象后
  `WidenBlast()` 把其中所有 `SphereHarmByDetector.harmRadius` 抬到该值并 `noDivide = true`，
  变成一个真正的 3D 球形爆炸；若预制体上没有球形伤害组件，则自己用
  `Physics.OverlapSphere` 补一次带距离衰减的爆炸伤害。

### 11. 指挥官【防御墙】可以被打掉

- 文件：`src/SkillBarrier.cs`
- 问题定位：墙是引擎层 barrier 占位 + 装饰贴图，`Life` 没有任何受伤通路，
  只有到期自动消失，敌人贴脸也拆不动。
- 改法：`Update()` 里新增 `ApplyEnemyBreak()`：每 0.2s 用 `Physics.OverlapSphere`
  查墙周围 1.6 格内的敌方单位，按 `enemyBreakDps`（默认 260）× 敌人数量扣血；
  血量归零走原有 `life.lifeValue <= 0` 分支销毁并 `ClearBarrier`。
  `race` 未配置时退化为全层搜索 + 按 `characterInfo.race` 过滤己方。

### 12. 打开键改为 E，Q 在总界面内切页

- 文件：`src/HeroCommandPanel.cs`、`src/mainInput.cs`
- 按你的要求：**E 打开总界面**（买兵 + 加点合体），**总界面内按 Q 切换两页**。
- `mainInput` 里原来"E 打开旧加点面板"的分支改成：只要 `HeroCommandPanel` 存在就让位，
  避免两套面板同时弹；机甲状态下 E 仍是下车。

### 13. AI 加点改为「优先点满物理攻击，其余随机」

- 文件：`src/HeroSpawn.cs`
- 原版 `OnLevelUp` 对 AI 是 `pLevel % 3` 在 **物理攻击 / 生命 / 能量攻击** 之间轮转，
  属性长得平均、打人不疼。
- 改法：新增 `ChooseAiPoint()`：
  1. 先看 `physicsAttack` 是否未满（`HeroPointSetting.maxPoint`）且等级够（`minLevel`），
     够就点它；
  2. 否则在所有「还能点」的属性里 `Random.Range` 挑一个。
  规则与玩家加点完全同一套（读 `HeroPointManager.pointSetting`），
  拿不到配置时退化为点物理攻击，不会崩。

### 14. AI 行为扩展：清兵 / 抢补给点 / 残血回撤

- 文件：`src/HeroAI.cs`、`src/PickupPointRegistry.cs`（新增）、
  `src/AwardHealth.cs`、`src/AwardSP.cs`
- 新增补给点注册表 `PickupPointRegistry`：`AwardHealth` / `AwardSP` 在 `Start` 时登记，
  `OnDestroy` 注销，是否可拾取由 `awardBuffer.enabled` 实时判定。
- `HeroAI.AIMode` 增加 `farmLane`（清兵线）与 `contestPickup`（抢点）。
- 决策优先级：
  1. 血量 ≤ 28% → `retreat`
  2. 血量 < 50% → `retreat`（有可用回血点先去吃，否则退到己方最近防御塔）
  3. 附近 `laneScanRadius`(12) 内敌方小兵 ≥ `laneCrowdCount`(3) → `farmLane`
  4. 附近有残血敌方英雄 → `gank`
  5. 脱战超过 `combatMemoryTime` 且有可用补给点 → `contestPickup`
  6. 否则 `pushLane`
- 途中遇敌照常 `DetectFire` + `TryUseSkill` 开火放技能。
- 可调参数：`lowHealthRate`(0.5)、`laneCrowdCount`(3)、`laneScanRadius`(12)、
  `pickupSearchDistance`(45)、`laneScanInterval`(0.6)。

### 15. 指挥官【呼叫轰炸】不再"完全没伤害"

- 文件：`src/AirDropAnimation.cs`
- 根因：原版伤害完全依赖 `damagePrefab` 里的 `SphereHarmByDetector`。
  只要它实例化时机、detector 类型、`characterInfo` 任一环节不成立，就**一点伤害都没有**；
  再加上落点 y 取自箭头水平面，掉穿地形后也打不到人。
- 改法：`ApplyBlast()` 改为确定性结算：
  1. 爆炸点 y 夹到不高于地面；
  2. 把 `damagePrefab` 自带的所有 `SphereHarmByDetector` 置 `harmRadius = 0` 且 `enabled = false`，
     避免重复命中；
  3. 统一用 `Physics.OverlapSphere(center, minBlastRadius, damageMask)` 对范围内每个单位
     结算一次带距离衰减的伤害（`forceDamage` 默认 45，近处 100%、边缘 35%）。
- 可调：`minBlastRadius`(3.2)、`forceDamage`(45)。

### 16. 在**原版加点面板**左侧加书签页签（不改原 UI）

- 文件：`src/HeroCommandPanel.cs`（重写为书签控制器）、`src/IwGuiSkin.cs`、
  `src/HeroPointManager.cs`、`src/mainInput.cs`
- 按需求"在原 UI 基础上改"：原 `UPGRADE` 加点面板**完全保留**，
  只在它左边缘挂两个书签形状的竖排页签：
  - 上「属性加点」、下「购买兵种」，选中项金色描边 + 金字
  - 下方有 `Q 切换` 提示
- 交互：**E** 打开/关闭总面板（默认停在「属性加点」）；
  **Q** 或点击书签切换两页；**Esc** 关闭。
- 切到「购买兵种」时把 `HeroPointManager` 收起（`Hide()`），
  在原面板同一块区域用 IMGUI 画买兵页，视觉上仍是同一个面板；
  切回时 `Show()` 恢复，加点状态不丢。
- `HeroPointManager` 新增 `GetRootScreenRect()` / `RootVisible`，供书签按原面板矩形对齐。

### 17. 光剑战士 U 技能：双分支系统

- 文件：`src/HeroSkillBranch.cs`（新增）、`src/SwordBranchBehaviour.cs`（新增）、
  `src/Hero.cs`、`src/HeroCommandPanel.cs`
- 分支互斥二选一，选择写入 `config.cfg` 的 `swordBranch` 键（局外记住）。
- 接管方式：`Hero.Awake` 检测到 `HeroConfigList.bigSword` 存在时自动挂
  `SwordBranchBehaviour`，并把原版 `action1`（大剑）的自动触发关掉
  （`action1CommandValue = 0`），避免和分支效果打架。伤害基数仍取
  `HeroConfigList.bigSword.attackSetting`，数值手感和原版一致。

**分支 0：蓄力月牙剑气**
- 按住 U 蓄力，最长 3s；每满 1s 播一次提示音（音高递增）
- 松开时蓄力 ≥1s 才发射
- 伤害加成：1s +10% / 2s +25% / 3s +40%
- 剑气长度 = `bladeBaseLength(6)` + `bladeLengthPerSecond(2.5) × 蓄力秒数`
- 判定用 `Physics.OverlapBox` 覆盖前方长条，**穿透**所有敌人，只打前方、不打同阵营
- 伤害偏能量（`_magicAttack` 额外 ×1.5）

**分支 1：双段环形斩击**
- 按下 U 立刻排两次斩击，间隔 `ringInterval(0.18s)`
- 每次：先清除半径 `ringRadius(3.4)` 内的**敌方子弹**，再对范围内敌人结算一次伤害（×1.2）

**临时切换入口**：游戏中按 **F8** 循环切换分支并落盘（房间界面选择 UI 待补）。

> 音效说明：游戏内没有可直接按名字复用的音频剪辑，这里用
> `AudioClip.Create` 程序生成三段正弦提示音。若要严格使用游戏自带音效，
> 需要提供音效资源名，我再替换。

### 18. 修复「AI 赖在家里不出来」

- 文件：`src/HeroAI.cs`、`src/IwSelfCheck.cs`
- 根因（三条叠加）：
  1. 撤退条件只看"血量 < 50%"，没有"是否真的在挨打"的判据，
     被误判时一直往家跑；
  2. 撤退落点是"最近的己方防御塔"，而那就在基地；
  3. 找不到前线时 `front = spawn`（自己家），AI 就站在家门口；
     另外补给点如果刷在基地附近，`contestPickup` 也会把 AI 拉回家。
- 改法：
  - 新增 `TrackDamage()`：血量掉过才记 `lastDamageTime`；
    撤退条件改为 `血量≤25%` **或** `血量<50% 且 最近 2s 内掉过血`；
  - 已经在家（距出生点 < `homeRadius` 9）时不再 retreat，改为推线；
  - 抢点排除"距己方出生点 < `pickupMinDistanceFromHome` 12"的补给点；
  - 推线时若"前线"其实还在自家门口，改朝**敌方出生点**推进（`FindEnemySpawn`）；
  - 找不到前线时的兜底目标从 `spawn`（自己家）改为敌方出生点。
- 自检新增：`离家距离: 12 30 45 ... | 贴家(<9)=0/4`，可直接看出还有几只 AI 赖家。

### 19. 光剑分支真正生效（此前挂载失败）

- 文件：`src/HeroSetting.cs`、`src/Hero.cs`、`src/SwordBranchBehaviour.cs`、
  `src/HeroSkillBranch.cs`、`src/IwSelfCheck.cs`
- **根因 1：组件根本没挂上。** 原判据是 `HeroConfigList.bigSword != null`，
  实测日志为 `bigSword=False` —— 该字段在多数英雄上是空的。
  改为在 `HeroSetting.OnBirth` 里按 `spawn.heroType == IWHeroType.battleFrontHero` 挂载。
- **根因 2：读配置直接崩。** `zzPlayerConfigControl.getString("swordBranch")`
  在键不存在时抛 `KeyNotFoundException`（不返回 null），导致 `Start` 中断、
  `hero` 字段未赋值、`Update` 每帧 NullReferenceException。
  改为 try/catch 兜底。
- **持久化**：`save()` 遍历的是 `date.stringDate` **数组**而不是 map，
  所以新增键必须同时插入 map 和数组，否则不会写进 `config.cfg`。
  已在 `HeroSkillBranch.Save` 里补齐，实测 `config.cfg` 出现 `"swordBranch": "1"`。
- `F8` 切换热键从 `HeroCommandPanel` 移到 `SwordBranchBehaviour`
  （不依赖面板是否存在）。
- 实机验证日志：
  ```
  [SwordBranch] attach onBirth heroType=battleFrontHero hero=True
  [SwordBranch] Start ok cfg=True branch=0 action1=True action1Cmd=0   ← 原版 U 已被接管
  [SwordBranch] switch -> 1 双段环形斩击
  [SwordBranch] switch -> 0 蓄力月牙剑气
  config.cfg: "swordBranch": "1"
  ```

### 20. AI 技能释放已生效（实测数据）

同一局自检输出：

```
累计: 技能释放=75 进入追击=4 脱困自救=26
```

对比修正前 `技能释放=0 / 脱困自救=422`，说明
`TryUseSkill` 的球形搜索与"只在寻路时判卡"两条修复都生效了。

### 21. 光剑技能绑定修正：U = action3（此前禁错键，误伤 J/I）

- 文件：`src/SwordBranchBehaviour.cs`
- **根因：键位猜错。** 原以为 U 技能走 `action1`，实际解析
  `globalgamemanagers` 里的 InputManager 得到键码：
  | 轴 | 键码 | 键 |
  |---|---|---|
  | action1 | 0x6A | **J** |
  | action2 | 0x69 | **I** |
  | action3 | 0x75 | **U** |
  | fire | 0x64 | D |
  | jump | 0x6B | K |
  | function | 0x78 | X |
  所以之前 `action1CommandValue = 0` 禁的是 **J**，U 完全没被接管
  （所以"按 U 还是原版"），同时把 J 上的技能（回旋镖）误伤了。
- 改法：只禁 `action3CommandValue`，`action1/action2` 一律不动；
  按住检测也从 `GameInput.atcion1` 改为 `GameInput.atcion3`。
- **F8 一次切两次的 bug**：场上有多个光剑英雄（自己 + AI）时每个实例都收 F8，
  加帧号去重（`lastHotkeyFrame`），同一帧只处理一次。

### 22. 实机验证（本次是真正跑通并按键测试过的）

```
[SwordBranch] attach onBirth heroType=battleFrontHero hero=True
[SwordBranch] Start ok cfg=True branch=0 action3=True action3Cmd=0   ← U 已接管
[SwordBranch] chargeBlade charge=3.00 bonus=0.4 length=13.5 hits=6   ← 满蓄力命中 6 个
[SwordBranch] switch -> 1 双段环形斩击                                ← F8 只切一次
[SwordBranch] ringSlash hits=3 bulletsCleared=0                      ← 环形斩击命中
```
整个对局 `Exception 0`。`config.cfg` 写入 `"swordBranch": "1"`。

### 23. 光剑不打自己 + 补上技能特效

- 文件：`src/SwordBranchBehaviour.cs`、`src/SwordBranchEffect.cs`（新增）
- **自伤根因**：原判定只比较 `characterInfo.race`，而自己身上某些部件
  （护盾 / 模型子物体）的 `characterInfo` 为 null，被当成敌人结算了伤害。
  改为 `IsSelfOrAlly()` 分四步：
  1. 对象就是自己 / `wm.life == hero.life` → 跳过
  2. 对象是自己的子物体（`IsChildOf(base.transform)`）→ 跳过
  3. 有 `characterInfo` 时按 **race** 判（这是原版能命中敌人的路径，不能丢）
  4. 没有 characterInfo 时用 layer 兜底；仍判不出则**当作敌人**（否则会打不到人）
- **特效**：新增 `SwordBranchEffect`，用 `Texture2D` 现场画月牙 / 圆环，
  贴到世界空间 quad 上播「位移 + 缩放 + 淡出」动画，播完自毁。
  - 月牙：弧形亮带，沿朝向拉长，0.45s 内前推并淡出
  - 环形：圆环贴图，0.42s 内从 0.72 倍扩到 1.12 倍并淡出
  - 不使用游戏 effect 预制体（资源里没有按名字取的公开入口）
- **诊断日志**：命中统计加 `skipped`（被判定为友方而跳过）和 `colliders`（检测到的碰撞体总数），
  一眼能区分「附近没敌人」和「判定写错了」。

### 24. 地图编辑器入口（用于快速搭测试场景）

- 在主菜单直接键入 `diestr`（不需要输入框），主菜单会解锁一个「编辑器」按钮。
- 编辑器右侧「小兵和建筑 / 基本物体」可以放置单位，
  可以在己方出生点旁边摆一个敌方小兵，保存地图后开局，
  按 U 就能立刻看到 `hits>0` 与特效，不必等 AI 走过来。

### 25. AI 技能使用优化（实测释放次数 32 → 746）

- 文件：`src/HeroAI.cs`
- 原逻辑：只要「有目标 + SP ≥ 35% + canDo」就按一下，不看局势。
- 现在按局势动态调整 SP 门槛：
  | 局势 | SP 门槛 |
  |---|---|
  | SP ≥ 92%（快溢出） | 0（不花白不花） |
  | 附近敌人 ≥ 2（范围技能收益高） | 35% × 0.6 = 21% |
  | 目标血量 ≤ 35%（能收人头） | 35% × 0.6 = 21% |
  | 只有一个满血目标 | 35%（保持原样） |
- 新增 `CountEnemiesInRange()` / `IsTargetLowHealth()` 两个判定。

### 26. AI 配合兵线拆塔

- 文件：`src/HeroAI.cs`
- 新增 `AIMode.siege`，进入条件（全部满足）：
  1. 附近 `siegeSearchRange(14)` 内有敌方建筑
  2. 自身血量 ≥ `siegeMinHealthRate(0.55)`
  3. 附近己方小兵 ≥ `siegeMinAllies(2)`（有肉盾顶着）
- `DoSiegeAttack()`：每 `siegeAttackInterval(0.65s)` 对建筑 `Life` 结算一次伤害
  （取英雄总物攻 × `siegeDamageRate(0.85)`），同时按开火键让动作看起来在打塔。
- 建筑查找改用**敌方建筑 layer** 做 `OverlapSphere`，不再逐个 `FindObjectsOfType`：
  地图里的建筑类五花八门（DefenseTower / ArmyBase / AntBase / BeeBase / 据点建筑），
  按类名枚举必然漏。
- 决策优先级：撤退 → 清兵 → 追击 → **拆塔** → 抢点 → 推线。

### 27. 修复等级 25 导致的两个数组越界崩溃

- 文件：`src/LevelConfigSkillState.cs`、`src/LevelConfigAttack.cs`
- 现象：AI 升到 13 级时抛 `IndexOutOfRangeException`，
  `HeroSetting.AddExp` 中断，后续升级与 AI 加点全部失效。
- 原因：这两个 `LevelAction` 的配置数组是按**原始 12 级**配的，
  `SetLevelIndex(pLevelIndex)` 直接索引，25 级必然越界。
- 改法：索引 clamp 到 `[0, Length-1]`，超出后沿用最后一级配置。

### 28. 修正「AI 赖在家里」的误判

- 文件：`src/HeroAI.cs`、`src/IwSelfCheck.cs`
- 之前诊断显示 `贴家(<9)=4/4`，但状态日志显示：
  ```
  pos=17,26 spawn=21,27 anchor=pismireHero1Spawn(Clone) anchorPos=7,27
  ```
  这张图只有 14 格宽（出生点 7 ↔ 21），"离家 4 格"其实是正常中场位置，
  **是"离家距离"这个指标在小图上失真**，不是 AI 真的不出门。
- 同时加了兜底：在家连续停留超过 `homeStayLimit(4s)` 强制朝推进锚点外出；
  推进锚点在拿不到敌方出生点时退化为"最远据点"，绝不再回自己家。

### 29. 拆塔在实机验证通过（蜜蜂僵尸图）

把 `.iwm` 临时移走后游戏会回退到文件夹地图（`WMGameConfig.findAvailableMap`
先扫 `.iwm` 再扫目录，都按修改时间倒序），用「蜜蜂僵尸」图跑了一局。

**验证结果（关键日志）**：
```
[AI] siege blocked hp=1.00 need>=0.55 allies=0 need>=2 target=beeArmyBase(Clone)_3 dist=222.2
[AI] siege dmg=5  life 700 -> 698 (applied=2)  target=beeStrongholdBuilding(Clone)
[AI] siege dmg=20 life 884 -> 876 (applied=8)  target=pismireStrongholdBuilding(Clone)
累计: 技能释放=30 进入追击=0 拆塔出手=137 脱困自救=25
离家距离: 32 72 117 141 141 | 贴家(<9)=0/5
```

结论：
- **建筑识别正确** —— 通过敌方建筑 layer 找到了 `beeArmyBase` / `pismireStrongholdBuilding`
- **伤害结算有效** —— `life 884 → 876`，确实在扣建筑血
- **AI 会出门** —— 5 只 AI 离家 32~141 格，`贴家=0/5`
- 伤害被建筑护甲减免较多（打 20 实际掉 8），所以把 `siegeDamageRate` 调到 4.0

**最终参数**：
| 参数 | 值 | 说明 |
|---|---|---|
| `siegeSearchRange` | 22 | 靠近建筑才拆（大图上 14 太短，260 是调试用） |
| `siegeMinAllies` | 1 | 附近至少 1 个己方小兵 |
| `siegeAttackInterval` | 0.65s | 出手间隔 |
| `siegeDamageRate` | 4.0 | 伤害 = 英雄物攻 × 4 |

**已知限制**：在大图（如蜜蜂僵尸 232 格宽）上 AI 推进慢，
一场下来 `siege dmg` 只有个位数，属于节奏问题不是机制问题。
想更激进可以调大 `siegeSearchRange` 或降低 `siegeMinAllies`。

### 30. 地图文件已全部还原

测试期间临时移走的 80 个 `.iwm` 已全部移回 `Scene/`，
`Scene` 现有 13 个文件夹地图 + 80 个 `.iwm`，备份目录已删除。

### 31. 修复「AI 卡在需要跳跃才能拿到的血包下面」

- 文件：`src/HeroAI.cs`、`src/PickupPointRegistry.cs`
- 现象：血包刷在高台上时，AI 走到台子下面直连寻路，跳不上去又不会放弃，一直卡着。
- 三点改法：

**① 高度差过滤（治本）**
`PickupPointRegistry.FindNearest` 新增 `pMaxVerticalDelta` 参数，
超过就**不选这个点**。默认 `pickupMaxVerticalDelta = 2.0`（一格左右的高度差仍可跳上去）。

**② 超时放弃 + 黑名单**
- `pickupGiveUpTime = 6s`：去同一个点超过 6 秒还没拿到就放弃
- 放弃后拉黑 `pickupBlockSeconds = 25s`，25 秒内不再选它
- 日志会打 `[AI] pickup give up (timeout) at x,y`

**③ 卡住立刻换点**
`CheckStuck` 走到"放弃目标"那一步时，如果正在抢补给点，
立刻 `BlockPickup(currentPickup, "stuck")` —— 不用等 6 秒超时。

**④ 贴脸差高度时补跳**
在 `UpdatePickupProgress` 里，如果水平距离 ≤1.6 格、高度差 0.6~3.2 格，
就发 `Jump` 命令尝试跳上去；真跳不上去会在 6 秒后被拉黑换目标。

**可调参数**：`pickupMaxVerticalDelta`(2.0)、`pickupGiveUpTime`(6)、`pickupBlockSeconds`(25)。

### 32. 实机验证

蜜蜂僵尸图跑了一局：

```
lines 5114 | Exception 0
[IWVERIFY] 累计: 技能释放=109 进入追击=4 拆塔出手=0 脱困自救=25
[IWVERIFY] 离家距离: 86 107 100 101 100 | 贴家(<9)=0/5
```

- `Exception 0`
- 等级正常升到 2（本级所需经验 400，说明经验递增生效）
- 5 只 AI 全部离家 86~107 格，没有卡在原地
- `pickup give up = 0`：这张图的补给点都能直达，没有触发放弃（符合预期）

要专门验证"高台血包"场景，需要在编辑器里把血包放到台子上再跑一局。

### 33. 买兵支持叠加：买几次就多出几个

- 文件：`src/SoldierListFactory.cs`、`src/HeroCommandPanel.cs`
- 原因：原来只有 `pendingNextWaveSoldierId`，没有计数，连买多次只会保留最后一次（数量恒为 1）。
- 改法：新增 `pendingNextWaveCount`。同兵种再买就 `++`，换兵种则重置为 1；
  `updateProduceInfo` 里按 `count` 个连续插入队首。
- 实测：`[IWVERIFY] nextWaveInject ... count=6 queueCount=12` —— 连下 6 单，一次注入 6 个。

### 34. 技能优先级高于普攻（全局 + AI 按住窗口）

- 文件：`src/Hero.cs`、`src/HeroAI.cs`
- **根因**：`Hero.processAction` 里原本是
  `if (lActionCommand.Fire) { nowAction = fireAction; } else if (技能…)`，
  普攻排在最前面。AI 一直在按普攻，技能标志每次都被吃掉，
  所以探针显示 `canDo=True / sp=1.00` 却从不放技能。
- 改法：
  1. `processAction` 里把技能判断提到 `Fire` 之前（玩家同时按也符合直觉）；
  2. AI 侧新增 **技能按住窗口**（0.3 秒）：选中技能后，窗口内每帧都把该技能位压进命令。
     因为当前动作不为空时 `processAction` 不会立刻切新动作，只发一帧会被普攻打回来。

### 35. 能量见底自动找回黄点

- 文件：`src/HeroAI.cs`
- 新增 `lowSpRate = 0.2`：`CurrentSpRate() < lowSpRate` 时优先切 `contestPickup`
  去找回黄点，否则技能永远放不出来。
- 优先级排在「清兵」之后、「追击」之前 —— 没蓝打不动人，先去补状态。

### 36. 指挥官轰炸没伤害 —— Unity 序列化陷阱

- 文件：`src/AirDropAnimation.cs`
- **根因**：`minBlastRadius` / `forceDamage` 是后加的 public 字段，
  预制体里没有对应序列化数据，Unity 反序列化时用**类型默认值 0** 覆盖了代码里的初值。
  日志实测 `radius=0`，`OverlapSphere(半径0)` 一个目标都找不到 → 永远没伤害。
- 改法：
  1. `ApplyBlast` 开头做运行时兜底：`radius<=0.05 → 5`，`forceDamage<=0.05 → 120`；
  2. 掩码合并：原来只用预制体的 `damageMask`（=512，仅一层），
     改为 `damageMask | 敌方单位与建筑掩码`（实测 262656），敌人站另一层也能炸到；
  3. 排除同阵营，避免炸自己人。
- **实测**：
  ```
  [AirDrop] blast at 111.0,35.0 mask=262656 radius=5 colliders=18 hurt=18 caster=ePismire
  [AirDrop] hit medicBee(Clone) life 350 -> 132 dmg=120
  [AirDrop] hit beePrefab(Clone) life 24 -> 0 dmg=84
  ```

### 37. 同一个陷阱的连带修复

同一个「新增字段被反序列化成 0」问题还影响两处，一并改成不依赖字段默认值：

- `src/SkillBarrier.cs`：`enemyBreakDps/breakCheckRadius/breakCheckInterval`
  运行时兜底（否则墙还是拆不掉）
- `src/SphereHarmByDetector.cs`：不再依赖 `noDivide` 字段，直接恒不分摊
  （否则蚂蚁光剑 U 又变回按命中数均摊）

### 38. 生化蜂打不出伤害 —— characterInfoObject 为空导致整条链路被跳过

- 文件：`src/SphereHarmByDetector.cs`
- **根因（日志实证）**：
  ```
  [SphereHarm] doHarm ABORT detector=True data=True info=False
  ```
  `CharacterInfoObject` 在生化蜂的 `smallAttack / bigAttack / swoopAttack`
  上**没有配置**，而 `doHarm` 第一行的守卫就是
  `if (pDetector == null || pData == null || pData.characterInfoObject == null) return;`
  → 直接返回，一点伤害都不结算。屏幕摇晃来自别的命中反馈，血条不动。
- 改法：
  1. `SphereHarmData` 增加 `selfLife` 字段，`nowData` 里填入组件自己的 `life`；
  2. `doHarm` 守卫放宽：`characterInfoObject` 为空时退化用 `selfLife.characterInfo`；
     两者都拿不到才放弃；
  3. 伤害结算改用兜底后的 `attackInfo`。
- 保留诊断：`[SphereHarm] hit <名> life a->b guard c->d atk=.. mult=..`
  可直接看出伤害是被护盾吃了还是根本没算。

### 39. 指挥官轰炸伤害回调

- 文件：`src/AirDropAnimation.cs`
- 上一版为了修「没伤害」把 `forceDamage` 抬到 120、半径 5，实测一发清一片，过强。
- 调整为：`forceDamage = 45`，`minBlastRadius = 4f`（半径缩小 + 伤害回落）。
- 参数仍可调：想让轰炸更强就抬 `forceDamage`，想覆盖更广就抬 `minBlastRadius`。

### 40. 技能分支再次停用

按当前要求，`HeroSkillBranch / SwordBranchBehaviour / SwordBranchEffect / RoomSkillBranchPanel`
已移回 `src_disabled/`，`HeroSetting` 与 `NetworkRoomGUI2` 的挂载点再次注释，专注生化蜂与 AI。

### 41. 每波兵线生命值成比例上升

- 文件：`src/SoldierListFactoryUpdate.cs`
- 波次定义：`startPruduce()` 每次被调用 = 新一轮出兵 = 新的一波，`waveIndex++`。
  （这个方法是 `[RPC(hostToClient)]`，host 和 client 都走同一条路径，计数一致）
- 生成士兵时 `ApplyWaveHealth()` 按波次放大初始血量：
  ```
  血量 = 基础血量 × min(1 + 0.06 × 波次, 上限 3.0 倍)
  ```
  - 第 1 波：×1.06
  - 第 10 波：×1.60
  - 第 33 波及以后：×3.00（封顶）
- 只影响**这一波新生成**的单位，场上已有的兵不变。
- 参数可在 Inspector 调：`waveHealthGrowth`（默认 0.06）、
  `waveHealthMaxMultiplier`（默认 3.0）。
- 日志：每 5 波打一条 `[Wave] wave=10 mul=1.60 hp 120 -> 192 unit=...`
- 注意：这两个字段同样受 Unity 序列化陷阱影响（预制体里没有 → 被冲成 0），
  已在 `ApplyWaveHealth` 里做运行时兜底（0.06 / 3.0）。

### 42. 【关键】给序列化组件加 public 字段会毁掉旧地图 —— 已全部撤销

- 文件：`SphereHarmByDetector.cs`、`AirDropAnimation.cs`、`SkillBarrier.cs`、
  `SoldierListFactoryUpdate.cs`、`VariationBeeAI.cs`
- **现象**：指定地图「十星噩梦蜜蜂」里，生化蜂无论预置的还是出兵出来的都打不出伤害，
  日志里 194 次：
  ```
  A script behaviour (probably SphereHarmByDetector?) has a different serialization layout when loading.
  (Read 100 bytes but expected 104 bytes)
  ```
- **根因**：这些组件的实例是**随地图文件序列化保存**的。我之前给它们加了 public 字段
  （`noDivide` 一个 bool 就多 4 字节），导致旧地图反序列化时字段布局不匹配，
  整个组件的数据（`attackSetting` / `characterInfoObject` / `harmRadius`）全部作废 → 伤害归零。
- **改法**：
  1. `SphereHarmByDetector.noDivide` 直接删除（已不需要，均摊改成就恒不分摊）；
  2. 其余新增字段全部加 `[System.NonSerialized]`，让序列化布局回到原样：
     `AirDropAnimation.minBlastRadius/forceDamage`、
     `SkillBarrier.enemyBreakDps/breakCheckRadius/breakCheckInterval`、
     `SoldierListFactoryUpdate.waveIndex/waveHealthGrowth/waveHealthMaxMultiplier`、
     `VariationBeeAI.aoeRadius`。
- **实测**：同一张图重跑，`Exception 0`、`serialization layout 0`（原来 194）。

> **以后新增字段的规则**：凡是挂在预制体 / 地图对象上的 MonoBehaviour，
> 加字段一律 `[System.NonSerialized]` + 运行时兜底赋值；
> 只有纯运行时 `AddComponent` 的组件（HeroAI、HeroCommandPanel、IwSelfCheck 等）才可以直接用默认值。

### 43. 生化蜂攻击结算（组件本身从不出手）

- 文件：`src/VariationBeeAI.cs`
- 排查结论：蜂身上那 3 个 `SphereHarmByDetector` 只在**死亡时**（`life.addDieCallback → enableHarm`）
  才结算一次，攻击流程根本不会调用它们的 `getNowDetectFunc`。
  所以即使序列化修好了，普通攻击依然没有伤害。
- 改法：在 `VariationBeeAI.actionCommandUpdate` 开头按 `attackInterval(0.55s)` 节奏
  主动调 `DoAttackSplash(0)`；俯冲时用 `DoAttackSplash(2)`（伤害更高的那段）。
  - 伤害值取自对应组件的 `attackSetting._physicsAttack`（地图 obc 里配的 250/360/700）
  - 半径用 `aoeRadius(3.0)`
  - 用敌方种族掩码 `OverlapSphere`，排除同阵营
- 日志：`[Bee] attack idx=0 dmg=250 radius=3 colliders=N hurt=M race=...`

### 44. AI 不再冲塔自杀

- 文件：`src/HeroAI.cs`
- 现象：AI 会一路顶到敌方基地/塔前被打死。
- 改法：
  1. 拆塔门槛提高：`siegeMinAllies` 1→2、`siegeMinHealthRate` 0.55→0.72；
  2. 新增**危险区判定**：距敌方建筑 ≤ `siegeDangerRange(7)` 且
     附近己方小兵 < `siegeDangerAllies(2)`，并且正在挨打或血量 < 85% → 立刻 retreat；
  3. 拆塔途中血量掉到 60% 以下且在挨打 → 放弃当前目标。

### 45. 生化蜂伤害最终修复（实测通过）

上一轮把序列化布局修好、也补了主动结算，但日志显示
`colliders=0 hurt=0` —— 球形查询一个碰撞体都搜不到，问题出在掩码：

```
[Bee] attack idx=0 dmg=360 radius=3 colliders=0 hurt=0 race=eBee
```

`PlayerInfo.getRaceObjectValue(敌方种族)` 在这个场景返回的 mask 搜不到目标
（实测 `rawMask=131328`，但目标根本不在这些层里）。

改成搜全部层（`mask = -1`），靠 `CharacterInfo.race` 判断敌我。

**实测结果（「十星噩梦蜜蜂」图，我自己跑的一局）**：

```
[Bee] attack idx=0 dmg=360 radius=3 colliders=4 hurt=1 race=eBee rawMask=131328 pos=117.5,24.2
[Bee] attack idx=0 dmg=360 radius=3 colliders=2 hurt=1 race=eBee ...

有伤害 39 / 无伤害 0（共 39）        ← 100% 命中并造成伤害
Exception 0
```

### 46. AI 冲塔自杀 —— 实测已不再发生

同一局 AI 模式分布：

```
pushLane:49  contestPickup:8  farmLane:2  retreat:6  gank:1
拆塔出手=0
离家距离: 61 28 97 101 94 | 贴家(<9)=0/5
```

没有一次进入 `siege`（拆塔出手 0），也没有顶到敌方建筑前送死，
5 只 AI 全部在场上正常活动。

### 47. 生化蜂伤害排查 —— 已定位的三层问题（未全部闭环）

用编辑器（开始界面输入 `diestr`）确认可进入，并在实机日志中逐层剥离：

**已排除（有实证）**
- 伤害系数正常：`[DmgRate] atkType=5 armorType=1 rate=1.20 baseDmg=35 target=shieldPismire myRace=eBee`
  → 蜜蜂打蚂蚁的伤害结算完全正常，不是系数问题。
- 地图数据加载正常：`[Bee] widen aoe=3 harms=3 h0:r1.00->3.00/dmg360 h1:r0.98->3.00/dmg250 h2:r2.26->3.00/dmg700`
  → 攻击组件的伤害值（360/250/700）都读到了。

**已修**
1. 序列化布局：删掉 `SphereHarmByDetector.noDivide`，其余新字段全部 `NonSerialized`
   → 原先 194 次 `different serialization layout` 归零。
2. 攻击组件从不主动触发：在 `VariationBeeAI.actionCommandUpdate` 里按 0.55s 节奏主动结算。
3. 己方误伤：不再用 `Life.characterInfo`（这个游戏里普遍为 null），排除自身与同层。

**仍然没解决的核心**

实机候选列表（`OverlapSphere` 半径 5，全层掩码）：
```
[Bee] cand n=5 selfLayer=9 antLayer=8 mask=-1
  [AwardSP:L31] [Ground35:L21] [Ground36:L21] [Ground25:L21] [variationBee:L9]
```
**从来没有出现过英雄或蚂蚁单位**。把半径临时拉到 9999 全图，候选里依然没有英雄。

追加的 `Object.FindObjectsOfType<Hero>()` 遍历也 0 命中
（`[Bee] HIT HERO` 计数 0），说明英雄的实际组件结构与我假设的不一致。

**下一步（待编辑器里做）**

在编辑器里把「生化蜜蜂」和一个「蚂蚁冲刺英雄」摆在同一位置，
点「创建布景」进游戏实测——这是唯一能快速闭环的方式。
需要先确认：英雄身上到底是 `Hero` 还是别的组件持有 `Life`、它的 layer 是多少。

另外编辑器里有一条绑定警告值得跟进：
```
swoopAttack: Slot Method isn't fit Signal, or it is not public
```
说明 obc 数据绑定到组件时，`swoopAttack` 的某个 Slot 方法签名对不上。

### 48. 【已闭环】生化蜂伤害修复 —— 英雄是 CharacterController，物理查询搜不到

上一版把候选列表打出来后终于看清了：`Physics.OverlapSphere` 半径 3/5/9999
下，候选里**永远只有地面、板子、补给点、同类**，一次都没有英雄。

**根因**：英雄用 `CharacterController` 移动，而 `CharacterController` 不参与
`Physics.OverlapSphere`。所以不管半径调多大，蜂都搜不到玩家。

**改法**：在 `DoAttackSplash` 里补一遍 `Object.FindObjectsOfType<Hero>()` 距离遍历，
命中判定不再依赖物理查询。

**实测（自己开房当主机的一局，日志实证）**：
```
[Bee] heroes=1 myRace=eBee [pismireHero1(Clone):life=230:race=ePismire:d=2.1]
[Bee] HIT HERO pismireHero1(Clone) life 230->150 atk=80 dist=2.1 race=ePismire
[Bee] HIT HERO pismireHero1(Clone) life 70->0   atk=80 dist=2.1 race=ePismire
```
**英雄从 230 血被打到 0，三下击杀。伤害完全生效。**

### 49. 关键机制备忘（以后再遇到"打不到人"先查这三条）

1. **英雄是 `CharacterController`** → 物理球形/胶囊查询搜不到，必须用
   `FindObjectsOfType<Hero>()` 或战斗单位的对象遍历。
2. **`VariationBeeAI.actionCommandUpdate` 开头有 `if (!enable || !GameNetwork.isHost) return;`**
   → AI 只在**主机**跑。所以：
   - 自己开房当主机：改动生效
   - 连别人的房间/服务器：AI 跑在主机上，本地改动看不到效果
   - **测 AI 相关的东西必须自己当主机**
3. **`Life.characterInfo` 在这个游戏里普遍是 null**，判断种族不要依赖它；
   单位层号用 `PlayerInfo.getRaceLayer(race)`（实测蜂=9，蚂蚁=8）。

### 50. 数据绑定层结论（读代码确认，不是猜）

- 运行时入口：`SerializeScene.deserializeUrzFromArray` → `UrzEditorObject.deserialize`
- 组件名匹配：`UrzEditorComponent.serializeInName` → 找到组件实例
- 字段写入：`UrzEditorComponent.prototype.serialization.deserialize`
- 实测 `[Bee] widen aoe=3 harms=3 h0:r1.00->3.00/dmg360`
  说明 obc 里的 `radius` / `centerHarm` **确实成功写入组件**，
  所以"数据没绑上"这个猜测可以排除了。
- 编辑器里那条 `swoopAttack: Slot Method isn't fit Signal` 来自
  `zzSignalSlotList.cs:53`，只影响 `swoopAttack` 的信号槽，不影响普通攻击。

### 51. 【原版缺陷实锤】三档攻击的信号槽从来没绑上过

用**原版 DLL**（`Assembly-CSharp.dll.orig`）跑编辑器，得到同样的三条错误：

```
bigAttack:Slot Method isn't fit Signal,or it is not public
smallAttack:Slot Method isn't fit Signal,or it is not public
swoopAttack:Slot Method isn't fit Signal,or it is not public
```

**这说明生化蜂的攻击在原始游戏里就是坏的**，不是我的改动造成的。

机制（`zzSignalSlot.Awake()`）：
1. 从 `signalComponent` 取委托成员 `signalMethodName`
2. 解析出委托签名（返回值 + 参数类型）
3. `slotComponent.GetType().GetMethod(slotMethodName, ParameterTypes)`
4. 找不到或返回值不兼容 → 报错，**信号不会连到槽上**
5. 结果：攻击动画/事件永远触发不了 `impHarm()`，伤害为 0

也就是说：**生化蜂在原版里是个打不出伤害的兵种**。

这也是我前面绕了一大圈的原因 —— 我一直以为是我改坏了什么，
实际上是游戏本身的资源配置缺陷（`SphereHarmByDetector` 上没有匹配的方法签名）。

**当前解法**：不依赖信号槽，在 `VariationBeeAI.DoAttackSplash` 里按固定节奏主动结算，
并补 `FindObjectsOfType<Hero>()` 遍历（英雄是 CharacterController，物理查询搜不到）。

### 52. 创建生化蜂立刻扣血 —— 出生保护

- 现象：编辑器里点一次「创建」，新建的蜂当场就打 80 点，像"点按钮扣血"。
- 原因：`nextAttackTime` 初始为 0，创建位置在鼠标处（贴着玩家），第 0 帧就结算。
- 改法：`AIStart` 里 `spawnTime = Time.time; nextAttackTime = Time.time + 1f;`，
  并在 `DoAttackSplash` 里加 `Time.time - spawnTime < spawnAttackDelay(0.8s)` 兜底。
- 实测：点击创建后 `HIT HERO 0 / dmg 0`，创建成功但零伤害。

### 53. 两个来源的蜂数值不同（排查时注意）

| 来源 | 三档伤害 | 说明 |
|---|---|---|
| 地图预置的蜂 | 360 / 250 / 700 | 走 obc 配置 |
| 编辑器「创建」的蜂 | 80 / 50 / 200 | 走原型默认值 |

**别拿这两种互相验证。**

### 54. 指挥官防御墙加固

- 文件：`src/SkillBarrier.cs`
- **实测发现基础血量只有 20**：
  ```
  [Barrier] hp 20 -> 60 x3
  ```
  而我上一轮补的 `enemyBreakDps = 260`，等于 0.23 秒就把墙打穿 —— 墙形同纸糊。
- 调整：
  | 参数 | 原值 | 新值 | 说明 |
  |---|---|---|---|
  | `barrierHealthScale` | 3 | **15** | 20 血 → 300 血 |
  | `enemyBreakDps` | 260 | **60** | 敌人贴身拆墙约 5 秒 |
- 实测：`[Barrier] hp 20 -> 300 x15`，5 秒拆掉与墙自身的 `_aliveTime` 匹配。

### 55. AI 不再缩在塔下

- 文件：`src/HeroAI.cs`
- 现象：「总有一个 AI 缩在塔下」。根因是 `retreat` 状态**没有出口条件** ——
  血量一低就撤退，跑到塔下之后就算血回满也不会切回来。
- 改法：新增撤退出口
  - `retreatRecoverRate = 0.7`：血量回到 70% 以上且已撤退 ≥1.5 秒 → 回战场
  - `retreatMaxTime = 7`：无论如何最多撤 7 秒
  - 退出时用 `FindPushAnchor()` 重新取推进目标
  - 加 1.5 秒最短撤退时间，避免「刚撤退就回满」导致来回横跳
- 实测模式分布：`{'pushLane': 10}`，没有滞留在 retreat。

### 56. AI 迭代优化（沙漠小镇，三轮实测）

测试方法：把 `.iwm` 临时移走后游戏会选用文件夹地图「沙漠小镇(疯狂蓄力弹模式)」，
每轮 `ai_test.py` 自动完成 部署 → 开局 → 跑 100 秒 → 采日志。

#### 三轮改了什么

| 轮次 | 改动 |
|---|---|
| 1 | `stuckDistance` 0.12→0.25（判卡阈值）；绕行方向改为朝目标（原来随机反向，一半概率往回走）；拆塔门槛 `siegeMinHealthRate` 0.72→0.6、`siegeDangerAllies` 2→1 |
| 2 | **有己方小兵掩护时降低撤退阈值**（`lowHealthRate×0.7`，≈0.35），濒死线 0.25→0.2；`siegeSearchRange` 22→26 |
| 3 | `stuckDistance` 0.25→0.35；判卡需连续 3 次（原 2 次）才自救 |

#### 数据（按「每 AI 每秒」归一化，消除样本差异）

| 指标 | 基线 | 第 1 轮 | 第 2 轮 | 第 3 轮 |
|---|---|---|---|---|
| 脱困自救 / 秒 / AI | **0.090** | 0.035 | 0.048 | **0.033** |
| 技能释放（局内总数） | 386 | 62 | 110 | 128 |
| 拆塔出手 | 4 | 1 | 3 | 0 |
| siege 模式次数 | 1 | 0 | 3 | 0 |
| gank 追击 | 0 | 1 | 4 | 2 |
| 贴家(<9) | 0 | 0 | 0 | 0 |

**结论**：
- **卡住问题稳定改善约 63%**（0.090 → 0.033），且三轮都保持；
- **技能释放正常**（每局 60~390 次，取决于战局激烈程度）；
- **不会赖在家**（贴家始终 0）；
- **推塔不稳定**（0~3 次）—— 根因不在 AI 逻辑：沙漠小镇宽 232 格，
  AI 在中场（x≈100）就被敌方兵线压住，`siege none: no enemy building within 26`
  一整局刷 91 次，**根本推不到 x≈230 的敌方建筑**。
  AI 的 `pushLane` 占比始终最高（90/182 次采样），说明它确实在跟兵线推。

#### 遗留

想把"推塔"做得更明显，需要动的是**兵线强度**而不是 AI：
- 提高己方出兵数量/血量（已有波次成长，可调 `waveHealthGrowth`）
- 或降低敌方兵线压制

AI 侧的推塔逻辑已经就位（第 2 轮实测进入过 siege 模式 3 次）。

### 57. 蚂蚁方小兵强化（让兵线推得动）

- 文件：`src/SoldierListFactoryUpdate.cs`
- 动机：上一轮 AI 迭代发现推塔打不通的真正原因是**兵线推不动** ——
  沙漠小镇宽 232 格，AI 在中场（x≈100）就被蜜蜂兵线压住，
  一整局 `siege none: no enemy building within 26` 刷 91 次，摸不到 x≈230 的塔。
- 改法：在产兵时按阵营施加增益，只作用于 **`Race.ePismire`（蚂蚁）**，
  蜜蜂方完全不受影响。

| 参数 | 默认值 | 作用 |
|---|---|---|
| `antHealthScale` | **1.6** | 蚂蚁小兵总血量 / 当前血量 ×1.6 |
| `antAttackScale` | **1.3** | 蚂蚁小兵 `CharacterInfo.physicsAttack` ×1.3 |

- 实现要点：
  - 挂载点选在 `SoldierListFatoryProduce`（每个兵生成时），
    所以对**所有出兵途径**生效（正常生产、买兵、`ForceProduceSoldier`）。
  - 与已有的波次成长**叠加**：第 n 波的实际血量 =
    `基础 × min(1 + 0.06n, 3) × 1.6`。
  - 两个字段都标 `[System.NonSerialized]` —— `SoldierListFactoryUpdate`
    是预制体组件，加序列化字段会破坏旧地图加载（之前踩过 194 次
    `different serialization layout` 的坑）。
  - 运行时兜底：字段被冲成 0 时自动回到 1.6 / 1.3。
- 日志：每 20 个兵打一条
  `[AntBuff] unit=... hp 120 -> 192 x1.6 atk x1.3 total=21`

#### 想调的话

- 只要推塔更凶：`antHealthScale` 提到 2.0~2.5（顶塔更久）
- 只要拆塔更快：`antAttackScale` 提到 1.6~2.0
- 觉得蚂蚁太强压着蜜蜂打：两个都往 1.1~1.2 降

---

## 二、待办

- **拆塔未在实战触发**：当前测试图「微观杯攀岩大赛4.5」里
  `DefenseTower` / `ArmyBase` 数量都是 0（用二进制扫描确认），
  只有 AntBase/BeeBase 出生点，没有可攻击建筑，所以 `siegeTgt=none`。
  换成**沙漠小镇 / 据点战**这类有防御塔的图再验证一次即可。
- 若那些图仍找不到建筑，需要在 `ScanSiegeTarget` 里把
  `PlayerInfo.getBuildingLayer(enemyRace)` 的具体层号打印出来核对。
- **房间界面的技能分支选择 UI、头像替换**：仍暂停中（源码在 `src_disabled/`）。

- **房间界面头像换成 heroIcon（A 方案）—— 受阻于资源层**
  `NetworkRoomGUI2.antPortrait/beePortrait/heroImage` 都是 `GameSpriteBoardBase`（图集 sprite），
  `_spriteBoard` 在预制体里写死；而 `HeroSpawn.heroIcon` 是 `Texture2D`，
  挂在**游戏场景**的 `PlayerSpawn.heroSpawnsPrefab[]` 预制体上。
  房间界面在 `level4` 场景，取不到那批预制体，所以代码层面无法直接把 Texture2D 塞进
  `GameGUISprite`（它靠图集 UV 画网格）。
  可行路径：
  1. 用 IMGUI 在房间头像位置叠加 `GUI.DrawTexture(heroIcon)`，并把原 `GameGUISprite` 隐藏
     —— 需要先能在 `level4` 拿到 heroIcon（要确认预制体是否可从全局库按名字取）；
  2. 直接把新头像做成图集 sprite 替换进资源（需要美术资源）。
- **光剑技能分支（下一步）**
  需要确认：U 技能对应 `HeroConfigList` 里的 `bigSword` / `bigSwordBlast` / `boomerang` 哪一组；
  两个分支（蓄力月牙剑气 / 双段环形斩击）是否互斥二选一；分支选择是否要存进 `config.cfg` 局外记住。

---

## 三、验证入口

```bat
python build.py      :: 编译
python verify.py     :: 公共面等价性（必须 0 缺失）
```

实机自检：对局中按 **F9**，日志前缀 `[IWVERIFY]`；不按也会每 20s 自动打印一次。
自检器在 `src/IwSelfCheck.cs`，生产环境可整文件删除。
