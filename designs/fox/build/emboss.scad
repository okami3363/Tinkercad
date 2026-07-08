// Multi-colour fox embossed on the panel front. Each colour is a separate
// coplanar raised part (same height) so a slicer prints them in different
// filaments. Run from this build/ directory so the "../art/svg/..." imports resolve.
//
//   PART = "orange" | "white" | "black" | "panel" | "solid" | "preview"
//
// Swap the panel by pointing PANEL_STL at a new file (or override with
// -D 'PANEL_STL="/path/to/new.stl"'). If the new panel has a different size or
// front-face position, update CX / CZ / FOX_W (see ../README.md).

PANEL_STL = "../../../shared/panel-blank.stl";
PART = "preview";

// Calibrated import size of ../art/svg/body.svg in OpenSCAD units (72 dpi).
// RE-MEASURE if you re-trace the fox: linear_extrude(1) import("../art/svg/body.svg"); export STL; read its X/Y bbox.
SVG_W = 79.37;
SVG_H = 74.045;

FOX_W  = 132;      // fox width on panel (mm)
CX     = 328;      // front-face centre X
CZ     = 87.57;    // fox centre Z -> bottom aligned to panel bottom (Z=26) at 132mm
EMBOSS = 1.5;      // raised height (mm)
EMBED  = 0.8;      // sink into panel for fusion (mm)
FLIP_Y = 1; MIRROR_X = 1;
S = FOX_W / SVG_W;

module place2d(file) {
    scale([S*MIRROR_X, S*FLIP_Y, 1])
        translate([-SVG_W/2, -SVG_H/2, 0])
            import(file);
}
module on_front(file) {
    translate([CX, 0, CZ]) rotate([90, 0, 0])
        translate([0, 0, -EMBED])
            linear_extrude(height = EMBED + EMBOSS)
                place2d(file);
}
module orange_part() { on_front("../art/svg/orange.svg"); }
module white_part()  { on_front("../art/svg/white.svg"); }
module black_part()  { on_front("../art/svg/black.svg"); }

if      (PART == "orange") orange_part();
else if (PART == "white")  white_part();
else if (PART == "black")  black_part();
else if (PART == "panel")  import(PANEL_STL, convexity = 10);
else if (PART == "solid")  union() { import(PANEL_STL, convexity = 10); on_front("../art/svg/body.svg"); }
else {                                        // coloured preview (black panel)
    color("#1a1a1a") import(PANEL_STL, convexity = 10);
    color("#ff9c00") orange_part();
    color("#f2f2f2") white_part();
    color("#141414") black_part();
}
