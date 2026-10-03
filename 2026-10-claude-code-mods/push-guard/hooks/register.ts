// Commands that destroy work: force push and recursive delete
const RISKY = /\bgit\s+push\b.*(--force|\s-f\b)|\brm\s+-(rf|fr|r)\b/

export function register(on) {
  // Runs before every shell command – on Windows Claude uses PowerShell
  on('tool.call', { tool: ['Bash', 'PowerShell'] }, async ($, e, next) => {
    if (RISKY.test(e.command)) {
      // No call to next: the command never runs, Claude reads the reason
      return { deny: 'push-guard: blocked "' + e.command + '". Ask the user first.' }
    }
    // Everything else runs as usual
    return next(e)
  })
}
