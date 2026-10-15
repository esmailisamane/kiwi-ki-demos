# Schreibt jedes Hook-Ereignis mit Zeitstempel (Millisekunden) in hooks.log.
# Bei Notification zusaetzlich: Windows-Benachrichtigung unten rechts (Toast), kostenlos, ohne Zusatzmodul.
$raw = [Console]::In.ReadToEnd()
$e = $raw | ConvertFrom-Json
$now = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.fff")
$type = $e.notification_type
if (-not $type) { $type = $e.tool_name }
"$now`t$($e.hook_event_name)`t$type`t$($e.message)" | Out-File -FilePath "$PSScriptRoot\..\..\hooks.log" -Append -Encoding utf8

if ($e.hook_event_name -eq "Notification") {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $t = $xml.GetElementsByTagName("text")
    $t.Item(0).AppendChild($xml.CreateTextNode("Claude Code")) | Out-Null
    $t.Item(1).AppendChild($xml.CreateTextNode($e.message)) | Out-Null
    $app = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($app).Show([Windows.UI.Notifications.ToastNotification]::new($xml))
}
