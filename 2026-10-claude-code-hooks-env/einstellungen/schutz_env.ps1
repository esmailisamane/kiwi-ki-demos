# PreToolUse-Hook: blockiert jeden Werkzeug-Aufruf, der die Datei .env nennt (Pfad oder Befehlstext).
# Exit-Code 2 = blockieren; die Meldung auf stderr liest Claude als Grund.
# Wichtig: Stürzt der Hook ab, blockiert er auch (catch) - sonst würde er im Fehlerfall alles durchlassen.
$ErrorActionPreference = 'Stop'
try {
    $e = [Console]::In.ReadToEnd() | ConvertFrom-Json
    $t = $e.tool_input
    $text = "$($t.command) $($t.file_path) $($t.path) $($t.pattern)"
    if ($text -match '(?i)\.env(?![\w.])') {
        [Console]::Error.WriteLine("Blockiert vom Hook: .env ist geschuetzt ($($e.tool_name)).")
        exit 2
    }
    exit 0
} catch {
    [Console]::Error.WriteLine("Hook-Fehler, sicherheitshalber blockiert: $_")
    exit 2
}
