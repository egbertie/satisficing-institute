# Figma 可编辑源文件说明

> 如何将SVG导入Figma进行深度编辑

---

## 快速导入步骤

### 1. 导入SVG
1. 打开 [Figma](https://figma.com) 并创建新文件
2. 直接将 `svg/totem_timeline.svg` 或 `svg/totem_pentagon.svg` 拖拽到画布
3. SVG将以可编辑的矢量图层形式导入

### 2. 字体替换
当前SVG使用的是系统默认字体，建议替换为：
- **中文标题**：思源宋体 (Source Han Serif CN)
- **中文正文**：思源黑体 (Source Han Sans CN)
- **英文**：Playfair Display / Inter

### 3. 导出设置
编辑完成后，使用Figma导出：
```
右侧栏 → Export → 添加导出预设
- PNG: 2x, PNG
- SVG: SVG（保留编辑性）
- PDF: PDF（印刷用）
```

---

## 设计系统建议

### 颜色变量 (Color Styles)
建议创建以下颜色样式：

```
🟫 土色/EARTH    #C9A227  →  主色，用于LIU图腾
⬜ 金色/METAL    #E8E4E1  →  主色，用于SIMON图腾
🟦 水色/WATER    #1A1A2E  →  主色，用于GUANYIN图腾
🟩 木色/WOOD     #2E5C45  →  主色，用于CONFUCIUS图腾
🟥 火色/FIRE     #DC143C  →  主色，用于HUINENG图腾
```

### 文字样式 (Text Styles)
```
H1 - 标题      思源宋体 32px Bold
H2 - 副标题    思源黑体 16px Regular
Body - 正文    思源黑体 14px Regular
Caption - 说明 思源黑体 11px Regular
English - 英文 Georgia 10px Italic
```

---

## 版本控制建议

在Figma中维护两个版本：
1. **工作文件**：可编辑，包含所有图层
2. **导出文件**：扁平化，用于最终导出

命名规范：
```
五路图腾_v2.4_时间线_工作版
五路图腾_v2.4_五边形_工作版
```

---

## 打印注意事项

如需印刷：
- **色彩模式**：CMYK（SVG为RGB，需转换）
- **出血**：四周各加3mm
- **分辨率**：300dpi
- **格式**：PDF/X-4

---

*补充文档生成时间：2026-03-14*
