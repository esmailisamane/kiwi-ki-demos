# Schreibt alle 2 Sekunden die Verbindungen der opencode-Prozesse auf, die NICHT zum eigenen Rechner gehen.
# Start: powershell -File netzwerk_log.ps1 -Ziel ausgaben\netzwerk.csv -Sekunden 600
param([string]$Ziel = "ausgaben\netzwerk.csv", [int]$Sekunden = 600)
$ende = (Get-Date).AddSeconds($Sekunden)
"zeit,prozess,entfernt,port,status,name" | Out-File -Encoding utf8 $Ziel
$gesehen = @{}
while ((Get-Date) -lt $ende) {
    $ids = (Get-Process -Name opencode -ErrorAction SilentlyContinue).Id
    if ($ids) {
        Get-NetTCPConnection -OwningProcess $ids -ErrorAction SilentlyContinue |
            Where-Object { $_.RemoteAddress -notin @("127.0.0.1", "::1", "0.0.0.0", "::") } |
            ForEach-Object {
                $key = "$($_.RemoteAddress):$($_.RemotePort)"
                if (-not $gesehen.ContainsKey($key)) {
                    $gesehen[$key] = 1
                    $adresse = $_.RemoteAddress
                    $name = (Get-DnsClientCache -ErrorAction SilentlyContinue | Where-Object { $_.Data -eq $adresse } |
                        Select-Object -ExpandProperty Entry -Unique) -join " "
                    "$(Get-Date -Format HH:mm:ss),$($_.OwningProcess),$adresse,$($_.RemotePort),$($_.State),$name" |
                        Out-File -Append -Encoding utf8 $Ziel
                }
            }
    }
    Start-Sleep -Seconds 2
}
