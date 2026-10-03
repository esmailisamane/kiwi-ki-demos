import { expect, test } from 'claude-code/testing'

test('blocks a force push', async ($, on) => {
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'git push --force origin main' })
  expect(r.deny).toContain('blocked')
})

test('blocks rm -rf', async ($, on) => {
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'rm -rf build' })
  expect(r.deny).toContain('blocked')
})

test('lets a normal push through', async ($, on) => {
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'git push origin feature/login' })
  expect(r.result).toBe('ran')
})

test('blocks the short form git push -f', async ($, on) => {
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'git push -f origin main' })
  expect(r.deny).toContain('blocked')
})

// Honest limit: the mod only reads the command text
test('LIMIT: misses a force push hidden in a script', async ($, on) => {
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'Bash', command: 'sh deploy.sh' })
  expect(r.result).toBe('ran')
})

test('blocks a force push in PowerShell (Windows)', async ($, on) => {
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'PowerShell', command: 'git push --force origin main' })
  expect(r.deny).toContain('blocked')
})
