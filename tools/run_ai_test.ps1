﻿param(
    [int]$WaitSeconds = 95,
    [string]$Tag = "t"
)

$Root = "D:\游戏\Insecters War"
Set-Location $Root
$tk = Join-Path $Root "服务器\tools"

Get-Process InsectersWar -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Copy-Item "iw-opensource\build\Assembly-CSharp.dll" "InsectersWar_Data\Managed\Assembly-CSharp.dll" -Force
Remove-Item "InsectersWar_Data\output_log.txt" -Force -ErrorAction SilentlyContinue

Start-Process -FilePath "InsectersWar.exe" -WorkingDirectory $Root
Start-Sleep -Seconds 16

$p = Get-Process InsectersWar -ErrorAction SilentlyContinue | Sort-Object StartTime -Descending | Select-Object -First 1
if (-not $p) { Write-Output "START_FAILED"; exit 1 }
$me = $p.Id
Write-Output ("pid=" + $me)

# 取窗口矩形并按相对比例换算点击坐标
function Tap([double]$rx, [double]$ry) {
    $line = & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tk "win_rect.ps1") $me 2>&1 | Select-Object -First 1
    $px = 0; $py = 0
    if ($line -match 'RECT (\d+) (\d+) (\d+) (\d+)') {
        $px = [int]$matches[1] + [int]([double]$matches[3] * $rx)
        $py = [int]$matches[2] + [int]([double]$matches[4] * $ry)
    }
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tk "click_at.ps1") -ProcessId $me -X $px -Y $py 2>&1 | Out-Null
    Start-Sleep -Milliseconds 800
}

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tk "click_button.ps1") $me "Play!" 2>&1 | Out-Null
Start-Sleep -Seconds 25

# 开始游戏 -> 房间列表
& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tk "hold_key.ps1") -ProcessId $me -Key "J" -HoldMs 130 2>&1 | Out-Null
Start-Sleep -Seconds 6

# 创建房间
for ($i = 0; $i -lt 8; $i++) { Tap 0.1424 0.3642 }
Start-Sleep -Seconds 3

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $tk "hold_key.ps1") -ProcessId $me -Key "J" -HoldMs 160 2>&1 | Out-Null
Start-Sleep -Seconds 8

# READY
for ($i = 0; $i -lt 10; $i++) { Tap 0.8654 0.8684 }

Start-Sleep -Seconds $WaitSeconds
Write-Output "--- done"
