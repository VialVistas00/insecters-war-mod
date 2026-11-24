param(
    [int]$ProcessId,
    [int]$W = 0,
    [int]$H = 0,
    [switch]$ReadOnly
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class WR {
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr hWnd, int x, int y, int w, int h, bool repaint);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr hWnd, out RECT r);
    [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr hWnd, ref POINT p);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X, Y; }
}
"@

$p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($null -eq $p) { Write-Output "NO_PROC"; exit 1 }
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Output "NO_HWND"; exit 2 }

if (-not $ReadOnly) {
    [void][WR]::ShowWindow($h, 9)                       # SW_RESTORE
    Start-Sleep -Milliseconds 300
    if ($W -gt 0 -and $H -gt 0) {
        [void][WR]::MoveWindow($h, 0, 0, $W, $H, $true)
        Start-Sleep -Milliseconds 700
    } else {
        [void][WR]::PostMessage($h, 0x0112, [IntPtr]0xF030, [IntPtr]::Zero)   # SC_MAXIMIZE
        Start-Sleep -Milliseconds 900
    }
}

$c = New-Object WR+RECT
[void][WR]::GetClientRect($h, [ref]$c)
$pt = New-Object WR+POINT
[void][WR]::ClientToScreen($h, [ref]$pt)

# 与 win_rect.ps1 同样的输出格式：客户区在屏幕上的矩形
Write-Output ("RECT " + $pt.X + " " + $pt.Y + " " + ($c.Right - $c.Left) + " " + ($c.Bottom - $c.Top))
