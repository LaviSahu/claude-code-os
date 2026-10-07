---
name: quiz-gate
description: Post-implementation understanding gate — explain a change, then quiz the user until they pass, before merging or moving on. Use when the user says "quiz gate", "quiz me on this change", or wants to verify they understand what was built before merging.
argument-hint: "[what to be quizzed on — defaults to the current change/PR]"
---

# Quiz gate — pass before merge

Shipped ≠ understood. This gate verifies the user actually understands a change
(theirs or an agent's) before it merges or before building on top of it.

## Steps

1. **Brief first.** Give a compact explainer of the change: what it does, the one or
   two design decisions that matter, and what would break if they're misunderstood.
   Aim for a 60-second read; intuition over file lists. For big changes, an HTML
   report artifact is better than text.
2. **Quiz — 3 to 5 multiple-choice questions**, one AskUserQuestion call (or numbered
   in chat if unavailable). First answer counts. Write them like good retrieval
   practice, not recall:
   - Test *consequences*, not trivia: "what happens when X?" beats "what is X called?"
   - Distractors must be the plausible misconceptions, mutually exclusive, never
     copied between questions.
   - Always include at least one question on the failure mode: data loss, wrong
     result, silent break.
3. **Grade honestly.** For each miss: name the misconception, explain why the right
   answer is right, and — most important — state the *practical consequence* of the
   misunderstanding ("you'd have lost your progress when...").
4. **Gate.** Fewer than all-correct on a substantial change → recommend NOT merging
   yet; offer a re-quiz with fresh questions after the explainer is re-read. The user
   can override — say so plainly, don't block silently.
5. **Feed the loop.** The misses are located unknowns. Suggest where they point:
   a doc to write, a concept for the next explainer, or a spec assumption to revisit.
