param(
    [int]$ProcessId,
    [int]$X,
    [int]$Y,
    [int]$DelayMs = 250
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@

$p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($null -eq $p) { Write-Output "NO_PROC"; exit 1 }
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Output "NO_HWND"; exit 2 }

[void][M]::ShowWindow($h, 9)
[void][M]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 200
[void][M]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 200

$fg = [M]::GetForegroundWindow()
[void][M]::SetCursorPos($X, $Y)
Start-Sleep -Milliseconds 120

$LDOWN = 0x0002
$LUP = 0x0004
[M]::mouse_event($LDOWN, 0, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds 60
[M]::mouse_event($LUP, 0, 0, 0, [UIntPtr]::Zero)

Write-Output ("CLICK " + $X + "," + $Y + " fg=" + $fg + " target=" + $h + " same=" + ($fg -eq $h))
