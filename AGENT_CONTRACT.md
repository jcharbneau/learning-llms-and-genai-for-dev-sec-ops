# AGENT CONTRACT (Global)

Mode: Contract Mode + token-efficient

## Hard Constraints
- Never output or request real secrets (keys, tokens, creds).
- Never create, modify, or paste `.env` files. Use `.env.example` placeholders only.
- Never scan or summarize:
  - `node_modules/`, `.venv/`, `.git/`, `dist/`, `build/`, `.next/`, `coverage/`
- Don’t add dependencies unless explicitly required; justify if you do.
- Minimize diffs: touch the fewest files possible.

## Output Rules
Before changes:
1) Plan (max 6 bullets)
2) Contract Check (1–3 bullets)
3) Files to change (list)

When returning code:
- Provide patch-style diffs or exact file contents for new files.
- No multi-solution dumping; give one best path.

## MAESTRO Mini Check (keep short)
Include 3–6 bullets on:
- threats/failure modes introduced
- controls/mitigations
- how to validate
