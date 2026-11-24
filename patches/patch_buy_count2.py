import io
import sys

sys.stdout.reconfigure(encoding="utf-8")
p = r"D:\游戏\Insecters War\iw-opensource\src\SoldierListFactory.cs"
s = io.open(p, encoding="utf-8-sig").read()

old = '''		int pending = ConsumePendingNextWave();
		if (pending >= 0 && pending < SoldierFactorySystem.Singleton.soldierList.Count)
		{
			WMSoldierProduceInfo info = SoldierFactorySystem.Singleton.soldierList[pending];
			if ((bool)info)
			{
				produceInfos.Insert(0, new SoldierProduceInfo(info, produceIntervalInSoldier));
				// 证明"只注入一次"：这行每次消费只打一次，下一波不再出现
				Debug.Log(string.Concat("[IWVERIFY] nextWaveInject route=", base.name,
					" soldier=", info.showName, " id=", pending,
					" queueCount=", produceInfos.Count,
					" remaining=", pendingNextWaveSoldierId));
			}
		}'''

new = '''		int pending = pendingNextWaveSoldierId;
		int pendingCount = pendingNextWaveCount;
		// 一次性消费：这一波注入后立刻清空，下一波回到原有配置
		pendingNextWaveSoldierId = -1;
		pendingNextWaveCount = 0;
		if (pending >= 0 && pending < SoldierFactorySystem.Singleton.soldierList.Count
			&& pendingCount > 0)
		{
			WMSoldierProduceInfo info = SoldierFactorySystem.Singleton.soldierList[pending];
			if ((bool)info)
			{
				// 买几次就插几个 —— 这才是"多次购买叠加"
				for (int k = 0; k < pendingCount; k++)
				{
					produceInfos.Insert(k, new SoldierProduceInfo(info, produceIntervalInSoldier));
				}
				Debug.Log(string.Concat("[IWVERIFY] nextWaveInject route=", base.name,
					" soldier=", info.showName, " id=", pending,
					" count=", pendingCount,
					" queueCount=", produceInfos.Count));
			}
		}'''

if old not in s:
    raise SystemExit("ANCHOR MISSING inject")
s = s.replace(old, new, 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok: inject loop")
