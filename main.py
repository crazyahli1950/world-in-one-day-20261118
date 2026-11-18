#!/usr/bin/env python3
"""
Sum up 18 November 2026's world news in one image.

Deterministic, offline generator: draws a newspaper front page with PIL.
Writes the entry image to /output/entry.png (or $OUTPUT_PATH).
No network, no randomness, no timestamps -> same bytes on every run.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (20, 24, 29)
MUTED = (92, 96, 100)
RED = (179, 35, 42)
NAVY = (18, 34, 64)
GREEN = (22, 122, 62)
LIGHT_LINE = (198, 190, 172)

FONT_CANDIDATES = {
    "serif_bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    ],
    "serif": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "serif_italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "sans_bold": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
}


def font(kind, size):
    for path in FONT_CANDIDATES[kind]:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


def text_w(draw, s, fnt):
    box = draw.textbbox((0, 0), s, font=fnt)
    return box[2] - box[0]


def fit_font(draw, s, kind, start_size, max_w, min_size=11):
    size = start_size
    while size > min_size and text_w(draw, s, font(kind, size)) > max_w:
        size -= 0.5
    return font(kind, size)


def wrap(draw, s, fnt, max_w):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(draw, trial, fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, s, fnt, max_w, leading, fill=INK):
    for line in wrap(draw, s, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def centered(draw, cx, y, s, fnt, fill=INK):
    draw.text((cx - text_w(draw, s, fnt) / 2, y), s, font=fnt, fill=fill)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 36
    R = W - M

    # ---------- dateline ----------
    f_small = font("sans_bold", 17)
    d.text((M, 24), "WEDNESDAY  •  18 NOVEMBER 2026", font=f_small, fill=INK)
    right = "THE WHOLE DAY IN ONE IMAGE"
    d.text((R - text_w(d, right, f_small), 24), right, font=f_small, fill=RED)
    d.line([(M, 52), (R, 52)], fill=INK, width=2)

    # ---------- masthead ----------
    centered(d, W / 2, 62, "THE WORLD IN ONE DAY", font("serif_bold", 62))
    d.line([(M, 142), (R, 142)], fill=INK, width=4)
    d.line([(M, 149), (R, 149)], fill=INK, width=1)

    # ---------- markets ticker (auto-fit) ----------
    d.rectangle([M, 162, R, 198], fill=INK)
    ticker = ("RISK-OFF DAY:  S&P 500 -1.0%   VIX +11% AT 25.5   GOLD -2.0% $3,785   "
              "BTC $64.8K FLAT   FEAR & GREED 11 - EXTREME FEAR")
    f_tick = fit_font(d, ticker, "sans_bold", 17, R - M - 24)
    centered(d, W / 2, 171, ticker, f_tick, fill=(245, 240, 228))

    # ---------- LEAD STORY ----------
    y = 214
    d.text((M, y), "SHENZHEN, CHINA  —  THE DAY'S TOP STORY", font=font("sans_bold", 18), fill=RED)
    y += 28
    f_head = font("serif_bold", 44)
    for line in ["Trump, Xi & Putin:", "Rival Powers Share", "One Table in China"]:
        d.text((M, y), line, font=f_head, fill=INK)
        y += 50
    y += 4
    para(
        d, M, y,
        "Xi Jinping greeted Donald Trump at Shenzhen airport in a rare personal "
        "welcome, then sat down with Vladimir Putin for a historic trilateral "
        "summit. Xi called for a multipolar world led by China and Russia; "
        "Ukraine urged the three to pressure Putin to end the war.",
        font("serif", 19.5), 596, 25,
    )

    # lead graphic panel
    px0, py0, px1, py1 = 664, 214, R, 516
    d.rounded_rectangle([px0, py0, px1, py1], radius=14, fill=NAVY)
    circles = [((222, 47, 54), "XI", "CHINA"), ((58, 92, 168), "TRUMP", "U.S.A."),
               ((148, 32, 40), "PUTIN", "RUSSIA")]
    cx_positions = [px0 + 56, px0 + 162, px0 + 268]
    cy = py0 + 66
    for (color, name, country), cx in zip(circles, cx_positions):
        d.ellipse([cx - 43, cy - 43, cx + 43, cy + 43], fill=color, outline=(240, 236, 224), width=3)
        f_init = font("sans_bold", 18 if len(name) > 2 else 23)
        centered(d, cx, cy - 12, name, f_init, fill=(255, 255, 255))
        centered(d, cx, cy + 54, country, font("sans_bold", 15), fill=(214, 205, 182))
    centered(d, (px0 + px1) / 2, py0 + 140, "THREE LEADERS. ONE SUMMIT.", font("sans_bold", 19), fill=(255, 255, 255))
    centered(d, (px0 + px1) / 2, py0 + 170, "A rare three-way meeting of the U.S.,", font("serif_italic", 16.5), fill=(214, 205, 182))
    centered(d, (px0 + px1) / 2, py0 + 190, "Chinese and Russian presidents.", font("serif_italic", 16.5), fill=(214, 205, 182))
    d.line([(px0 + 30, py0 + 228), (px1 - 30, py0 + 228)], fill=(198, 154, 44), width=2)
    centered(d, (px0 + px1) / 2, py0 + 240, "\u201cRussia and China should lead", font("serif_italic", 16.5), fill=(240, 236, 224))
    centered(d, (px0 + px1) / 2, py0 + 260, "the push to a multipolar world.\u201d", font("serif_italic", 16.5), fill=(240, 236, 224))
    centered(d, (px0 + px1) / 2, py0 + 282, "- XI JINPING, AT THE SUMMIT", font("sans_bold", 12.5), fill=(214, 205, 182))

    d.line([(M, 530), (R, 530)], fill=INK, width=2)

    # ---------- ROW 2 ----------
    y2 = 546
    col_w = 464
    f_h2 = font("serif_bold", 29)
    d.text((M, y2), "MIDDLE EAST", font=font("sans_bold", 16), fill=RED)
    y2l = y2 + 24
    for line in wrap(d, "Gulf Erupts: U.S. Hits Iran, Tankers Struck at Hormuz", f_h2, col_w):
        d.text((M, y2l), line, font=f_h2, fill=INK)
        y2l += 34
    y2l += 2
    para(
        d, M, y2l,
        "Gulf states intercepted Iranian and Houthi missiles and drones after "
        "U.S. jets struck an IRGC missile site on Qeshm Island. Five tankers "
        "were hit in and around the Strait of Hormuz, the chokepoint for a "
        "fifth of the world's oil.",
        font("serif", 19), col_w, 24.5,
    )
    x2 = 524
    d.text((x2, y2), "TECHNOLOGY & AI", font=font("sans_bold", 16), fill=GREEN)
    y2r = y2 + 24
    for line in wrap(d, "Nvidia's $115.8 Billion Blowout Quarter", f_h2, col_w):
        d.text((x2, y2r), line, font=f_h2, fill=INK)
        y2r += 34
    y2r += 2
    para(
        d, x2, y2r,
        "Revenue up 103% in a year smashed every forecast and lifted the stock "
        "4.8% after hours - even as the board said it will not reinstate "
        "founder Jensen Huang, and a global AI selloff bruised tech shares.",
        font("serif", 19), col_w, 24.5,
    )
    d.line([(512, 546), (512, 768)], fill=LIGHT_LINE, width=2)
    d.line([(M, 780), (R, 780)], fill=INK, width=2)

    # ---------- ROW 3: three minis ----------
    y3 = 796
    minis = [
        ("WAR IN EUROPE", "Kyiv Hits the Crimea Bridge",
         "Zelensky confirmed a Ukrainian strike partly destroyed Russia's "
         "bridge to Crimea on the summit's eve."),
        ("HEALTH", "U.S. Loses Measles-Free Status",
         "Over 5,400 cases this year ended America's measles-elimination "
         "status, officials confirmed."),
        ("CRYPTO", "$6.3B Heist - Binance Expands",
         "Weeks after a record $6.3 billion hack, Binance vowed to expand "
         "into five Asian markets, saying its finances are sound."),
    ]
    col3_w = 296
    xs = [M, M + col3_w + 32, M + 2 * (col3_w + 32)]
    f_h3 = font("serif_bold", 22)
    for (kick, head, body), x in zip(minis, xs):
        d.text((x, y3), kick, font=font("sans_bold", 14.5), fill=RED)
        yy = y3 + 21
        for line in wrap(d, head, f_h3, col3_w):
            d.text((x, yy), line, font=f_h3, fill=INK)
            yy += 26
        yy += 1
        para(d, x, yy, body, font("serif", 16.5), col3_w, 21)
    d.line([(xs[1] - 16, y3), (xs[1] - 16, 928)], fill=LIGHT_LINE, width=2)
    d.line([(xs[2] - 16, y3), (xs[2] - 16, 928)], fill=LIGHT_LINE, width=2)

    # ---------- bottom band ----------
    d.rectangle([M, 942, R, 1010], fill=(238, 231, 214))
    d.text((M + 14, 952), "ALSO TODAY", font=font("sans_bold", 15), fill=RED)
    also = [
        "Voyager 1 reaches one light-day from Earth - a first for any spacecraft",
        "Russian military plane crash kills all 19 aboard  •  M6.0 quake hits Papua New Guinea",
    ]
    yy = 952
    for line in also:
        d.text((M + 128, yy), line, font=font("serif", 16.5), fill=INK)
        yy += 20
    d.text((M + 14, 990),
           "Prince William awards five Earthshot Prizes of $1.3M each  •  Dozens hurt as trains collide near Prague"
           "   |   Sources: Reuters, AP, AFP, Japan Times, NDTV, GFZ",
           font=font("serif_italic", 13.5), fill=MUTED)

    out = os.environ.get("OUTPUT_PATH")
    if not out:
        out = "/output/entry.png" if os.path.isdir("/output") else os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG")
    print("wrote", out)


if __name__ == "__main__":
    main()
