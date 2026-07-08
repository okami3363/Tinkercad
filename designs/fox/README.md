# 狐狸浮雕面板

橘/白/黑三色狐狸浮雕，貼在黑色 Steam Machine 面板上。另有「狐狸躺 Steam logo」變體。

## 成品在哪
- **`output/multicolor/`** — 主版本：黑面板 + 原色狐狸
  - `fox-panel-multicolor.3mf` — 一次匯入的多色檔（**送代印用這個**）
  - `1_panel` / `2_fox_orange` / `3_fox_white` / `4_fox_black` `.stl` — AMS 分色件
  - `fox-panel-combined-single.stl` — 一體單色件（看整體/單色印）
  - `README.md` — 切片與列印說明
- **`output/steam-logo/`** — 變體：狐狸躺 Steam logo（黑面板 + 藍圓 + 白活塞）
- **`previews/`** — 各版本渲染圖

## 設計參數（目前值）
- 狐狸 **132mm** 寬、置中 X、**底部貼齊面板底邊**（`CZ=87.57`）
- 凸起 **1.5mm**、嵌入 **0.8mm**；顏色：橘 `#FF9C00`、白、黑；面板黑
- 面板正面 **Y=0**、中心 **(328, 89)**、尺寸 **156×126×14.5mm**
- 列印：狐狸面朝上、面板背面貼床、建議加 Brim

---

## 重建

### 換面板（最常見）
1. 換掉 `shared/panel-blank.stl`（或用 `-D 'PANEL_STL="路徑"'` 覆蓋）。
2. 若新面板**尺寸/正面位置不同** → 改 `build/emboss.scad` 的 `CX / CZ / FOX_W`（用 `build/stlbbox.py` 量新面板）。
3. 從 `build/` 匯出：
   ```bash
   cd designs/fox/build
   OSC=/opt/homebrew/bin/openscad
   OUT=../output/multicolor
   cp ../../../shared/panel-blank.stl "$OUT/1_panel.stl"
   $OSC -o "$OUT/2_fox_orange.stl" -D 'PART="orange"' emboss.scad
   $OSC -o "$OUT/3_fox_white.stl"  -D 'PART="white"'  emboss.scad
   $OSC -o "$OUT/4_fox_black.stl"  -D 'PART="black"'  emboss.scad
   $OSC -o "$OUT/fox-panel-combined-single.stl" -D 'PART="solid"' emboss.scad
   python3 make_3mf.py
   ```
4. 檢查：`python3 stlbbox.py ../output/multicolor/4_fox_black.stl`

### 換狐狸圖
1. 換掉 `art/sticker.PNG`（需 8-bit 調色盤 PNG）。
2. 重描（在 `build/`）：
   ```bash
   cd designs/fox/build
   python3 masks.py
   python3 masks_color.py
   for m in body orange white black; do potrace -s -t 2 -o ../art/svg/$m.svg $m.pbm; done
   rm -f *.pbm *_view.png
   ```
3. 校正 `build/emboss.scad` 的 `SVG_W / SVG_H`（新描圖尺寸會變）：
   ```bash
   printf 'linear_extrude(1) import("../art/svg/body.svg");\n' > /tmp/cal.scad
   $OSC -o /tmp/cal.stl /tmp/cal.scad && python3 stlbbox.py /tmp/cal.stl
   # 把 size 的 X、Y 填回 SVG_W、SVG_H
   ```
4. 接著同「換面板」步驟 3–4。

### Steam logo 變體
`build/emboss-steam-logo.scad`（PART：`panel/blue/white_logo/orange/fox_white/black`），輸出到 `output/steam-logo/`。
> 注意：`output/steam-logo/` 內含描自 Valve Steam 商標的幾何 —— 個人自用沒問題，公開分享請自行斟酌。

## build/ 檔案
| 檔 | 用途 |
|---|---|
| `emboss.scad` | 主建模（各色件 / 一體件 / 預覽） |
| `emboss-steam-logo.scad` | Steam logo 變體 |
| `masks.py` / `masks_color.py` | 重描狐狸（改圖才需要） |
| `make_3mf.py` | 打包多色 `.3mf` |
| `pnglib.py` / `stlbbox.py` | PNG 解碼庫 / STL 檢查 |
| `steam_piston.py` | 從 Steam logo 圖抽活塞（需原圖） |
