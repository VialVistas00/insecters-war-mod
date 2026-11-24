param(
    [int]$ProcessId,
    [int]$X,
    [int]$Y,
    [int]$HoverMs = 500,
    [switch]$NoClick
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class A2 {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@

$p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($null -eq $p) { Write-Output "NO_PROC"; exit 1 }
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Output "NO_HWND"; exit 2 }

[void][A2]::ShowWindow($h, 9)
Start-Sleep -Milliseconds 200
[void][A2]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 350
[void][A2]::SetCursorPos($X, $Y)
Start-Sleep -Milliseconds $HoverMs
if (-not $NoClick) {
    [A2]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 70
    [A2]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
}
$fg = [A2]::GetForegroundWindow()
Write-Output ("CLICK {0},{1} fg={2} same={3}" -f $X, $Y, $fg, ($fg -eq $h))
