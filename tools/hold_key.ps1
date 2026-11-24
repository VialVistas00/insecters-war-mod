param(
    [int]$ProcessId,
    [string]$Key = "U",
    [int]$HoldMs = 1600
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($null -eq $p) { Write-Output "NO_PROC"; exit 1 }
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Output "NO_HWND"; exit 2 }

[void][W]::ShowWindow($h, 9)   # SW_RESTORE
[void][W]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 400

$vk = [byte][char]$Key.ToUpper()
$KEYUP = 0x0002

[W]::keybd_event($vk, 0, 0, [UIntPtr]::Zero)
Start-Sleep -Milliseconds $HoldMs
[W]::keybd_event($vk, 0, $KEYUP, [UIntPtr]::Zero)

Write-Output ("SENT " + $Key + " hold " + $HoldMs + "ms hwnd=" + $h)
