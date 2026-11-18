#!/usr/bin/env python3
"""Draw the 17 November 2026 world-news front page (1024x1024 PNG).

One image summing up the world's news of Tuesday 17 November 2026:
lead story (Kerch Bridge) + four panels (Hormuz, Trump, JPMorgan, Nvidia)
+ an ALSO TODAY strip. Wording verified against live reporting on
18 November 2026; claims are attributed where the sources attribute them
(Russia's drone figures, the IRGC tanker claim, the expected trilateral).

Deterministic: fixed text, fixed layout, no network, no timestamps.
Run: python3 draw_infographic.py  ->  entry.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
WHITE = (255, 255, 255)
LEAD_BLUE = (27, 42, 74)
STRIP_DARK = (17, 17, 17)
STEEL = (143, 163, 200)

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
assert os.path.exists(FONT_BOLD), "bold font missing"
assert os.path.exists(FONT_REG), "regular font missing"


def font(bold, size):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            assert cur, "single word wider than panel"
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    for ln in lines:
        assert draw.textlength(ln, font=fnt) <= max_w, "line overflows: %r" % ln
    return lines


def fit_text(draw, text, max_w, max_h, sizes, leading_extra=5):
    """Largest font size from sizes whose wrapped text fits max_w x max_h."""
    for size in sizes:
        fnt = font(False, size)
        lines = wrap(draw, text, fnt, max_w)
        if len(lines) * (size + leading_extra) <= max_h:
            return fnt, lines, size
    raise AssertionError("text does not fit %dx%d: %r" % (max_w, max_h, text[:60]))


def draw_lines(draw, lines, x, y, fnt, fill, leading_extra=5):
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += fnt.size + leading_extra
    return y


def draw_icon(draw, kind, x, y, w, h, colour):
    """Simple geometric icon (rectangles / lines / polygons only)."""
    if kind == "tanker":
        # hull, containers, flame, waves
        draw.rectangle([x, y + h - 12, x + 150, y + h - 3], fill=(120, 30, 25))
        draw.polygon([(x + 150, y + h - 12), (x + 172, y + h - 3),
                      (x + 150, y + h - 3)], fill=(120, 30, 25))
        for i, cw in enumerate((26, 22, 26)):
            draw.rectangle([x + 12 + i * 34, y + h - 26, x + 12 + i * 34 + cw,
                            y + h - 12], fill=(90, 90, 96))
        draw.polygon([(x + 96, y + 2), (x + 102, y + 12), (x + 90, y + 12)],
                     fill=(230, 120, 20))
        draw.line([x + 180, y + h - 6, x + 210, y + h - 6], fill=(90, 110, 150), width=2)
        draw.line([x + 190, y + h - 1, x + 216, y + h - 1], fill=(90, 110, 150), width=2)
    elif kind == "flags":
        for i, fc in enumerate(((29, 78, 216), (180, 35, 24), (21, 128, 61))):
            px = x + 24 + i * 64
            draw.line([px, y + 2, px, y + h - 2], fill=INK, width=3)
            draw.rectangle([px, y + 2, px + 42, y + 18], fill=fc)
    elif kind == "bank":
        draw.polygon([(x + 8, y + 10), (x + 62, y + 2), (x + 116, y + 10)],
                     fill=(110, 100, 80))
        for i in range(3):
            cx0 = x + 16 + i * 36
            draw.rectangle([cx0, y + 12, cx0 + 10, y + h - 6], fill=(110, 100, 80))
        draw.rectangle([x + 8, y + h - 6, x + 116, y + h - 2], fill=(110, 100, 80))
        draw.polygon([(x + 140, y + 2), (x + 156, y + 26), (x + 124, y + 26)],
                     fill=(230, 180, 20))
        draw.text((x + 140, y + 8), "!", font=font(True, 14), fill=INK, anchor="ma")
    elif kind == "chip":
        draw.rectangle([x + 8, y + 4, x + 34, y + 30], fill=(40, 40, 44))
        draw.rectangle([x + 14, y + 10, x + 28, y + 24], fill=(90, 160, 220))
        for i in range(3):
            draw.rectangle([x + 12 + i * 8, y, x + 15 + i * 8, y + 4], fill=(40, 40, 44))
            draw.rectangle([x + 12 + i * 8, y + 30, x + 15 + i * 8, y + 34],
                           fill=(40, 40, 44))
        pts = [(x + 48, y + 28), (x + 72, y + 20), (x + 92, y + 22),
               (x + 116, y + 8), (x + 140, y + 4)]
        draw.line(pts, fill=(21, 128, 61), width=3)
        draw.polygon([(x + 140, y + 4), (x + 130, y + 2), (x + 132, y + 12)],
                     fill=(21, 128, 61))


img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)
MX = 28
report = []

# --- Masthead: black band + title ---
mast_y, mast_h = 20, 70
d.rectangle([MX, mast_y, W - MX, mast_y + mast_h], fill=INK)
d.text((W // 2, mast_y + mast_h // 2), "THE WORLD IN ONE DAY",
       font=font(True, 46), fill=WHITE, anchor="mm")
# --- Dateline ---
date_y = mast_y + mast_h + 6
d.text((W // 2, date_y + 14), "TUESDAY, 17 NOVEMBER 2026",
       font=font(True, 26), fill=INK, anchor="mm")

# --- Lead story: full-width dark-blue panel ---
lead_y, lead_h = 130, 276
d.rectangle([MX, lead_y, W - MX, lead_y + lead_h], fill=LEAD_BLUE)
lx, lw = MX + 16, W - 2 * MX - 32
d.text((lx, lead_y + 16), "KERCH BRIDGE HIT AGAIN",
       font=font(True, 52), fill=WHITE)
summary_y = lead_y + 16 + 64 + 8
icon_h = 40
icon_y = lead_y + lead_h - icon_h - 8
avail_h = icon_y - 6 - summary_y
lead_summary = (
    "Ukraine strikes the bridge to occupied Crimea for a second day running "
    "and a road span collapses. Russia hits two bridges over the Dnipro in Kyiv "
    "and says it shot down 1,441 drones in the war's biggest aerial attack.")
sum_f, sum_lines, sum_size = fit_text(d, lead_summary, lw, avail_h, [22, 21, 20, 19])
draw_lines(d, sum_lines, lx, summary_y, sum_f, WHITE)
report.append(("LEAD", "KERCH BRIDGE HIT AGAIN", 52, sum_size, len(sum_lines)))
# bridge silhouette: deck with a fallen span, two towers, cables, crack, water
ix0, ix1, iy = lx, lx + lw, icon_y
deck_y = iy + 18
d.line([ix0, deck_y, ix0 + 400, deck_y], fill=STEEL, width=4)
d.line([ix0 + 536, deck_y, ix1, deck_y], fill=STEEL, width=4)
d.polygon([(ix0 + 400, deck_y), (ix0 + 536, deck_y + 14),
           (ix0 + 536, deck_y + 18), (ix0 + 400, deck_y + 4)], fill=STEEL)
for tx in (ix0 + 180, ix0 + 700):
    d.rectangle([tx, iy + 2, tx + 6, deck_y], fill=STEEL)
    d.line([tx + 3, iy + 2, ix0 + 60, deck_y], fill=STEEL, width=2)
    d.line([tx + 3, iy + 2, ix0 + 400, deck_y], fill=STEEL, width=2)
    d.line([tx + 3, iy + 2, ix0 + 536, deck_y], fill=STEEL, width=2)
    d.line([tx + 3, iy + 2, ix1 - 60, deck_y], fill=STEEL, width=2)
crack = [(ix0 + 458, deck_y - 2), (ix0 + 468, deck_y - 10), (ix0 + 478, deck_y - 4),
         (ix0 + 488, deck_y - 12), (ix0 + 498, deck_y - 6)]
d.line(crack, fill=WHITE, width=2)
for wy in (iy + 30, iy + 35, iy + 39):
    d.line([ix0 + 40, wy, ix0 + 300, wy], fill=STEEL, width=2)
    d.line([ix0 + 620, wy, ix0 + 880, wy], fill=STEEL, width=2)

# --- 2x2 grid ---
panels = [
    ("HORMUZ ON EDGE", (180, 35, 24),
     "Two oil tankers hit naval mines and catch fire near the Strait of Hormuz, "
     "Iran's Revolutionary Guard says. A third US aircraft carrier, "
     "USS Theodore Roosevelt, reaches the Middle East.", "tanker"),
    ("TRUMP'S ASIA TRIP", (29, 78, 216),
     "Trump arrives in Manila for the ASEAN summit. He heads to Shenzhen for APEC, "
     "where a three-way meeting with Xi and Putin is expected.", "flags"),
    ("JPMORGAN OUTAGE", (194, 65, 12),
     "A software bug, not a cyberattack, slows JPMorgan online banking, branch "
     "transactions and Zelle payments for thousands of customers.", "bank"),
    ("NVIDIA EARNINGS", (21, 128, 61),
     "Nvidia reports after the close in its first earnings since founder-CEO Jensen "
     "Huang resigned after 33 years: record revenue of $115.8 billion beats "
     "forecasts, but the board says it will not reinstate him as CEO.", "chip"),
]
cell_w, cell_h, gap = 474, 212, 14
grid_y = 418
for i, (head, colour, body, icon) in enumerate(panels):
    cx = MX + (i % 2) * (cell_w + gap)
    cy = grid_y + (i // 2) * (cell_h + gap)
    d.rectangle([cx, cy, cx + cell_w, cy + cell_h], fill=WHITE,
                outline=(200, 196, 186), width=1)
    d.rectangle([cx, cy, cx + cell_w, cy + 38], fill=colour)
    d.text((cx + 14, cy + 19), head, font=font(True, 25), fill=WHITE, anchor="lm")
    bx, bw = cx + 14, cell_w - 28
    by = cy + 38 + 8
    icon_h2 = 30
    icon_y2 = cy + cell_h - icon_h2 - 6
    avail = icon_y2 - 6 - by
    bf, blines, bsize = fit_text(d, body, bw, avail, [20, 19, 18, 17, 16])
    draw_lines(d, blines, bx, by, bf, INK)
    report.append(("PANEL %d" % (i + 1), head, 25, bsize, len(blines)))
    draw_icon(d, icon, bx, icon_y2, bw, icon_h2, colour)

# --- ALSO TODAY strip ---
strip_y, strip_h = 868, 118
d.rectangle([MX, strip_y, W - MX, strip_y + 28], fill=STRIP_DARK)
d.text((MX + 14, strip_y + 14), "ALSO TODAY", font=font(True, 20),
       fill=WHITE, anchor="lm")
items = [
    "ULA Vulcan rocket fails, destroying 40 Amazon Leo satellites",
    "Five European states plan a migrant return hub in Rwanda",
    "Houthis push Yemen's government army back from the Red Sea coast",
    "At least 17 killed in two shootings in South Africa",
    "WHO validates Eritrea's elimination of trachoma",
    "Singapore seeks trusted access to advanced AI chips",
]
body_y = strip_y + 28 + 8
col_w = (W - 2 * MX - 2 * 14) // 3
row_h = 2 * (14 + 4)
for idx, item in enumerate(items):
    col, row = idx % 3, idx // 3
    ix = MX + 14 + col * (col_w + 14)
    iy2 = body_y + row * row_h
    fnt = font(False, 14)
    lines = wrap(d, "\u2022 " + item, fnt, col_w)
    assert len(lines) <= 2, "strip item too long: %r" % item
    draw_lines(d, lines, ix, iy2, fnt, INK, leading_extra=4)
report.append(("STRIP", "ALSO TODAY (6 items, 3 cols x 2 rows)", 20, 14, 2))

img.save("entry.png", format="PNG")
size = os.path.getsize("entry.png")
assert img.size == (1024, 1024)
assert size <= 1048576, "entry.png too big: %d" % size
print("entry.png: %dx%d px, %d bytes" % (img.size[0], img.size[1], size))
print("LAYOUT REPORT")
for name, head, hsize, bsize, nlines in report:
    print("  %s: headline %dpt, body %dpt, %d lines -- %s"
          % (name, hsize, bsize, nlines, head))
