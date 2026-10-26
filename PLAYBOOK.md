# @themockit daily posting playbook

Every day one reasoning/aptitude question goes out as an Instagram **Reel at 10:00 IST**,
and its **answer as a Story at 20:00 IST** the same day. Posted via Metricool
(brand/blogId `7657981`, timezone `Asia/Calcutta`, network `instagram`).

## Daily steps
1. Read `schedule.json`. If today's date (IST) is already listed, stop — nothing to do.
2. Add a NEW question to `questions.json` with `day` = previous max + 1.
   - Original question (never copied from elsewhere), 4 options, exactly one correct.
   - Rotate types: number series, letter series, coding-decoding, odd one out, analogies,
     simple maths tricks, blood relations, direction sense. Keep it solvable in ~10 sec.
   - Vary the position of the correct option. Verify the answer by working it out in code.
   - Short punchy `hook` (e.g. "Only 2% get this right"), `prompt`, a one-line `question`
     that fits on one line, and a 1–2 sentence `explanation`.
3. `python3 gen.py <day>` → `posts/day<N>/reel.mp4`, `cover.jpg`, `answer.png`.
   Look at `answer.png` to check nothing overflows.
4. Commit and push to `main`. Public URLs:
   `https://raw.githubusercontent.com/maaz-azhar-9/themockit-posts/main/posts/day<N>/<file>`
5. Metricool `createScheduledPost`:
   - Reel at 10:00 today: media = reel.mp4 URL, `videoThumbnailUrl` = cover.jpg URL,
     `instagramData: {"type": "REEL", "showReelOnFeed": true}`, caption below.
   - Story at 20:00 today: media = answer.png URL, `instagramData: {"type": "STORY"}`, no text.
   If it is already past 10:00, post the reel ~5 min from now instead.
6. Append `{"date": "<YYYY-MM-DD>", "day": N}` to `schedule.json`, commit, push.

## Caption template (English)
```
<hook> 🧠

<question> — what comes next?   (adapt wording to the question type)
Drop your answer in the comments 👇 Answer on our story tonight!

Want to practice questions like this every day? 🚀
themockit.com uses AI to build custom mock tests for any exam, subject or interview topic.
Pick your difficulty, get questions instantly, and review every answer.
Real practice before the real exam 💯

🔗 Link in bio — try it today!

#reasoning #reasoningtricks #mathspuzzle #brainteaser #iqtest #mocktest #ssc #sscgd
#ssccgl #bankexam #ibpspo #rrbntpc #upsc #governmentjobs #competitiveexams
#exampreparation #quiz #puzzle #studygram #themockit
```
Vary the opening line day to day so posts don't look copy-pasted.
