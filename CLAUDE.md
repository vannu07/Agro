# Farm-IQ Project Context

## Integrated Build Stack (2026 Edition)
- **IDE**: Google Antigravity
- **Design**: Google Stitch
- **Implementation**: Claude Code
- **Stack**: React (suggested), HTML/Tailwind (from Stitch), Node.js

## Architecture Decisions
- Design in Stitch, convert to React via Claude Code.
- Multi-agent orchestration managed through Antigravity Mission Control.

## Project Rules
- Maintain clean Git history: commit after each accepted diff.
- Reference Stitch screens via `@stitch` or MCP proxy for implementation.
- Use `.claude/commands/` for custom automation.

## Environment Config
- `STITCH_API_KEY`: Configured in `.env`
- `PROJECT_ID`: antigravity-01-489409
