"""Generate body + detail bitmaps from ../sticker.PNG for potrace.
Only needed if the FOX IMAGE changes (not for a panel swap). Run from src/.
  body   = whole fox silhouette (alpha >= 128)
  detail = black regions (opaque + dark)"""
import os
from pnglib import decode_palette_png, write_pbm, write_png_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.normpath(os.path.join(HERE, "..", "sticker.PNG"))

def view(path, w, h, bits):
    buf = bytearray()
    for y in range(h):
        for x in range(w):
            buf += b"\x00\x00\x00" if bits[y][x] else b"\xff\xff\xff"
    write_png_rgb(path, w, h, buf)

m = decode_palette_png(SRC)
W, H, plte, trns, idx = m["w"], m["h"], m["plte"], m["trns"], m["idx"]
body   = [[False]*W for _ in range(H)]
detail = [[False]*W for _ in range(H)]
for y in range(H):
    r = idx[y]
    for x in range(W):
        pi = r[x]
        if trns[pi] >= 128:
            body[y][x] = True
            rr, gg, bb = plte[pi]
            if max(rr, gg, bb) < 70:
                detail[y][x] = True

write_pbm(os.path.join(HERE, "body.pbm"), W, H, body)
write_pbm(os.path.join(HERE, "detail.pbm"), W, H, detail)
view(os.path.join(HERE, "body_view.png"), W, H, body)
view(os.path.join(HERE, "detail_view.png"), W, H, detail)
print("wrote body.pbm detail.pbm (+ views). Next: potrace -s -t 4 -o svg/body.svg body.pbm")
