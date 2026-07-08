"""Report triangle count + bounding box of an STL (ascii or binary)."""
import struct, sys, re

def bbox(path):
    with open(path, "rb") as f:
        d = f.read()
    lo = [1e30]*3; hi = [-1e30]*3
    if d[:5] == b"solid" and b"facet" in d[:2000]:
        n = "ascii"
        for m in re.finditer(rb"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)", d):
            for j in range(3):
                v = float(m.group(j+1)); lo[j] = min(lo[j], v); hi[j] = max(hi[j], v)
    else:
        n = struct.unpack("<I", d[80:84])[0]
        for i in range(n):
            b = 84 + i*50 + 12
            for v in range(3):
                xyz = struct.unpack("<fff", d[b+v*12:b+v*12+12])
                for j in range(3):
                    lo[j] = min(lo[j], xyz[j]); hi[j] = max(hi[j], xyz[j])
    print(f"tris={n}")
    print(f"min  {[round(x,3) for x in lo]}")
    print(f"max  {[round(x,3) for x in hi]}")
    print(f"size {[round(hi[j]-lo[j],3) for j in range(3)]}")

if __name__ == "__main__":
    bbox(sys.argv[1])
