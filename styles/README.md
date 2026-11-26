# 风格库（`styles/`）

本目录将「视觉风格配置」从渲染代码中抽离出来，方便按题材自动匹配或随时新增自定义风格。

## 目录结构

- `styles/motion/*.json`：平面信息图 / 套模板路线（`motion/make.py`）的风格配置。
- `styles/iso/*.json`：2.5D 等轴测旅程路线（`iso/iso_journey.py`）的调色板配置。

## 风格文件结构

每个 `.json` 文件包含两部分：

1. **`meta`（供 Agent / SKILL 做风格决策用）**：
   - `name`：中文名称（如 `"石墨绿"`）
   - `route`：所属路线（`"motion"` 或 `"iso"`）
   - `mood`：气质关键词数组（如 `["科技", "极简", "工具"]`）
   - `best_for`：最适合的题材描述
   - `visual_note`：视觉特点简述

2. **主题色板字段**：
   - `motion` 路线：`bg`, `panel`, `deep`, `line`, `accent`, `accent_dim`, `on_accent`, `text`, `grey`, `grid`, `win_dark`, `win_light`, `swatches`（浅底主题可加 `"light": true`，可选 `"accent2"`）
   - `iso` 路线：`bg`, `ink`, `muted`, `rule`, `road`, `curb`, `dash`, `card`, `cardline`, `shadow`, `plinth`, `plinth_top`, `leaf`, `trunk`, `paver`, `metal`, `screen`, `dark`, `wood`, `pillar`, `mug`, `red`, `kinds`

## 如何新增一个风格

1. 复制 `styles/motion/` 或 `styles/iso/` 下最接近的一个 `.json` 文件并重命名（如 `styles/motion/ocean-blue.json`）。
2. 修改 `meta` 描述与色值（注意遵守 `docs/wechat-svg-rules.md`，仅使用纯色与透明度，不使用渐变/滤镜）。
3. 无需修改 Python 代码，生成时直接指定 `"theme": "ocean-blue"`（或 `"palette": "xxx"`）即可生效。
