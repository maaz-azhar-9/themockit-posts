"""Generate daily @themockit assets from questions.json.

Usage: python3 gen.py <day>
Outputs in posts/day<N>/: reel.mp4 (1080x1920, 8s still), answer.png (story).
Question entry fields: day, difficulty (Medium/Hard/Very Hard), hook, prompt, question, options [4], answer (index 0-3), explanation.
"""
import json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = "/usr/share/fonts/truetype/google-fonts/"
BG, CARD, EDGE = (14, 17, 28), (27, 32, 50), (55, 63, 92)
ACCENT, WHITE, MUTED = (255, 196, 0), (245, 246, 250), (150, 158, 180)
GREEN = (46, 204, 113)
W, H = 1080, 1920


def font(size, weight="Bold"):
    return ImageFont.truetype(f"{FONT_DIR}Poppins-{weight}.ttf", size)


def fit(d, text, size, maxw, weight="Bold"):
    while size > 20 and d.textlength(text, font=font(size, weight)) > maxw:
        size -= 2
    return font(size, weight)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def base(q, d):
    tag = f"DAILY BRAIN TEST  #{q['day']}"
    tf = font(40)
    tw = d.textlength(tag, font=tf)
    d.rounded_rectangle([(W - tw) / 2 - 34, 170, (W + tw) / 2 + 34, 250], 40, fill=ACCENT)
    d.text((W / 2, 210), tag, font=tf, fill=BG, anchor="mm")
    d.text((W / 2, 340), q["hook"], font=fit(d, q["hook"], 66, W - 120), fill=WHITE, anchor="mm")
    d.text((W / 2, 420), q["prompt"], font=fit(d, q["prompt"], 40, W - 140, "Medium"), fill=MUTED, anchor="mm")
    d.rounded_rectangle([60, 490, W - 60, 760], 40, fill=CARD)
    # short series fit on one big line; longer GK/current-affairs questions wrap to <=4 lines
    one = fit(d, q["question"], 84, W - 200)
    if one.size >= 60:
        d.text((W / 2, 625), q["question"], font=one, fill=ACCENT, anchor="mm")
    else:
        size = 56
        while True:
            f = font(size)
            lines = wrap(d, q["question"], f, W - 180)
            if (len(lines) <= 4 and len(lines) * size * 1.25 <= 240) or size <= 30:
                break
            size -= 2
        lh = size * 1.25
        y = 625 - lh * (len(lines) - 1) / 2
        for i, line in enumerate(lines):
            d.text((W / 2, y + i * lh), line, font=f, fill=ACCENT, anchor="mm")


def options(q, d, y0=830, highlight=None):
    bw, bh, gap = 450, 170, 60
    x0 = (W - (2 * bw + gap)) / 2
    of = min((fit(d, str(v), 60, bw - 190) for v in q["options"]), key=lambda f: f.size)
    for i, v in enumerate(q["options"]):
        x = x0 + (i % 2) * (bw + gap)
        y = y0 + (i // 2) * (bh + 44)
        ok = highlight == i
        d.rounded_rectangle([x, y, x + bw, y + bh], 32, fill=(22, 70, 45) if ok else CARD,
                            outline=GREEN if ok else EDGE, width=5 if ok else 3)
        cx, cy = x + 78, y + bh / 2
        d.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=GREEN if ok else ACCENT)
        d.text((cx, cy), "ABCD"[i], font=font(44), fill=BG, anchor="mm")
        d.text((x + 165, cy), str(v), font=of, fill=WHITE, anchor="lm")


def footer(d):
    d.line([(W / 2 - 130, 1770), (W / 2 + 130, 1770)], fill=EDGE, width=3)
    d.text((W / 2, 1830), "@themockit", font=font(44), fill=ACCENT, anchor="mm")


def reel_frame(q):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    base(q, d)
    options(q, d)
    diff = q.get("difficulty")
    if diff:
        col = {"Medium": (46, 204, 113), "Hard": (255, 140, 0), "Very Hard": (255, 59, 92)}.get(diff, ACCENT)
        label = f"Difficulty: {diff}"
        lf = font(42)
        lw = d.textlength(label, font=lf)
        d.rounded_rectangle([(W - lw) / 2 - 36, 1290, (W + lw) / 2 + 36, 1370], 40, outline=col, width=4)
        d.text((W / 2, 1330), label, font=lf, fill=col, anchor="mm")
    cy = 1480
    d.text((W / 2, cy), "Comment your answer below", font=font(56), fill=ACCENT, anchor="mm")
    d.text((W / 2, cy + 90), "Answer on our story at 6 PM", font=font(40, "Medium"), fill=MUTED, anchor="mm")
    footer(d)
    return img


def answer_story(q):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    base(q, d)
    options(q, d, highlight=q["answer"])
    ans = f"Answer: {'ABCD'[q['answer']]}) {q['options'][q['answer']]}"
    d.text((W / 2, 1340), ans, font=fit(d, ans, 72, W - 120), fill=GREEN, anchor="mm")
    ef = font(40, "Medium")
    for i, line in enumerate(wrap(d, q["explanation"], ef, W - 160)[:4]):
        d.text((W / 2, 1440 + i * 58), line, font=ef, fill=WHITE, anchor="mm")
    d.text((W / 2, 1700), "Practice more at themockit.com", font=font(40), fill=ACCENT, anchor="mm")
    footer(d)
    return img


def main(day):
    qs = json.load(open(os.path.join(ROOT, "questions.json")))
    q = next(x for x in qs if x["day"] == day)
    out = os.path.join(ROOT, "posts", f"day{day}")
    os.makedirs(out, exist_ok=True)
    frame = reel_frame(q)
    frame.save(f"{out}/cover.jpg", quality=90)
    with tempfile.TemporaryDirectory() as tmp:
        frame.save(f"{tmp}/frame.png")
        # 8s still video; music.m4a in repo root is used if present, else a silent track
        music = os.path.join(ROOT, "music.m4a")
        audio = ["-stream_loop", "-1", "-i", music] if os.path.exists(music) else \
                ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "30",
                        "-i", f"{tmp}/frame.png", *audio, "-t", "8",
                        "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-tune", "stillimage", "-af", "afade=t=out:st=7:d=1",
                        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
                        f"{out}/reel.mp4"], check=True)
    answer_story(q).save(f"{out}/answer.png")
    print(out)


if __name__ == "__main__":
    main(int(sys.argv[1]))
