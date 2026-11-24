param(
    [int]$ProcessId,
    [string]$Text = "diestr",
    [int]$DelayMs = 120
)

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class T {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
}
"@

$p = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
if ($null -eq $p) { Write-Output "NO_PROC"; exit 1 }
$h = $p.MainWindowHandle
if ($h -eq [IntPtr]::Zero) { Write-Output "NO_HWND"; exit 2 }

[void][T]::ShowWindow($h, 9)
[void][T]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 500

$KEYUP = 0x0002
foreach ($ch in $Text.ToCharArray()) {
    $vk = [byte][char]([string]$ch).ToUpper()
    [T]::keybd_event($vk, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 40
    [T]::keybd_event($vk, 0, $KEYUP, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds $DelayMs
}
Write-Output ("TYPED " + $Text + " hwnd=" + $h)
