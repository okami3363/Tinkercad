"""Pure-stdlib decoder for the 8-bit palette PNG + placement analysis.
Reused later to emit per-colour PBM masks for potrace."""
import struct, zlib, sys

def decode_palette_png(path):
    with open(path, "rb") as f:
        d = f.read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    i = 8
    w = h = bitdepth = colortype = None
    plte = []          # list of (r,g,b)
    trns = []          # alpha per palette index (parallel to plte); default 255
    idat = bytearray()
    while i < len(d):
        (ln,) = struct.unpack(">I", d[i:i+4]); typ = d[i+4:i+8]; body = d[i+8:i+8+ln]
        if typ == b"IHDR":
            w, h, bitdepth, colortype = struct.unpack(">IIBB", body[:10])
        elif typ == b"PLTE":
            plte = [tuple(body[j:j+3]) for j in range(0, ln, 3)]
        elif typ == b"tRNS":
            trns = list(body)
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + ln  # length + type + body + crc
    assert colortype == 3 and bitdepth == 8, f"expected 8-bit palette, got ct={colortype} bd={bitdepth}"
    while len(trns) < len(plte):
        trns.append(255)

    raw = zlib.decompress(bytes(idat))
    stride = w  # 1 byte/pixel for 8-bit palette
    bpp = 1

    def paeth(a, b, c):
        p = a + b - c; pa = abs(p-a); pb = abs(p-b); pc = abs(p-c)
        return a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)

    idx = []            # idx[y] = bytearray of palette indices
    prev = bytearray(stride)
    p = 0
    for _y in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if ft == 1:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                line[x] = (line[x] + a) & 255
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif ft == 4:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                c = prev[x-bpp] if x >= bpp else 0
                line[x] = (line[x] + paeth(a, prev[x], c)) & 255
        idx.append(line); prev = line
    return dict(w=w, h=h, plte=plte, trns=trns, idx=idx)


def write_pbm(path, w, h, bits):
    rb = (w+7)//8; out = bytearray()
    for y in range(h):
        row = bits[y]
        for bx in range(rb):
            b = 0
            for k in range(8):
                x = bx*8+k
                if x < w and row[x]:
                    b |= 1 << (7-k)
            out.append(b)
    with open(path, "wb") as f:
        f.write(b"P4\n%d %d\n" % (w, h)); f.write(bytes(out))


def write_png_rgb(path, w, h, buf):
    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t+d) & 0xffffffff)
    raw = bytearray()
    for y in range(h):
        raw.append(0); raw += buf[y*w*3:(y+1)*w*3]
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def decode_rgb_png(path):
    with open(path, "rb") as f:
        d = f.read()
    assert d[:8] == b"\x89PNG\r\n\x1a\n"
    i = 8; w = h = bd = ct = None; idat = bytearray()
    while i < len(d):
        (ln,) = struct.unpack(">I", d[i:i+4]); typ = d[i+4:i+8]; body = d[i+8:i+8+ln]
        if typ == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", body[:10])
        elif typ == b"IDAT":
            idat += body
        elif typ == b"IEND":
            break
        i += 12 + ln
    assert bd == 8 and ct in (2, 6), f"want 8-bit RGB/RGBA, got bd={bd} ct={ct}"
    ch = 3 if ct == 2 else 4
    raw = zlib.decompress(bytes(idat)); stride = w*ch; bpp = ch

    def paeth(a, b, c):
        p = a+b-c; pa = abs(p-a); pb = abs(p-b); pc = abs(p-c)
        return a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)

    rows = []; prev = bytearray(stride); p = 0
    for _ in range(h):
        ft = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if ft == 1:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                line[x] = (line[x]+a) & 255
        elif ft == 2:
            for x in range(stride):
                line[x] = (line[x]+prev[x]) & 255
        elif ft == 3:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                line[x] = (line[x]+((a+prev[x]) >> 1)) & 255
        elif ft == 4:
            for x in range(stride):
                a = line[x-bpp] if x >= bpp else 0
                c = prev[x-bpp] if x >= bpp else 0
                line[x] = (line[x]+paeth(a, prev[x], c)) & 255
        rows.append(line); prev = line
    return dict(w=w, h=h, ch=ch, rows=rows)


def analyze(path):
    m = decode_palette_png(path)
    w, h, plte, trns, idx = m["w"], m["h"], m["plte"], m["trns"], m["idx"]
    # counts per palette index
    counts = [0]*len(plte)
    for row in idx:
        for v in row:
            counts[v] += 1
    total = w*h

    # background: corner pixels (they're almost always background)
    corners = [idx[0][0], idx[0][w-1], idx[h-1][0], idx[h-1][w-1]]
    bg = max(set(corners), key=corners.count)
    bg_transparent = any(trns[k] == 0 for k in range(len(plte)))
    transp_idxs = [k for k in range(len(plte)) if trns[k] == 0]

    print(f"image: {w} x {h} px, palette entries: {len(plte)}")
    print("palette (idx: RGB alpha  count  %):")
    for k in range(len(plte)):
        tag = []
        if k == bg: tag.append("BG(corner)")
        if trns[k] == 0: tag.append("transparent")
        r,g,b = plte[k]
        if max(r,g,b) < 70: tag.append("DARK")
        print(f"  {k:3d}: ({r:3d},{g:3d},{b:3d}) a={trns[k]:3d}  {counts[k]:7d}  {100*counts[k]/total:5.1f}%  {' '.join(tag)}")

    # foreground = anything that's not background index and not transparent
    bg_set = set(transp_idxs) | {bg}
    dark_set = {k for k in range(len(plte)) if max(plte[k]) < 70 and k not in bg_set}

    fx0 = fy0 = 10**9; fx1 = fy1 = -1
    dx0 = dy0 = 10**9; dx1 = dy1 = -1
    for y in range(h):
        row = idx[y]
        for x in range(w):
            v = row[x]
            if v not in bg_set:
                if x < fx0: fx0 = x
                if x > fx1: fx1 = x
                if y < fy0: fy0 = y
                if y > fy1: fy1 = y
                if v in dark_set:
                    if x < dx0: dx0 = x
                    if x > dx1: dx1 = x
                    if y < dy0: dy0 = y
                    if y > dy1: dy1 = y
    print(f"\nbackground index: {bg}  transparent indices: {transp_idxs}  dark(detail) indices: {sorted(dark_set)}")
    print(f"fox content bbox (px): x[{fx0},{fx1}] y[{fy0},{fy1}]  -> size {fx1-fx0+1} x {fy1-fy0+1}")
    print(f"padding around fox (px): left={fx0} right={w-1-fx1} top={fy0} bottom={h-1-fy1}")

    # ---- placement: contain-fit (no distortion), anchor image top-right to panel top-right ----
    PX0,PX1, PZ0,PZ1 = 250.0,406.0, 26.0,152.0   # panel front-face extent
    PW, PH = PX1-PX0, PZ1-PZ0
    s = min(PW/w, PH/h)                            # mm per px, contain-fit
    limit = "width" if PW/w < PH/h else "height"
    img_w_mm, img_h_mm = w*s, h*s
    # image px (px_x from left, px_y from top) -> panel mm, top-right anchored:
    #   X = PX1 - (w - px_x)*s ;  Z = PZ1 - px_y*s
    def X(px): return PX1 - (w - px)*s
    def Z(py): return PZ1 - py*s
    print(f"\ncontain-fit scale: {s:.4f} mm/px  (limited by {limit})")
    print(f"image on panel (mm): width={img_w_mm:.1f}  height={img_h_mm:.1f}")
    print(f"image canvas spans: X[{X(0):.1f},{X(w):.1f}]  Z[{Z(h):.1f},{Z(0):.1f}]")
    print(f"left blank strip: {X(0)-PX0:.1f} mm")
    print(f"FOX actually spans: X[{X(fx0):.1f},{X(fx1+1):.1f}]  Z[{Z(fy1+1):.1f},{Z(fy0):.1f}]")
    print(f"  fox gap to panel edges (mm): right={PX1-X(fx1+1):.1f} top={PZ1-Z(fy0):.1f} "
          f"left={X(fx0)-PX0:.1f} bottom={Z(fy1+1)-PZ0:.1f}")

if __name__ == "__main__":
    analyze(sys.argv[1])
