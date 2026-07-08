"""Partition the fox (alpha>=128) into orange / white / black bitmaps by nearest
reference colour, for potrace. Only needed if the FOX IMAGE changes. Run from src/."""
import os
from pnglib import decode_palette_png, write_pbm, write_png_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.normpath(os.path.join(HERE, "..", "sticker.PNG"))
BLACK, WHITE, ORANGE = (0, 0, 0), (255, 255, 255), (255, 156, 0)

def nearest(rgb):
    r, g, b = rgb
    dk = r*r + g*g + b*b
    dw = (r-255)**2 + (g-255)**2 + (b-255)**2
    do = (r-255)**2 + (g-156)**2 + b*b
    mn = min(dk, dw, do)
    return "k" if mn == dk else ("w" if mn == dw else "o")

m = decode_palette_png(SRC)
W, H, plte, trns, idx = m["w"], m["h"], m["plte"], m["trns"], m["idx"]
orange = [[False]*W for _ in range(H)]
white  = [[False]*W for _ in range(H)]
black  = [[False]*W for _ in range(H)]
view = bytearray()
for y in range(H):
    for x in range(W):
        pi = idx[y][x]
        if trns[pi] >= 128:
            c = nearest(plte[pi])
            if c == "w":   white[y][x]  = True; view += bytes((230, 230, 230))
            elif c == "k": black[y][x]  = True; view += bytes((25, 25, 25))
            else:          orange[y][x] = True; view += bytes((255, 156, 0))
        else:
            view += bytes((120, 140, 150))

write_pbm(os.path.join(HERE, "orange.pbm"), W, H, orange)
write_pbm(os.path.join(HERE, "white.pbm"),  W, H, white)
write_pbm(os.path.join(HERE, "black.pbm"),  W, H, black)
write_png_rgb(os.path.join(HERE, "partition_view.png"), W, H, view)
print("wrote orange/white/black.pbm. Next: for m in orange white black; do potrace -s -t 2 -o svg/$m.svg $m.pbm; done")
