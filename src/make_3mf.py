"""Pack the 4 multi-colour STL parts into one coloured .3mf (zip + 3MF XML),
oriented fox-up (panel back on bed). Paths are relative to this script.
Run:  python3 src/make_3mf.py"""
import os, struct, re, zipfile, xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
DST  = os.path.normpath(os.path.join(HERE, "..", "steam-machine-fox-multicolor"))
OUT  = os.path.join(DST, "fox-panel-multicolor.3mf")

# (file, base-material index)   materials: 0=black 1=orange 2=white
PARTS = [("1_panel.stl", 0), ("4_fox_black.stl", 0),
         ("2_fox_orange.stl", 1), ("3_fox_white.stl", 2)]

def parse_stl(path):
    d = open(path, "rb").read()
    tris = []
    if d[:5] == b"solid" and b"facet" in d[:2000]:
        v = re.findall(rb"vertex\s+([-\d.eE+]+)\s+([-\d.eE+]+)\s+([-\d.eE+]+)", d)
        for i in range(0, len(v), 3):
            tris.append(tuple(tuple(float(c) for c in v[i+k]) for k in range(3)))
    else:
        n = struct.unpack("<I", d[80:84])[0]
        for i in range(n):
            b = 84 + i*50 + 12
            tris.append(tuple(struct.unpack("<fff", d[b+k*12:b+(k+1)*12]) for k in range(3)))
    return tris

def tf(v):                       # fox-up: panel back on bed, centred on plate
    x, y, z = v
    return (x - 328.0, z - 89.0, 14.5 - y)

def mesh_xml(tris):
    idx = {}; verts = []; tl = []
    def vid(v):
        v = tf(v); key = (round(v[0], 3), round(v[1], 3), round(v[2], 3))
        j = idx.get(key)
        if j is None:
            j = len(verts); idx[key] = j; verts.append(key)
        return j
    for t in tris:
        a, b, c = vid(t[0]), vid(t[1]), vid(t[2])
        if a != b and b != c and a != c:
            tl.append(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>')
    vl = "".join(f'<vertex x="{x:.3f}" y="{y:.3f}" z="{z:.3f}"/>' for x, y, z in verts)
    return f"<vertices>{vl}</vertices><triangles>{''.join(tl)}</triangles>"

objects = []; comps = []; oid = 2
for fname, mat in PARTS:
    mx = mesh_xml(parse_stl(os.path.join(DST, fname)))
    objects.append(f'<object id="{oid}" type="model" pid="1" pindex="{mat}"><mesh>{mx}</mesh></object>')
    comps.append(f'<component objectid="{oid}"/>'); oid += 1

group = f'<object id="100" type="model"><components>{"".join(comps)}</components></object>'
model = ('<?xml version="1.0" encoding="UTF-8"?>'
  '<model unit="millimeter" xml:lang="en-US"'
  ' xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
  ' xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">'
  '<resources><basematerials id="1">'
  '<base name="Black" displaycolor="#1A1A1AFF"/>'
  '<base name="Orange" displaycolor="#FF9C00FF"/>'
  '<base name="White" displaycolor="#F2F2F2FF"/>'
  '</basematerials>' + "".join(objects) + group +
  '</resources><build><item objectid="100"/></build></model>')
ET.fromstring(model)   # validate

CT = ('<?xml version="1.0" encoding="UTF-8"?>'
  '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
  '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8"?>'
  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
  '<Relationship Target="/3D/3dmodel.model" Id="rel0"'
  ' Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", CT)
    z.writestr("_rels/.rels", RELS)
    z.writestr("3D/3dmodel.model", model)
print("wrote", OUT)
