# 重建指南 (REBUILD)

狐狸浮雕面板的原始碼。**改面板或改狐狸時用這裡重新生成，不用從頭來。**

## 需要的工具
- **OpenSCAD**：`brew install --cask openscad`（headless CLI，路徑通常 `/opt/homebrew/bin/openscad`）
- **potrace**：`brew install potrace`（只有重描狐狸圖才需要）
- **python3**：只用標準庫

> 註：OpenSCAD 若被 macOS Gatekeeper 擋，執行一次 `xattr -dr com.apple.quarantine /Applications/OpenSCAD-*.app`。

## 檔案
| 檔案 | 用途 |
|---|---|
| `svg/*.svg` | 狐狸描好的向量（body/orange/white/black）。**與面板無關，通常不用重做** |
| `emboss_color.scad` | 主建模：狐狸貼上面板 → 輸出各色零件 / 一體件 / 預覽 |
| `make_3mf.py` | 把 4 個色件打包成 `fox-panel-multicolor.3mf` |
| `masks.py` / `masks_color.py` / `pnglib.py` | 從 `../sticker.PNG` 重新產生遮罩（**只有狐狸圖改了才需要**） |
| `stlbbox.py` | 檢查 STL 的三角面數與 bbox |
| `steam-logo-variant/` | 狐狸躺 Steam logo 版本的腳本（參考） |

---

## 情況 A：換面板（最常見）

1. 把新面板 STL 放好，記住路徑（下面用 `$PANEL`）。
2. **新面板尺寸/正面位置和舊的一樣** → 直接到步驟 4。
3. **不同尺寸** → 量新面板正面，更新 `emboss_color.scad` 頂部：
   - `CX` = 正面中心 X；`CZ` = 讓狐狸底部對齊你要的高度；`FOX_W` = 狐狸寬(mm)
   - 本專案面板正面在 **Y=0**、中心 **(328, 89)**、尺寸 **156×126×14.5mm**
   - 量新面板：`python3 stlbbox.py $PANEL`
4. **匯出各色零件**（在 `src/` 執行）：
   ```bash
   cd src
   OSC=/opt/homebrew/bin/openscad
   PANEL=../你的新面板.stl
   OUT=../steam-machine-fox-multicolor
   cp "$PANEL" "$OUT/1_panel.stl"
   $OSC -o "$OUT/2_fox_orange.stl" -D "PANEL_STL=\"$PANEL\"" -D 'PART="orange"' emboss_color.scad
   $OSC -o "$OUT/3_fox_white.stl"  -D "PANEL_STL=\"$PANEL\"" -D 'PART="white"'  emboss_color.scad
   $OSC -o "$OUT/4_fox_black.stl"  -D "PANEL_STL=\"$PANEL\"" -D 'PART="black"'  emboss_color.scad
   # 一體單色件（可選）：
   $OSC -o "$OUT/fox-panel-combined-single.stl" -D "PANEL_STL=\"$PANEL\"" -D 'PART="solid"' emboss_color.scad
   ```
5. **打包 3mf**：`python3 make_3mf.py`
6. **檢查**：`python3 stlbbox.py ../steam-machine-fox-multicolor/4_fox_black.stl`（狐狸底部 Z 應接近面板底邊）

## 情況 B：換狐狸圖

1. 換掉專案根目錄的 `sticker.PNG`（需為 8-bit 調色盤 PNG）。
2. **重新產生遮罩 + 描圖**：
   ```bash
   cd src
   python3 masks.py         # -> body.pbm detail.pbm
   python3 masks_color.py   # -> orange.pbm white.pbm black.pbm
   for m in body orange white black; do potrace -s -t 2 -o svg/$m.svg $m.pbm; done
   rm -f *.pbm *_view.png
   ```
3. **重新校正** `emboss_color.scad` 的 `SVG_W` / `SVG_H`（新描圖尺寸會變）：
   ```bash
   printf 'linear_extrude(1) import("svg/body.svg");\n' > /tmp/cal.scad
   $OSC -o /tmp/cal.stl /tmp/cal.scad && python3 stlbbox.py /tmp/cal.stl
   ```
   把印出來的 `size` 的 X、Y 填回 `SVG_W`、`SVG_H`。
4. 接著同情況 A 的步驟 4–6。

---

## 目前的設計參數
- 狐狸 **132mm** 寬、置中 X、**底部貼齊面板底邊**（`CZ=87.57`）
- 凸起 **1.5mm**、嵌入面板 **0.8mm**
- 顏色：橘 `#FF9C00`、白、黑；面板黑
- 列印：狐狸面朝上、面板背面貼床、建議加 Brim
