param([int]$ProcessId, [string]$ButtonText = "Play!")

Add-Type @"
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;

public class W32 {
    public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr hParent, EnumProc cb, IntPtr lParam);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetWindowThreadProcessId(IntPtr hWnd, out int pid);
    [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr hWnd, uint msg, IntPtr w, IntPtr l);

    public const uint BM_CLICK = 0x00F5;
    public const uint WM_LBUTTONDOWN = 0x0201;
    public const uint WM_LBUTTONUP = 0x0202;

    public static List<IntPtr> FindByPid(int pid) {
        List<IntPtr> list = new List<IntPtr>();
        EnumWindows((h, l) => {
            int p; GetWindowThreadProcessId(h, out p);
            if (p == pid) list.Add(h);
            return true;
        }, IntPtr.Zero);
        return list;
    }

    public static List<IntPtr> Children(IntPtr parent) {
        List<IntPtr> list = new List<IntPtr>();
        EnumChildWindows(parent, (h, l) => { list.Add(h); return true; }, IntPtr.Zero);
        return list;
    }

    public static string Text(IntPtr h) {
        StringBuilder sb = new StringBuilder(256);
        GetWindowText(h, sb, 256);
        return sb.ToString();
    }
}
"@

$tops = [W32]::FindByPid($ProcessId)
if ($tops.Count -eq 0) { Write-Output "NO_TOP"; exit 1 }

foreach ($top in $tops) {
    $kids = [W32]::Children($top)
    foreach ($k in $kids) {
        $t = [W32]::Text($k)
        if ($t -eq $ButtonText) {
            [void][W32]::PostMessage($k, [W32]::BM_CLICK, [IntPtr]::Zero, [IntPtr]::Zero)
            Write-Output ("BM_CLICK sent to '" + $t + "' hwnd=" + $k)
            exit 0
        }
    }
    if ([W32]::Text($top) -eq $ButtonText) {
        [void][W32]::PostMessage($top, [W32]::BM_CLICK, [IntPtr]::Zero, [IntPtr]::Zero)
        Write-Output ("BM_CLICK sent to top '" + $ButtonText + "'")
        exit 0
    }
}

Write-Output "NO_BUTTON"
foreach ($top in $tops) {
    foreach ($k in [W32]::Children($top)) {
        $t = [W32]::Text($k)
        if ($t.Length -gt 0) { Write-Output ("child: " + $t) }
    }
}
exit 2
