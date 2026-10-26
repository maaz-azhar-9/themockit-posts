"""Generate daily @themockit assets from questions.json.

Usage: python3 gen.py <day>
Outputs in posts/day<N>/: reel.mp4 (1080x1920, 8s animated), answer.png (story).
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


def options(q, d, y0=830, highlight=None, only=None):
    bw, bh, gap = 450, 170, 60
    x0 = (W - (2 * bw + gap)) / 2
    of = min((fit(d, str(v), 60, bw - 190) for v in q["options"]), key=lambda f: f.size)
    for i, v in enumerate(q["options"]):
        if only is not None and i != only:
            continue
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


def _layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def reel_layers(q):
    """Static background + separately animated layers (options, difficulty, CTA)."""
    bg = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(bg)
    base(q, d)
    footer(d)
    opts = []
    for i in range(4):
        img, ld = _layer()
        options(q, ld, only=i)
        opts.append(img)
    diff_img, dd = _layer()
    diff = q.get("difficulty")
    if diff:
        col = {"Medium": (46, 204, 113), "Hard": (255, 140, 0), "Very Hard": (255, 59, 92)}.get(diff, ACCENT)
        label = f"Difficulty: {diff}"
        lf = font(38)
        lw = dd.textlength(label, font=lf)
        rx = RIGHT_X
        dd.rounded_rectangle([rx - lw / 2 - 30, 1350, rx + lw / 2 + 30, 1424], 37, outline=col, width=4)
        dd.text((rx, 1387), label, font=lf, fill=col, anchor="mm")
    cta, cd = _layer()
    cd.text((RIGHT_X, 1505), "Comment your", font=font(54), fill=ACCENT, anchor="mm")
    cd.text((RIGHT_X, 1572), "answer below!", font=font(54), fill=ACCENT, anchor="mm")
    cd.text((RIGHT_X, 1655), "Answer on our story at 6 PM", font=font(32, "Medium"), fill=MUTED, anchor="mm")
    return bg, opts, diff_img, cta


RIGHT_X = 700  # centre of the text block to the right of the cat
CAT_BOX = (40, 1255, 470, 1760)  # area the cat + thought bubble occupy (left side)


def draw_cat(t):
    """Original cute ginger cat, paw on chin, thinking. Drawn 2x and downscaled.
    All motions have periods dividing 8 s, so the reel loops seamlessly."""
    import math
    S = 2
    bw, bh = CAT_BOX[2] - CAT_BOX[0], CAT_BOX[3] - CAT_BOX[1]
    img = Image.new("RGBA", (bw * S, bh * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    def P(x, y):
        return (x * S, y * S)

    def E(cx, cy, rx, ry, **kw):
        d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S, (cy + ry) * S], **kw)

    FUR, DARK, CREAM = (247, 168, 84), (214, 120, 45), (255, 236, 210)
    PINK, INK = (255, 150, 170), (40, 30, 35)
    sway = math.sin(2 * math.pi * t / 4)          # head sway, 4 s
    bob = math.sin(2 * math.pi * t / 2)           # bubble bob, 2 s
    tap = max(0.0, math.sin(2 * math.pi * t / 1))  # paw tap, 1 s
    cx, base_y = 205, 480

    # tail: swishing curve behind body
    ang = 0.35 * math.sin(2 * math.pi * t / 2)
    pts = []
    for k in range(13):
        u = k / 12
        x = cx + 95 + 70 * u + 40 * math.sin(u * 2.4 + ang * 2) * u
        y = base_y - 30 - 150 * u + 30 * math.cos(u * 3 + ang) * u
        pts.append(P(x, y))
    d.line(pts, fill=DARK, width=30 * S, joint="curve")
    E(pts[-1][0] / S, pts[-1][1] / S, 15, 15, fill=DARK)

    # body
    E(cx, base_y - 85, 115, 105, fill=FUR)
    E(cx, base_y - 70, 70, 75, fill=CREAM)
    # back feet
    E(cx - 70, base_y - 8, 45, 22, fill=FUR)
    E(cx + 70, base_y - 8, 45, 22, fill=FUR)

    # head (sways a little)
    hx, hy = cx + 6 * sway, 235 + 3 * abs(sway)
    tilt = 7 * sway
    for side in (-1, 1):  # ears
        ex = hx + side * 62
        d.polygon([P(ex - 38, hy - 30), P(ex + side * 18, hy - 120 + (tilt * side) * 0.6), P(ex + 40, hy - 40)], fill=FUR)
        d.polygon([P(ex - 20, hy - 42), P(ex + side * 12, hy - 98 + (tilt * side) * 0.6), P(ex + 22, hy - 48)], fill=PINK)
    E(hx, hy, 105, 88, fill=FUR)
    for k in (-1, 0, 1):  # forehead stripes
        d.line([P(hx + k * 22, hy - 86), P(hx + k * 16, hy - 56)], fill=DARK, width=8 * S)
    E(hx, hy + 30, 52, 38, fill=CREAM)  # muzzle

    # eyes: look up-right (thinking), blink at 1.8 s and 5.8 s
    blink = any(abs(t - b) < 0.09 for b in (1.8, 5.8))
    for side in (-1, 1):
        ex, ey = hx + side * 40, hy - 8
        if blink:
            d.arc([P(ex - 18, ey - 6), P(ex + 18, ey + 14)], 200, 340, fill=INK, width=5 * S)
        else:
            E(ex, ey, 19, 23, fill=INK)
            E(ex + 7, ey - 9, 7, 7, fill=(255, 255, 255))
            E(ex - 5, ey + 7, 3, 3, fill=(255, 255, 255))
    # nose + mouth (small "hmm")
    d.polygon([P(hx - 9, hy + 14), P(hx + 9, hy + 14), P(hx, hy + 24)], fill=PINK)
    d.arc([P(hx - 14, hy + 22), P(hx + 2, hy + 40)], 20, 160, fill=INK, width=4 * S)
    d.arc([P(hx - 2, hy + 22), P(hx + 14, hy + 40)], 20, 160, fill=INK, width=4 * S)
    # whiskers
    for side in (-1, 1):
        for k in (-1, 0, 1):
            d.line([P(hx + side * 48, hy + 28 + k * 9), P(hx + side * 112, hy + 20 + k * 16)],
                   fill=(255, 245, 235), width=3 * S)
    # blush
    E(hx - 62, hy + 30, 14, 8, fill=(255, 140, 140, 150))
    E(hx + 62, hy + 30, 14, 8, fill=(255, 140, 140, 150))

    # paw raised to chin, tapping
    px, py = hx - 30, hy + 78 - 6 * tap
    d.line([P(cx - 60, base_y - 120), P(px, py)], fill=FUR, width=46 * S)
    E(px, py, 30, 26, fill=FUR)
    for k in (-1, 0, 1):
        d.line([P(px + k * 11, py - 22), P(px + k * 11, py - 10)], fill=DARK, width=3 * S)

    # thought bubble (bobs), with a "?" that pulses
    by = 70 + 8 * bob
    E(hx + 105, hy - 92 + 4 * bob, 9, 9, fill=(255, 255, 255))
    E(hx + 128, hy - 120 + 6 * bob, 14, 14, fill=(255, 255, 255))
    bx = 345
    E(bx, by, 72, 58, fill=(255, 255, 255))
    E(bx - 45, by + 12, 38, 34, fill=(255, 255, 255))
    E(bx + 45, by + 12, 38, 34, fill=(255, 255, 255))
    q_size = int((70 + 8 * max(0.0, math.sin(2 * math.pi * t / 2))) * S)
    d.text(P(bx, by + 4), "?", font=font(q_size // S * S), fill=BG, anchor="mm")

    return img.resize((bw, bh), Image.LANCZOS)


def reel_frame_at(layers, t, dur):
    """Everything stays on screen (no pop-in), so the loop never 'resets';
    only the cat, its bubble and a gentle CTA glow move."""
    import math
    bg, opts, diff, cta = layers
    f = bg.copy()
    for o in opts:
        f.paste(o, (0, 0), o)
    f.paste(diff, (0, 0), diff)
    # CTA breathes very slightly (period 2 s)
    p = 0.85 + 0.15 * (0.5 + 0.5 * math.sin(2 * math.pi * t / 2))
    f.paste(cta, (0, 0), cta.getchannel("A").point(lambda a: int(a * p)))
    cat = draw_cat(t)
    f.paste(cat, (CAT_BOX[0], CAT_BOX[1]), cat)
    return f


def reel_frame(q):
    """Final fully-revealed frame (used as cover)."""
    layers = reel_layers(q)
    return reel_frame_at(layers, 0.5, 8.0)


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
    reel_frame(q).save(f"{out}/cover.jpg", quality=90)
    layers = reel_layers(q)
    dur, fps = 8.0, 30
    # music.m4a in repo root is used if present, else a silent track
    music = os.path.join(ROOT, "music.m4a")
    audio = ["-stream_loop", "-1", "-i", music] if os.path.exists(music) else \
            ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
    proc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error",
                             "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                             *audio, "-t", str(dur), "-map", "0:v", "-map", "1:a",
                             "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                             "-af", "afade=t=out:st=7:d=1", "-c:a", "aac", "-b:a", "128k",
                             "-movflags", "+faststart", f"{out}/reel.mp4"], stdin=subprocess.PIPE)
    for n in range(int(dur * fps)):
        proc.stdin.write(reel_frame_at(layers, n / fps, dur).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise SystemExit("ffmpeg failed")
    answer_story(q).save(f"{out}/answer.png")
    print(out)


if __name__ == "__main__":
    main(int(sys.argv[1]))
