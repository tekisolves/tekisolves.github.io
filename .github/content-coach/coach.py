#!/usr/bin/env python3
"""Content coach: emails Khaya about the next blog post, on a realistic schedule.

Runs daily from GitHub Actions. No AI, no paid services, standard library only.
It knows a post is done when the post's file exists in the repo, so there is
nothing to tick off by hand: publish the post and the bot sees it.

At most one email a day. Order of priority:
  shipped  -> a task just got done: well done, share it, here's what's next
  overdue  -> the day after a due date, then every 2nd day until it's done
  due      -> today is ship day
  soon     -> 2 days before a due date
  session  -> a session evening (Tue/Thu by default)

Usage:
  python3 coach.py run            # what the workflow runs
  python3 coach.py run --test     # send today's email even if one went already
  python3 coach.py run --date 2026-12-06   # pretend it's another day (dry runs)
"""
import argparse, datetime as dt, json, os, smtplib, sys
from email.message import EmailMessage

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
PLAN = os.path.join(HERE, "plan.json")
STATE = os.path.join(HERE, "state.json")

# Lines are picked by date so they rotate without repeating every day.
OPENERS = {
    "session": [
        "Tonight is a session night. You don't need to feel ready. You need to start.",
        "Motivation is a visitor. Discipline lives here. Tonight you sit down anyway.",
        "Nobody is coming to make this happen for you, and that's the good news: it means you can.",
        "You've built harder things than a blog post from a phone in Termux. This is well within you.",
        "The version of you who has 10 posts live started with an evening exactly like this one.",
        "Shy founders win with content. It works while you sleep and it never has to cold call anyone.",
        "Small and done beats big and someday. Forty-five minutes. That's the deal.",
    ],
    "soon": [
        "Two days to ship. Plenty of time if you start tonight, not much if you don't.",
        "The due date is close enough to feel now. Good. Use that.",
        "You're two sessions away from a finished post. Make the next one count.",
    ],
    "due": [
        "Ship day. Done and live beats perfect and private.",
        "Today it goes out. If it's 80% there, that's a post. Publish it and improve it later.",
        "This is the moment the work becomes real. Put it out there.",
    ],
    "overdue": [
        "It slipped. That's allowed once. The rule is: never miss twice.",
        "Missing a date doesn't make you undisciplined. Not coming back would. You're reading this, so come back.",
        "No guilt, just the next step. Shrink the post if you have to, but ship something.",
        "The streak isn't broken until you decide it is. Sit down tonight.",
    ],
    "shipped": [
        "You shipped it. That's not luck, that's you keeping a promise to yourself.",
        "Live. Indexed soon. Working for you while you sleep. Well done.",
        "Another one out the door. This is what discipline looks like from the inside: quiet, and done.",
    ],
}

SESSION_PLAN = [
    "Minutes 0 to 5: open the draft (or Claude) and reread where you stopped.",
    "Minutes 5 to 40: one thing only. No tabs, no phone scrolling, no 'quick checks'.",
    "Minutes 40 to 45: write one line for next time: what to do first.",
]

SHARE_STEPS = [
    "Post it on the Retro Arsenal itch.io devlog",
    "Cross-post to Dev.to (set the canonical URL to the Teki Solves blog)",
    "Share it in one subreddit that fits (r/gamedev, r/godot, r/phaser), following their rules",
]


def pick(kind, day):
    lines = OPENERS[kind]
    return lines[day.toordinal() % len(lines)]


def is_done(task):
    """Done = the file exists. A blog post still marked 'draft: true' doesn't count yet."""
    p = task.get("done_when")
    if not p:
        return False
    full = os.path.join(REPO, p)
    if not os.path.exists(full):
        return False
    if full.endswith(".md"):
        head = open(full, encoding="utf-8").read().split("---")[:2]
        if any(line.strip().lower() in ("draft: true", "draft: yes") for line in "".join(head).splitlines()):
            return False
    return True


def load(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def send(subject, text):
    to, pw = os.environ.get("TEKI_EMAIL"), os.environ.get("GMAIL_APP_PASSWORD")
    if not (to and pw):
        print(f"[no email secrets set] would send:\nSubject: {subject}\n\n{text}")
        return
    m = EmailMessage()
    m["Subject"], m["From"], m["To"] = subject, f"Teki content coach <{to}>", to
    m.set_content(text)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
        s.login(to, pw.replace(" ", ""))
        s.send_message(m)
    print(f"Emailed: {subject}")


def task_block(t, today):
    due = dt.date.fromisoformat(t["due"])
    days = (due - today).days
    when = ("today" if days == 0 else "tomorrow" if days == 1
            else f"in {days} days" if days > 0 else f"{-days} day(s) ago")
    return (f"NEXT: {t['title']}\n"
            f"Due: {due.strftime('%a %d %b')} ({when})\n"
            f"Why it matters: {t['why']}\n\n"
            f"Your first step (the only one you need to think about):\n  {t['first_step']}")


def footer(plan, state):
    shipped = state.get("shipped", {})
    on_time = sum(1 for v in shipped.values() if v.get("on_time"))
    total = sum(1 for t in plan["tasks"] if t.get("done_when"))
    bar = "#" * len(shipped) + "-" * (total - len(shipped))
    return (f"\n\nProgress: [{bar}] {len(shipped)} of {total} shipped, {on_time} on time.\n\n"
            "Open Claude and say \"content session\". The plan lives in your repo, so Claude can pick it up from there.\n"
            "Need a new date? Edit .github/content-coach/plan.json. Moving a date is fine. Deleting the habit isn't.\n"
            "Your own bot, running on GitHub. No AI, no cost.")


def build_email(plan, state, today):
    tasks = plan["tasks"]
    shipped = state.setdefault("shipped", {})

    # 1. Anything newly done since last run?
    newly = [t for t in tasks if t["id"] not in shipped and is_done(t)]
    for t in newly:
        shipped[t["id"]] = {"date": today.isoformat(),
                            "on_time": today <= dt.date.fromisoformat(t["due"])}
    upcoming = [t for t in tasks if t["id"] not in shipped and not is_done(t)]
    # Reminder-only tasks (no file to check) drop off the day after their date.
    upcoming = [t for t in upcoming if t.get("done_when")
                or dt.date.fromisoformat(t["due"]) >= today]
    nxt = upcoming[0] if upcoming else None

    if newly:
        t = newly[-1]
        body = pick("shipped", today) + f"\n\nDONE: {t['title']}\n"
        if t["id"] == "blog":
            body += "The blog exists. Every post from here has a home."
        else:
            body += ("\nNow give it legs (15 minutes, tonight or tomorrow):\n"
                     + "\n".join(f"  [ ] {s}" for s in SHARE_STEPS))
        if nxt:
            body += "\n\n" + task_block(nxt, today)
        return f"Shipped: {t['title']}", body

    if not nxt:
        return ("Plan complete. Time for the next one",
                "Every task in the plan is done. That's a run of months where you kept showing up.\n\n"
                "Open Claude and say \"plan the next content run\". Keep the habit alive.")

    due = dt.date.fromisoformat(nxt["due"])
    days = (due - today).days
    if days < 0 and nxt.get("done_when") and (-days) % 2 == 1:
        body = (pick("overdue", today) + "\n\n" + task_block(nxt, today) +
                "\n\nIf it feels too big: cut it in half. A short post that's live beats a long one in drafts.")
        return f"Never miss twice: {nxt['title']}", body
    if days == 0:
        body = (pick("due", today) + "\n\n" + task_block(nxt, today) +
                "\n\nChecklist before you hit publish:\n  [ ] Title says what it does\n"
                "  [ ] One screenshot or GIF\n  [ ] Link to Retro Arsenal at the end")
        return f"Ship day: {nxt['title']}", body
    if days == 2:
        return f"2 days: {nxt['title']}", pick("soon", today) + "\n\n" + task_block(nxt, today)
    if today.strftime("%a") in plan.get("session_days", []):
        mins = plan.get("session_minutes", 45)
        body = (pick("session", today) + "\n\n" + task_block(nxt, today) +
                f"\n\nTonight's {mins} minutes:\n" + "\n".join(f"  {s}" for s in SESSION_PLAN))
        return f"Session tonight: {nxt['title']}", body
    return None


# ---------- business plan reviews (Sundays) ----------
REVIEW_OPENERS = [
    "Fifteen minutes now saves you a week of working on the wrong thing.",
    "Founders don't fail from lack of effort. They fail from effort pointed the wrong way. Point it.",
    "This is the boss meeting. You're the boss. Show up to it.",
    "A plan you don't look at is a wish. Make it a plan again.",
    "Honest numbers beat good vibes. Look at them anyway, especially if they're small.",
]

INCOME_METRICS = [
    "Money in this period (EUR): sales, tips, client work",
    "Retro Arsenal: itch.io views, downloads, sales (itch.io > Analytics)",
    "Website: clicks from Google (Search Console > Performance)",
    "Free sample: downloads / demo visits",
    "Customer conversations: messages sent, replies, interviews done",
    "Hours spent on things that can make money vs everything else",
]

SOFT_CHECK = [
    "Did I keep the promises I made to myself this week? Which one did I break, and why?",
    "What did I avoid because it felt uncomfortable (a message, a call, a price)? Do that first next week.",
    "Where did I build or tidy instead of selling or talking to people?",
    "What's one thing I did well that I want to repeat?",
]

def review_email(today):
    """Sunday evenings: weekly review. First Sunday of the month: monthly. First Sunday of Jan/Apr/Jul/Oct: quarterly."""
    if today.strftime("%a") != "Sun":
        return None
    first_sunday = today.day <= 7
    opener = REVIEW_OPENERS[today.toordinal() % len(REVIEW_OPENERS)]
    soft = "\n".join(f"  - {q}" for q in SOFT_CHECK)
    metrics = "\n".join(f"  [ ] {m}" for m in INCOME_METRICS)
    if first_sunday and today.month in (1, 4, 7, 10):
        subject = "Quarterly review: rewrite the 90-day plan (2 hours)"
        body = (f"{opener}\n\nThis is the big one. Block 2 hours this week.\n\n"
                f"1. Fill in the numbers for the last 3 months:\n{metrics}\n\n"
                "2. Which threads made money or moved you closer to money? Keep those.\n"
                "3. Which ones didn't? Pause or drop them. Fewer threads, more depth.\n"
                "4. Rewrite the 90-day plan: 1 income goal, 2-3 projects that serve it, weekly targets.\n\n"
                f"Soft skills check:\n{soft}\n\nOpen Claude and say \"quarterly review\" to do it together.")
    elif first_sunday:
        subject = "Monthly review: check the numbers (45 min)"
        body = (f"{opener}\n\nOnce a month you check the scoreboard. Small numbers are fine. Unknown numbers aren't.\n\n"
                f"Last month's numbers:\n{metrics}\n\n"
                "Then ask: what's working (do more), what isn't (cut or change), what's the one bet for this month?\n\n"
                f"Soft skills check:\n{soft}\n\nOpen Claude and say \"monthly review\" with your numbers.")
    else:
        subject = "Weekly review: 15 minutes with your plan"
        body = (f"{opener}\n\n"
                "1. Open your business plan and read the 90-day goals. Just read them.\n"
                "2. Last week: what moved you closer to income? What didn't?\n"
                "3. Pick the 2-3 things for this week that serve those goals. Move them to \"This week\" in Trello. Everything else waits.\n"
                "4. Put your 2 session evenings in your calendar.\n\n"
                f"Soft skills check (answer honestly, nobody's grading you):\n{soft}")
    return subject, body + "\n\nA plan only works if you look at it. You just did. That's the habit.\nYour own bot, running on GitHub. No AI, no cost."


def cmd_run(args):
    today = dt.date.fromisoformat(args.date) if args.date else dt.date.today()
    plan = load(PLAN, None)
    state = load(STATE, {})
    already = state.get("last_sent") == today.isoformat() and not args.test
    mail = None if already else build_email(plan, state, today)
    if mail:
        subject, body = mail
        send(subject, body + footer(plan, state))
        state["last_sent"] = today.isoformat()
    else:
        print("Quiet day, no content email.")
    review = review_email(today)
    if review and (state.get("last_review") != today.isoformat() or args.test):
        send(*review)
        state["last_review"] = today.isoformat()
    if not args.date:  # don't save state for pretend dates
        with open(STATE, "w") as f:
            json.dump(state, f, indent=2)
            f.write("\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--test", action="store_true")
    r.add_argument("--date")
    a = ap.parse_args()
    cmd_run(a)
