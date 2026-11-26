"""配色主题加载器。

从仓库根目录 `styles/motion/*.json` 动态加载所有主题，新增风格只需放入新 JSON，无需改动本文件。

字段：
  bg 底色 · panel 面板 · deep 更深的面（影子/代码块/终端）· line 分隔线和柱子底
  accent 主强调色 · accent_dim 强调色压暗一档（亮底主题用来写字）· on_accent 强调色块上的字
  text 主文字 · grey 次要文字 · grid 网格透明度
  win_dark / win_light 产品窗口的暗/亮两套皮肤（换肤场景从 light 换到 dark）
  swatches 换肤场景里展示的 7 个色点
"""
import json
from pathlib import Path

_STYLES_DIR = Path(__file__).resolve().parent.parent / "styles" / "motion"


def _load_themes():
    loaded = {}
    if not _STYLES_DIR.is_dir():
        return loaded
    for path in sorted(_STYLES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("meta", None)
        loaded[path.stem] = data
    return loaded


THEMES = _load_themes()


def get(name):
    if name not in THEMES:
        raise SystemExit(f"没有主题「{name}」，可选：{' / '.join(THEMES)}")
    return THEMES[name]


def list_meta():
    """返回所有风格的元信息，供脚本或决策流程检索。"""
    items = {}
    if not _STYLES_DIR.is_dir():
        return items
    for path in sorted(_STYLES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        items[path.stem] = data.get("meta", {})
    return items
