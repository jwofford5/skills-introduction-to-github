#!/usr/bin/env python3
"""Build "One Master and the Freedom from Worry" -- a silent text-card video.

Usage:
    python3 build.py stills   # one still per card + layout checks (video-build/stills)
    python3 build.py render   # full render -> ../one-master-freedom-from-worry.mp4

Every frame is drawn with Pillow and encoded with ffmpeg.
"""
import math
import os
import shutil
import subprocess
import sys
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFont

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
SAGE_L = (182, 196, 174)

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
        C(2, "body", "Mom, I made this for you. It comes from a sermon I wrote on Matthew 6."),
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
                      "is paying attention."),
        C(35, "closing", "I love you, Mom.", "Josh"),
    ],
]
CARDS = [c for s in SECTIONS for c in s]

# Hand-set line breaks where the automatic balancing reads awkwardly.
LINE_BREAKS = {18: ['"Consider the lilies of the field,', 'how they grow; they toil not,',
                    'neither do they spin."']}

# Vertical band the text may occupy, per illustration (illustrations stay outside it).
TEXT_ZONE = {None: (0, H), "coins": (70, 780), "lamp": (70, 640), "path": (70, 720),
             "birds": (260, 1030), "lilies": (70, 590), "moon": (70, 720), "sun": (70, 610)}


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
    """Returns (card timings, illustration groups, total seconds)."""
    t = 0.5
    timings, groups = [], []
    for si, sec in enumerate(SECTIONS):
        if si:
            t += 1.0  # plain background between sections
        for card in sec:
            fo = 2.5 if card["kind"] == "closing" else 1.0
            tm = dict(card=card, t0=t, fi=1.0, hold=hold_for(card, k), fo=fo)
            tm["end"] = t + tm["fi"] + tm["hold"] + fo
            timings.append(tm)
            if card["illus"]:
                if card["keep"]:
                    groups[-1]["end"] = tm["end"]
                else:
                    groups.append(dict(name=card["illus"], t0=t, end=tm["end"],
                                       T1=tm["fi"] + tm["hold"]))
            t = tm["end"]
    return timings, groups, t + 1.5


def solve_timeline():
    full = build_timeline(1.0)
    if full[2] <= TARGET_SECONDS:
        return full + (1.0,)
    lo, hi = 0.3, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if build_timeline(mid)[2] > TARGET_SECONDS:
            hi = mid
        else:
            lo = mid
    return build_timeline(lo) + (lo,)


def frame_spec(f, timings, groups):
    """What is on screen at frame f."""
    t = f / FPS
    spec = dict(card=None, a=0.0, illus=None, ia=0.0, it=0.0, D=1.0, T1=1.0)
    for tm in timings:
        if tm["t0"] <= t < tm["end"]:
            a_in = smooth((t - tm["t0"]) / tm["fi"])
            a_out = smooth((tm["end"] - t) / tm["fo"])
            spec["card"], spec["a"] = tm["card"]["n"], round(min(a_in, a_out), 4)
            break
    for g in groups:
        if g["t0"] <= t < g["end"]:
            ia = min(smooth(t - g["t0"]), smooth(g["end"] - t))
            spec.update(illus=g["name"], ia=round(ia, 4), it=t - g["t0"],
                        D=g["end"] - g["t0"], T1=g["T1"])
            break
    return spec


# ---------------------------------------------------------------- backgrounds
def make_bg(color, strength):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    v = np.clip((d - 0.42) / 0.58, 0, 1) ** 2
    return np.array(color, np.float32)[None, None, :] * (1 - strength * v)[..., None]


_bg = {}


def bg(name):
    if name not in _bg:
        _bg[name] = make_bg(CREAM, 0.075) if name == "cream" else make_bg(NAVY, 0.30)
    return _bg[name]


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
    if len(lines) > 1 and len(lines[-1].split()) == 1:  # try one more line instead
        best.clear()
        alt = solve(0, minl[0] + 1)[1]
        lines = alt or lines
    assert " ".join(lines) == " ".join(words)
    return lines


def layout(card):
    """Returns list of (string, font, color, baseline_y) plus optional rule position."""
    kind = card["kind"]
    navy = kind in ("title", "section", "word")
    main_col = CREAM if navy else BROWN
    size = {"title": SZ_TITLE, "section": SZ_TITLE, "word": SZ_WORD, "body": SZ_BODY,
            "scripture": SZ_SCRIPTURE, "closing": SZ_CLOSING}[kind]
    f_main = font(kind == "scripture", size)
    lines = LINE_BREAKS.get(card["n"]) or wrap(card["text"], f_main)
    assert " ".join(lines) == card["text"]
    lh = round(size * (1.2 if navy else 1.34))
    asc, desc = f_main.getmetrics()
    height = asc + (len(lines) - 1) * lh + desc * 0.6
    sub = card["sub"]
    if sub:
        sub_size = SZ_REF if kind == "scripture" else SZ_SMALL
        f_sub = font(False, sub_size)
        sub_col = BROWN if kind == "closing" else GOLD
        gap = {"scripture": 0.62, "title": 1.05, "closing": 0.75}[kind] * size
        s_asc, s_desc = f_sub.getmetrics()
        height += gap - desc * 0.6 + s_asc + s_desc * 0.6
    z0, z1 = TEXT_ZONE[card["illus"]]
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


def text_layer(n):
    """Cropped float RGBA layer for card n: (x0, y0, rgb, alpha)."""
    if n not in _text_cache:
        card = CARDS[n - 1]
        items, rule, _ = layout(card)
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        for s, f, col, y in items:
            d.text((W / 2, y), s, font=f, fill=col + (255,), anchor="ms")
        if rule:
            d.line([(W / 2 - 90, rule), (W / 2 + 90, rule)], fill=GOLD + (255,), width=3)
        box = img.getbbox()
        arr = np.asarray(img.crop(box), np.float32)
        _text_cache[n] = (box[0], box[1], arr[..., :3], arr[..., 3:] / 255.0, box)
    return _text_cache[n]


# ---------------------------------------------------------------- drawing kit
SS = 3  # supersampling for illustrations


class Canvas:
    """Supersampled RGBA canvas over a region of the frame, in frame coordinates."""

    def __init__(self, region, k=1.0, pivot=(W / 2, H), shift=(0, 0)):
        self.x0, self.y0, self.x1, self.y1 = region
        self.k, self.pivot, self.shift = k, pivot, shift
        self.img = Image.new("RGBA", ((self.x1 - self.x0) * SS, (self.y1 - self.y0) * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def P(self, p):
        x = (p[0] - self.pivot[0]) * self.k + self.pivot[0] + self.shift[0]
        y = (p[1] - self.pivot[1]) * self.k + self.pivot[1] + self.shift[1]
        return ((x - self.x0) * SS, (y - self.y0) * SS)

    def L(self, r):
        return r * self.k * SS

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
        size = (self.x1 - self.x0, self.y1 - self.y0)
        return self.img.convert("RGBa").resize(size, Image.LANCZOS).convert("RGBA")


def bezier(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n
        a, b, c, d = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


def smooth_closed(pts, n=14):
    """Closed Catmull-Rom curve through pts."""
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
    """Polygon around a centre line whose width goes from w0 to w1."""
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


def blade(base, angle, length, width, n=18):
    """Leaf / petal: pointed at both ends, starting at base, pointing along angle (0 = up)."""
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


# ---------------------------------------------------------------- illustrations
# Each returns (x0, y0, RGBA image). t = seconds since it appeared, D = total seconds on screen.

def draw_coins(t, D, T1):
    c = Canvas((560, 800, 1360, 1070), k=1 + 0.04 * t / D, pivot=(960, 1040))
    shadow = (226, 215, 194, 255)
    c.ellipse(820, 1012, 160, 13, fill=shadow)
    c.ellipse(1150, 1022, 170, 15, fill=shadow)
    # folded cloth: three soft layers
    for x0, y0, x1, y1, col in ((690, 962, 950, 1010, BLUE), (702, 916, 938, 964, BLUE_L),
                                (714, 870, 926, 918, BLUE)):
        c.rrect(x0, y0, x1, y1, 22, col + (255,))
    for x in (872, 892):
        c.rrect(x, 870, x + 9, 918, 0, GOLD_XL + (255,))
    c.rrect(714, 870, 926, 918, 22, None)

    def stack(x, base, count):
        rx, ry, th = 64, 19, 15
        for i in range(count):
            y = base - i * th
            side = (GOLD if i % 2 == 0 else GOLD_D) + (255,)
            c.ellipse(x, y, rx, ry, fill=side)
            c.rrect(x - rx, y - th, x + rx, y, 0, side)
            c.ellipse(x, y - th, rx, ry, fill=GOLD_L + (255,))
        c.ellipse(x, base - count * th, rx * 0.66, ry * 0.66, outline=GOLD + (255,), width=2.5)

    stack(1090, 1000, 5)
    stack(1222, 1004, 2)
    stack(1152, 1034, 1)
    return 560, 800, c.finish()


def draw_lamp(t, D, T1):
    region = (560, 650, 1360, 1070)
    p = smooth(t / D)
    sx = -26
    fx, fy = 1186 + sx, 858
    # soft glow that slowly brightens
    yy, xx = np.mgrid[region[1]:region[3], region[0]:region[2]].astype(np.float32)
    R = 150 + 48 * p
    fall = np.clip(1 - np.hypot(xx - fx, yy - fy) / R, 0, 1) ** 1.6
    glow = np.zeros((region[3] - region[1], region[2] - region[0], 4), np.float32)
    glow[..., :3] = (238, 204, 128)
    glow[..., 3] = 255 * (0.16 + 0.50 * p) * fall
    base = Image.fromarray(glow.astype(np.uint8), "RGBA")

    c = Canvas(region, shift=(sx, 0))
    gl, g, gd = GOLD_L + (255,), GOLD + (255,), GOLD_D + (255,)
    c.ellipse(960, 1040, 190, 12, fill=(226, 215, 194, 255))
    c.ellipse(812, 942, 38, 34, outline=g, width=13)                       # handle
    c.polygon([(915, 990), (1005, 990), (1032, 1030), (888, 1030)], g)     # foot
    c.ellipse(960, 1030, 72, 9, fill=g)
    c.polygon(smooth_closed([(1040, 918), (1105, 912), (1160, 896), (1190, 890), (1196, 904),
                             (1160, 932), (1110, 972), (1050, 996)]), gl)  # spout
    c.ellipse(960, 955, 140, 50, fill=gl)                                  # body
    c.ellipse(950, 915, 62, 13, fill=g)                                    # lid
    c.ellipse(950, 899, 11, 10, fill=gd)
    # flame, breathing very slowly
    s = 1 + 0.035 * math.sin(2 * math.pi * t / 5.5)
    bx, by = 1186, 896

    def flame(scale, col):
        pts = [(0, 2), (17, -16), (14, -44), (0, -80), (-12, -44), (-17, -16)]
        c.polygon(smooth_closed([(bx + x * scale, by + y * scale * s) for x, y in pts]), col)

    flame(1.0, (222, 170, 86, 255))
    flame(0.55, (246, 220, 158, 255))
    return region[0], region[1], Image.alpha_composite(base, c.finish())


def draw_path(t, D, T1):
    region = (240, 740, 1680, 1080)
    kw = dict(k=1 + 0.04 * t / D, pivot=(960, 1040))
    c = Canvas(region, **kw)
    c.ellipse(960, 1040, 640, 270, fill=SAGE_L + (255,))
    road = (240, 231, 208, 255)
    left = bezier((930, 990), (900, 900), (760, 860), (650, 760))
    right = bezier((990, 990), (1020, 900), (1160, 860), (1270, 760))
    c.polygon(ribbon(left, 120, 26), road)
    c.polygon(ribbon(right, 120, 26), road)
    c.polygon(ribbon(bezier((960, 1110), (960, 1060), (960, 1020), (960, 960)), 230, 170), road)
    # keep the roads on the hill
    m = Canvas(region, **kw)
    m.ellipse(960, 1040, 640, 270, fill=(255, 255, 255, 255))
    r, g, b, a = c.img.split()
    c.img = Image.merge("RGBA", (r, g, b, ImageChops.multiply(a, m.img.split()[3])))
    c.d = ImageDraw.Draw(c.img)
    for x, y, s in ((520, 930, 1.0), (1400, 925, 0.9), (700, 1010, 1.1), (1230, 1000, 1.0),
                    (960, 850, 0.9)):
        for ang in (-0.5, 0.0, 0.5):
            c.polygon(blade((x + ang * 14 * s, y), ang, 30 * s, 9 * s), SAGE + (255,))
    return region[0], region[1], c.finish()


BIRDS = [(470, 132, 58, 0.0), (670, 186, 46, 1.7), (860, 108, 64, 3.1), (1040, 170, 42, 4.4)]


def draw_birds(t, D, T1):
    region = (300, 30, 1620, 240)
    c = Canvas(region)
    col = BLUE + (255,)
    for i, (x, y, w, ph) in enumerate(BIRDS):
        x = x + (13.0 + i * 0.9) * t
        y = y + 7 * math.sin(2 * math.pi * (t + ph * 2) / 9.0)
        lift = 0.62 + 0.2 * math.sin(2 * math.pi * (t + ph) / 5.0)
        hgt = w * lift
        for sgn in (-1, 1):
            c.line(bezier((x, y), (x + sgn * 0.3 * w, y - hgt * 0.95), (x + sgn * 0.72 * w, y - hgt * 0.9),
                          (x + sgn * w, y - hgt * 0.25), n=24), w * 0.13, col)
        c.ellipse(x, y + w * 0.02, w * 0.1, w * 0.085, fill=col)
    return region[0], region[1], c.finish()


LILIES = [(790, 280, -14, 0.9, 0.0), (960, 335, 4, 1.0, 2.5), (1130, 262, 16, 0.88, 5.0)]


def draw_lilies(t, D, T1):
    region = (600, 600, 1320, 1080)
    c = Canvas(region)
    g = smooth(t / T1)            # grows during the first card, then rests
    for x, full_h, lean, fs, ph in LILIES:
        hgt = full_h * (0.5 + 0.5 * g)
        sway = 4 * math.sin(2 * math.pi * (t + ph) / 11.0)
        top = (x + lean + sway, 1085 - hgt)
        stem = bezier((x, 1090), (x - lean * 0.3, 1085 - hgt * 0.4),
                      (x + lean * 1.2 + sway * 0.5, 1085 - hgt * 0.7), top, n=40)
        for frac, side in ((0.24, -1), (0.44, 1), (0.64, -1)):
            base = stem[int(frac * 40)]
            ls = (0.7 + 0.3 * g) * fs
            c.polygon(blade(base, side * 0.85, 105 * ls, 26 * ls), SAGE + (255,))
        c.line(stem, 9, SAGE_D + (255,))
        s = fs * (0.55 + 0.45 * g)
        open_ = 0.75 + 0.25 * g
        c.polygon(blade((top[0], top[1] + 12 * s), 0, 34 * s, 30 * s), SAGE_D + (255,))  # calyx
        for ang in (-1.05, 1.05):
            c.polygon(blade(top, ang * open_, 96 * s, 36 * s), GOLD_L + (255,))
        for ang in (-0.52, 0.52):
            c.polygon(blade(top, ang * open_, 112 * s, 40 * s), GOLD_XL + (255,))
        c.polygon(blade(top, 0, 118 * s, 42 * s), (233, 216, 176, 255))
        for ang in (-0.22, 0.0, 0.22):
            tip = (top[0] + math.sin(ang) * 74 * s, top[1] - math.cos(ang) * 74 * s)
            c.line([(top[0], top[1] - 20 * s), tip], 2.6 * s, GOLD + (255,))
            c.ellipse(tip[0], tip[1], 5.5 * s, 5.5 * s, fill=GOLD + (255,))
    for x in range(650, 1290, 46):  # grass
        for ang, ln in ((-0.35, 44), (0.1, 60), (0.45, 38)):
            c.polygon(blade((x + ang * 20, 1084), ang, ln, 9), SAGE_L + (255,))
    return region[0], region[1], c.finish()


STARS = [(640, 850, 15, BLUE, 0.0), (770, 965, 10, GOLD_L, 1.3), (1175, 835, 12, BLUE, 2.9),
         (1300, 945, 16, GOLD_L, 4.2), (530, 975, 9, BLUE_L, 5.1), (1410, 860, 9, BLUE, 0.7),
         (1090, 1000, 8, BLUE_L, 3.6), (850, 800, 8, BLUE_L, 2.2)]


def draw_moon(t, D, T1):
    region = (440, 750, 1480, 1060)
    c = Canvas(region)
    for x, y, r, col, ph in STARS:
        r = 1.7 * r * (0.9 + 0.18 * math.sin(2 * math.pi * (t + ph) / 6.5))
        pts = []
        for i in range(8):
            rr = r if i % 2 == 0 else r * 0.3
            a = math.pi / 4 * i
            pts.append((x + rr * math.sin(a), y - rr * math.cos(a)))
        c.polygon(pts, col + (255,))
    mx, my = 948 + 26 * t / D, 912 - 10 * t / D
    c.ellipse(mx, my, 84, 84, fill=GOLD_L + (255,))
    c.ellipse(mx + 40, my - 24, 76, 76, fill=(0, 0, 0, 0))
    return region[0], region[1], c.finish()


def draw_sun(t, D, T1):
    region = (300, 625, 1620, 1010)
    horizon = 968
    p = t / D
    cy = horizon + 92 - 172 * (1 - (1 - p) ** 1.4)   # rises slowly across all three cards
    c = Canvas(region)
    grow = 1 + 0.06 * p
    c.ellipse(960, cy, 212 * grow, 212 * grow, fill=GOLD_XL + (70,))
    c.ellipse(960, cy, 166 * grow, 166 * grow, fill=GOLD_XL + (130,))
    c.ellipse(960, cy, 118, 118, fill=(214, 178, 104, 255))
    a, b = c.P((region[0], horizon)), c.P((region[2], region[3]))
    c.d.rectangle([a[0], a[1], b[0], b[1]], fill=(0, 0, 0, 0))   # nothing shows below the horizon
    for hx, rx, ry, col in ((600, 250, 40, SAGE_L), (1330, 240, 30, SAGE_L), (1170, 160, 19, SAGE)):
        x, y = c.P((hx, horizon))
        c.d.chord([x - c.L(rx), y - c.L(ry), x + c.L(rx), y + c.L(ry)], 180, 360, fill=col + (255,))
    c.line([(340, horizon), (1580, horizon)], 5, SAGE_D + (255,))
    return region[0], region[1], c.finish()


ILLUS = dict(coins=draw_coins, lamp=draw_lamp, path=draw_path, birds=draw_birds,
             lilies=draw_lilies, moon=draw_moon, sun=draw_sun)


# ---------------------------------------------------------------- compositing
def render(spec):
    frame = bg("cream")
    card = CARDS[spec["card"] - 1] if spec["card"] else None
    copied = False
    if card and card["kind"] in ("title", "section", "word") and spec["a"] > 0:
        a = spec["a"]
        frame = frame * (1 - a) + bg("navy") * a
        copied = True
    if not copied:
        frame = frame.copy()
    if spec["illus"] and spec["ia"] > 0:
        x0, y0, img = ILLUS[spec["illus"]](spec["it"], spec["D"], spec["T1"])
        arr = np.asarray(img, np.float32)
        a = arr[..., 3:] / 255.0 * spec["ia"]
        sl = frame[y0:y0 + arr.shape[0], x0:x0 + arr.shape[1]]
        sl[:] = sl * (1 - a) + arr[..., :3] * a
    if card and spec["a"] > 0:
        x0, y0, rgb, alpha, _ = text_layer(card["n"])
        a = alpha * spec["a"]
        sl = frame[y0:y0 + rgb.shape[0], x0:x0 + rgb.shape[1]]
        sl[:] = sl * (1 - a) + rgb * a
    return np.clip(frame + 0.5, 0, 255).astype(np.uint8)


def frame_path(f):
    return os.path.join(FRAMES, "f_%06d.png" % f)


def render_chunk(args):
    start, stop = args
    timings, groups, _, _ = solve_timeline()
    seen = {}
    for f in range(start, stop):
        spec = frame_spec(f, timings, groups)
        # frames with no moving illustration repeat exactly: hard-link instead of redrawing
        key = (spec["card"], spec["a"]) if not spec["illus"] else None
        if key is not None and key in seen:
            os.link(seen[key], frame_path(f))
            continue
        Image.fromarray(render(spec)).save(frame_path(f), compress_level=1)
        if key is not None:
            seen[key] = frame_path(f)
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
    timings, groups, total, k = solve_timeline()
    print("font: %s\n  %s\n  %s" % (FONT_NAME, FONT_REG, FONT_ITA))
    print("hold scale k = %.4f   total = %.3f s (%d frames)" % (k, total, round(total * FPS)))
    for tm in timings:
        c = tm["card"]
        print("  card %2d  %-9s words %2d  start %7.2f  hold %5.2f" %
              (c["n"], c["kind"], n_words(c), tm["t0"], tm["hold"]))
    return timings, groups, total, k


def cmd_stills():
    timings, groups, total, k = print_timing()
    shutil.rmtree(STILLS, ignore_errors=True)
    os.makedirs(STILLS)
    problems = []
    for tm in timings:
        card = tm["card"]
        n = card["n"]
        f = int((tm["t0"] + tm["fi"] + tm["hold"] * 0.5) * FPS)
        spec = frame_spec(f, timings, groups)
        Image.fromarray(render(spec)).save(os.path.join(STILLS, "card_%02d.png" % n))
        items, _, lines = layout(card)
        box = text_layer(n)[4]
        print("card %2d | %s%s" % (n, " / ".join(lines), ("  ||  " + card["sub"]) if card["sub"] else ""))
        if box[0] < MARGIN or box[2] > W - MARGIN or box[1] < 40 or box[3] > H - 40:
            problems.append("card %d: text box %s outside margins" % (n, box))
        if any(len(l) > MAX_CHARS for l in lines):
            problems.append("card %d: line longer than %d chars" % (n, MAX_CHARS))
        if len(lines) > 1 and len(lines[-1].split()) == 1:
            problems.append("card %d: one word alone on last line" % n)
        if card["illus"]:
            g = [g for g in groups if g["t0"] <= tm["t0"] < g["end"]][0]
            for i in range(41):  # sample the illustration across its whole life
                it = (g["end"] - g["t0"]) * i / 40
                x0, y0, img = ILLUS[card["illus"]](it, g["end"] - g["t0"], g["T1"])
                ib = img.getbbox()
                ib = (ib[0] + x0, ib[1] + y0, ib[2] + x0, ib[3] + y0)
                pad = 24
                if not (ib[2] < box[0] - pad or ib[0] > box[2] + pad or
                        ib[3] < box[1] - pad or ib[1] > box[3] + pad):
                    problems.append("card %d: illustration %s overlaps text %s at t=%.1f" % (n, ib, box, it))
                    break
    # contact sheets, four cards each
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
    timings, groups, total, k = print_timing()
    nframes = round(total * FPS)
    shutil.rmtree(FRAMES, ignore_errors=True)
    os.makedirs(FRAMES)
    step = 150
    chunks = [(s, min(s + step, nframes)) for s in range(0, nframes, step)]
    done = 0
    with Pool(os.cpu_count()) as pool:
        for n in pool.imap_unordered(render_chunk, chunks):
            done += n
            print("\rframes %d / %d" % (done, nframes), end="", flush=True)
    print()
    cmd = [ffmpeg_bin(), "-y", "-loglevel", "error", "-framerate", str(FPS),
           "-i", os.path.join(FRAMES, "f_%06d.png"),
           "-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
           "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-pix_fmt", "yuv420p",
           "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
           "-r", str(FPS), "-an", "-movflags", "+faststart", OUT]
    subprocess.check_call(cmd)
    if os.path.getsize(OUT) > 0:
        shutil.rmtree(FRAMES)
    print("wrote", OUT)


if __name__ == "__main__":
    {"stills": cmd_stills, "render": cmd_render}[sys.argv[1] if len(sys.argv) > 1 else "stills"]()
