# Quid Design System Skill

> **Read-only.** This repo is auto-published from [`netbasequid/quid-design-system-working`](https://github.com/netbasequid/quid-design-system-working). To make changes, work there.

Claude Code skill that applies the Quid (Terminal) design aesthetic to HTML artifacts. Provides Figma-exported design tokens compiled into a single CSS stylesheet with shadcn/ui-aligned semantic variables.

## Using this skill

Add to your `vendored_skill_sources.json`:

```json
{
  "name": "quid",
  "url": "https://github.com/netbasequid/quid-design-system-skill/archive/refs/heads/main.tar.gz",
  "skills": ["quid-design-system"]
}
```

Then run the sync script to pull the skill into your local skills directory.
