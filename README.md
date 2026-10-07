# claude-code-os

**A complete personal operating system for Claude Code** — global config, skills, subagents, slash commands, and hooks, extracted from a real daily-driver setup.

This isn't a starter template. It's the actual config running production usage: routing rules that keep a paid plan from burning quota on work a free model can do, a hook that files every session into a knowledge base without being asked, and a review gate that won't let a change merge until you can explain it back.

## Why this exists

- **Most Claude Code repos show you prompts. This one shows you a system** — the config, skills, agents, and hooks wired together, not a single clever prompt in isolation.
- **It's opinionated about cost.** A hard dispatch tree decides, per task, whether Claude even *should* answer — or whether a free-tier CLI should do it instead.
- **It's opinionated about rigor.** Nothing ships without a spec freeze and a quiz you have to pass yourself — the system distrusts your "yeah that looks right" as much as the model's.
- **It's plain text and git.** No database, no proprietary format. Copy the files in, edit them, version them like code.

## Quick start

```bash
git clone https://github.com/<you>/claude-code-os.git
cd claude-code-os

# copy what you want into your global Claude Code config
cp CLAUDE.md ~/.claude/CLAUDE.md
cp -r skills/* ~/.claude/skills/
cp -r agents/* ~/.claude/agents/
cp -r commands/* ~/.claude/commands/
cp hooks/session-capture.py ~/.claude/hooks/
cp settings.example.json ~/.claude/settings.json   # merge, don't overwrite, if you already have one
```

Then open `CLAUDE.md` and `hooks/session-capture.py` and fill in the placeholders — model/CLI names, vault path, thresholds. None of this works with the paths left as-is; it's a template of a real setup, not a drop-in binary.

## The star-bait: four ideas worth stealing

### 1. A budget-aware dispatch tree

`CLAUDE.md` includes a decision tree that runs before every response and routes work by kind, not by default habit:

```
coding task?        → cheap coding CLI, not the paid model inline
research / lookup?  → a grounded search MCP or a free-tier LLM
long draft (>400w)?  → free-tier LLM
vault/file op?       → paid plan (needs tool access)
short reply?          → paid plan is fine
```

The paid Claude session is reserved for orchestration and genuinely hard multi-step reasoning — everything else gets offloaded. Every response ends with a **model attribution footer** naming which model or CLI did which part:

```
_[Synthesis: Claude | Research: free-tier LLM via CLI]_
```

If the paid model handled something the tree says should've been offloaded, the footer says so — an **offload flag**, self-reported, every time. It's a cost discipline that's legible in every reply instead of buried in a billing dashboard.

### 2. Unknowns-first development, ending in a quiz you have to pass

The premise: on any non-trivial change, the bottleneck is unclarified requirements, not model capability. So nothing gets built until the unknowns are surfaced.

```
 blindspot pass  →  /grill-me  →  /prototype  →  /to-spec
(find unknown      (one Q at a   (throwaway    (freeze the
 unknowns first)     time, forces   variants to    spec before
                      a real answer) react to)      any code is
                                                     written)
        │
        ▼
   dispatch the build
        │
        ▼
   /code-review  (standards axis + spec axis)
        │
        ▼
   /quiz-gate  →  you explain the change back,
                   get quizzed on it, and a
                   substantive change does not
                   merge until you pass
```

The last step is the one people skip everywhere else: an AI-assisted change merges only after the *human* demonstrates they understood it. Wrong answers on the quiz are treated as located unknowns and fed back into the next loop, not brushed past.

### 3. Version-control `~/.claude` without turning it into a git repo

`bin/claudecfg` is three lines:

```sh
#!/bin/sh
exec git --git-dir="$HOME/.claude/config.git" --work-tree="$HOME/.claude" "$@"
```

It points git's `--git-dir` at a detached folder (`~/.claude/config.git`) while treating `~/.claude` itself as the working tree — so `~/.claude` never contains a `.git` folder and never gets mistaken for a project repo by tools that walk up the directory tree looking for one. This is the same trick people use for dotfiles; it's just rarely applied to Claude Code's config directory, where it matters more because Claude Code itself treats `.git` presence as a signal.

```bash
claudecfg init          # one-time: creates the detached git dir
claudecfg add -A
claudecfg commit -m "tune dispatch rules"
claudecfg log --oneline
```

Your entire global setup — skills, agents, commands, hooks, preferences — becomes a normal git history you can diff, branch, and roll back, with zero risk of Claude Code or any other tool getting confused about what repo it's standing in.

### 4. A SessionEnd hook that files itself away

`hooks/session-capture.py` runs when a session ends and, without being asked:

- Skips trivial sessions (fewer than 5 user messages or under 2000 chars) — no noise for a two-line Q&A.
- Summarizes substantive sessions with a free-tier LLM CLI (keeps this off the paid-model budget too).
- Appends one line to a running `sessions.md` log and writes a full dated session note into an Obsidian vault (or any plain-markdown knowledge base you point it at).
- Dedupes against a manual `/wrap` command via a session-id marker, so a session summarized by hand doesn't get double-filed.
- Is written to **never block or fail session exit** — worst case, it silently no-ops; it will not hang your terminal or crash the CLI on the way out.

The result: your second brain gets fed from every real session automatically, and the failure mode of a broken hook is "nothing got filed today," never "Claude Code won't quit."

## Directory tour

### `CLAUDE.md`
The global preferences file, ~6KB. Beyond the dispatch tree and attribution footers above, it also defines:
- A **mental-models latticework** section — for real decisions, reason through named models (inversion, base rates, opportunity cost, incentives, margin of safety, circle of competence) instead of one convenient frame, and surface where they disagree before recommending.
- Working-style rules (be concise, be honest first, verify before claiming something works) that apply regardless of which model is answering.

### `skills/`
Eight skills, invoked as `/skill-name` inside Claude Code:

| Skill | What it does |
|---|---|
| `code-review` | Two-axis review — standards (a Fowler code-smell baseline) and spec conformance — run separately, not blended |
| `diagnosing-bugs` | Feedback-loop-first debugging discipline: reproduce, narrow, verify, before touching code |
| `tdd` | Test-driven development workflow |
| `to-spec` | Freezes a spec from a conversation before any code gets written |
| `prototype` | Throwaway-variant patterns (logic TUI + UI variants) for "I'll know it when I see it" requirements |
| `grilling` / `grill-me` | One question at a time, with a recommended answer offered per question, to pull real requirements out of a vague ask |
| `quiz-gate` | The post-review gate described above — explain it, get quizzed, pass before merge |
| `handoff` | Structured session handoff for picking up work later or passing it to someone else |

Most of these are built on or adapted from **Matt Pocock's** excellent Claude Code skills (MIT licensed). Full attribution below.

### `agents/`
Four subagent templates, each with deliberate model routing baked into the frontmatter — cheaper models for routine work, stronger reasoning reserved for what needs it:

- **`domain-specialist`** — deep-domain Q&A and write-ups in a specific field; swap in your own domain.
- **`vault-research-delegate`** — read-only search and synthesis over an Obsidian (or any markdown) vault, kept separate from any agent that writes.
- **`brand-content-writer`** — public-facing copy with brand-voice discipline instead of generic marketing tone.
- **`revenue-strategist`** — pressure-tests money moves with BUILD / PARK / KILL verdicts, ICE scoring, and a blunt passive-income test: *does revenue still flow if you don't touch it for a month?*

### `commands/`
- **`/lattice`** — runs the mental-models latticework as a deliberate, deep pass on one specific decision.
- **`/model-usage`** — a quota tracker so you can see, at a glance, how much of the paid plan the dispatch tree actually saved.
- **`/wrap`** — manual session wrap-up that files structured notes into an Obsidian vault (the counterpart to the automatic hook above).

### `hooks/session-capture.py`
See the star-bait section above. Wired via `settings.example.json`.

### `bin/claudecfg`
See the star-bait section above.

### `settings.example.json`
Minimal wiring to register the SessionEnd hook. Merge its contents into your own `~/.claude/settings.json` — don't just overwrite it.

## Philosophy

- **Durable plain text over clever tools.** Markdown and git outlast any specific model, CLI, or wrapper. Everything here is designed to survive the next tool churn.
- **Cheapest capable model, always.** Reach for the strongest model reflexively and you pay premium rates for lookup-and-summarize work a free tier handles fine. Match the model to the task, every time, not out of habit.
- **Verify before claiming it works.** A model saying a fix works is not the fix working. Check the actual behavior before reporting done.
- **Unknowns-first.** Most bad AI-assisted output traces back to an unclarified requirement, not a weak model. Surface the unknown before you write the code, and quiz yourself on the result before you trust it.

## Attribution

Several skills in `skills/` are derived from or inspired by **Matt Pocock's** Claude Code skills, MIT licensed. Full license text: [`skills/MATTPOCOCK-LICENSE.txt`](skills/MATTPOCOCK-LICENSE.txt). Go look at the original work: **https://github.com/mattpocock**

## License

MIT — see [`LICENSE`](LICENSE). The Matt Pocock–derived skills additionally carry the attribution above per their original MIT terms.
