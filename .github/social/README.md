# Social engine

Free and approval-first. GitHub Actions does the work, Gemini's free tier drafts captions, and Buffer's free API does the posting.

## Add a post
1. Copy a file in `content/social/` and rename it `YYYY-MM-DD-short-name.yml`. The `id` must match the file name.
2. Fill in `date`, `link`, `honest`, an optional `card` (rendered for you), `media` or `video`, and one block per platform under `posts`.
   Want AI to write it? Leave a platform's `text` empty, add `facts:` (a list of true things to say) and an optional `brief:` angle under the platform. Gemini writes 3 options into `content/social/drafts/<id>.md` and puts the first one that passes the checks in the brief.
3. Write `{link}` where the link goes. The engine adds tracking (`utm_source=facebook` and so on).
4. Open a pull request. The bot renders the card, runs the checks and lists everything in the run summary.
5. Merge it. Merging is the approval. After the site deploys, the posts are queued in Buffer at their time.

## The checks (from `brand.json`)
- No em or en dashes, and no hype phrases.
- Length and hashtag limits per platform.
- Alt text on every image.
- Instagram captions have no links (they don't click). Say "link in bio".
- YouTube needs a video and a title.
- At most 2 Facebook link posts per month (Page link limit).
- Every brief has an `honest:` line saying what it claims and why it's true.

## Who posts where (both free plans together)
- **Buffer** (3 channels, 10 queued each): Facebook, Instagram, YouTube. Driven by the briefs here.
- **Metricool** (20 published a month, resets on the 1st): Pinterest, Bluesky, TikTok. No free API, so Claude schedules these and lists them in `metricool.json`.
- X: by hand for now.

## Daily check (12:30 Irish time)
`social-remind.yml` runs `engine.py remind`. It reads both calendars and emails Khaya only if something needs him: an empty day in the next 7, a platform with nothing coming, a failing brief, or Metricool near its monthly limit. The fix is usually one message to Claude: "do this week's posts".

## Limits
- Buffer free: 10 queued posts per channel, so the engine only queues posts due in the next 7 days. The daily run tops it up.

## Commands
```
python3 .github/social/engine.py check     # brand rules
python3 .github/social/engine.py draft     # captions for empty posts (needs GEMINI_API_KEY)
python3 .github/social/engine.py render    # cards (needs playwright)
python3 .github/social/engine.py publish --dry-run
python3 .github/social/engine.py doctor    # Buffer key + channels (needs BUFFER_API_KEY)
```

## Roadmap
- **Admin dashboard** (planned): one private page for everything that needs Khaya's input, such as posts to approve, SEO check results and the daily reminders. It would replace the email.
- Weekly auto-brief PR: next week's briefs pre-drafted, so Khaya only reviews.
- Feedback loop: UTM clicks from Cloudflare feeding the best hooks back into the drafter.
