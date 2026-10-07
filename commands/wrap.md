---
description: Wrap up the session — recap with models used, then file it into the vault (raw/ session note + sessions.md line).
argument-hint: [optional focus/title override]
---

Wrap up this session in three steps. Vault root: `<path to your vault>`.

1. **Recap in chat** — concise: what was decided/built/learned, open items (max 2 next actions, park the rest), and the mandatory "Models used this session:" line.

2. **File a session note** at `<vault>/raw/YYYY-MM-DD-<slug>-session.md` (slug from the title; skip if the session was trivial — say so instead):

   ```markdown
   # <Title> — Session Notes
   **Date:** YYYY-MM-DD
   **Project:** <project/area>
   **Tags:** #session <2-4 topical tags>

   ---

   ## What this session was about
   ## Key ideas & decisions
   ## Methodology — how it was done
   ## Open items / next steps
   ```

   Substance over length — decisions and gotchas, not a transcript. Link related vault notes with `[[wikilinks]]`.

3. **Append one line** to `<vault>/command-center/sessions.md` (newest entries at top):

   ```
   - [done] YYYY-MM-DD | <Title> | <1-2 sentence summary> <!-- sid:<first 8 chars of session id, if known> -->
   ```

   Use `[active]` instead of `[done]` if work is mid-flight. The `sid` marker stops the SessionEnd auto-capture hook from double-filing this session — include it whenever the session id is available.

If the user passed arguments, treat them as the title/focus for the write-up.
