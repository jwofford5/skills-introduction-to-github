#!/usr/bin/env python3
"""Build "One Master and the Freedom from Worry".

One continuous shot drifting across a hand-drawn landscape while the light moves from
dawn, through the day, into night, and out to a sunrise. The words appear over the scene.
Every frame is drawn with Pillow/numpy and encoded with ffmpeg; the music is synthesised
in music.py (drop your own video-build/music.mp3, .m4a or .wav in to use that instead).

Usage:
    python3 build.py stills   # one still per card + layout checks (video-build/stills)
    python3 build.py render   # full render -> ../one-master-freedom-from-worry.mp4
"""
import math
import os
import random
import shutil
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "one-master-freedom-from-worry.mp4")
FRAMES = os.path.join(HERE, "frames_tmp")
STILLS = os.path.join(HERE, "stills")

W, H, FPS = 1920, 1080, 30
MARGIN = 200
MAX_CHARS = 38
TARGET_SECONDS = 357.0  # must land between 4.5 and 6 minutes

CREAM = (246, 240, 228)   # #F6F0E4
BROWN = (46, 36, 24)      # #2E2418
GOLD = (154, 123, 63)     # #9A7B3F
NAVY = (30, 42, 58)       # #1E2A3A
GOLD_D = (136, 108, 54)
GOLD_L = (201, 172, 112)
GOLD_XL = (224, 203, 155)
BLUE = (138, 155, 168)
BLUE_L = (178, 190, 199)
SAGE = (143, 165, 138)
SAGE_D = (112, 136, 108)

SZ_BODY, SZ_SCRIPTURE, SZ_REF = 82, 84, 60
SZ_TITLE, SZ_WORD, SZ_SMALL, SZ_CLOSING = 128, 170, 64, 104

# ---------------------------------------------------------------- fonts
FONT_CHOICES = [  # in order of preference: (name, regular file, italic file)
    ("Georgia", "georgia.ttf", "georgiai.ttf"),
    ("Georgia", "Georgia.ttf", "Georgia Italic.ttf"),
    ("Palatino", "pala.ttf", "palai.ttf"),
    ("Cambria", "cambria.ttf", "cambriai.ttf"),
    ("Times New Roman", "times.ttf", "timesi.ttf"),
    ("Times New Roman", "Times New Roman.ttf", "Times New Roman Italic.ttf"),
    ("Liberation Serif (Times New Roman metric-compatible)",
     "LiberationSerif-Regular.ttf", "LiberationSerif-Italic.ttf"),
    ("DejaVu Serif", "DejaVuSerif.ttf", "DejaVuSerif-Italic.ttf"),
]
FONT_DIRS = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.fonts"),
             "/Library/Fonts", "/System/Library/Fonts", "C:/Windows/Fonts"]


def find_fonts():
    index = {}
    for d in FONT_DIRS:
        for root, _, files in os.walk(d):
            for f in files:
                index.setdefault(f, os.path.join(root, f))
    for name, reg, ita in FONT_CHOICES:
        if reg in index and ita in index:
            return name, index[reg], index[ita]
    raise SystemExit("No serif font found")


FONT_NAME, FONT_REG, FONT_ITA = find_fonts()
_fonts = {}


def font(italic, size):
    key = (italic, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_ITA if italic else FONT_REG, size)
    return _fonts[key]


# ---------------------------------------------------------------- script
def C(n, kind, text, sub=None, illus=None, keep=False):
    return dict(n=n, kind=kind, text=text, sub=sub, illus=illus, keep=keep)


SECTIONS = [
    [  # OPENING
        C(1, "title", "One Master and the Freedom from Worry", "Matthew 6:19-34"),
        C(2, "body", "Mom, I made this for you. It comes from a sermon on Matthew 6."),
        C(3, "body", "Jesus makes one argument in this passage. A person can have only one master."),
        C(4, "body", "The person who belongs to God as Father has no reason to live in anxiety."),
    ],
    [  # SECTION ONE
        C(5, "section", "Three Pictures"),
        C(6, "scripture", '"Where your treasure is, there will your heart be also."',
          "Matthew 6:21", illus="coins"),
        C(7, "body", "The treasure pulls the heart after it. We come to love what we invest in."),
        C(8, "scripture", '"If therefore thine eye be single, thy whole body shall be full of light."',
          "Matthew 6:22", illus="lamp"),
        C(9, "body", "The way we look at what we have shapes our whole life. A generous eye "
                     "can be glad when someone else is blessed."),
        C(10, "scripture", '"No man can serve two masters."', "Matthew 6:24", illus="path"),
        C(11, "body", "Loyalty cannot be divided. Sooner or later one master wins the "
                      "decisions that matter."),
    ],
    [  # SECTION TWO
        C(12, "word", "Therefore."),
        C(13, "scripture", '"Therefore I say unto you, Take no thought for your life."', "Matthew 6:25"),
        C(14, "body", "That word ties everything together. If God is your only master, then "
                      "the master you serve is responsible for you."),
        C(15, "scripture", '"Behold the fowls of the air: for they sow not, neither do they reap, '
                           'nor gather into barns; yet your heavenly Father feedeth them."',
          "Matthew 6:26", illus="birds"),
        C(16, "body", "Jesus points to the birds as evidence."),
        C(17, "body", "Worry accomplishes nothing. No one can add a single hour to his life "
                      "by being anxious about it."),
        C(18, "scripture", '"Consider the lilies of the field, how they grow; they toil not, '
                           'neither do they spin."', "Matthew 6:28", illus="lilies"),
        C(19, "scripture", '"Even Solomon in all his glory was not arrayed like one of these."',
          "Matthew 6:29", illus="lilies", keep=True),
        C(20, "body", "If God clothes the grass that way, he will clothe you.",
          illus="lilies", keep=True),
        C(21, "scripture", '"Your heavenly Father knoweth that ye have need of all these things."',
          "Matthew 6:32"),
    ],
    [  # SECTION THREE
        C(22, "section", "Planning and Worrying"),
        C(23, "body", "Planning makes a budget, schedules the appointment, and prepares for the day."),
        C(24, "body", "Worry lies awake at three in the morning and goes over the same thing "
                      "again and again.", illus="moon"),
        C(25, "body", "When you notice that loop, stop and name it."),
        C(26, "body", "Look at the evidence of the Father's care. Hand him the thing you cannot carry."),
    ],
    [  # SECTION FOUR
        C(27, "section", "Seek First"),
        C(28, "scripture", '"But seek ye first the kingdom of God, and his righteousness; and all '
                           'these things shall be added unto you."', "Matthew 6:33"),
        C(29, "body", "The things we worry about are added. They come along with the main thing."),
    ],
    [  # SECTION FIVE
        C(30, "section", "Today"),
        C(31, "scripture", '"Sufficient unto the day is the evil thereof."', "Matthew 6:34",
          illus="sun"),
        C(32, "body", "Each day has its own trouble, and God gives grace for each day as it comes.",
          illus="sun", keep=True),
        C(33, "body", "Do today's work and leave tomorrow with the Father.", illus="sun", keep=True),
    ],
    [  # CLOSING
        C(34, "body", "The freedom Jesus offers is the freedom of a child who knows his Father "
                      "is paying attention.", illus="sun", keep=True),
        C(35, "closing", "I love you, Mom.", "Josh", illus="sun", keep=True),
    ],
]
CARDS = [c for s in SECTIONS for c in s]

# Hand-set line breaks where the automatic balancing reads awkwardly.
LINE_BREAKS = {18: ['"Consider the lilies of the field,', 'how they grow; they toil not,',
                    'neither do they spin."']}

SIZE_OVERRIDE = {15: 74}   # the longest verse, so it clears the birds above and the trees below
VEIL_KINDS = ("title", "section", "word")     # shown over a navy veil
DARK_SKY = (24, 25, 26, 28, 29)               # night / pre-dawn cards: cream text
FEATURES = ("coins", "lamp", "path", "birds", "lilies")   # things drawn into the scene

# Vertical band the text may occupy, so it stays clear of what is drawn in the scene.
TEXT_ZONE = {None: (60, 680), "coins": (60, 560), "lamp": (60, 500), "path": (60, 600),
             "birds": (170, 640), "lilies": (40, 500), "moon": (60, 680), "sun": (60, 540)}


# ---------------------------------------------------------------- timing
def smooth(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def n_words(card):
    return len((card["text"] + " " + (card["sub"] or "")).split())


def hold_for(card, k):
    if card["kind"] == "section":
        return 4.0
    if card["kind"] == "word":
        return 5.0
    if card["kind"] == "closing":
        return 8.0
    return max(6.0, k * (n_words(card) / 2 + 3))


def build_timeline(k):
    t = 0.5
    timings, groups = {}, []
    for si, sec in enumerate(SECTIONS):
        if si:
            t += 1.0  # a breath of scene with no words between sections
        for card in sec:
            fo = 2.5 if card["kind"] == "closing" else 1.0
            tm = dict(card=card, t0=t, fi=1.0, hold=hold_for(card, k), fo=fo)
            tm["end"] = t + tm["fi"] + tm["hold"] + fo
            timings[card["n"]] = tm
            if card["illus"] in FEATURES:
                if card["keep"]:
                    groups[-1]["end"] = tm["end"]
                else:
                    groups.append(dict(name=card["illus"], t0=t, end=tm["end"],
                                       T1=tm["fi"] + tm["hold"]))
            t = tm["end"]
    return timings, groups, t + 1.5


def solve_timeline():
    if build_timeline(1.0)[2] <= TARGET_SECONDS:
        return build_timeline(1.0) + (1.0,)
    lo, hi = 0.3, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if build_timeline(mid)[2] > TARGET_SECONDS:
            hi = mid
        else:
            lo = mid
    return build_timeline(lo) + (lo,)


TIMINGS, GROUPS, TOTAL, KSCALE = solve_timeline()
T = TIMINGS
NFRAMES = round(TOTAL * FPS)


# ---------------------------------------------------------------- text
def wrap(text, fnt, max_w=W - 2 * MARGIN, max_chars=MAX_CHARS):
    """Fewest lines possible, then as evenly balanced as possible, no lone last word."""
    words = text.split()
    n = len(words)
    width = lambda i, j: fnt.getlength(" ".join(words[i:j]))
    ok = lambda i, j: (len(" ".join(words[i:j])) <= max_chars and width(i, j) <= max_w) or j == i + 1
    INF = float("inf")
    minl = [INF] * (n + 1)
    minl[n] = 0
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if ok(i, j) and minl[j] + 1 < minl[i]:
                minl[i] = minl[j] + 1
    best = {}

    def solve(i, left):
        if i == n:
            return (0.0, []) if left == 0 else (INF, [])
        if left == 0:
            return INF, []
        if (i, left) in best:
            return best[(i, left)]
        res = (INF, [])
        for j in range(i + 1, n + 1):
            if not ok(i, j):
                break
            cost = width(i, j) ** 2
            if j < n:
                if words[j - 1][-1] in ".;:":
                    cost -= 60000
                elif words[j - 1][-1] == ",":
                    cost -= 15000
                elif any(w[-1] in ".;:" for w in words[max(i, j - 2):j - 1]):
                    cost += 90000  # a new sentence starting at the very end of a line
            if j == n and j - i == 1 and i > 0:
                cost += 1e9  # a word alone on the last line
            sub = solve(j, left - 1)
            if cost + sub[0] < res[0]:
                res = (cost + sub[0], [" ".join(words[i:j])] + sub[1])
        best[(i, left)] = res
        return res

    lines = solve(0, minl[0])[1]
    if len(lines) > 1 and len(lines[-1].split()) == 1:
        best.clear()
        lines = solve(0, minl[0] + 1)[1] or lines
    return lines


def layout(card):
    """Returns ([(string, font, colour, baseline_y)], rule_y or None, lines)."""
    kind = card["kind"]
    veil = kind in VEIL_KINDS
    dark = veil or card["n"] in DARK_SKY
    main_col = CREAM if dark else BROWN
    size = {"title": SZ_TITLE, "section": SZ_TITLE, "word": SZ_WORD, "body": SZ_BODY,
            "scripture": SZ_SCRIPTURE, "closing": SZ_CLOSING}[kind]
    size = SIZE_OVERRIDE.get(card["n"], size)
    f_main = font(kind == "scripture", size)
    lines = LINE_BREAKS.get(card["n"]) or wrap(card["text"], f_main)
    assert " ".join(lines) == card["text"]
    lh = round(size * (1.2 if veil else 1.34))
    asc, desc = f_main.getmetrics()
    height = asc + (len(lines) - 1) * lh + desc * 0.6
    sub = card["sub"]
    if sub:
        sub_size = SZ_REF if kind == "scripture" else SZ_SMALL
        f_sub = font(False, sub_size)
        sub_col = BROWN if kind == "closing" else (GOLD_L if dark else GOLD)
        gap = {"scripture": 0.62, "title": 1.05, "closing": 0.75}[kind] * size
        s_asc, s_desc = f_sub.getmetrics()
        height += gap - desc * 0.6 + s_asc + s_desc * 0.6
    z0, z1 = (0, 1000) if veil else TEXT_ZONE[card["illus"]]
    y = (z0 + z1) / 2 - height / 2 + asc
    items = []
    for ln in lines:
        items.append((ln, f_main, main_col, y))
        y += lh
    rule = None
    if sub:
        y_last = y - lh
        if kind == "title":
            rule = y_last + gap * 0.46
        items.append((sub, f_sub, sub_col, y_last + gap + s_asc))
    return items, rule, lines


_text_cache = {}


def text_items(n):
    """Per-line masks for card n: list of dicts(x, y, mask, color, halo, hx, hy), bbox."""
    if n in _text_cache:
        return _text_cache[n]
    card = CARDS[n - 1]
    items, rule, _ = layout(card)
    veil = card["kind"] in VEIL_KINDS
    out, boxes = [], []
    specs = [("text", it) for it in items]
    if rule:
        specs.insert(len(specs) - 1, ("rule", rule))
    for kind, it in specs:
        img = Image.new("L", (W, H), 0)
        d = ImageDraw.Draw(img)
        if kind == "rule":
            d.line([(W / 2 - 90, it), (W / 2 + 90, it)], fill=255, width=3)
            col = GOLD_L
        else:
            s, f, col, y = it
            d.text((W / 2, y), s, font=f, fill=255, anchor="ms")
        box = img.getbbox()
        boxes.append(box)
        e = dict(x=box[0], y=box[1], mask=np.asarray(img.crop(box), np.float32) / 255.0,
                 color=np.array(col, np.float32), halo=None)
        if not veil:   # soft halo keeps the words readable over the moving sky
            pad = 80
            hb = (max(0, box[0] - pad), max(0, box[1] - pad), min(W, box[2] + pad), min(H, box[3] + pad))
            blur = np.asarray(img.crop(hb).filter(ImageFilter.GaussianBlur(26)), np.float32) / 255.0
            e.update(halo=np.clip(blur * 2.4, 0, 1) * 0.62, hx=hb[0], hy=hb[1])
        out.append(e)
    bbox = (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))
    _text_cache[n] = (out, bbox)
    return _text_cache[n]


# ---------------------------------------------------------------- compositing kit
def blit_mask(frame, mask, xf, yf, color, opacity=1.0):
    """Blend a flat colour through a 2-D alpha mask at a sub-pixel position."""
    if opacity <= 0.002:
        return
    x0, y0 = math.floor(xf), math.floor(yf)
    fx, fy = xf - x0, yf - y0
    m = mask
    if fx > 0.01:
        t = np.zeros((m.shape[0], m.shape[1] + 1), np.float32)
        t[:, :-1] += m * (1 - fx)
        t[:, 1:] += m * fx
        m = t
    if fy > 0.01:
        t = np.zeros((m.shape[0] + 1, m.shape[1]), np.float32)
        t[:-1] += m * (1 - fy)
        t[1:] += m * fy
        m = t
    h, w = m.shape
    a0, b0 = max(0, -y0), max(0, -x0)
    a1, b1 = min(h, H - y0), min(w, W - x0)
    if a1 <= a0 or b1 <= b0:
        return
    a = (m[a0:a1, b0:b1] * opacity)[..., None]
    reg = frame[y0 + a0:y0 + a1, x0 + b0:x0 + b1]
    reg *= 1 - a
    reg += a * np.asarray(color, np.float32)


def blit_sprite(frame, spr, xf, yf, opacity=1.0, tint=None, haze=None):
    """spr: (h, w, 4) float32, premultiplied rgb 0..255 and alpha 0..1."""
    if opacity <= 0.002:
        return
    x0, y0 = math.floor(xf), math.floor(yf)
    fx, fy = xf - x0, yf - y0
    s = spr
    if fx > 0.01:
        t = np.zeros((s.shape[0], s.shape[1] + 1, 4), np.float32)
        t[:, :-1] += s * (1 - fx)
        t[:, 1:] += s * fx
        s = t
    if fy > 0.01:
        t = np.zeros((s.shape[0] + 1, s.shape[1], 4), np.float32)
        t[:-1] += s * (1 - fy)
        t[1:] += s * fy
        s = t
    h, w = s.shape[:2]
    a0, b0 = max(0, -y0), max(0, -x0)
    a1, b1 = min(h, H - y0), min(w, W - x0)
    if a1 <= a0 or b1 <= b0:
        return
    s = s[a0:a1, b0:b1]
    a = s[..., 3:] * opacity
    rgb = s[..., :3] * opacity
    if tint is not None:
        rgb = rgb * tint
    if haze is not None:
        rgb = rgb * (1 - haze[1]) + haze[0] * a * haze[1]
    reg = frame[y0 + a0:y0 + a1, x0 + b0:x0 + b1]
    reg *= 1 - a
    reg += rgb


SS = 2  # supersampling for drawn shapes


class Canvas:
    """Supersampled RGBA canvas over a region of the frame, in frame coordinates."""

    def __init__(self, region, k=1.0, pivot=(W / 2, H), shift=(0.0, 0.0), ss=SS):
        x0, y0, x1, y1 = region
        self.x0, self.y0 = max(0, int(x0)), max(0, int(y0))
        self.x1, self.y1 = min(W, int(x1)), min(H, int(y1))
        self.k, self.pivot, self.shift, self.ss = k, pivot, shift, ss
        self.img = Image.new("RGBA", ((self.x1 - self.x0) * ss, (self.y1 - self.y0) * ss), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def F(self, p):  # design coords -> frame coords
        return ((p[0] - self.pivot[0]) * self.k + self.pivot[0] + self.shift[0],
                (p[1] - self.pivot[1]) * self.k + self.pivot[1] + self.shift[1])

    def P(self, p):
        x, y = self.F(p)
        return ((x - self.x0) * self.ss, (y - self.y0) * self.ss)

    def L(self, r):
        return r * self.k * self.ss

    def ellipse(self, cx, cy, rx, ry, fill=None, outline=None, width=0):
        x, y = self.P((cx, cy))
        self.d.ellipse([x - self.L(rx), y - self.L(ry), x + self.L(rx), y + self.L(ry)],
                       fill=fill, outline=outline, width=round(self.L(width)))

    def polygon(self, pts, fill):
        self.d.polygon([self.P(p) for p in pts], fill=fill)

    def line(self, pts, width, fill):
        q = [self.P(p) for p in pts]
        w = max(1, round(self.L(width)))
        self.d.line(q, fill=fill, width=w, joint="curve")
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=fill)

    def rrect(self, x0, y0, x1, y1, r, fill):
        a, b = self.P((x0, y0)), self.P((x1, y1))
        self.d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=self.L(r), fill=fill)

    def finish(self):
        """-> (x0, y0, premultiplied float sprite)"""
        size = (self.x1 - self.x0, self.y1 - self.y0)
        arr = np.asarray(self.img.convert("RGBa").resize(size, Image.LANCZOS), np.float32).copy()
        arr[..., 3] /= 255.0
        return self.x0, self.y0, arr


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def smooth_closed(pts, n=14):
    out, m = [], len(pts)
    for i in range(m):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % m], pts[(i + 2) % m]
        for j in range(n):
            t = j / n
            out.append(tuple(
                0.5 * (2 * p1[a] + (p2[a] - p0[a]) * t + (2 * p0[a] - 5 * p1[a] + 4 * p2[a] - p3[a]) * t * t
                       + (3 * p1[a] - p0[a] - 3 * p2[a] + p3[a]) * t ** 3) for a in (0, 1)))
    return out


def ribbon(center, w0, w1):
    left, right, n = [], [], len(center)
    for i, (x, y) in enumerate(center):
        ax, ay = center[max(i - 1, 0)]
        bx, by = center[min(i + 1, n - 1)]
        tx, ty = bx - ax, by - ay
        ln = math.hypot(tx, ty) or 1
        nx, ny = -ty / ln, tx / ln
        w = (w0 + (w1 - w0) * i / (n - 1)) / 2
        left.append((x + nx * w, y + ny * w))
        right.append((x - nx * w, y - ny * w))
    return left + right[::-1]


def blade(base, angle, length, width, n=14):
    """Leaf / petal / grass blade, pointed at both ends (angle 0 = straight up)."""
    ca, sa = math.cos(angle), math.sin(angle)
    a, b = [], []
    for i in range(n + 1):
        t = i / n
        along = t * length
        hw = width / 2 * math.sin(math.pi * t ** 0.8) ** 0.9
        for side, lst in ((1, a), (-1, b)):
            lx, ly = side * hw, -along
            lst.append((base[0] + lx * ca - ly * sa, base[1] + lx * sa + ly * ca))
    return a + b[::-1]


_kernels = {}


def dot(r):
    """Soft round dot mask of radius ~r."""
    key = round(r * 4) / 4
    if key not in _kernels:
        n = int(math.ceil(key * 3))
        y, x = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
        _kernels[key] = np.exp(-(x * x + y * y) / (2 * (key * 0.8) ** 2)).astype(np.float32)
    return _kernels[key]


# ---------------------------------------------------------------- light through the day
def rgb(*v):
    return np.array(v, np.float32)


#            sky top            sky middle          sky at horizon      light on the land    clouds
STATES = {
    "dawn":      (rgb(196, 202, 216), rgb(238, 224, 208), rgb(250, 216, 178), rgb(.90, .86, .86), .50),
    "morning":   (rgb(204, 220, 228), rgb(238, 236, 226), rgb(248, 238, 214), rgb(1.0, 1.0, .98), .62),
    "day":       (rgb(182, 208, 224), rgb(226, 235, 234), rgb(245, 240, 222), rgb(1.0, 1.0, 1.0), .70),
    "afternoon": (rgb(220, 212, 196), rgb(244, 228, 194), rgb(248, 210, 152), rgb(1.0, .92, .80), .45),
    "night":     (rgb(16, 24, 42),    rgb(28, 40, 64),    rgb(50, 64, 92),    rgb(.26, .32, .46), .10),
    "predawn":   (rgb(22, 32, 56),    rgb(52, 58, 90),    rgb(204, 140, 116), rgb(.38, .38, .50), .16),
    "sunrise":   (rgb(206, 212, 220), rgb(246, 228, 200), rgb(252, 208, 148), rgb(.96, .88, .78), .50),
    "morning2":  (rgb(210, 224, 230), rgb(246, 240, 226), rgb(252, 236, 204), rgb(1.0, 1.0, .97), .62),
}
KEYS = [(0, "dawn"), (T[5]["t0"], "dawn"), (T[5]["end"], "morning"),
        (T[12]["t0"], "morning"), (T[12]["end"], "day"),
        (T[22]["t0"], "day"), (T[22]["end"], "afternoon"),
        (T[23]["end"] - 3.0, "afternoon"), (T[24]["t0"] + 1.5, "night"),
        (T[27]["t0"], "night"), (T[27]["end"], "predawn"),
        (T[30]["t0"], "predawn"), (T[30]["end"], "sunrise"),
        (T[33]["end"], "sunrise"), (T[34]["t0"] + 3.0, "morning2"), (TOTAL + 1, "morning2")]


def weights(t):
    for (ta, a), (tb, b) in zip(KEYS, KEYS[1:]):
        if ta <= t < tb:
            w = smooth((t - ta) / (tb - ta))
            return {a: 1.0} if a == b else {a: 1 - w, b: w}
    return {KEYS[-1][1]: 1.0}


def palette(t):
    ws = weights(t)
    top, mid, hor, tint, cloud = (sum(STATES[s][i] * w for s, w in ws.items()) for i in range(5))
    return dict(top=top, mid=mid, hor=hor, tint=tint, cloud=float(cloud), w=ws)


# ---------------------------------------------------------------- the land
SPEED = dict(cloud=1.5, far=2.5, mid=5.0, near=10.0)   # pixels per second: one slow, steady drift
HILL = {  # base height, [(amplitude, wavelength, phase)], crest colour, base colour, haze
    "far":  (735, [(36, 410, 0.6), (15, 170, 2.1), (6, 67, 4.0)], rgb(170, 192, 190), rgb(152, 178, 174), .46),
    "mid":  (838, [(26, 330, 1.9), (10, 120, 0.4)], rgb(156, 182, 150), rgb(132, 162, 130), .22),
    "near": (928, [(20, 520, 3.3), (8, 190, 1.2)], rgb(130, 160, 122), rgb(102, 134, 98), .05),
}
GROUP = {g["name"]: g for g in GROUPS}
for g in GROUPS:
    g["mid"] = (g["t0"] + g["end"]) / 2
    g["wx"] = SPEED["near"] * g["mid"] + W / 2     # where it stands in the world
PATH_WX = GROUP["path"]["wx"]


def profile(layer, xw):
    base, waves, _, _, _ = HILL[layer]
    y = base + sum(a * np.sin(xw / l + p) for a, l, p in waves)
    if layer == "near":   # a broad rise, so the forked road has a hill to climb
        y = y - 118 * np.exp(-((xw - PATH_WX) / 700.0) ** 2)
    return y


XS = np.arange(W, dtype=np.float32)
YS = np.arange(H, dtype=np.float32)


def draw_hill(frame, layer, t, pal):
    _, _, crest, base, haze = HILL[layer]
    y = profile(layer, XS + SPEED[layer] * t)
    top = max(0, int(y.min()) - 1)
    rows = YS[top:, None]
    mask = np.clip(rows - y[None, :] + 0.5, 0, 1)[..., None]
    depth = np.clip((rows - y[None, :]) / 230.0, 0, 1)[..., None]
    c0 = crest * pal["tint"] * (1 - haze) + pal["hor"] * haze
    c1 = base * pal["tint"] * (1 - haze) + pal["hor"] * haze
    col = c0 + (c1 - c0) * depth
    reg = frame[top:]
    reg *= 1 - mask
    reg += col * mask
    return y


def make_tree(kind, scale):
    c = Canvas((0, 0, 220, 260), k=scale, pivot=(110, 250), ss=3)
    trunk, dark, light = (118, 102, 84, 255), (98, 130, 98, 255), (120, 150, 114, 255)
    if kind == 0:      # round tree
        c.rrect(103, 150, 117, 250, 4, trunk)
        c.ellipse(110, 110, 62, 66, fill=dark)
        c.ellipse(96, 96, 40, 42, fill=light)
    elif kind == 1:    # tall cypress
        c.rrect(105, 200, 115, 250, 3, trunk)
        c.polygon(blade((110, 225), 0, 215, 58), dark)
        c.polygon(blade((104, 215), -0.03, 170, 30), light)
    else:              # a pair of small round trees
        c.rrect(74, 190, 84, 250, 3, trunk)
        c.rrect(142, 205, 150, 250, 3, trunk)
        c.ellipse(79, 160, 44, 46, fill=dark)
        c.ellipse(70, 150, 27, 28, fill=light)
        c.ellipse(146, 182, 32, 34, fill=dark)
        c.ellipse(140, 175, 19, 20, fill=light)
    return c.finish()[2]


_rng = random.Random(4)
TREES = []
_x = -150.0
while _x < SPEED["mid"] * TOTAL + W + 200:
    TREES.append((_x, _rng.choice([0, 0, 1, 2]), _rng.uniform(0.45, 0.68)))
    _x += _rng.uniform(170, 460)
_tree_sprites = {}


def draw_trees(frame, t, pal, dbg=None):
    cam = SPEED["mid"] * t
    for i, (wx, kind, sc) in enumerate(TREES):
        sx = wx - cam
        if -230 < sx < W + 10:
            if i not in _tree_sprites:
                _tree_sprites[i] = make_tree(kind, sc)
            base = float(profile("mid", wx + 110)) + 6
            blit_sprite(frame, _tree_sprites[i], sx, base - 250, tint=pal["tint"],
                        haze=(pal["hor"], 0.20))
            if dbg is not None:
                top = base - (240 if kind == 1 else 208) * sc
                dbg.append(("tree", (sx + 110 - 45 * sc, top, sx + 110 + 45 * sc, base)))


def make_cloud(seed):
    r = random.Random(seed)
    img = Image.new("L", (760, 280), 0)
    d = ImageDraw.Draw(img)
    for _ in range(r.randint(5, 8)):
        cx, cy = r.uniform(170, 590), r.uniform(120, 170)
        rx, ry = r.uniform(90, 170), r.uniform(34, 60)
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=255)
    d.rectangle([60, 172, 700, 280], fill=0)
    d.rounded_rectangle([120, 150, 640, 186], radius=18, fill=255)
    return np.asarray(img.filter(ImageFilter.GaussianBlur(20)), np.float32) / 255.0


CLOUD_SPAN = 3800
CLOUDS = [(i * CLOUD_SPAN / 9 + _rng.uniform(-120, 120), _rng.uniform(20, 330), 100 + i)
          for i in range(9)]
_cloud_masks = {}


def draw_clouds(frame, t, pal):
    col = pal["mid"] + (rgb(255, 255, 255) - pal["mid"]) * pal["cloud"]
    for wx, y, seed in CLOUDS:
        if seed not in _cloud_masks:
            _cloud_masks[seed] = make_cloud(seed)
        sx = (wx - SPEED["cloud"] * t * (1 + (seed % 3) * 0.25)) % CLOUD_SPAN - 800
        blit_mask(frame, _cloud_masks[seed], sx, y, col, 0.62)


STARS = [(_rng.uniform(0, W), _rng.uniform(0, 700), _rng.uniform(1.1, 2.4), _rng.uniform(0, 6.28),
          _rng.uniform(0.4, 1.1)) for _ in range(120)]
MOTES = [(_rng.uniform(0, W), _rng.uniform(0, H), _rng.uniform(1.6, 3.8), _rng.uniform(0, 6.28),
          _rng.uniform(0.5, 1.2)) for _ in range(34)]
FIREFLIES = [(_rng.uniform(80, W - 80), _rng.uniform(700, 1040), _rng.uniform(0, 6.28),
              _rng.uniform(0, 6.28), _rng.uniform(0.6, 1.1)) for _ in range(22)]
_moon = {}


def moon_pos(t):
    p = (t - T[24]["t0"]) / max(1.0, T[26]["end"] - T[24]["t0"])
    return 1688 + 30 * p, 214 - 34 * p


def draw_heavens(frame, t, pal, dbg):
    night = pal["w"].get("night", 0) + 0.55 * pal["w"].get("predawn", 0)
    if night > 0.01:
        for x, y, r, ph, sp in STARS:
            a = night * (0.55 + 0.4 * math.sin(t * 0.7 * sp + ph))
            blit_mask(frame, dot(r), x - r * 3, y - r * 3, (236, 236, 222), a)
    mw = min(1.0, max(0.0, (pal["w"].get("night", 0) - 0.75) * 4))
    if mw > 0.01:
        if not _moon:
            c = Canvas((0, 0, 180, 180), ss=4)
            c.ellipse(90, 90, 62, 62, fill=(238, 226, 184, 255))
            c.ellipse(122, 72, 58, 58, fill=(0, 0, 0, 0))
            _moon["s"] = c.finish()[2]
        mx, my = moon_pos(t)
        blit_mask(frame, dot(60), mx - 180, my - 180, (150, 160, 190), 0.30 * mw)
        blit_sprite(frame, _moon["s"], mx - 90, my - 90, opacity=mw)
        if dbg is not None:
            dbg.append(("moon", (mx - 62, my - 62, mx + 62, my + 62)))
    sw = pal["w"].get("sunrise", 0) + pal["w"].get("morning2", 0)
    if sw > 0.01:
        a, b, c = T[30]["end"], T[33]["end"], TOTAL
        sy = 752 - 86 * min(1, (t - a) / (b - a)) if t < b else 666 - 22 * (t - b) / (c - b)
        sy = min(sy, 800)
        yy = YS[:, None] - sy
        xx = XS[None, :] - 960
        d = np.sqrt(xx * xx + yy * yy)
        glow = (np.clip(1 - d / 620, 0, 1) ** 2 * 0.55 * sw)[..., None]
        frame *= 1 - glow
        frame += glow * rgb(255, 228, 160)
        disc = (np.clip(64 - d + 0.5, 0, 1) * sw)[..., None]
        frame *= 1 - disc
        frame += disc * rgb(255, 240, 190)
        if dbg is not None:
            dbg.append(("sun", (896, sy - 64, 1024, min(sy + 64, 735))))


def draw_motes(frame, t, pal):
    night = pal["w"].get("night", 0) + pal["w"].get("predawn", 0) * 0.5
    day = 1 - min(1, night * 1.6)
    if day > 0.02:
        for x, y, r, ph, sp in MOTES:
            sx = (x + 7 * t * sp + 22 * math.sin(0.23 * t + ph)) % (W + 60) - 30
            sy = (y - 8 * t * sp) % (H + 60) - 30
            a = day * 0.30 * (0.6 + 0.4 * math.sin(0.5 * t + ph * 2))
            blit_mask(frame, dot(r), sx - r * 3, sy - r * 3, (255, 250, 232), a)
    if night > 0.02:
        for x, y, p1, p2, sp in FIREFLIES:
            sx = x + 70 * math.sin(0.11 * t * sp + p1) + 26 * math.sin(0.29 * t + p2)
            sy = y + 34 * math.sin(0.15 * t * sp + p2)
            a = night * max(0.0, math.sin(0.8 * t * sp + p1)) ** 2
            blit_mask(frame, dot(7), sx - 21, sy - 21, (232, 226, 140), a * 0.45)
            blit_mask(frame, dot(2), sx - 6, sy - 6, (250, 246, 190), a)


_grs = np.random.default_rng(9)
GRASS = _grs.uniform(0, 1, (700, 4))


def draw_grass(frame, t, pal, near_y):
    cam = SPEED["near"] * t
    y0, y1 = int(near_y.min()) - 60, int(near_y.max()) + 26
    c = Canvas((0, y0, W, y1))
    _, _, crest, base, _ = HILL["near"]
    cols = [tuple(int(v) for v in np.clip(k * pal["tint"], 0, 255)) + (255,)
            for k in (crest * 1.10, crest * 0.90, base * 1.02)]
    step = 30.0
    i0 = int(cam // step) - 1
    for i in range(i0, i0 + int(W / step) + 3):
        g = GRASS[i % 700]
        wx = i * step + g[0] * 20
        sx = wx - cam
        by = float(profile("near", wx)) + 5
        sway = 0.10 * math.sin(0.9 * t + wx * 0.011) + 0.05 * math.sin(0.37 * t + g[1] * 6)
        for j, ang in enumerate((-0.42, 0.04, 0.46)):
            ln = (22 + 30 * g[(j + 1) % 4]) * (1.25 if j == 1 else 1.0)
            c.polygon(blade((sx + ang * 16, by), ang + sway, ln, 7.5), cols[(i + j) % 3])
    x, y, spr = c.finish()
    blit_sprite(frame, spr, x, y)


# ---------------------------------------------------------------- things in the scene
def feat_x(g, t):
    return g["wx"] - SPEED["near"] * t


def bbox_of(x0, y0, spr):
    ys, xs = np.where(spr[..., 3] > 0.06)
    return (x0 + xs.min(), y0 + ys.min(), x0 + xs.max(), y0 + ys.max()) if len(xs) else None


def draw_coins(frame, g, t, a, pal, dbg):
    cx = feat_x(g, t)
    base = float(profile("near", g["wx"])) + 22
    c = Canvas((cx - 470, base - 300, cx + 470, base + 30), k=1.12, pivot=(960, 1040),
               shift=(cx - 960, base - 1040))
    c.rrect(640, 1004, 1300, 1050, 18, (198, 190, 172, 255))      # a flat stone
    c.rrect(640, 1030, 1300, 1050, 12, (176, 168, 150, 255))
    for x0, y0, x1, y1, col in ((690, 958, 950, 1006, BLUE), (702, 912, 938, 960, BLUE_L),
                                (714, 866, 926, 914, BLUE)):
        c.rrect(x0, y0, x1, y1, 22, col + (255,))                   # folded cloth
    for x in (872, 892):
        c.rrect(x, 866, x + 9, 914, 0, GOLD_XL + (255,))

    def stack(x, bottom, count):
        rx, ry, th = 64, 19, 15
        for i in range(count):
            y = bottom - i * th
            side = (GOLD if i % 2 == 0 else GOLD_D) + (255,)
            c.ellipse(x, y, rx, ry, fill=side)
            c.rrect(x - rx, y - th, x + rx, y, 0, side)
            c.ellipse(x, y - th, rx, ry, fill=GOLD_L + (255,))
        c.ellipse(x, bottom - count * th, rx * 0.66, ry * 0.66, outline=GOLD + (255,), width=2.5)

    stack(1090, 1000, 5)
    stack(1222, 1002, 2)
    stack(1150, 1024, 1)
    x, y, spr = c.finish()
    blit_sprite(frame, spr, x, y, opacity=a, tint=pal["tint"])
    if dbg is not None:
        dbg.append(("coins", bbox_of(x, y, spr)))


def draw_lamp(frame, g, t, a, pal, dbg):
    cx = feat_x(g, t)
    base = float(profile("near", g["wx"])) + 22
    p = smooth((t - g["t0"]) / (g["end"] - g["t0"]))
    c = Canvas((cx - 420, base - 300, cx + 420, base + 30), pivot=(960, 1040),
               shift=(cx - 960 - 26, base - 1040))
    gl, gd_, gdd = GOLD_L + (255,), GOLD + (255,), GOLD_D + (255,)
    c.rrect(700, 1022, 1240, 1062, 16, (198, 190, 172, 255))       # a flat stone
    c.rrect(700, 1044, 1240, 1062, 10, (176, 168, 150, 255))
    c.ellipse(812, 942, 38, 34, outline=gd_, width=13)
    c.polygon([(915, 990), (1005, 990), (1032, 1028), (888, 1028)], gd_)
    c.polygon(smooth_closed([(1040, 918), (1105, 912), (1160, 896), (1190, 890), (1196, 904),
                             (1160, 932), (1110, 972), (1050, 996)]), gl)
    c.ellipse(960, 955, 140, 50, fill=gl)
    c.ellipse(950, 915, 62, 13, fill=gd_)
    c.ellipse(950, 899, 11, 10, fill=gdd)
    s = 1 + 0.05 * math.sin(2 * math.pi * t / 4.5)
    bx, by = 1186, 896
    for scale, col in ((1.0, (226, 172, 84, 255)), (0.55, (250, 226, 164, 255))):
        pts = [(0, 2), (17, -16), (14, -44), (0, -80), (-12, -44), (-17, -16)]
        c.polygon(smooth_closed([(bx + x * scale + 2 * math.sin(t * 0.9) * (y < -40), by + y * scale * s)
                                 for x, y in pts]), col)
    fx, fy = c.F((1186, 858))
    R = 150 + 60 * p                                                # the light slowly grows
    n = int(R)
    yy, xx = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
    glow = np.clip(1 - np.hypot(xx, yy) / R, 0, 1) ** 1.6
    blit_mask(frame, glow, fx - n, fy - n, (250, 214, 136), a * (0.20 + 0.52 * p))
    x, y, spr = c.finish()
    blit_sprite(frame, spr, x, y, opacity=a, tint=pal["tint"])
    if dbg is not None:
        b = bbox_of(x, y, spr)
        dbg.append(("lamp", (b[0], min(b[1], fy - R * 0.8), b[2], b[3])))


def draw_path(frame, g, t, a, pal, near_y, dbg):
    cx = feat_x(g, t)
    c = Canvas((cx - 620, 700, cx + 620, H))
    road = (238, 229, 206, 255)
    for s in (-1, 1):
        c.polygon(ribbon(bezier((cx + s * 34, 1010), (cx + s * 70, 935), (cx + s * 215, 890),
                                (cx + s * 345, 770)), 132, 24), road)
    c.polygon(ribbon(bezier((cx, 1120), (cx, 1070), (cx, 1030), (cx, 980)), 250, 168), road)
    x, y, spr = c.finish()
    hill = np.clip(YS[y:y + spr.shape[0], None] - near_y[None, x:x + spr.shape[1]] - 0.5, 0, 1)
    spr *= hill[..., None]                                          # the road lies on the hill
    blit_sprite(frame, spr, x, y, opacity=a, tint=pal["tint"])
    if dbg is not None:
        dbg.append(("path", bbox_of(x, y, spr)))


LILIES = [(-335, 228, -12, 0.84, 0.0), (-165, 278, 8, 0.93, 1.9), (0, 318, -4, 1.0, 3.4),
          (170, 264, 12, 0.9, 4.6), (340, 220, -8, 0.82, 5.7)]


def draw_lilies(frame, g, t, a, pal, dbg):
    cx = feat_x(g, t)
    c = Canvas((cx - 480, 420, cx + 480, H))
    grow = smooth((t - g["t0"]) / g["T1"])      # they grow while the first verse is on screen
    for dx, full_h, lean, fs, ph in LILIES:
        x = cx + dx
        by = float(profile("near", g["wx"] + dx)) + 16
        hgt = full_h * (0.45 + 0.55 * grow)
        sway = 9 * math.sin(2 * math.pi * (t + ph) / 7.0) + 3 * math.sin(2 * math.pi * (t + ph) / 2.9)
        top = (x + lean + sway, by - hgt)
        stem = bezier((x, by + 6), (x - lean * 0.3, by - hgt * 0.4),
                      (x + lean * 1.2 + sway * 0.45, by - hgt * 0.7), top, n=40)
        ls = (0.7 + 0.3 * grow) * fs
        for frac, side in ((0.24, -1), (0.44, 1), (0.64, -1)):
            c.polygon(blade(stem[int(frac * 40)], side * 0.85 + sway * 0.006, 108 * ls, 27 * ls),
                      SAGE + (255,))
        c.line(stem, 9, SAGE_D + (255,))
        s = fs * (0.5 + 0.5 * grow)
        op = 0.72 + 0.28 * grow
        tilt = sway * 0.012
        c.polygon(blade((top[0], top[1] + 12 * s), tilt, 34 * s, 30 * s), SAGE_D + (255,))
        for ang in (-1.05, 1.05):
            c.polygon(blade(top, ang * op + tilt, 96 * s, 36 * s), GOLD_L + (255,))
        for ang in (-0.52, 0.52):
            c.polygon(blade(top, ang * op + tilt, 112 * s, 40 * s), (232, 214, 170, 255))
        c.polygon(blade(top, tilt, 118 * s, 42 * s), (244, 232, 200, 255))
        for ang in (-0.22, 0.0, 0.22):
            tip = (top[0] + math.sin(ang + tilt) * 74 * s, top[1] - math.cos(ang + tilt) * 74 * s)
            c.line([(top[0], top[1] - 20 * s), tip], 2.6 * s, GOLD + (255,))
            c.ellipse(tip[0], tip[1], 5.5 * s, 5.5 * s, fill=GOLD + (255,))
    x, y, spr = c.finish()
    blit_sprite(frame, spr, x, y, opacity=a, tint=pal["tint"])
    if dbg is not None:
        dbg.append(("lilies", bbox_of(x, y, spr)))


# flocks: (start, end, start x, y, size, speed px/s, [(dx, dy, scale, phase)])
_V = [(0, 0, 1.0, 0.0), (-78, 34, 0.82, 1.3), (-150, -22, 0.9, 2.6), (-236, 46, 0.72, 3.9),
      (-322, 6, 0.8, 5.0)]
_B = GROUP["birds"]
FLOCKS = [
    (T[2]["t0"] + 1, T[4]["end"], -80, 628, 22, 30, _V[:4]),               # far off, at dawn
    (_B["t0"], _B["end"], 560, 80, 50, 44, _V),                            # "Behold the fowls of the air"
    (T[31]["end"] - 4, T[34]["end"], -120, 600, 24, 30, _V),               # crossing the sunrise
]


def draw_birds(frame, t, pal, dbg):
    for t0, t1, x0, y0, size, speed, members in FLOCKS:
        if not (t0 <= t < t1):
            continue
        a = min(smooth(t - t0), smooth(t1 - t))
        u = t - t0
        c = Canvas((0, y0 - 90, W, y0 + 110))
        col = (104, 122, 138, 255)
        for dx, dy, sc, ph in members:
            w = size * sc
            x = x0 + dx * size / 50 + speed * u
            y = y0 + dy * size / 50 + 6 * math.sin(2 * math.pi * (u + ph * 2) / 8.0)
            lift = 0.55 + 0.38 * math.sin(2 * math.pi * (u + ph) / 2.6)     # slow wingbeats
            hgt = w * lift
            for sgn in (-1, 1):
                c.line(bezier((x, y), (x + sgn * 0.3 * w, y - hgt * 0.95),
                              (x + sgn * 0.72 * w, y - hgt * 0.9), (x + sgn * w, y - hgt * 0.25), n=20),
                       max(1.6, w * 0.13), col)
            c.ellipse(x, y + w * 0.02, w * 0.1, w * 0.085, fill=col)
        x, y, spr = c.finish()
        blit_sprite(frame, spr, x, y, opacity=a, tint=pal["tint"] * 0.5 + 0.5)
        if dbg is not None and size > 40:
            dbg.append(("birds", bbox_of(x, y, spr)))


# ---------------------------------------------------------------- one frame
_vig = {}


def vignette():
    if "v" not in _vig:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _vig["v"] = (1 - 0.13 * np.clip((d - 0.42) / 0.58, 0, 1) ** 2)[..., None]
    return _vig["v"]


def feature_alpha(g, t):
    return min(smooth(t - g["t0"]), smooth(g["end"] - t)) if g["t0"] <= t < g["end"] else 0.0


def render(t, dbg=None):
    pal = palette(t)
    # sky
    y = YS
    a = np.clip(y / 430, 0, 1)
    a = a * a * (3 - 2 * a)
    b = np.clip((y - 430) / 330, 0, 1)
    b = b * b * (3 - 2 * b)
    col = (pal["top"][None] * (1 - a[:, None]) + pal["mid"][None] * a[:, None]) * (1 - b[:, None]) \
        + pal["hor"][None] * b[:, None]
    frame = np.repeat(col[:, None, :], W, axis=1).astype(np.float32)
    draw_heavens(frame, t, pal, dbg)
    draw_clouds(frame, t, pal)
    draw_hill(frame, "far", t, pal)
    draw_hill(frame, "mid", t, pal)
    draw_trees(frame, t, pal, dbg)
    near_y = draw_hill(frame, "near", t, pal)
    for g in GROUPS:
        fa = feature_alpha(g, t)
        if fa <= 0:
            continue
        if g["name"] == "path":
            draw_path(frame, g, t, fa, pal, near_y, dbg)
        elif g["name"] == "coins":
            draw_coins(frame, g, t, fa, pal, dbg)
        elif g["name"] == "lamp":
            draw_lamp(frame, g, t, fa, pal, dbg)
        elif g["name"] == "lilies":
            draw_lilies(frame, g, t, fa, pal, dbg)
    draw_grass(frame, t, pal, near_y)
    draw_birds(frame, t, pal, dbg)
    draw_motes(frame, t, pal)
    frame *= vignette()

    # words
    for tm in TIMINGS.values():
        if not (tm["t0"] <= t < tm["end"]):
            continue
        card = tm["card"]
        u = t - tm["t0"]
        out = smooth((tm["end"] - t) / tm["fo"])
        veil = card["kind"] in VEIL_KINDS
        if veil:
            va = min(smooth(u / tm["fi"]), out) * 0.82
            frame *= 1 - va
            frame += va * rgb(*NAVY)
        items, _ = text_items(card["n"])
        stagger = min(0.24, 0.9 / max(1, len(items) - 1))
        halo_col = rgb(20, 28, 46) if card["n"] in DARK_SKY else rgb(*CREAM)
        alphas = [min(smooth((u - i * stagger) / 0.85), out) for i in range(len(items))]
        for it, al in zip(items, alphas):
            if it["halo"] is not None:
                blit_mask(frame, it["halo"], it["hx"], it["hy"], halo_col, al)
        for i, (it, al) in enumerate(zip(items, alphas)):
            rise = (1 - smooth((u - i * stagger) / 0.85)) * 16 - (1 - out) * 8   # drift up into place
            blit_mask(frame, it["mask"], it["x"], it["y"] + rise, it["color"], al)
    # open from, and close to, the cream background
    edge = min(smooth(t / 1.5), smooth((TOTAL - 1.4 - t) / 2.6 + 0.0) if t > TOTAL - 4.0 else 1.0)
    if edge < 1:
        frame = frame * edge + rgb(*CREAM) * (1 - edge)
    return np.clip(frame + 0.5, 0, 255).astype(np.uint8)


def frame_path(f):
    return os.path.join(FRAMES, "f_%06d.png" % f)


def render_chunk(args):
    start, stop = args
    for f in range(start, stop):
        Image.fromarray(render(f / FPS)).save(frame_path(f), compress_level=1)
    return stop - start


# ---------------------------------------------------------------- commands
def ffmpeg_bin():
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "imageio-ffmpeg"])
        import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def print_timing():
    print("font: %s" % FONT_NAME)
    print("hold scale k = %.4f   total = %.3f s (%d frames)" % (KSCALE, TOTAL, NFRAMES))
    for n, tm in TIMINGS.items():
        print("  card %2d  %-9s words %2d  start %7.2f  hold %5.2f" %
              (n, tm["card"]["kind"], n_words(tm["card"]), tm["t0"], tm["hold"]))


def overlaps(a, b, pad=18):
    return not (a[2] < b[0] - pad or a[0] > b[2] + pad or a[3] < b[1] - pad or a[1] > b[3] + pad)


def cmd_stills():
    print_timing()
    shutil.rmtree(STILLS, ignore_errors=True)
    os.makedirs(STILLS)
    problems = []
    for n, tm in TIMINGS.items():
        card = tm["card"]
        _, _, lines = layout(card)
        box = text_items(n)[1]
        print("card %2d | %s%s" % (n, " / ".join(lines), ("  ||  " + card["sub"]) if card["sub"] else ""))
        if box[0] < MARGIN or box[2] > W - MARGIN or box[1] < 40 or box[3] > H - 40:
            problems.append("card %d: text box %s outside margins" % (n, box))
        if any(len(l) > MAX_CHARS for l in lines):
            problems.append("card %d: line longer than %d chars" % (n, MAX_CHARS))
        if len(lines) > 1 and len(lines[-1].split()) == 1:
            problems.append("card %d: one word alone on last line" % n)
        for i, frac in enumerate((0.03, 0.5, 0.97)):   # start, middle and end of the card
            dbg = []
            img = render(tm["t0"] + (tm["end"] - tm["t0"]) * frac, dbg)
            if i == 1:
                Image.fromarray(img).save(os.path.join(STILLS, "card_%02d.png" % n))
            if card["kind"] in VEIL_KINDS:
                continue
            for name, b in dbg:
                if b is not None and overlaps(b, box):
                    problems.append("card %d: %s %s overlaps text %s (at %.0f%%)" %
                                    (n, name, tuple(int(v) for v in b), box, frac * 100))
    for s in range(0, len(CARDS), 4):
        sheet = Image.new("RGB", (W, H), (90, 90, 90))
        for j, card in enumerate(CARDS[s:s + 4]):
            im = Image.open(os.path.join(STILLS, "card_%02d.png" % card["n"]))
            im = im.resize((W // 2 - 6, H // 2 - 6), Image.LANCZOS)
            sheet.paste(im, ((j % 2) * W // 2 + 3, (j // 2) * H // 2 + 3))
        sheet.save(os.path.join(STILLS, "sheet_%02d.png" % (s // 4 + 1)))
    print("\nPROBLEMS:" if problems else "\nNo layout problems found.")
    for p in problems:
        print("  " + p)


def cmd_render():
    print_timing()
    shutil.rmtree(FRAMES, ignore_errors=True)
    os.makedirs(FRAMES)
    step = 60
    chunks = [(s, min(s + step, NFRAMES)) for s in range(0, NFRAMES, step)]
    done = 0
    with Pool(os.cpu_count()) as pool:
        for n in pool.imap_unordered(render_chunk, chunks):
            done += n
            if done % 600 < step:
                print("frames %d / %d" % (done, NFRAMES), flush=True)

    # sound: your own track if you put one next to this script, otherwise the synthesised score
    own = [os.path.join(HERE, "music" + e) for e in (".mp3", ".m4a", ".wav") if
           os.path.exists(os.path.join(HERE, "music" + e))]
    if own:
        audio = own[0]
        print("using your music:", audio)
    else:
        from music import make_music
        audio = os.path.join(FRAMES, "score.wav")
        moods = [(0, "day"), (T[22]["end"], "night"), (T[27]["t0"], "rise"), (T[30]["end"], "home")]
        chords, rms = make_music(TOTAL, moods, audio)
        print("score: %d chords, %.1f dB RMS" % (len(chords), rms))
    cmd = [ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS),
           "-i", os.path.join(FRAMES, "f_%06d.png"), "-stream_loop", "-1" if own else "0", "-i", audio,
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-af", "afade=t=in:d=3,afade=t=out:st=%.2f:d=6" % (TOTAL - 6.5),
           "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-t", "%.3f" % TOTAL,
           "-movflags", "+faststart", OUT]
    subprocess.check_call(cmd)
    if os.path.getsize(OUT) > 0:
        shutil.rmtree(FRAMES)
    print("wrote", OUT)


if __name__ == "__main__":
    {"stills": cmd_stills, "render": cmd_render}[sys.argv[1] if len(sys.argv) > 1 else "stills"]()
