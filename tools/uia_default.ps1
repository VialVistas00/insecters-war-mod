Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$procId = [int]$args[0]
$name = if ($args.Count -gt 1) { $args[1] } else { "Play!" }

$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $procId)
$win = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $cond)
if ($null -eq $win) { Write-Output "NO_WINDOW"; exit 1 }

$btnCond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::NameProperty, $name)
$btn = $win.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $btnCond)
if ($null -eq $btn) { Write-Output "NO_BUTTON"; exit 2 }

$r = $btn.Current.BoundingRectangle
Write-Output ("BOUNDS " + $r.X + "," + $r.Y + "," + $r.Width + "," + $r.Height)

$legacy = $null
if ($btn.TryGetCurrentPattern([System.Windows.Automation.LegacyIAccessiblePattern]::Pattern, [ref]$legacy)) {
    $legacy.DoDefaultAction()
    Write-Output "LEGACY_OK"
    exit 0
}
Write-Output "NO_LEGACY"
exit 3
