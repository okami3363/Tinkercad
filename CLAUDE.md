# CLAUDE.md — 專案 AI 上手指南

給未來的 AI session：這份是快速上手，**動手改東西前先讀 `designs/fox/README.md`**（有完整重建步驟）。

## 這是什麼
自訂 **Steam Machine 面板浮雕**設計。流程：一張圖 → 描成向量(SVG) → OpenSCAD 把圖壓到面板正面 → 匯出多色 STL + `.3mf` 送 3D 列印/代印。每個設計獨立在 `designs/<名字>/`，共用 `shared/panel-blank.stl`。

## 結構
```
README.md                    repo 總覽 + 如何新增設計
shared/panel-blank.stl       面板毛胚（所有設計共用）
designs/fox/
├─ README.md                 ★ 設計說明 + 重建步驟（動手前先讀）
├─ art/   sticker.PNG + svg/  來源圖 + 描好的向量
├─ build/ emboss.scad 等      建模腳本（自帶工具）
├─ output/ multicolor/ steam-logo/   交付 STL + .3mf
└─ previews/                 渲染圖（設計歷程）
```

## 環境與工具（重要）
- **OpenSCAD**：`/opt/homebrew/bin/openscad`（headless CLI；是 x86_64 走 Rosetta）。若被 Gatekeeper 擋：`xattr -dr com.apple.quarantine /Applications/OpenSCAD-*.app`。可 headless 出 STL 與 PNG。
- **potrace**：`/opt/homebrew/bin/potrace`（點陣→向量；只有換圖才需要）。
- **python3**：**只有標準庫**。沒有 numpy / PIL / trimesh。PNG 用自寫的 `build/pnglib.py`（只解 8-bit palette 與 RGB）；STL 檢查用 `build/stlbbox.py`。
- 暫存/中間檔請放 scratchpad，別汙染專案。
- 回應一律**繁體中文**（見全域 `~/.claude/CLAUDE.md`）。

## 常見任務
**換面板 / 改狐狸大小・位置**（改 `build/emboss.scad` 的 `PANEL_STL / CX / CZ / FOX_W`，從 `build/` 重跑）：
```bash
cd designs/fox/build
OSC=/opt/homebrew/bin/openscad; OUT=../output/multicolor
cp ../../../shared/panel-blank.stl "$OUT/1_panel.stl"
$OSC -o "$OUT/2_fox_orange.stl" -D 'PART="orange"' emboss.scad
$OSC -o "$OUT/3_fox_white.stl"  -D 'PART="white"'  emboss.scad
$OSC -o "$OUT/4_fox_black.stl"  -D 'PART="black"'  emboss.scad
$OSC -o "$OUT/fox-panel-combined-single.stl" -D 'PART="solid"' emboss.scad
python3 make_3mf.py
```
**看預覽**（彩色，黑面板）：
```bash
$OSC -o /tmp/p.png -D 'PART="preview"' --projection=o --camera=0,0,0,90,0,0,0 --viewall --autocenter --imgsize=900,740 emboss.scad
```
**換狐狸圖 / 新增設計** → 見 `designs/fox/README.md` 與根 `README.md`。

## 關鍵幾何事實
- 面板 **156×126×14.5mm**；正面平面在 **Y=0**（法線 −Y、朝觀看者）、中心 **(X=328, Z=89)**、底邊 Z=26、頂邊 Z=152。座標：X=寬、Y=深、Z=高。
- 狐狸凸起往 **−Y（朝外）**；列印時**狐狸面朝上、面板背面貼床**（背面接觸小，建議 Brim）。
- 目前參數：狐狸 **132mm 寬**、置中 X、**底部貼齊面板底邊 `CZ=87.57`**、凸起 1.5mm、嵌入 0.8mm；顏色 橘 `#FF9C00`／白／黑，面板黑。
- **OpenSCAD 匯入 potrace SVG = 72 dpi**（1px≈0.3528mm）。`body.svg` 匯入尺寸 = **79.37×74.045** = `SVG_W/SVG_H`。**重描圖後必須重量這兩個值**（`linear_extrude(1) import("../art/svg/body.svg")` 匯出後看 bbox）。

## 地雷
- `emboss.scad` 用相對路徑，**必須從 `build/` 執行**（`../../../shared`、`../art/svg`）。
- OpenSCAD 匯入 SVG 有 y 軸翻轉問題 → 用 `FLIP_Y`（目前 =1 正確）。改動後**渲染預覽確認方向**再定案。
- 每個色件是獨立 `linear_extrude`（各自 manifold、密合）。**別**改用 `body − white − black` 的 3D 布林（會產生非-manifold）。
- 分色是「最近參考色」分類（見 `masks_color.py`：橘/白/黑）。
- `.3mf`：`make_3mf.py` 產生的是**通用 3MF**（幾何+色，送代印可用）；OrcaSlicer「另存專案」的 `-self.3mf` 才是完整專案檔。
- `designs/fox/output/steam-logo/` 內含 **Valve Steam 商標衍生幾何** —— 個人自用沒問題，若要放公開 repo 請提醒使用者斟酌。

## 驗證
改完務必：`python3 build/stlbbox.py <out.stl>`（確認 bbox / 狐狸底部 Z=26），或 `PART="preview"` 渲染看一眼。
