# Figure Tooling for SAR Quality-Aware Scheduling Paper

## 已安装工具

| 工具 | 用途 |
|---|---|
| **SciencePlots** | 出版级 matplotlib 样式（Nature/IEEE/Science 等一键切换） |
| **style_presets.py** | 期刊风格预设 + 配置助手 |
| **figure_export.py** | 多格式出版级导出（PDF/PNG，自动 DPI/尺寸检查） |
| **color_palettes.py** | 色盲友好配色方案 |

## 快速使用

### SciencePlots 单行切换

```python
import matplotlib.pyplot as plt
import scienceplots

plt.style.use(['science', 'nature'])          # Nature 风格
plt.style.use(['science', 'ieee'])            # IEEE 风格
plt.style.use(['science', 'nature', 'cjk-sc'])  # 中文论文
```

### 出版级导出

```python
from scripts.figure_export import save_publication_figure

fig, ax = plt.subplots(figsize=(3.5, 2.625))  # Nature 单栏
ax.plot(x, y)
save_publication_figure(fig, 'fig1_example', formats=['pdf', 'png'], dpi=300)
```

### 期刊要求参考

```bash
# 需要查期刊出图规范时
Read "references/journal_requirements.md"
```

## 目录结构

```
figures/
├── styles/              # matplotlib 样式文件
│   ├── nature.mplstyle
│   ├── publication.mplstyle
│   └── presentation.mplstyle
├── scripts/             # Python 辅助脚本
│   ├── style_presets.py
│   ├── figure_export.py
│   └── color_palettes.py
└── references/          # 出版级出图参考文档
    ├── journal_requirements.md
    ├── color_palettes.md
    ├── matplotlib_examples.md
    └── publication_guidelines.md
```

## 升级现有代码

在 `gen_all_figures.py` 中替换手写 `rcParams`：

```python
# 改前
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, ...})

# 改后
plt.style.use(['science', 'nature'])
```

SciencePlots 会自动处理字体、轴线、刻度、颜色等出版级细节。