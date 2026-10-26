# @themockit daily posting playbook

Every day one question (reasoning, maths, GK or current affairs) goes out as an Instagram **Reel at 10:00 IST**,
and its **answer as a Story at 18:00 IST** the same day. Posted via Metricool
(brand/blogId `7657981`, timezone `Asia/Calcutta`, network `instagram`).

## Daily steps
1. Read `schedule.json`. If today's date (IST) is already listed, stop — nothing to do.
2. Add a NEW question to `questions.json` with `day` = previous max + 1.
   - Original question (never copied from elsewhere), 4 options, exactly one correct.
   - **Audience = general public**, not only SSC/UPSC aspirants. Questions should feel like
     they could appear in any exam (banking, railways, CAT, placements, interviews, quizzes)
     but a curious non-aspirant can still have a go.
   - **Category** (add a `category` field) — rotate in this weekly order, then repeat:
     Reasoning, GK, Maths, Current Affairs, Reasoning, GK, Current Affairs.
     Look at the previous entry's category and take the next one in the cycle.
     - *Reasoning*: series, coding-decoding, odd one out, analogies, blood relations,
       direction sense, clock/calendar, logic riddles. Solvable by logic alone.
     - *Maths*: quick aptitude — percentages, ages, ratios, speed, simple tricks. School maths.
     - *GK*: well-known, stable facts (geography, science, history, India & world firsts,
       sports records, inventions). Popular, not obscure trivia.
     - *Current Affairs*: something from the **last 30 days** that made national/international
       news (awards, sports results, space missions, appointments, major launches, records).
       Find it with WebSearch and confirm the fact on at least 2 reliable sources (official
       sites, PIB, major news outlets) before using it. Stick to neutral facts — never
       party-political opinions, elections framing, religion or anything divisive.
       If you cannot confirm a fact on 2 sources, switch to a GK question instead.
   - For GK/Current Affairs use `prompt` "General Knowledge" / "Current Affairs", write the
     full question in `question` (it wraps automatically), keep each option under ~16
     characters, and in `explanation` give the fact in one line (add "as of <Month Year>"
     for current affairs).
   - Reasoning/Maths types: don't repeat the same sub-type two days in a row.
   - **Style: "looks halwa, but isn't."** Every question must look easy at first glance but
     hide a trap, so people comment fast and many get it wrong. Techniques:
     - include the obvious-but-wrong answer as one of the options (the "gut" answer);
     - a pattern that seems simple (+2, x2) but switches or alternates;
     - wording traps (e.g. "how many months have 28 days?", "a doctor's brother…");
     - common misconceptions in GK (e.g. the famous-but-wrong answer as a distractor);
     - maths where the quick mental shortcut gives the wrong result.
     Still fair: one clearly correct answer that feels obvious once explained.
   - **`difficulty`**: rotate "Medium", "Hard", "Very Hard" so no two consecutive days match
     (look at the last 2 entries). Make the question genuinely match the label.
   - Vary the position of the correct option. Verify Reasoning/Maths answers by working
     them out in code; verify GK/Current Affairs answers with web sources.
   - Short punchy `hook` matching the difficulty (e.g. Medium: "Can you get this in 10 sec?",
     Hard: "Most people get this wrong", Very Hard: "Only 2% get this right"), `prompt`,
     a `question`, and a 1–2 sentence `explanation`.
3. `python3 gen.py <day>` → `posts/day<N>/reel.mp4` (8s animated: options pop in one by one, slow zoom; uses the approved `music.m4a` — never regenerate or change it unless Maaz asks), `cover.jpg`, `answer.png`.
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
   - Reasoning / Maths: #reasoning #reasoningtricks #logicalreasoning #aptitude #quantitativeaptitude
   - GK / Current Affairs: #gk #generalknowledge #gkquiz #gkquestions #currentaffairs
     #currentaffairs2026 #dailyquiz #triviatime #knowledge #didyouknow
   - Exams (mix several, not all): #competitiveexams #exampreparation #mocktest #bankexam
     #ssc #railway #catexam #placementprep #interviewprep #governmentjobs #upsc
   - Study: #studygram #studymotivation #learneveryday #education
3. Always end with #themockit. Never reuse yesterday's exact set (check the last caption in
   Metricool with getScheduledPosts or the previous day's commit).
