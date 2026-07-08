// Black panel + flat Steam logo (blue circle + white ring + white piston) with
// a raised 132mm multi-colour fox lounging on top. Flat layer sits flush in a
// shallow pocket (Y 0..POCKET); fox is raised (Y 0..-EMBOSS) so it covers the
// logo where they overlap (the white piston stays behind the fox).

PANEL_STL = "/Users/fetc_imac24/Documents/Projects/Tinkercad/steam-machine-front-panel-blank-customizable-stl.stl";
PART = "preview";

// ---- circle / logo geometry ----
CCX = 328; CCZ = 89;          // circle centre on panel front
CIRC_D = 115; RING_W = 3; POCKET = 1.0;
K = 57.5/220;                 // logo-image px -> panel mm  (circle R_img=220px -> 57.5mm)
PW = 367*K; PH = 283*K;       // piston bbox size (mm)
PDX = -28.5*K;                // piston centre offset from circle centre, X (mm)
PDZ = -2.5*K;                 // piston centre offset, Z (mm)  [+img-down -> -Z]
PFLIP = 1;                    // flip piston vertically if render shows upside-down

// ---- fox ----
SVG_W = 79.37; SVG_H = 74.045; FOX_W = 132; FCX = 328; FCZ = 89;
EMBOSS = 1.5; EMBED = 0.3; FOXFLIP = 1;
S = FOX_W / SVG_W;

// ---------- flat Steam-logo layer (2D in u-v = local X-Z) ----------
module piston2d() {
    translate([PDX, PDZ]) scale([1, PFLIP])
        resize([PW, PH], auto=false)
            import("steam_piston.svg", center=true);
}
module blue2d() { difference() { circle(d=CIRC_D, $fn=240); piston2d(); } }
module ring2d() { difference() { circle(d=CIRC_D+2*RING_W, $fn=240); circle(d=CIRC_D, $fn=240); } }
module white2d(){ piston2d(); ring2d(); }

module flat() {   // extrude a 2D u-v shape into the pocket (panel Y 0..POCKET)
    translate([CCX, 0, CCZ]) rotate([90, 0, 0])
        translate([0, 0, -POCKET]) linear_extrude(POCKET) children();
}
module blue_flat()  { flat() blue2d(); }
module white_flat() { flat() white2d(); }

// ---------- panel with pocket ----------
module pocket_cut() {
    translate([CCX, -0.02, CCZ]) rotate([-90, 0, 0])
        cylinder(h = POCKET+0.04, d = CIRC_D+2*RING_W, $fn=240);
}
module panel_black() { difference() { import(PANEL_STL, convexity=10); pocket_cut(); } }

// ---------- raised fox ----------
module fox_place(f) { scale([S, S*FOXFLIP, 1]) translate([-SVG_W/2, -SVG_H/2, 0]) import(f); }
module fox_on_front(f) {
    translate([FCX, 0, FCZ]) rotate([90, 0, 0])
        translate([0, 0, -EMBED]) linear_extrude(EMBED+EMBOSS) fox_place(f);
}
module fox_orange() { fox_on_front("orange.svg"); }
module fox_white()  { fox_on_front("white.svg"); }
module fox_black()  { fox_on_front("black.svg"); }

if      (PART == "panel")      panel_black();
else if (PART == "blue")       blue_flat();
else if (PART == "white_logo") white_flat();
else if (PART == "orange")     fox_orange();
else if (PART == "fox_white")  fox_white();
else if (PART == "black")      fox_black();
else if (PART == "logo") {                       // flat layer only, no panel (fast check)
    color("#1b3a6b") blue_flat();
    color("#f2f2f2") white_flat();
}
else {                                            // full preview
    color("#1a1a1a") panel_black();
    color("#1b3a6b") blue_flat();
    color("#f2f2f2") white_flat();
    color("#ff9c00") fox_orange();
    color("#f7f7f7") fox_white();
    color("#141414") fox_black();
}
