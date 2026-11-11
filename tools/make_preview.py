"""Draw the 1200x630 link-preview image for the site.  usage: make_preview.py <out.png>"""
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
BG, INK, MUTED = (14, 15, 30), (236, 234, 246), (162, 160, 192)
GOLD, BLUE, WHITE_KEY, BLACK_KEY, LINE = (232, 186, 92), (125, 179, 220), (230, 229, 239), (20, 19, 42), (44, 46, 76)
img = Image.new('RGB', (W, H), BG)
d = ImageDraw.Draw(img)
didot = lambda s: ImageFont.truetype('/System/Library/Fonts/Supplemental/Didot.ttc', s)
avenir = lambda s, i=0: ImageFont.truetype('/System/Library/Fonts/Avenir Next.ttc', s, index=i)

d.text((72, 70), 'PIANO CHORD TRAINER', font=avenir(24, 5), fill=MUTED, spacing=4)
d.text((72, 112), 'Play it from the', font=didot(92), fill=INK)
d.text((72, 214), 'chords', font=didot(92), fill=GOLD)
d.text((72, 336), 'Falling notes, a chord for every bar and rolling sheet music.', font=avenir(30), fill=MUTED)
d.text((72, 378), 'Chopin · Debussy · more coming', font=avenir(30), fill=MUTED)

# falling notes landing on a keyboard
top, kh, n = 470, 160, 28
ww = (W - 0) / n
gold_keys, blue_keys = {25, 27}, {22, 24}
for i in range(n):
    x = i * ww
    fill = GOLD if i in gold_keys else BLUE if i in blue_keys else WHITE_KEY
    d.rectangle([x + 1, top, x + ww - 1, H], fill=fill)
    d.line([x, top, x, H], fill=LINE, width=2)
for i in range(n):
    if i % 7 in (0, 1, 3, 4, 5):
        x = (i + 1) * ww - ww * 0.31
        d.rectangle([x, top, x + ww * 0.62, top + kh * 0.6], fill=BLACK_KEY)
for i, h, col in [(22, 150, BLUE), (24, 260, BLUE), (25, 90, GOLD), (27, 330, GOLD)]:
    x = i * ww + 6
    d.rounded_rectangle([x, top - h - 8, x + ww - 12, top - 8], radius=6, fill=col)
d.line([0, top - 2, W, top - 2], fill=GOLD, width=3)
img.save(sys.argv[1], optimize=True)
print('saved', sys.argv[1])
