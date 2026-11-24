# 把 iw-mod 的改动同步到 GitHub
# 用法：在 PowerShell 里执行  .\push.ps1  "提交说明"

param([string]$Message = "update")

$Root = "D:\游戏\Insecters War\iw-mod"
Set-Location $Root

# 从凭据管理器取 token（不落盘）
$cred = "protocol=https`nhost=github.com`n`n" | git credential fill 2>&1
$tok = ($cred | Select-String -Pattern '^password=(.+)$').Matches[0].Groups[1].Value
if (-not $tok) { Write-Output "未找到 GitHub 凭据"; exit 1 }

git add -A
git -c user.name="VialVistas00" -c user.email="VialVistas00@users.noreply.github.com" commit -m $Message
if ($LASTEXITCODE -ne 0) { Write-Output "没有需要提交的改动"; }

# 临时把 token 放进 remote，推完立刻还原（token 不会留在 .git/config）
git remote set-url origin ("https://" + $tok + "@github.com/VialVistas00/insecters-war-mod.git")
# 本机全局代理 127.0.0.1:7890 未必在跑，这里强制绕过
git -c http.proxy= -c https.proxy= push origin main
git remote set-url origin "https://github.com/VialVistas00/insecters-war-mod.git"

Write-Output "完成：https://github.com/VialVistas00/insecters-war-mod"
