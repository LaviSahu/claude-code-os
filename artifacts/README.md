# Operating System — Superman Assets

Personal operating assets — the ways of working codified into instruments any Claude
session can pick up cold. Two self-contained HTML pages plus a hub, versioned here.

Open **`index.html`** for the suite hub, or any page directly in a browser.

## The suite

### `latticework-lens.html` — The Latticework Lens · *thinking*
An interactive decision instrument (module M2, made usable). State a decision, choose
2–4 relevant mental models, walk each with a tailored probing question, then name where
the models **disagree** — the disagreement is where the clarity lives. Exports a clean
markdown block ready for `[[decisions]]` in the vault. Notes autosave to the browser.

### `dispatch-cockpit.html` — The Dispatch Cockpit · *doing*
A routing console (module M3, made clickable). Walk a task through the free-tier
dispatch HARD RULES — first match wins — and it calls the destination (`glm-do`,
Gemini MCP, `llm -T quality`, or "stay on the paid plan"). Then generate the mandatory
model-attribution footer, with an offload flag when the paid plan did offload-worthy work.

## Build notes

- Each page is fully self-contained: inline CSS/JS, no external assets or webfonts
  (safe under a strict CSP), theme-aware (light + dark), responsive, and respects
  `prefers-reduced-motion`.
- Distinct visual identity per page so the suite reads as three instruments, not one
  template: amber console (playbook), jade study (lens), cyan cockpit (dispatch).

**Updating:** edit a page, then republish it to the same Claude Artifact URL to keep
the link stable.
