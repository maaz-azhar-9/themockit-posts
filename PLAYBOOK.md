# @themockit daily posting playbook

Every day one reasoning/aptitude question goes out as an Instagram **Reel at 10:00 IST**,
and its **answer as a Story at 18:00 IST** the same day. Posted via Metricool
(brand/blogId `7657981`, timezone `Asia/Calcutta`, network `instagram`).

## Daily steps
1. Read `schedule.json`. If today's date (IST) is already listed, stop — nothing to do.
2. Add a NEW question to `questions.json` with `day` = previous max + 1.
   - Original question (never copied from elsewhere), 4 options, exactly one correct.
   - **Audience = general public**, not only SSC/UPSC aspirants. Use the kind of aptitude/
     reasoning questions that appear across ALL exams (banking, railways, CAT, GMAT/GRE,
     campus placements, interviews, olympiads) but that a smart non-aspirant can still solve
     with logic alone — no syllabus knowledge, no GK, no formulas beyond school maths.
   - Rotate types: number series, letter series, coding-decoding, odd one out, analogies,
     quick maths tricks, age/ratio puzzles, clock/calendar, blood relations, direction sense,
     logic riddles. Don't repeat the same type two days in a row.
   - **`difficulty`**: rotate "Medium", "Hard", "Very Hard" so no two consecutive days match
     (look at the last 2 entries). Make the question genuinely match the label.
   - Vary the position of the correct option. Verify the answer by working it out in code.
   - Short punchy `hook` matching the difficulty (e.g. Medium: "Can you get this in 10 sec?",
     Hard: "Most people get this wrong", Very Hard: "Only 2% get this right"), `prompt`,
     a one-line `question`, and a 1–2 sentence `explanation`.
3. `python3 gen.py <day>` → `posts/day<N>/reel.mp4` (8s, uses the approved `music.m4a` — never regenerate or change it unless Maaz asks), `cover.jpg`, `answer.png`.
   Look at `answer.png` to check nothing overflows.
4. Commit and push to `main`. Public URLs:
   `https://raw.githubusercontent.com/maaz-azhar-9/themockit-posts/main/posts/day<N>/<file>`
5. Metricool `createScheduledPost`:
   - Reel at 10:00 today: media = reel.mp4 URL, `videoThumbnailUrl` = cover.jpg URL,
     `instagramData: {"type": "REEL", "showReelOnFeed": true}`, caption below.
   - Story at 18:00 today: media = answer.png URL, `instagramData: {"type": "STORY"}`, no text.
   If it is already past 10:00, post the reel ~5 min from now instead.
6. Append `{"date": "<YYYY-MM-DD>", "day": N}` to `schedule.json`, commit, push.

## Caption template (English)
```
<hook> 🧠

<question> — what comes next?   (adapt wording to the question type)
Drop your answer in the comments 👇 Answer on our story at 6 PM!

Want to practice questions like this every day? 🚀
themockit.com uses AI to build custom mock tests for any exam, subject or interview topic.
Pick your difficulty, get questions instantly, and review every answer.
Real practice before the real exam 💯

🔗 Link in bio — try it today!

<hashtags — see below>
```
Vary the opening line day to day so posts don't look copy-pasted.

## Hashtags (15–20, different mix every day)
1. Do 1–2 quick web searches for hashtags trending right now on Instagram in the
   quiz / puzzle / brain teaser / exam prep / study niche (e.g. "trending instagram hashtags
   quiz this week", "trending study hashtags instagram <month year>"). Take only ones that fit.
2. Fill the rest from this pool, choosing tags that match today's question type:
   - Broad: #quiz #puzzle #brainteaser #riddle #iqtest #braingames #logic #thinkfast
     #challenge #canyousolveit #mindgames #funwithmaths #mathstricks #maths
   - Reasoning: #reasoning #reasoningtricks #logicalreasoning #aptitude #quantitativeaptitude
   - Exams (mix several, not all): #competitiveexams #exampreparation #mocktest #bankexam
     #ssc #railway #catexam #placementprep #interviewprep #governmentjobs #upsc
   - Study: #studygram #studymotivation #learneveryday #education
3. Always end with #themockit. Never reuse yesterday's exact set (check the last caption in
   Metricool with getScheduledPosts or the previous day's commit).
