#!/usr/bin/env python3
"""Adds an entry to SEO-CHANGELOG.md after each deploy (newest first).

  python3 changelog.py --message-file MSG --files-file FILES --check-file CHECK

MSG is the commit message, FILES the changed paths (one per line), CHECK the output
of `seo_bot.py check`. Standard library only.
"""
import argparse, datetime as dt, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOG = os.path.join(ROOT, "SEO-CHANGELOG.md")
HEADER = "# Teki Solves: SEO change log\n\nNewest first. Updated automatically after every deploy.\n"

def describe(path):
    """Plain-English area for each changed file, so the log reads well for non-developers."""
    rules = [(r"^source/products\.json$", "Product details (titles, prices, descriptions)"),
             (r"^source/build\.py$", "Page templates and SEO tags"),
             (r"^source/style\.css$", "Design and layout"),
             (r"^source/assets/", "Images"),
             (r"^\.github/seo-bot/feeds\.json$", "SEO bot news sources"),
             (r"^\.github/seo-bot/", "SEO bot rules"),
             (r"^\.github/workflows/", "Automation (build, deploy, checks)"),
             (r"^source/[0-9a-f]{32}\.txt$", "IndexNow key"),
             (r"\.md$", "Documentation")]
    for pat, label in rules:
        if re.search(pat, path): return label
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--message-file", required=True)
    ap.add_argument("--files-file", required=True)
    ap.add_argument("--check-file", required=True)
    a = ap.parse_args()

    msg = open(a.message_file, encoding="utf-8").read().strip().splitlines()
    if msg and msg[0].startswith("Merge pull request"):
        pr = re.search(r"#(\d+)", msg[0])
        rest = [l for l in msg[1:] if l.strip()]
        title = (rest[0] if rest else msg[0]) + (f" (PR #{pr.group(1)})" if pr else "")
        details = rest[1:]
    else:
        title, details = (msg[0] if msg else "Site update"), msg[1:]
    details = [l.strip() for l in details if l.strip().startswith("- ")]
    details = [l for l in details if not re.match(r"- (Co-Authored-By|Claude-Session)", l)]

    files = [f.strip() for f in open(a.files_file, encoding="utf-8") if f.strip()]
    if files and all(f == "SEO-CHANGELOG.md" or f.endswith("state.json") for f in files):
        print("Only the log or bot state changed; nothing to record."); return
    areas = sorted({d for d in map(describe, files) if d})

    check = open(a.check_file, encoding="utf-8").read()
    m = re.search(r"(\d+) pages checked, (\d+) critical", check)
    warns = len(re.findall(r"^warning", check, re.M))
    result = f"{m.group(1)} pages checked, {m.group(2)} critical problems, {warns} minor warnings" if m else "check output not available"

    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = [f"## {now}: {title}", ""]
    entry += details or ["- (no details in the commit message)"]
    if areas: entry += [f"- Areas changed: {', '.join(areas)}"]
    entry += [f"- SEO check after deploy: {result}", ""]

    old = open(LOG, encoding="utf-8").read() if os.path.exists(LOG) else HEADER
    body = old[len(HEADER):] if old.startswith(HEADER) else old
    open(LOG, "w", encoding="utf-8").write(HEADER + "\n" + "\n".join(entry) + "\n" + body.lstrip("\n"))
    print(f"Logged: {title}")

if __name__ == "__main__":
    main()
