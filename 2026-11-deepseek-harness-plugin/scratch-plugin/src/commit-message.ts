import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'commit-message'
export const inject = ['tools']

export interface Config {
  maxLength: number
}

export const Config: Schema<Config> = Schema.object({
  maxLength: Schema.number().default(72),
})

export function apply(ctx: Context, config: Config) {
  ctx.tools.register(defineTool({
    name: 'commit_message',
    description: 'Format a short commit message from a type and a summary.',
    parameters: {
      type: { type: 'string', required: true, description: 'fix, feat or docs' },
      summary: { type: 'string', required: true, description: 'What changed, in a few words' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const line = `${args.type}: ${args.summary}`
      return line.slice(0, config.maxLength)
    },
  }))
}
