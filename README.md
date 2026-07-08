# Tinkercad — 面板浮雕設計

自訂 Steam Machine 面板的浮雕設計。**每個設計獨立一包**，共用同一塊面板毛胚與流程，方便之後持續擴充。

## 結構
```
Tinkercad/
├─ shared/
│  └─ panel-blank.stl        面板毛胚（156×126×14.5mm，所有設計共用的底）
└─ designs/
   └─ fox/                   狐狸浮雕設計 → 見 designs/fox/README.md
```

## 每個設計的內部（`designs/<名字>/`）
```
├─ README.md    摘要、參數、怎麼重建
├─ art/         來源素材（圖 + 描好的 svg）
├─ build/       建模腳本（OpenSCAD + Python，自帶工具）
├─ output/      交付檔（STL、.3mf）
└─ previews/    渲染圖
```

## 新增一個設計
1. 複製 `designs/fox` → `designs/<新名字>`
2. 換掉 `art/` 裡的圖並重描（見該設計 README 的「換狐狸圖」）
3. 改 `build/emboss.scad` 的參數（大小、位置、顏色）
4. 從 `build/` 重跑匯出 → `output/`

## 工具需求
- **OpenSCAD**：`brew install --cask openscad`
- **potrace**：`brew install potrace`（只有重描圖才需要）
- **python3**：只用標準庫
