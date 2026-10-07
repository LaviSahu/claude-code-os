#!/usr/bin/env python3
"""SessionEnd hook: auto-file substantive sessions into the vault
(command-center/sessions.md + raw/ note) unless /wrap already did.
Must never fail or block — always exits 0."""
import json, os, re, subprocess, sys
from datetime import datetime

DEFAULT_VAULT = "/path/to/your/obsidian-vault"  # or set SESSION_CAPTURE_VAULT
LLM = "llm"  # any CLI that takes a prompt and prints a completion


def extract_text(content):
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [b.get("text", "") for b in content
                 if isinstance(b, dict) and b.get("type") == "text"]
        return "\n".join(p for p in parts if p).strip()
    return ""


def main():
    hook = json.load(sys.stdin)
    sid = str(hook.get("session_id", ""))[:8]
    tpath = hook.get("transcript_path", "")
    cwd = hook.get("cwd", "") or ""
    if not sid or not tpath or not os.path.isfile(tpath):
        return

    vault = os.environ.get("SESSION_CAPTURE_VAULT", DEFAULT_VAULT)
    sessions_md = os.path.join(vault, "command-center", "sessions.md")
    raw_dir = os.path.join(vault, "raw")
    if not os.path.isfile(sessions_md) or not os.path.isdir(raw_dir):
        return
    if sid in open(sessions_md, encoding="utf-8", errors="replace").read():
        return  # already filed (by /wrap or a previous run)

    user_msgs, last_assistant = [], ""
    with open(tpath, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                e = json.loads(line)
            except (ValueError, TypeError):
                continue
            msg = e.get("message") or {}
            text = extract_text(msg.get("content"))
            if not text:
                continue
            if e.get("type") == "user":
                user_msgs.append(text)
            elif e.get("type") == "assistant":
                last_assistant = text

    if len(user_msgs) < 5 or sum(len(m) for m in user_msgs) + len(last_assistant) < 2000:
        return  # not substantive

    prompt = (
        "Summarize this Claude Code session. Reply with EXACTLY two lines:\n"
        "TITLE: <max 60 chars>\nSUMMARY: <1-2 sentences, max 300 chars>\n\n"
        "First request:\n" + user_msgs[0][:1500] + "\n\nLater requests:\n"
        + "\n".join(m[:200] for m in user_msgs[1:31])
        + "\n\nFinal assistant message:\n" + last_assistant[-1500:]
    )
    title = summary = ""
    try:
        out = subprocess.run([LLM, "-T", "fast", prompt], capture_output=True,
                             text=True, timeout=45).stdout
        mt = re.search(r"^TITLE:\s*(.+)$", out, re.M)
        ms = re.search(r"^SUMMARY:\s*(.+)$", out, re.M)
        if mt and ms:
            title, summary = mt.group(1).strip()[:60], ms.group(1).strip()[:300]
    except Exception:
        pass
    if not title:
        title = user_msgs[0].replace("\n", " ")[:60]
        summary = "(auto-captured; summary unavailable)"

    day = datetime.now().strftime("%Y-%m-%d")
    with open(sessions_md, "a", encoding="utf-8") as f:
        f.write(f"- [done] {day} | {title} | {summary} <!-- sid:{sid} auto -->\n")

    slug = re.sub(r"-+", "-", re.sub(r"[^a-z0-9]", "-", title.lower())).strip("-")[:50]
    note = os.path.join(raw_dir, f"{day}-{slug}-session.md")
    if os.path.exists(note):
        note = os.path.join(raw_dir, f"{day}-{slug}-{sid}-session.md")
    with open(note, "w", encoding="utf-8") as f:
        f.write(f"""# {title} — Session Notes
**Date:** {day}
**Project:** {os.path.basename(cwd) or "unknown"}
**Tags:** #session #auto-captured

---

## Summary
{summary}

## Auto-capture
Filed automatically by the SessionEnd hook (session {sid}). Replace with a
proper /wrap-style write-up if this session mattered.
""")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
