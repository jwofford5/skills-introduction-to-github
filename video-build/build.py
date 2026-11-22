#!/usr/bin/env python3
"""Build "One Master and the Freedom from Worry".

The words lead. They arrive one at a time on warm paper, the key word of each line in gold,
and each picture is fine ink line or light called up by the line on screen: a heart drawn
toward a point of gold, light filling the page, one line splitting in two, a worry that
loops until it is named. Every frame is drawn with Pillow/numpy and encoded with ffmpeg;
the music is synthesised in music.py (put your own video-build/music.mp3, .m4a or .wav
next to this file to use that instead).

Usage:
    python3 build.py stills   # stills of every card + layout checks (video-build/stills)
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
from PIL import Image, ImageDraw, ImageFont

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
VEIL_KINDS = ("title", "section", "word")     # the page turns navy for these
DARK_CARDS = (24, 25, 26, 28, 29)             # night and the hour before dawn: cream text
FEATURES = ()

# The word (or words) each picture grows from; shown in gold.
EMPHASIS = {3: ["one"], 6: ["treasure", "heart"], 7: ["treasure", "heart"], 8: ["light"],
            10: ["two"], 11: ["one"], 15: ["fowls"], 16: ["birds"], 18: ["lilies"],
            19: ["glory"], 20: ["grass"], 23: ["Planning"], 24: ["Worry", "again"], 25: ["stop"],
            26: ["Hand"], 28: ["first"], 29: ["added"], 31: ["day"], 32: ["grace"],
            33: ["today's"], 34: ["freedom"]}

# Vertical band the words may occupy on cards that have a drawing beneath (or birds above).
_LOW = (60, 650)
ZONES = {6: _LOW, 7: _LOW, 10: _LOW, 11: _LOW, 15: (200, 690), 16: (220, 900),
         18: (40, 590), 19: (40, 590), 20: (40, 590), 23: _LOW, 24: _LOW, 25: _LOW, 26: _LOW,
         28: _LOW, 29: _LOW, 31: _LOW, 32: _LOW, 33: _LOW, 34: _LOW, 35: _LOW}


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
    """Returns ([(line, font, colour, baseline_y)], rule_y or None, lines)."""
    kind = card["kind"]
    veil = kind in VEIL_KINDS
    dark = veil or card["n"] in DARK_CARDS
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
    z0, z1 = ZONES.get(card["n"], (110, 930))
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


def text_words(n):
    """One mask per word for card n, in reading order: list of dicts, and the text bbox."""
    if n in _text_cache:
        return _text_cache[n]
    card = CARDS[n - 1]
    items, rule, lines = layout(card)
    dark = card["kind"] in VEIL_KINDS or n in DARK_CARDS
    key = [k.lower() for k in EMPHASIS.get(n, [])]
    out, boxes = [], []

    def add(draw_fn, col):
        img = Image.new("L", (W, H), 0)
        draw_fn(ImageDraw.Draw(img))
        box = img.getbbox()
        boxes.append(box)
        out.append(dict(x=box[0], y=box[1], mask=np.asarray(img.crop(box), np.float32) / 255.0,
                        color=np.array(col, np.float32)))

    for li, (s, f, col, y) in enumerate(items):
        is_sub = card["sub"] and li == len(items) - 1
        if is_sub and rule:
            add(lambda d: d.line([(W / 2 - 90, rule), (W / 2 + 90, rule)], fill=255, width=3), GOLD_L)
        x0 = W / 2 - f.getlength(s) / 2
        words = s.split(" ")
        for wi, w in enumerate(words):
            px = x0 + f.getlength(" ".join(words[:wi]) + (" " if wi else ""))
            c = col
            if not is_sub and w.strip('".,;:').lower() in key:
                c = GOLD_L if dark else GOLD       # the word the picture grows from
            add(lambda d, w=w, px=px: d.text((px, y), w, font=f, fill=255, anchor="ls"), c)
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


SS = 3  # supersampling for line work


class Ink:
    """A supersampled canvas for fine line drawing over a region of the frame."""

    def __init__(self, region=(200, 600, 1720, 1080)):
        self.x0, self.y0, self.x1, self.y1 = region
        self.img = Image.new("RGBA", ((self.x1 - self.x0) * SS, (self.y1 - self.y0) * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, p):
        return ((p[0] - self.x0) * SS, (p[1] - self.y0) * SS)

    def line(self, pts, width, col, p=1.0):
        """Draw the first fraction p of a polyline, so lines can draw themselves."""
        if p <= 0 or len(pts) < 2:
            return
        n = max(2, int(round(len(pts) * min(1.0, p))))
        q = [self.P(a) for a in pts[:n]]
        w = max(1, round(width * SS))
        self.d.line(q, fill=col + (255,), width=w, joint="curve")
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=col + (255,))

    def fill(self, pts, col):
        self.d.polygon([self.P(a) for a in pts], fill=col + (255,))

    def dot(self, x, y, r, col):
        a = self.P((x, y))
        self.d.ellipse([a[0] - r * SS, a[1] - r * SS, a[0] + r * SS, a[1] + r * SS], fill=col + (255,))

    def put(self, frame, opacity=1.0, dbg=None, name=""):
        size = (self.x1 - self.x0, self.y1 - self.y0)
        arr = np.asarray(self.img.convert("RGBa").resize(size, Image.LANCZOS), np.float32)
        a = arr[..., 3:] / 255.0 * opacity
        reg = frame[self.y0:self.y1, self.x0:self.x1]
        reg *= 1 - a
        reg += arr[..., :3] * opacity
        if dbg is not None:
            ys, xs = np.where(arr[..., 3] > 20)
            if len(xs):
                dbg.append((name, (self.x0 + xs.min(), self.y0 + ys.min(),
                                   self.x0 + xs.max(), self.y0 + ys.max())))


def bezier(p0, p1, p2, p3, n=60):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def blade(base, angle, length, width, n=24):
    """Closed outline of a leaf or petal, pointed at both ends (angle 0 = straight up)."""
    ca, sa = math.cos(angle), math.sin(angle)
    a, b = [], []
    for i in range(n + 1):
        t = i / n
        hw = width / 2 * math.sin(math.pi * t ** 0.8) ** 0.9
        for side, lst in ((1, a), (-1, b)):
            lx, ly = side * hw, -t * length
            lst.append((base[0] + lx * ca - ly * sa, base[1] + lx * sa + ly * ca))
    return a + b[::-1] + [a[0]]


def circle(cx, cy, r, n=90, start=-math.pi / 2):
    return [(cx + r * math.cos(start + 2 * math.pi * i / n), cy + r * math.sin(start + 2 * math.pi * i / n))
            for i in range(n + 1)]


_kernels = {}


def dot(r):
    key = round(r * 2) / 2
    if key not in _kernels:
        n = int(math.ceil(key * 3))
        y, x = np.mgrid[-n:n + 1, -n:n + 1].astype(np.float32)
        _kernels[key] = np.exp(-(x * x + y * y) / (2 * (key * 0.8) ** 2)).astype(np.float32)
    return _kernels[key]


def glow(frame, x, y, r, col, opacity):
    k = dot(r)
    n = k.shape[0] // 2
    blit_mask(frame, k, x - n, y - n, col, opacity)


def prog(t, start, dur):
    return min(1.0, max(0.0, (t - start) / dur))


# ---------------------------------------------------------------- the paper and its light
def rgb(*v):
    return np.array(v, np.float32)


#            top of page          middle              foot of page
STATES = {
    "paper":     (rgb(243, 238, 228), rgb(246, 240, 228), rgb(246, 236, 216)),
    "dawn":      (rgb(236, 230, 224), rgb(246, 238, 226), rgb(250, 226, 200)),
    "afternoon": (rgb(242, 234, 216), rgb(246, 232, 206), rgb(246, 216, 172)),
    "night":     (rgb(16, 24, 42),    rgb(26, 38, 60),    rgb(40, 54, 80)),
    "predawn":   (rgb(22, 32, 56),    rgb(48, 54, 86),    rgb(190, 132, 112)),
    "sunrise":   (rgb(238, 232, 226), rgb(248, 234, 208), rgb(252, 208, 150)),
    "morning":   (rgb(244, 240, 230), rgb(248, 242, 230), rgb(252, 238, 208)),
}
KEYS = [(0, "dawn"), (T[4]["end"], "dawn"), (T[5]["end"], "paper"),
        (T[22]["t0"], "paper"), (T[22]["end"], "afternoon"),
        (T[23]["end"] - 3.0, "afternoon"), (T[24]["t0"] + 1.5, "night"),
        (T[27]["t0"], "night"), (T[27]["end"], "predawn"),
        (T[30]["t0"], "predawn"), (T[30]["end"], "sunrise"),
        (T[33]["end"], "sunrise"), (T[34]["t0"] + 3.0, "morning"), (TOTAL + 1, "morning")]


def weights(t):
    for (ta, a), (tb, b) in zip(KEYS, KEYS[1:]):
        if ta <= t < tb:
            w = smooth((t - ta) / (tb - ta))
            return {a: 1.0} if a == b else {a: 1 - w, b: w}
    return {KEYS[-1][1]: 1.0}


LW, LH = W // 4, H // 4
LX = (np.arange(LW, dtype=np.float32) + 0.5) * 4
LY = (np.arange(LH, dtype=np.float32) + 0.5) * 4
_static = {}


def static():
    if not _static:
        y, x = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
        _static["vig"] = (1 - 0.10 * np.clip((d - 0.42) / 0.58, 0, 1) ** 2)[..., None]
        g = np.random.default_rng(3).normal(0, 1.0, (H, W)).astype(np.float32)
        _static["grain"] = (g * 1.5)[..., None]          # paper tooth; also stops banding
    return _static


def sun_y(t):
    a, b = T[31]["t0"], T[33]["end"]
    return 985 - 150 * prog(t, a, b - a) - 30 * prog(t, b, TOTAL - b)


HORIZON = 905


def background(t):
    ws = weights(t)
    top, mid, foot = (sum(STATES[s][i] * w for s, w in ws.items()) for i in range(3))
    a = np.clip(LY / 430, 0, 1)
    a = (a * a * (3 - 2 * a))[:, None]
    b = np.clip((LY - 430) / 520, 0, 1)
    b = (b * b * (3 - 2 * b))[:, None]
    col = (top[None] * (1 - a) + mid[None] * a) * (1 - b) + foot[None] * b
    small = np.repeat(col[:, None, :], LW, axis=1).astype(np.float32)
    xx, yy = LX[None, :], LY[:, None]

    def wash(cx, cy, r, colour, alpha):
        if alpha <= 0.003:
            return
        m = (np.clip(1 - np.hypot(xx - cx, yy - cy) / r, 0, 1) ** 1.7 * alpha)[..., None]
        small[:] = small * (1 - m) + colour * m

    # slow drifting light: the page is never quite still
    lift = mid + (rgb(255, 252, 244) - mid) * 0.5
    for i, (px, py, sp) in enumerate(((0.30, 0.35, 0.021), (0.72, 0.55, 0.017), (0.5, 0.8, 0.013))):
        wash(W * (px + 0.16 * math.sin(sp * t * 2 * math.pi + i * 2.1)),
             H * (py + 0.12 * math.cos(sp * 1.3 * t * 2 * math.pi + i)), 720, lift, 0.34)
    # "thy whole body shall be full of light"
    lb = smooth(prog(t, T[8]["t0"] + 1.2, T[8]["hold"] * 0.9)) * smooth((T[9]["end"] - t) / 2.5)
    wash(960, 400, 420 + 1100 * lb, rgb(255, 238, 190), 0.78 * lb)
    # the treasure: a point of gold
    tr = smooth(prog(t, T[6]["t0"] + 0.8, 1.6)) * smooth((T[7]["end"] - t) / 1.2)
    wash(TREASURE[0], TREASURE[1], 190 + 60 * prog(t, T[7]["t0"], T[7]["end"] - T[7]["t0"]),
         rgb(246, 208, 120), 0.55 * tr)
    # "seek ye first": one light
    sk = smooth(prog(t, T[28]["t0"] + 0.8, 2.5)) * smooth((T[29]["end"] - t) / 1.2)
    wash(seek_x(t), 850, 210, rgb(246, 214, 150), 0.42 * sk)
    # the sun, behind the horizon line
    sw = ws.get("sunrise", 0) + ws.get("morning", 0)
    if sw > 0.01:
        sy = sun_y(t)
        m = np.clip(1 - np.hypot(xx - 960, yy - sy) / 760, 0, 1) ** 2 * 0.62 * sw
        m = (m * np.clip((HORIZON + 40 - yy) / 80, 0, 1))[..., None]
        small[:] = small * (1 - m) + rgb(255, 226, 160) * m
    chans = [np.asarray(Image.fromarray(small[..., c]).resize((W, H), Image.BICUBIC)) for c in range(3)]
    frame = np.stack(chans, axis=-1).astype(np.float32)
    if sw > 0.01:   # the disc itself, sharp, and only above the horizon
        sy = sun_y(t)
        y0, y1 = max(0, int(sy - 90)), HORIZON
        if y1 > y0:
            d = np.hypot(np.arange(840, 1080, dtype=np.float32)[None, :] - 960,
                         np.arange(y0, y1, dtype=np.float32)[:, None] - sy)
            m = (np.clip(84 - d + 0.5, 0, 1) * sw)[..., None]
            reg = frame[y0:y1, 840:1080]
            reg *= 1 - m
            reg += m * rgb(255, 242, 200)
    return frame, ws


TREASURE = (1210, 850)


def seek_x(t):
    return 960 + 110 * smooth(prog(t, T[29]["t0"] + 1, T[29]["hold"]))


# ---------------------------------------------------------------- pictures the words call up
INK = (132, 104, 52)       # gold-brown ink on paper
INK_SOFT = (176, 150, 100)
NIGHT_INK = (206, 212, 226)
_rs = random.Random(5)
STARS = [(_rs.uniform(0, W), _rs.uniform(0, 1000), _rs.uniform(1.0, 2.2), _rs.uniform(0, 6.28),
          _rs.uniform(0.4, 1.1)) for _ in range(110)]
GRASS = [(960 + _rs.uniform(-470, 470), _rs.uniform(20, 52), _rs.uniform(-0.35, 0.35), _rs.uniform(0, 1))
         for _ in range(64)]
_moon = {}


def fade(t, a, b, d=1.2):
    return min(smooth((t - a) / d), smooth((b - t) / d)) if a <= t < b else 0.0


def g_heart(frame, t, dbg):
    """6-7: the heart is drawn, then is pulled across to the treasure."""
    a = fade(t, T[6]["t0"], T[7]["end"])
    if a <= 0:
        return
    pull = smooth(prog(t, T[7]["t0"] + 1.6, T[7]["hold"] * 0.85))
    cx = 760 + (TREASURE[0] - 760) * pull
    cy, s = 850, 4.4
    pts = []
    for i in range(121):
        th = math.pi + 2 * math.pi * i / 120
        pts.append((cx + s * 16 * math.sin(th) ** 3,
                    cy - s * (13 * math.cos(th) - 5 * math.cos(2 * th) - 2 * math.cos(3 * th) - math.cos(4 * th))))
    ink = Ink()
    ink.line(pts, 3.2, INK, prog(t, T[6]["t0"] + 2.0, 3.0))
    ink.put(frame, a, dbg, "heart")


def g_fork(frame, t, dbg):
    """10-11: one road becomes two; then only one remains."""
    a = fade(t, T[10]["t0"], T[11]["end"])
    if a <= 0:
        return
    u = t - T[10]["t0"]
    stem = [(960, 1070 - i * 8.5) for i in range(21)]
    left = bezier((960, 900), (960, 845), (890, 800), (770, 715))
    right = bezier((960, 900), (960, 845), (1030, 800), (1150, 715))
    gone = smooth(prog(t, T[11]["t0"] + 1 + T[11]["hold"] * 0.45, 3.0))
    ink = Ink()
    ink.line(stem, 3.6, INK, prog(u, 1.0, 1.6))
    ink.line(left, 3.6, INK, prog(u, 2.6, 2.6))
    ink.put(frame, a, dbg, "fork")
    ink = Ink()
    ink.line(right, 3.6, INK, prog(u, 2.6, 2.6))
    ink.put(frame, a * (1 - gone), dbg, "fork")


def g_birds(frame, t, dbg):
    """15-16: birds, gliding. No flapping."""
    a = fade(t, T[15]["t0"], T[16]["end"], 1.5)
    if a <= 0:
        return
    u = t - T[15]["t0"]
    ink = Ink((0, 20, W, 200))
    for dx, dy, w in ((0, 0, 38), (-92, 26, 30), (-186, -8, 34), (-284, 34, 27), (-380, 10, 29)):
        x = 760 + dx + 20 * u
        y = 112 + dy - 0.5 * u + 3 * math.sin(u * 0.4 + dx)
        for sgn in (-1, 1):
            ink.line(bezier((x, y), (x + sgn * 0.35 * w, y - 0.42 * w), (x + sgn * 0.75 * w, y - 0.40 * w),
                            (x + sgn * w, y - 0.12 * w), n=16), 2.6, (96, 108, 122))
    ink.put(frame, a * 0.9, dbg, "birds")


LILIES = [(-230, 262, -16, 0.9, 0.0, 0.0), (0, 322, 6, 1.0, 2.3, 1.2), (236, 246, 18, 0.86, 4.1, 2.2)]


def g_lilies(frame, t, dbg):
    """18-20: the lilies draw themselves upward; Solomon's glory; then the grass."""
    a = fade(t, T[18]["t0"], T[20]["end"])
    if a <= 0:
        return
    u = t - T[18]["t0"]
    span = T[18]["hold"]
    glory = smooth(prog(t, T[19]["t0"] + 1.0, 4.0))
    lines, fills = Ink((300, 560, 1620, 1080)), Ink((300, 560, 1620, 1080))
    base = 1052
    for dx, hgt, lean, s, ph, delay in LILIES:
        x = 960 + dx
        sway = 5 * math.sin(2 * math.pi * (t + ph) / 9.0)
        top = (x + lean + sway, base - hgt)
        stem = bezier((x, base), (x - lean * 0.3, base - hgt * 0.4),
                      (x + lean * 1.2 + sway * 0.5, base - hgt * 0.7), top, n=60)
        sp = prog(u, 0.8 + delay, span * 0.42)
        lines.line(stem, 3.4, (104, 128, 100), sp)
        for frac, side in ((0.28, -1), (0.5, 1)):
            lp = prog(sp, frac, 0.3)
            lines.line(blade(stem[int(frac * 60)], side * 0.9, 96 * s, 25 * s), 2.6, (124, 146, 118), lp)
        tilt = sway * 0.01
        petals = [(-1.02, 82, 31), (1.02, 82, 31), (-0.5, 100, 35), (0.5, 100, 35), (0.0, 108, 37)]
        for i, (ang, ln, wd) in enumerate(petals):
            shape = blade(top, ang + tilt, ln * s, wd * s)
            pp = prog(u, 0.8 + delay + span * 0.40 + i * 0.35, span * 0.24)
            if glory > 0 and pp >= 1:
                fills.fill(shape, (236, 208, 136))
            lines.line(shape, 2.8, INK, pp)
        for ang in (-0.2, 0.0, 0.2):
            tip = (top[0] + math.sin(ang + tilt) * 62 * s, top[1] - math.cos(ang + tilt) * 62 * s)
            pp = prog(u, 0.8 + delay + span * 0.72, 1.5)
            lines.line([(top[0], top[1] - 14 * s), tip], 2.0, INK, pp)
            if pp >= 1:
                lines.dot(tip[0], tip[1], 4 * s, INK)
    for i, (gx, ln, ang, r) in enumerate(GRASS):    # "if God clothes the grass that way"
        gp = prog(t, T[20]["t0"] + 0.8 + r * 3.0, 1.4)
        bend = ang + 0.07 * math.sin(t * 0.8 + gx * 0.02)
        lines.line(bezier((gx, base + 6), (gx, base - ln * 0.4), (gx + bend * ln * 0.5, base - ln * 0.8),
                          (gx + bend * ln, base - ln), n=10), 2.2, (124, 146, 118), gp)
    fills.put(frame, a * glory * 0.55)
    lines.put(frame, a, dbg, "lilies")


def g_plan(frame, t, dbg):
    """23: planning -- a straight line, marked off evenly."""
    a = fade(t, T[23]["t0"], T[23]["end"] - 0.8)
    if a <= 0:
        return
    u = t - T[23]["t0"]
    p = prog(u, 1.2, 5.5)
    ink = Ink()
    ink.line([(540 + i * 8.4, 850) for i in range(101)], 3.2, INK, p)
    for i in range(8):
        x = 540 + i * 120
        tp = prog(p, i / 7 * 0.99, 0.04)
        ink.line([(x, 850), (x, 850 - 22 * tp)], 3.0, INK, 1 if tp else 0)
    ink.put(frame, a, dbg, "plan")


def loop_stop():
    return T[25]["t0"] + 2.0


def g_loop(frame, t, dbg):
    """24-26: worry goes round and round; it stops when it is named; then it is handed over."""
    a = fade(t, T[24]["t0"], T[26]["end"])
    if a <= 0:
        return
    start = T[24]["t0"] + 1.0
    th_max = 2 * math.pi * (min(t, loop_stop()) - start) / 3.4
    give = smooth(prog(t, T[26]["t0"] + 1.0 + T[26]["hold"] * 0.35, T[26]["hold"] * 0.6))
    cy = 860 - 190 * give
    pts, th = [], 0.0
    while th < th_max:
        pts.append((960 + (165 + 24 * math.sin(2.3 * th + 1)) * math.cos(th),
                    cy + (60 + 13 * math.sin(3.1 * th)) * math.sin(th) + 7 * math.sin(0.5 * th)))
        th += 0.05
    ink = Ink((200, 560, 1720, 1080))
    ink.line(pts, 2.6, NIGHT_INK)
    ink.put(frame, a * 0.8 * (1 - give), dbg if give < 0.5 else None, "loop")


def g_seek(frame, t, dbg):
    """28-29: one thing first; the rest come along behind it."""
    a = fade(t, T[28]["t0"], T[29]["end"])
    if a <= 0:
        return
    u = t - T[28]["t0"]
    x = seek_x(t)
    ink = Ink()
    ink.line(circle(x, 850, 50), 3.4, (228, 196, 128), prog(u, 1.0, 2.6))
    follow = smooth(prog(t, T[29]["t0"] + 1.0, T[29]["hold"] * 0.8))
    appear = prog(t, T[29]["t0"] + 0.6, 1.6)
    for i, (off, r, start) in enumerate(((-118, 17, 520), (-176, 12, 430), (-222, 9, 350))):
        sx = start + (x + off - start) * follow
        ink.line(circle(sx, 850 + 10 * math.sin(t * 0.5 + i) * (1 - follow), r, n=40), 2.6,
                 (206, 186, 140), appear)
    ink.put(frame, a, dbg, "seek")


def g_horizon(frame, t, dbg):
    """31-35: a horizon for the sun to rise over."""
    a = fade(t, T[31]["t0"], TOTAL)
    if a <= 0:
        return
    ink = Ink((200, HORIZON - 10, 1720, HORIZON + 10))
    ink.line([(320 + i * 12.8, HORIZON) for i in range(101)], 2.6, INK, smooth(prog(t, T[31]["t0"] + 0.4, 4.0)))
    ink.put(frame, a * 0.85)
    if dbg is not None:
        dbg.append(("sun", (876, sun_y(t) - 84, 1044, HORIZON)))


def g_night(frame, t, ws, dbg):
    night = ws.get("night", 0) + 0.5 * ws.get("predawn", 0)
    if night > 0.01:
        for x, y, r, ph, sp in STARS:
            glow(frame, x, y, r, (232, 232, 220), night * (0.5 + 0.35 * math.sin(t * 0.6 * sp + ph)))
    mw = min(1.0, max(0.0, (ws.get("night", 0) - 0.75) * 4))
    if mw > 0.01:
        if not _moon:
            img = Image.new("L", (720, 720), 0)
            d = ImageDraw.Draw(img)
            d.ellipse([112, 112, 608, 608], fill=255)
            d.ellipse([240, 40, 704, 504], fill=0)
            _moon["m"] = np.asarray(img.resize((180, 180), Image.LANCZOS), np.float32) / 255.0
        p = prog(t, T[24]["t0"], T[26]["end"] - T[24]["t0"])
        mx, my = 1650 + 30 * p, 210 - 30 * p
        glow(frame, mx, my, 70, (140, 152, 186), 0.28 * mw)
        blit_mask(frame, _moon["m"], mx - 90, my - 90, (238, 228, 190), mw)
        if dbg is not None:
            dbg.append(("moon", (mx - 62, my - 62, mx + 62, my + 62)))


GESTURES = [g_heart, g_fork, g_birds, g_lilies, g_plan, g_loop, g_seek, g_horizon]


# ---------------------------------------------------------------- one frame
def render(t, dbg=None):
    frame, ws = background(t)
    st = static()
    frame += st["grain"]
    g_night(frame, t, ws, dbg)
    for g in GESTURES:
        g(frame, t, dbg)
    frame *= st["vig"]
    for tm in TIMINGS.values():
        if not (tm["t0"] <= t < tm["end"]):
            continue
        card = tm["card"]
        u = t - tm["t0"]
        out = smooth((tm["end"] - t) / tm["fo"])
        if card["kind"] in VEIL_KINDS:      # the page itself turns navy for a title
            va = min(smooth(u / tm["fi"]), out) * 0.93
            frame *= 1 - va
            frame += va * rgb(*NAVY)
        words, _ = text_words(card["n"])
        dt = min(0.15, 2.2 / max(1, len(words)))     # the words arrive one at a time
        drift = -9 * (u / (tm["end"] - tm["t0"]) - 0.5)
        for i, wd in enumerate(words):
            sin_ = smooth((u - i * dt) / 0.55)
            blit_mask(frame, wd["mask"], wd["x"], wd["y"] + drift + (1 - sin_) * 12 - (1 - out) * 6,
                      wd["color"], min(sin_, out))
    edge = min(smooth(t / 1.5), smooth((TOTAL - 1.4 - t) / 2.6) if t > TOTAL - 4.0 else 1.0)
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


def overlaps(a, b, pad=20):
    return not (a[2] < b[0] - pad or a[0] > b[2] + pad or a[3] < b[1] - pad or a[1] > b[3] + pad)


def cmd_stills():
    print_timing()
    shutil.rmtree(STILLS, ignore_errors=True)
    os.makedirs(STILLS)
    problems = []
    for n, tm in TIMINGS.items():
        card = tm["card"]
        _, _, lines = layout(card)
        box = text_words(n)[1]
        print("card %2d | %s%s" % (n, " / ".join(lines), ("  ||  " + card["sub"]) if card["sub"] else ""))
        if box[0] < MARGIN or box[2] > W - MARGIN or box[1] < 40 or box[3] > H - 40:
            problems.append("card %d: text box %s outside margins" % (n, box))
        if any(len(l) > MAX_CHARS for l in lines):
            problems.append("card %d: line longer than %d chars" % (n, MAX_CHARS))
        if len(lines) > 1 and len(lines[-1].split()) == 1:
            problems.append("card %d: one word alone on last line" % n)
        for i, frac in enumerate((0.12, 0.5, 0.75, 0.93)):
            dbg = []
            img = render(tm["t0"] + (tm["end"] - tm["t0"]) * frac, dbg)
            if frac in (0.5, 0.93):
                Image.fromarray(img).save(os.path.join(STILLS, "card_%02d%s.png" % (n, "" if i == 1 else "b")))
            if card["kind"] in VEIL_KINDS:
                continue
            for name, b in dbg:
                if overlaps(b, box):
                    problems.append("card %d: %s %s overlaps text %s (at %.0f%%)" %
                                    (n, name, tuple(int(v) for v in b), box, frac * 100))
    for suffix in ("", "b"):
        for s in range(0, len(CARDS), 6):
            sheet = Image.new("RGB", (W, 720), (90, 90, 90))
            for j, card in enumerate(CARDS[s:s + 6]):
                im = Image.open(os.path.join(STILLS, "card_%02d%s.png" % (card["n"], suffix)))
                sheet.paste(im.resize((636, 356), Image.LANCZOS), ((j % 3) * 640 + 2, (j // 3) * 360 + 2))
            sheet.save(os.path.join(STILLS, "sheet%s_%02d.png" % (suffix, s // 6 + 1)))
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
           "-c:v", "libx264", "-preset", "slow", "-crf", "23", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-t", "%.3f" % TOTAL,
           "-movflags", "+faststart", OUT]
    subprocess.check_call(cmd)
    if os.path.getsize(OUT) > 0:
        shutil.rmtree(FRAMES)
    print("wrote", OUT)


if __name__ == "__main__":
    {"stills": cmd_stills, "render": cmd_render}[sys.argv[1] if len(sys.argv) > 1 else "stills"]()
