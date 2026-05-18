# Quid Design System Skill

Claude Code skill that applies the Quid (Terminal) design aesthetic to HTML artifacts. Provides Figma-exported design tokens compiled into a single CSS stylesheet with shadcn/ui-aligned semantic variables.

## Syncing

Add to your `vendored_skill_sources.json`:

```json
{
  "name": "quid",
  "url": "https://github.com/netbasequid/quid-design-system-skill/archive/refs/heads/main.tar.gz",
  "skills": ["quid-design-system"]
}
```

Then run the sync script to pull the skill into your local skills directory.

## Updating tokens

1. Replace files in `skills/quid-design-system/tokens/` with new Figma exports.
2. Run `python3 skills/quid-design-system/build_tokens.py` to regenerate `quid.css`.
3. Check `skills/quid-design-system/example.html` in a browser before committing.
