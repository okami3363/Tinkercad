"""Extract the white Steam piston mark from the logo image: white pixels that
lie INSIDE the blue circle (outer white background is excluded). Writes a PBM
for potrace + a view, and prints the circle/piston geometry for placement."""
from pnglib import decode_rgb_png, write_pbm, write_png_rgb

SC = "/private/tmp/claude-501/-Users-fetc-imac24-Documents-Projects-Tinkercad/afa0a5c5-7e03-45f0-976b-c71c2962793f/scratchpad"
m = decode_rgb_png(f"{SC}/steam_logo.png")
w, h, ch, rows = m["w"], m["h"], m["ch"], m["rows"]

def px(x, y):
    o = x*ch; r = rows[y]
    return r[o], r[o+1], r[o+2]

def is_blue(r, g, b):  return b > r + 15 and b > g + 5 and b > 55
def is_white(r, g, b): return r > 185 and g > 185 and b > 185

# circle from blue extent
bx0 = by0 = 10**9; bx1 = by1 = -1
for y in range(h):
    for x in range(w):
        if is_blue(*px(x, y)):
            bx0 = min(bx0, x); bx1 = max(bx1, x); by0 = min(by0, y); by1 = max(by1, y)
ccx, ccy = (bx0+bx1)/2, (by0+by1)/2
R = min(bx1-bx0, by1-by0)/2

# piston = white inside circle
piston = [[False]*w for _ in range(h)]
px0 = py0 = 10**9; px1 = py1 = -1; n = 0
rr = (R*0.97)**2
for y in range(h):
    for x in range(w):
        if (x-ccx)**2 + (y-ccy)**2 <= rr and is_white(*px(x, y)):
            piston[y][x] = True; n += 1
            px0 = min(px0, x); px1 = max(px1, x); py0 = min(py0, y); py1 = max(py1, y)

write_pbm(f"{SC}/steam_piston.pbm", w, h, piston)
# view: piston white on dark-blue disc on black
buf = bytearray()
for y in range(h):
    for x in range(w):
        if piston[y][x]:
            buf += bytes((255, 255, 255))
        elif (x-ccx)**2 + (y-ccy)**2 <= R*R:
            buf += bytes((27, 58, 107))
        else:
            buf += bytes((20, 20, 20))
write_png_rgb(f"{SC}/steam_piston_view.png", w, h, buf)

print(f"circle center=({ccx:.0f},{ccy:.0f}) R={R:.0f}px")
print(f"piston px={n}  bbox x[{px0},{px1}] y[{py0},{py1}]")
print(f"piston center vs circle center (px): dx={ (px0+px1)/2 - ccx:.1f} dy={ (py0+py1)/2 - ccy:.1f}")
print(f"piston size / circle-diameter: {(px1-px0)/(2*R):.3f} x {(py1-py0)/(2*R):.3f}")
