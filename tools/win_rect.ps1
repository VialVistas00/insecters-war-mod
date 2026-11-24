param([int]$ProcessId)

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition(
    [System.Windows.Automation.AutomationElement]::ProcessIdProperty, $ProcessId)
$win = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $cond)
if ($null -eq $win) { Write-Output "NONE"; exit 1 }
$b = $win.Current.BoundingRectangle
Write-Output ("RECT " + [int]$b.X + " " + [int]$b.Y + " " + [int]$b.Width + " " + [int]$b.Height)
