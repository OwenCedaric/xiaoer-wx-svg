#!/usr/bin/env python3
"""生成演示站 site/dist：Chronicle 编年体风格首页、主题广场（/themes/）、粘贴台（/paste/）、模板演示页、sitemap / robots / llms.txt。

  python3 site/build.py            # 先跑一遍各模板生成 out/，再拼站
  WXSVG_CASES=cases.json python3 site/build.py   # 另加首页「真实作品」栏（作品文件不进仓库）

扩展主题：往 styles/motion/*.json 或 styles/iso/*.json 放入新配置文件，重新运行本脚本即可自动出现在 /themes/ 页面。
原作者：Xiaoer Omia (https://svg.xiaoeromia.com) · Chronicle 界面与主题重构：Cedaric
"""
import asyncio
import json
import os
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = HERE / "dist"
OUT = ROOT / "out"
STYLES_DIR = ROOT / "styles"
BASE = "https://svg.xiaoeromia.com"
REPO = "https://github.com/OwenCedaric/xiaoer-wx-svg"
UPSTREAM_REPO = "https://github.com/Jane-xiaoer/xiaoer-wx-svg"
OMIA = "https://xiaoeromia.com"

# slug, 名称, 路线, 适合, 生成命令（相对仓库根）, 输出目录名, 缩略图截哪一秒
DEMOS = [
    ("chronicle-essay", "编年体 · 深度长文", "套模板 · Chronicle", "深度长文、思想随笔、人物访谈：80% 几何圆、空心描边大字、虚线章节与双人结构化对话（主题作者：Cedaric）",
     ["motion/make.py", "templates/storyboards/编年体-深度长文示例.json"], "编年体-深度长文示例", 14),
    ("isometric-journey", "等轴测旅程 · 3D", "等轴测旅程", "流程、路线、链路：Z 字公路串起一站站 2.5D 小场景，零件一块块拼起来，光点沿路跑；结尾带建议卡和工具墙",
     ["iso/iso_journey.py", "templates/storyboards/等轴测-小耳的四台电脑.json"], "等轴测-小耳的四台电脑", 40),
    ("fm-laundry", "等轴测 · 产品故事（带图片帧）", "等轴测旅程", "有真实 3D 资产或作品图的产品：浪漫开场问一句、角色说话泡泡、一站站真帧动画、作品一幅幅晾上绳子、点一下猜答案、结尾大网址",
     ["iso/iso_journey.py", "templates/storyboards/等轴测-小耳FM洗衣房.json", "--grow", "--speed", "0.8"], "等轴测-小耳FM洗衣房", 14),
    ("product-launch", "产品发布 · 8 屏", "套模板", "软件产品：一堆东西被吸成品牌、产品窗口长出来、数字滚动、价格卡",
     ["motion/make.py", "templates/storyboards/产品-Omia-8屏.json"], "产品-Omia-8屏", 70),
    ("hardware-app", "硬件 + App · 带互动", "套模板", "硬件产品：账单吐出来盖章、设备蓝牙同步、点一下开会字幕循环冒出",
     ["motion/make.py", "templates/storyboards/硬件加App-录音卡-带互动.json"], "硬件加App-录音卡-带互动", 70),
    ("methodology", "方法论 · 6 屏", "套模板", "方法、清单、教程：线稿自己画、三个大字砸下、要点卡片",
     ["motion/make.py", "templates/storyboards/方法论-番茄工作法.json"], "方法论-番茄工作法", 60),
    ("minimal", "最小示例 · 3 屏", "底层格式", "直接写元素和时间轴：画圈、放大、逐字出现，适合想自己从零搭的人",
     ["wxsvg.py", "templates/raw/最小示例-3屏.json"], "最小示例-3屏", 20),
]

CSS = """
:root {
  --c-bg-light: #fbf9f6;
  --c-bg-dark: #1c1f26;
  --c-ink-light: #3d4451;
  --c-ink-dark: #d2d6dd;
  --c-muted-light: #757d8a;
  --c-muted-dark: #a0a7b4;
  --c-accent-light: #82a1b9;
  --c-accent-dark: #9cb4cd;
  --c-fill-light: rgba(61, 68, 81, 0.06);
  --c-fill-dark: rgba(210, 214, 221, 0.08);
  --c-line-light: rgba(61, 68, 81, 0.20);
  --c-line-dark: rgba(210, 214, 221, 0.20);
  --c-stroke-light: rgba(61, 68, 81, 0.60);
  --c-stroke-dark: rgba(210, 214, 221, 0.60);

  --bg: var(--c-bg-light);
  --ink: var(--c-ink-light);
  --muted: var(--c-muted-light);
  --accent: var(--c-accent-light);
  --fill: var(--c-fill-light);
  --line: var(--c-line-light);
  --stroke-tint: var(--c-stroke-light);
  --sans: -apple-system, "PingFang SC", "Noto Sans SC", "Microsoft YaHei", sans-serif;
  --serif: "Songti SC", "Noto Serif CJK SC", "STSong", Georgia, serif;
  --mono: "SFMono-Regular", Menlo, Consolas, monospace;

  color-scheme: light dark;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: var(--c-bg-dark);
    --ink: var(--c-ink-dark);
    --muted: var(--c-muted-dark);
    --accent: var(--c-accent-dark);
    --fill: var(--c-fill-dark);
    --line: var(--c-line-dark);
    --stroke-tint: var(--c-stroke-dark);
  }
}

@supports (color: light-dark(white, black)) {
  :root {
    --bg: light-dark(var(--c-bg-light), var(--c-bg-dark));
    --ink: light-dark(var(--c-ink-light), var(--c-ink-dark));
    --muted: light-dark(var(--c-muted-light), var(--c-muted-dark));
    --accent: light-dark(var(--c-accent-light), var(--c-accent-dark));
    --fill: light-dark(var(--c-fill-light), var(--c-fill-dark));
    --line: light-dark(var(--c-line-light), var(--c-line-dark));
    --stroke-tint: light-dark(var(--c-stroke-light), var(--c-stroke-dark));
  }
}

:root:has(> head > meta[name="color-scheme"][content="dark"]) { color-scheme: dark; }
:root:has(> head > meta[name="color-scheme"][content="light"]) { color-scheme: light; }

* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--sans);
  font-weight: 300;
  line-height: 1.85;
  text-align: left;
  overflow-wrap: break-word;
}
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; text-underline-offset: 4px; }
h1, h2, h3, .serif { font-family: var(--serif); font-weight: 600; color: var(--ink); }
.wrap { max-width: 944px; margin: 0 auto; padding: 0 24px; }
.mono {
  font-family: var(--mono);
  letter-spacing: 0.14em;
  font-size: 12px;
  color: var(--accent);
  text-transform: uppercase;
  font-weight: 600;
}

/* Nav */
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 22px 0;
  border-bottom: 1px solid var(--line);
}
.brand { font-family: var(--serif); font-weight: 700; font-size: 18px; color: var(--ink); letter-spacing: 0.04em; }
.nav-links { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.nav-links a { color: var(--ink); font-size: 14px; font-weight: 400; }
.nav-links a[aria-current="page"] { color: var(--accent); font-weight: 600; }
.theme-btn {
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 4px 10px;
  font-size: 12px;
  font-family: var(--mono);
  cursor: pointer;
}
.theme-btn:hover { color: var(--ink); border-color: var(--accent); }

/* Buttons (flat, no drop shadow) */
.btn {
  display: inline-block;
  padding: 10px 20px;
  border-radius: 4px;
  background: var(--ink);
  color: var(--bg);
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--ink);
  cursor: pointer;
  font-family: var(--sans);
  text-decoration: none;
  transition: opacity 0.15s ease;
}
.btn:hover { opacity: 0.85; text-decoration: none; }
.btn.ghost { background: transparent; color: var(--ink); border: 1px solid var(--line); }
.btn.ghost:hover { border-color: var(--accent); color: var(--accent); }
.btn.active { background: var(--accent); border-color: var(--accent); color: var(--bg); }

/* Chronicle Hero & Geometric Anchor */
.hero-stage {
  position: relative;
  padding: 72px 0 48px;
  display: grid;
  grid-template-columns: 1fr 375px;
  gap: 56px;
  align-items: center;
}
.hero-circle {
  position: absolute;
  left: -120px;
  top: 24px;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  border: 1px solid var(--line);
  pointer-events: none;
  z-index: 0;
}
.hero-stage > * { position: relative; z-index: 1; }
.hollow {
  font-family: var(--serif);
  font-weight: 700;
  color: transparent;
  -webkit-text-stroke: 1px var(--stroke-tint);
  line-height: 1.0;
}

/* Section Break */
.sec-break {
  position: relative;
  margin: 96px 0 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
  text-align: center;
}
.sec-break::before, .sec-break::after {
  content: "";
  flex: 1;
  border-top: 1px dashed var(--line);
}
.sec-break h2 {
  margin: 0;
  font-size: clamp(26px, 3vw, 34px);
  line-height: 1.2;
  position: relative;
  z-index: 1;
}
.sec-break .wm {
  position: absolute;
  font-family: var(--serif);
  font-size: 120px;
  font-weight: 700;
  color: var(--ink);
  opacity: 0.04;
  pointer-events: none;
  user-select: none;
  line-height: 1;
}
@media (max-width: 480px) {
  .sec-break::before, .sec-break::after { display: none; }
  .sec-break { margin: 64px 0 32px; }
}

/* Epigraph */
.epigraph {
  max-width: 660px;
  margin: 80px auto;
  text-align: center;
  font-family: var(--serif);
  font-style: italic;
  font-size: 18px;
  color: var(--muted);
  line-height: 1.85;
}

/* Phone preview */
.phone {
  width: 375px;
  max-width: 100%;
  background: #14161b;
  border: 1px solid var(--line);
  border-radius: 26px;
  padding: 10px;
}
.screen {
  background: #fff;
  border-radius: 18px;
  overflow: hidden;
  height: 680px;
  overflow-y: auto;
}
.screen h1 { font-size: 18px; line-height: 1.4; margin: 0; padding: 16px 16px 4px; color: #111; }
.screen .meta { font-size: 12px; color: #888; padding: 0 16px 12px; }

/* Cards (zero physical drop shadow, subtle fill + hairline border) */
.grid-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 24px;
}
.card {
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 6px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: border-color 0.2s ease;
}
.card:hover { border-color: var(--accent); text-decoration: none; }
.card-body { padding: 18px 20px 20px; flex: 1; display: flex; flex-direction: column; gap: 8px; }
.card-title { font-family: var(--serif); font-size: 20px; font-weight: 600; color: var(--ink); margin: 0; line-height: 1.35; }
.card-desc { color: var(--muted); font-size: 14px; line-height: 1.65; margin: 0; }

/* Structured Chat Box (Chronicle 2.5) */
.chat-box {
  max-width: 608px;
  margin: 0 auto;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 12px 0;
}
.chat-box::before {
  content: "";
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 1px;
  background: var(--line);
}
.bubble {
  max-width: 85%;
  padding: 14px 18px;
  font-size: 15px;
  line-height: 1.75;
  position: relative;
  z-index: 1;
}
.bubble.left {
  align-self: flex-start;
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 2px 10px 10px 10px;
}
.bubble.right {
  align-self: flex-end;
  background: var(--fill);
  border-radius: 10px 2px 10px 10px;
}
@media (max-width: 640px) {
  .chat-box::before { display: none; }
  .bubble { max-width: 90%; }
}

/* Theme Swatches & Tags */
.swatches { display: flex; gap: 8px; align-items: center; }
.swatch { width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--line); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 3px;
  background: var(--fill);
  color: var(--muted);
}

/* Coda & Footer */
.coda {
  margin: 96px 0 40px;
  text-align: center;
}
.coda-row {
  font-family: var(--serif);
  font-size: 14px;
  letter-spacing: 0.14em;
  color: var(--muted);
  text-transform: uppercase;
}
.coda-mark { font-size: clamp(64px, 10vw, 104px); margin: 20px 0; display: block; }
footer {
  border-top: 1px solid var(--line);
  margin-top: 40px;
  padding: 36px 0 120px;
  color: var(--muted);
  font-size: 14px;
  line-height: 1.85;
}

@media (max-width: 900px) {
  .hero-stage { grid-template-columns: 1fr; padding-top: 40px; }
  .three-col { grid-template-columns: 1fr !important; }
  .demo-grid { grid-template-columns: 1fr !important; }
}
"""

THEME_HEAD_SCRIPT = """<meta name="color-scheme" content="light dark">
<script>
try {
  const s = localStorage.getItem("color-scheme");
  if (s === "light" || s === "dark") document.querySelector('meta[name="color-scheme"]').content = s;
} catch (e) {}
</script>"""

THEME_TOGGLE_JS = """
(function() {
  const meta = document.querySelector('meta[name="color-scheme"]');
  const btn = document.getElementById('theme-toggle');
  if (!meta || !btn) return;
  const mq = matchMedia('(prefers-color-scheme: dark)');
  function currentRendered() {
    if (meta.content === 'light' || meta.content === 'dark') return meta.content;
    return mq.matches ? 'dark' : 'light';
  }
  function renderLabel() {
    const mode = currentRendered();
    btn.textContent = mode === 'dark' ? 'LIGHT' : 'DARK';
    btn.setAttribute('aria-label', mode === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  }
  btn.addEventListener('click', () => {
    const target = currentRendered() === 'dark' ? 'light' : 'dark';
    const sys = mq.matches ? 'dark' : 'light';
    try {
      if (target === sys) localStorage.removeItem('color-scheme');
      else localStorage.setItem('color-scheme', target);
    } catch (e) {}
    meta.content = target === sys ? 'light dark' : target;
    renderLabel();
  });
  addEventListener('storage', (e) => {
    if (e.key === 'color-scheme') {
      meta.content = (e.newValue === 'light' || e.newValue === 'dark') ? e.newValue : 'light dark';
      renderLabel();
    }
  });
  mq.addEventListener('change', renderLabel);
  renderLabel();
})();
"""

COPY_JS = """
function copyHtml(html,ok,fail){
  const done=()=>ok&&ok();
  if(navigator.clipboard&&window.ClipboardItem){
    navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([html],{type:'text/html'}),'text/plain':new Blob(['请在公众号编辑器里粘贴'],{type:'text/plain'})})]).then(done,()=>legacy());
  }else legacy();
  function legacy(){const box=document.createElement('div');box.contentEditable='true';box.style.cssText='position:fixed;left:-9999px;top:0;width:375px';
    box.innerHTML=html;document.body.appendChild(box);const r=document.createRange();r.selectNodeContents(box);
    const s=getSelection();s.removeAllRanges();s.addRange(r);const k=document.execCommand('copy');s.removeAllRanges();box.remove();k?done():(fail&&fail());}
}
"""


def load_all_styles():
    """扫描 styles/motion/*.json 与 styles/iso/*.json，供 /themes/ 页面动态渲染。"""
    items = []
    for route in ("motion", "iso"):
        d = STYLES_DIR / route
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.json")):
            raw = json.loads(p.read_text(encoding="utf-8"))
            meta = raw.get("meta", {})
            if route == "motion":
                swatches = [raw.get("bg"), raw.get("panel"), raw.get("text"), raw.get("grey"), raw.get("accent")]
            else:
                swatches = [raw.get("bg"), raw.get("card"), raw.get("ink"), raw.get("muted"), raw.get("red")]
            items.append({
                "id": p.stem,
                "route": meta.get("route", route),
                "name": meta.get("name", p.stem),
                "author": meta.get("author", "Xiaoer Omia"),
                "source": meta.get("source", ""),
                "mood": meta.get("mood", []),
                "best_for": meta.get("best_for", ""),
                "visual_note": meta.get("visual_note", ""),
                "bg": raw.get("bg", "#fbf9f6"),
                "panel": raw.get("panel") or raw.get("card") or "#f1efec",
                "ink": raw.get("text") or raw.get("ink") or "#3d4451",
                "muted": raw.get("grey") or raw.get("muted") or "#757d8a",
                "accent": raw.get("accent") or raw.get("red") or "#82a1b9",
                "swatches": [c for c in swatches if c],
                "file": f"styles/{route}/{p.name}",
            })
    return items


def head(title, desc, path, index=True, extra=""):
    robots = "index,follow" if index else "noindex,nofollow"
    return f"""<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
{THEME_HEAD_SCRIPT}
<meta name="referrer" content="no-referrer">
<meta name="robots" content="{robots}">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{BASE}{path}">
<meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(desc)}">
<meta property="og:site_name" content="小耳公众号SVG · Xiaoer Omia"><meta property="og:url" content="{BASE}{path}">
<meta property="og:image" content="{BASE}/og.jpg">
<style>{CSS}</style>{extra}</head><body>"""


def nav(active=""):
    def link(href, label, key):
        cur = ' aria-current="page"' if active == key else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    return f"""<div class="wrap"><nav>
  <a href="/" class="brand">小耳公众号SVG</a>
  <div class="nav-links">
    {link("/#works", "作品", "works")}
    {link("/#templates", "模板", "templates")}
    {link("/themes/", "主题库", "themes")}
    {link("/paste/", "粘贴台", "paste")}
    <a href="{REPO}">GitHub</a>
    <button class="theme-btn" id="theme-toggle" type="button">DARK</button>
  </div>
</nav></div>"""


FOOT = f"""<div class="wrap">
<div class="coda">
  <div class="coda-row">CHRONICLE EDITION</div>
  <span class="hollow coda-mark">静</span>
  <div class="coda-row">VACUUM AS RHYTHM</div>
</div>
<footer>
  <div>原作与引擎：<a href="{OMIA}">Xiaoer Omia</a>（<a href="{UPSTREAM_REPO}">Jane-xiaoer/xiaoer-wx-svg</a>）· Chronicle 界面与主题重构：<strong>Cedaric</strong>（<a href="{REPO}">OwenCedaric/xiaoer-wx-svg</a>）</div>
  <div style="margin-top:6px">代码 MIT 开源 · 推到草稿箱 ≠ 发布，发布永远由你自己点。</div>
</footer></div><script>{THEME_TOGGLE_JS}</script>"""


def demo_page(slug, name, route, fit, article, sb_path=""):
    title = f"{name} · 公众号 SVG 动效模板 · 小耳公众号SVG"
    desc = f"{name}：{fit}。纯 SVG，公众号原生支持，可一键复制到公众号编辑器。"
    return head(title, desc, f"/t/{slug}/") + nav("templates") + f"""
<div class="wrap demo-grid" style="display:grid;grid-template-columns:385px 1fr;gap:48px;padding-top:48px;align-items:start">
  <div>
    <div class="phone"><div class="screen" id="screen"><h1>{escape(name)}</h1><div class="meta">演示 · 动画从打开那一刻开始</div><div id="art"></div></div></div>
    <p style="text-align:center;margin-top:14px"><button class="btn ghost" onclick="replay()">重播</button></p>
  </div>
  <div>
    <div class="mono">{escape(route)}</div>
    <h1 style="font-size:34px;margin:8px 0 12px;line-height:1.25">{escape(name)}</h1>
    <p style="color:var(--muted);font-size:16px">{escape(fit)}</p>
    <p style="margin:24px 0"><button class="btn" id="cp" onclick="cp()">复制这个演示到公众号</button> <span id="msg" style="color:var(--accent);margin-left:10px;font-size:14px"></span></p>
    <h3 style="margin-top:48px;font-size:20px">想用这个模板做你自己的内容</h3>
    <p style="color:var(--muted);font-size:15px">把仓库交给你的 AI agent（Claude Code、Codex、Cursor……），说：</p>
    <pre id="ask" style="white-space:pre-wrap;background:var(--fill);border:1px solid var(--line);border-radius:4px;padding:16px;font-size:13px;font-family:var(--mono);line-height:1.6">用 {REPO} 的「{escape(route)}」{f"（照 {escape(sb_path)} 改）" if sb_path else ""}给我做一篇公众号 SVG 动效长图，题材是：____，资料在：____</pre>
    <p><button class="btn ghost" onclick="cpText()">复制这句话</button> <a class="btn ghost" href="/themes/" style="margin-left:8px">挑选配色主题</a></p>
  </div>
</div>
<template id="src">{article.replace("</template", "<\\\\/template")}</template>
<script>{COPY_JS}
const src=document.getElementById('src').innerHTML.trim();
function replay(){{const a=document.getElementById('art');a.innerHTML='';document.getElementById('screen').scrollTop=0;requestAnimationFrame(()=>a.innerHTML=src);}}
function cp(){{copyHtml(src,()=>msg.textContent='已复制，去公众号编辑器里粘贴',()=>msg.textContent='复制失败，换 Chrome 再试');}}
function cpText(){{navigator.clipboard.writeText(document.getElementById('ask').textContent);msg.textContent='已复制这句话';}}
replay();</script>""" + FOOT + "</body></html>"


def case_page(c, article):
    title = f"{c['title']} · {c['product']} · 小耳公众号SVG 真实作品"
    desc = f"{c['product']}：{c['desc']}。用小耳公众号SVG 做的真实公众号动效长图。"
    return head(title, desc, f"/work/{c['slug']}/") + nav("works") + f"""
<div class="wrap demo-grid" style="display:grid;grid-template-columns:385px 1fr;gap:48px;padding-top:48px;align-items:start">
  <div>
    <div class="phone"><div class="screen" id="screen"><h1>{escape(c['title'])}</h1><div class="meta">真实作品 · 动画从打开那一刻开始</div><div id="art"></div></div></div>
    <p style="text-align:center;margin-top:14px"><button class="btn ghost" onclick="replay()">重播</button></p>
  </div>
  <div>
    <div class="mono">REAL WORK · {escape(c['product'])}</div>
    <h1 style="font-size:34px;margin:8px 0 12px;line-height:1.25">{escape(c['title'])}</h1>
    <p style="color:var(--muted);font-size:16px">{escape(c['desc'])}</p>
    <p style="color:var(--muted)">这是小耳自己的产品，文章原样放在这里，和发进公众号的是同一份。</p>
    <p style="margin-top:24px">{f'<a class="btn" href="{escape(c["link"])}">去看{escape(c["product"])}</a> ' if c.get("link") else ""}<a class="btn ghost" href="/#templates">用模板做你自己的</a></p>
  </div>
</div>
<template id="src">{article.replace("</template", "<\\\\/template")}</template>
<script>const src=document.getElementById('src').innerHTML.trim();
function replay(){{const a=document.getElementById('art');a.innerHTML='';document.getElementById('screen').scrollTop=0;requestAnimationFrame(()=>a.innerHTML=src);}}
replay();</script>""" + FOOT + "</body></html>"


def cases_section(cases):
    if not cases:
        return ""
    def card(c):
        if c.get("status") == "soon":
            return f"""<div class="card" style="border-style:dashed">
<div style="aspect-ratio:4/5;display:flex;align-items:center;justify-content:center;background:var(--fill);color:var(--muted);font-size:15px">制作中</div>
<div class="card-body"><div class="mono">{escape(c['product'])}</div><h3 class="card-title">{escape(c['title'])}</h3>
<p class="card-desc">{escape(c['desc'])}</p></div></div>"""
        return f"""<a href="/work/{c['slug']}/" class="card">
<img src="/work/{c['slug']}/thumb.jpg" alt="{escape(c['title'])} 截图" loading="lazy" style="display:block;width:100%;aspect-ratio:4/5;object-fit:cover;object-position:top;background:var(--fill)">
<div class="card-body"><div class="mono">{escape(c['product'])}</div><h3 class="card-title">{escape(c['title'])}</h3>
<p class="card-desc">{escape(c['desc'])}</p></div></a>"""
    return f"""<div class="wrap" id="works">
  <div class="sec-break"><span class="wm">作</span><h2>真实作品</h2></div>
  <p style="color:var(--muted);margin:0 0 28px;text-align:center">小耳自己的产品，用这套工具做的真实公众号文章。</p>
  <div class="grid-cards">{"".join(card(c) for c in cases)}</div>
</div>"""


def themes_page(styles):
    title = "主题库 · 独立可扩展风格系统 · 小耳公众号SVG"
    desc = "独立抽离的公众号 SVG 主题风格库：支持一键复制提示词，往 styles/ 放入 JSON 即可扩展全新风格。"
    cards_html = []
    for s in styles:
        sw = "".join(f'<span class="swatch" style="background:{escape(c)}" title="{escape(c)}"></span>' for c in s["swatches"])
        tags = "".join(f'<span class="tag">{escape(m)}</span>' for m in s["mood"])
        route_label = "平面信息图 · Motion" if s["route"] == "motion" else "等轴测 3D · Iso"
        prompt_text = f'用 {REPO} 的「{s["id"]}」主题（{s["route"]} 路线）给我做一篇公众号 SVG 动效长图，题材是：____，资料在：____'
        cards_html.append(f"""<article class="card theme-card" data-route="{escape(s['route'])}" style="border-color:var(--line)">
  <div style="background:{escape(s['bg'])};color:{escape(s['ink'])};padding:22px 20px;border-bottom:1px solid var(--line);position:relative">
    <div style="font-family:var(--mono);font-size:11px;letter-spacing:0.14em;color:{escape(s['accent'])};text-transform:uppercase">{escape(s['id'])}</div>
    <div style="font-family:var(--serif);font-size:24px;font-weight:700;margin:6px 0 8px;line-height:1.25">{escape(s['name'])}</div>
    <div style="background:{escape(s['panel'])};color:{escape(s['muted'])};padding:10px 12px;border-radius:4px;font-size:12px;line-height:1.5">
      {escape(s['visual_note'] or s['best_for'])}
    </div>
  </div>
  <div class="card-body">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap">
      <span class="mono">{escape(route_label)}</span>
      <span style="font-size:12px;color:var(--muted)">作者：{escape(s['author'])}</span>
    </div>
    <div class="swatches" style="margin:4px 0">{sw}</div>
    <p class="card-desc"><strong>适用：</strong>{escape(s['best_for'])}</p>
    <div class="tags">{tags}</div>
    <div style="margin-top:auto;padding-top:12px;display:flex;justify-content:space-between;align-items:center;gap:8px">
      <code style="font-size:11px;color:var(--muted)">{escape(s['file'])}</code>
      <button class="btn ghost" style="padding:5px 12px;font-size:12px" onclick="copyPrompt(this)" data-prompt="{escape(prompt_text)}">复制提示词</button>
    </div>
  </div>
</article>""")

    return head(title, desc, "/themes/") + nav("themes") + f"""
<div class="wrap" style="padding-top:56px">
  <div class="mono">STYLE REGISTRY · EXTENSIBLE</div>
  <h1 style="font-size:42px;margin:10px 0 14px;line-height:1.15">主题风格库</h1>
  <p style="max-width:680px;color:var(--muted);font-size:17px">所有主题已从渲染代码独立抽离至 <code>styles/</code> 目录。Agent 会根据你的内容自动匹配现有风格，或在现有风格不贴合时建议并生成全新风格。</p>

  <div style="display:flex;gap:10px;flex-wrap:wrap;margin:28px 0 32px" id="filters">
    <button class="btn active" type="button" data-filter="all">全部风格 ({len(styles)})</button>
    <button class="btn ghost" type="button" data-filter="motion">平面信息图 · Motion</button>
    <button class="btn ghost" type="button" data-filter="iso">等轴测 3D · Iso</button>
  </div>

  <div class="grid-cards" id="theme-grid">
    {"".join(cards_html)}
  </div>

  <div class="sec-break"><span class="wm">拓</span><h2>如何拓展一个新主题</h2></div>
  <div class="chat-box">
    <div class="bubble left"><strong>01 · 新建配置文件</strong><br>复制 <code>styles/motion/chronicle-light.json</code>（或 <code>styles/iso/paper.json</code>），修改 <code>meta</code> 适用描述与纯色色板。</div>
    <div class="bubble right"><strong>02 · 守住微信红线</strong><br>只使用纯色与透明度，不使用原生渐变、<code>filter</code> 滤镜或 <code>id</code>（详见 <code>docs/wechat-svg-rules.md</code>）。</div>
    <div class="bubble left"><strong>03 · 自动生效</strong><br>无需修改任何 Python 渲染逻辑：分镜直接填新主题名即可渲染，运行 <code>python3 site/build.py</code> 即可自动出现在本页面。</div>
  </div>
</div>
<script>
document.getElementById('filters').addEventListener('click', (e) => {{
  const btn = e.target.closest('button[data-filter]');
  if (!btn) return;
  const f = btn.dataset.filter;
  document.querySelectorAll('#filters button').forEach(b => {{
    b.className = b === btn ? 'btn active' : 'btn ghost';
  }});
  document.querySelectorAll('.theme-card').forEach(c => {{
    c.style.display = (f === 'all' || c.dataset.route === f) ? 'flex' : 'none';
  }});
}});
function copyPrompt(btn) {{
  navigator.clipboard.writeText(btn.dataset.prompt).then(() => {{
    const old = btn.textContent;
    btn.textContent = '已复制';
    setTimeout(() => btn.textContent = old, 1600);
  }});
}}
</script>""" + FOOT + "</body></html>"


def paste_page():
    title = "粘贴台：把 SVG 动效长图一键复制到公众号 · 小耳公众号SVG"
    desc = "把 AI agent 生成的公众号 SVG 动效文章放进来预览，一键复制，粘贴到公众号编辑器就能发布。文章只在你的浏览器里，不上传。"
    return head(title, desc, "/paste/") + nav("paste") + """
<div class="wrap" style="padding-top:32px">
<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;position:sticky;top:0;background:var(--bg);padding:14px 0;z-index:5;border-bottom:1px solid var(--line)">
<button class="btn" id="cp" onclick="cp()" disabled>复制到公众号</button>
<button class="btn ghost" onclick="replay()">重播</button>
<label class="btn ghost" style="cursor:pointer">打开 article.html<input type="file" accept=".html,.htm" id="file" hidden></label>
<span id="msg" style="color:var(--accent);font-size:14px"></span></div>
<div id="warn" style="display:none;margin-top:16px;padding:12px 16px;border:1px solid var(--accent);background:var(--fill);border-radius:4px;font-size:14px"></div>
<div id="drop" style="margin-top:28px;border:1px dashed var(--line);border-radius:6px;padding:64px 20px;text-align:center;color:var(--muted)">
<p style="font-size:18px;margin:0 0 8px;font-family:var(--serif);color:var(--ink)">把 agent 生成的 <b>article.html</b> 拖到这里</p>
<p style="margin:0;font-size:14px">或者让 agent 运行 <code>python3 tools/paste.py out/…/article.html</code>，会自动带着文章打开本页。文章只在你的浏览器里，不会上传。</p></div>
<div style="display:flex;justify-content:center;margin-top:28px"><div class="phone" id="ph" style="display:none"><div class="screen" id="screen"><div id="art"></div></div></div></div>
<ol style="max-width:608px;margin:40px auto 0;font-size:15px;color:var(--muted)">
<li>点「复制到公众号」</li><li>公众号后台 →「新的创作」→「文章」，在正文里按 Ctrl / ⌘ + V</li>
<li>填标题、上传封面，点「预览」发到手机检查，再群发</li></ol></div>
<script>""" + COPY_JS + r"""
let src='';
function show(html){src=html.trim();document.getElementById('drop').style.display='none';document.getElementById('ph').style.display='block';
  document.getElementById('cp').disabled=false;
  const w=document.getElementById('warn');
  if(/file:\/\/|href="(?!https?:)[^"]+\.(jpe?g|png|gif|webp)"/i.test(src)){w.style.display='block';w.textContent='⚠️ 文章里有本地图片，粘进公众号会丢失。请先在 agent 里填公众号 AppID，用 --push 把图片传到微信图床。';}
  replay();}
function replay(){if(!src)return;const a=document.getElementById('art');a.innerHTML='';document.getElementById('screen').scrollTop=0;requestAnimationFrame(()=>a.innerHTML=src);}
function cp(){copyHtml(src,()=>msg.textContent='已复制，去公众号编辑器里粘贴',()=>msg.textContent='复制失败，换 Chrome / Edge 再试');}
async function fromHash(){const m=location.hash.match(/z=([A-Za-z0-9_-]+)/);if(!m)return;
  try{let b=m[1].replace(/-/g,'+').replace(/_/g,'/');while(b.length%4)b+='=';
    const bytes=Uint8Array.from(atob(b),c=>c.charCodeAt(0));
    const ds=new Blob([bytes]).stream().pipeThrough(new DecompressionStream('deflate-raw'));
    show(await new Response(ds).text());}catch(e){msg.textContent='链接里的文章读不出来：'+e;}}
function readFile(f){const r=new FileReader();r.onload=()=>show(r.result);r.readAsText(f,'utf-8');}
document.getElementById('file').onchange=e=>e.target.files[0]&&readFile(e.target.files[0]);
const d=document.getElementById('drop');['dragover','dragenter'].forEach(k=>addEventListener(k,e=>{e.preventDefault();d.style.borderColor='var(--accent)';}));
addEventListener('drop',e=>{e.preventDefault();const f=e.dataTransfer.files[0];f&&readFile(f);});
fromHash();
</script>""" + FOOT + "</body></html>"


def index_page(cards, hero_article, styles, cases=()):
    title = "小耳公众号SVG：让公众号文章自己动起来 · Chronicle 重构版"
    desc = "纯 SVG 公众号动效长图：往下拉一屏屏长出来，线稿自己画、数字滚动、等轴测 3D 小场景一块块拼起来。没有视频和代码，公众号原生支持。"
    ld = json.dumps({"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "小耳公众号SVG（xiaoer-wx-svg）",
                     "applicationCategory": "DesignApplication", "operatingSystem": "macOS, Windows, Linux",
                     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "CNY"}, "url": BASE, "sameAs": [REPO, UPSTREAM_REPO],
                     "publisher": {"@type": "Organization", "name": "Xiaoer Omia", "url": OMIA}, "description": desc}, ensure_ascii=False)
    grid = "".join(f"""<a href="/t/{s}/" class="card">
<img src="/t/{s}/thumb.jpg" alt="{escape(n)} 演示截图" loading="lazy" style="display:block;width:100%;aspect-ratio:4/5;object-fit:cover;object-position:top;background:var(--fill)">
<div class="card-body"><div class="mono">{escape(r)}</div><h3 class="card-title">{escape(n)}</h3>
<p class="card-desc">{escape(fit)}</p></div></a>""" for s, n, r, fit in cards)

    install_cmd = "npx skills add OwenCedaric/xiaoer-wx-svg -a claude-code codex cursor -g -y"
    ask = f"用 {REPO} 给我做一篇公众号 SVG 动效长图，题材是：____，资料在：____"
    return head(title, desc, "/", extra=f'<script type="application/ld+json">{ld}</script>') + nav() + f"""
<div class="wrap hero-stage">
  <div class="hero-circle" aria-hidden="true"></div>
  <div>
    <div class="mono">OPEN SOURCE · CHRONICLE EDITION · CEDARIC</div>
    <h1 style="font-size:clamp(36px,4.5vw,52px);line-height:1.15;margin:14px 0 20px">让公众号文章<br>自己动起来</h1>
    <p style="font-size:17px;color:var(--muted);max-width:480px">纯 SVG 动效长图：往下拉，一屏屏长出来。线稿自己画、数字滚动、3D 小场景一块块拼好。没有视频、没有 GIF、没有一行代码在跑，公众号原生支持。</p>
    <p style="font-size:15px;color:var(--muted);max-width:480px">交给你的 AI agent（Claude Code、Codex、Cursor……），它会先根据题材匹配或建议视觉风格，再生成、自检并交付。</p>
    <pre style="white-space:pre-wrap;font-size:12px;font-family:var(--mono);background:var(--fill);border:1px solid var(--line);border-radius:4px;padding:12px 14px;margin:20px 0">{escape(install_cmd)}</pre>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <a class="btn" href="#start">开始使用</a>
      <a class="btn ghost" href="/themes/">浏览主题库 ({len(styles)})</a>
      <a class="btn ghost" href="#templates">看模板</a>
    </div>
  </div>
  <div><div class="phone"><div class="screen" id="screen"><h1>实时演示 · 往下滑</h1><div class="meta">打开即播 · 纯 SVG 时间轴</div><div id="art"></div></div></div></div>
</div>

<div class="wrap">
  <div class="epigraph">“界面应当向内容俯首，而非与之争夺注意力。留白，本身就是阅读的呼吸。”</div>
</div>

{cases_section(cases)}

<div class="wrap" id="start">
  <div class="sec-break"><span class="wm">序</span><h2>三步交付</h2></div>
  <div class="three-col" style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">
    <div class="card"><div class="card-body">
      <div class="mono">STEP 01</div><h3 class="card-title">把 Skill 交给 agent</h3>
      <pre id="ask" style="white-space:pre-wrap;font-size:12px;font-family:var(--mono);background:var(--fill);padding:10px;border-radius:4px;margin:4px 0">{escape(ask)}</pre>
      <button class="btn ghost" style="align-self:flex-start;padding:6px 14px;font-size:13px" onclick="navigator.clipboard.writeText(document.getElementById('ask').textContent);this.textContent='已复制'">复制这句话</button>
    </div></div>
    <div class="card"><div class="card-body">
      <div class="mono">STEP 02</div><h3 class="card-title">风格路由、生成与自检</h3>
      <p class="card-desc">agent 会先扫描 <code>styles/</code> 为你推荐最契合的主题或全新风格提案，确认后生成分镜与长图并截帧自检。</p>
    </div></div>
    <div class="card"><div class="card-body">
      <div class="mono">STEP 03</div><h3 class="card-title">推草稿箱，或一键复制</h3>
      <p class="card-desc">填了 AppID 可直接推进公众号草稿箱；不填也能用<a href="/paste/">粘贴台</a>一键复制，粘进公众号编辑器。</p>
    </div></div>
  </div>
</div>

<div class="wrap" id="templates">
  <div class="sec-break"><span class="wm">版</span><h2>模板与路线</h2></div>
  <p style="color:var(--muted);margin:0 0 28px;text-align:center">包含 Chronicle 编年体杂志长文、等轴测 3D 旅程、信息图套模板与底层格式。</p>
  <div class="grid-cards">{grid}</div>
</div>

<div class="wrap">
  <div class="sec-break"><span class="wm">规</span><h2>公众号实测规矩</h2></div>
  <div class="chat-box">
    <div class="bubble left"><strong>会被微信删掉或拒收：</strong>所有 <code>id</code>、<code>fill-opacity</code> 动画、<code>xlink:href</code>、滤镜、渐变、<code>mask</code>、<code>clipPath</code>、<code>&lt;style&gt;</code>、JS；插音频整篇拒收。</div>
    <div class="bubble right"><strong>会被原生保留：</strong><code>animate</code>、<code>animateTransform</code>、点击触发、静态 <code>transform</code> 与微信图床图片。每一条都经草稿箱拉回比对验证。</div>
  </div>
  <p style="text-align:center;margin-top:24px"><a class="btn ghost" href="{UPSTREAM_REPO}/blob/main/docs/wechat-svg-rules.md">查看完整规矩表</a></p>
</div>

<template id="src">{hero_article.replace("</template", "<\\\\/template")}</template>
<script>const src=document.getElementById('src').innerHTML.trim();document.getElementById('art').innerHTML=src;</script>
{FOOT}</body></html>"""


def with_mmbiz(article, sbdir, assets):
    if not assets:
        return article
    mp = sbdir / assets / "mmbiz.json"
    if not mp.exists():
        return article
    pre = assets.rstrip("/") + "/"
    for rel, url in json.loads(mp.read_text(encoding="utf-8")).items():
        article = article.replace(f'href="{pre}{rel}"', f'href="{url}"')
    return article


async def thumbs(jobs):
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("⚠️ 未安装 playwright，跳过页面缩略图生成（HTML 页面已照常构建）")
        return
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        tmp = Path(tempfile.mkdtemp()) / "thumb.html"
        for article, t, dest, base in jobs:
            tmp.write_text(f'<!doctype html><base href="{Path(base).resolve().as_uri()}/"><body style="margin:0;width:1080px">{article}</body>',
                           encoding="utf-8")
            await pg.goto(tmp.as_uri())
            await pg.wait_for_load_state("load")
            await pg.wait_for_timeout(300)
            await pg.evaluate(f"document.querySelectorAll('svg').forEach(s=>{{s.pauseAnimations();s.setCurrentTime({t})}})")
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=str(dest), type="jpeg", quality=82, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
        await b.close()


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "paste").mkdir(parents=True)
    (DIST / "themes").mkdir(parents=True)
    styles = load_all_styles()
    cards, jobs, urls = [], [], ["/", "/themes/", "/paste/"]
    hero = None
    for slug, name, route, fit, cmd, outname, t in DEMOS:
        subprocess.run([sys.executable, *cmd], cwd=ROOT, check=True, capture_output=True)
        art = (OUT / outname / "article.html").read_text(encoding="utf-8")
        sbdir = (ROOT / cmd[1]).parent
        web = with_mmbiz(art, sbdir, json.loads((ROOT / cmd[1]).read_text(encoding="utf-8")).get("assets"))
        d = DIST / "t" / slug
        d.mkdir(parents=True)
        (d / "index.html").write_text(demo_page(slug, name, route, fit, web, cmd[1]), encoding="utf-8")
        jobs.append((art, t, d / "thumb.jpg", sbdir))
        cards.append((slug, name, route, fit))
        urls.append(f"/t/{slug}/")
        if slug == "chronicle-essay":
            hero = art
    if hero is None and cards:
        hero = (OUT / DEMOS[0][5] / "article.html").read_text(encoding="utf-8")
    cases = json.loads(Path(os.environ["WXSVG_CASES"]).read_text(encoding="utf-8")) if os.environ.get("WXSVG_CASES") else []
    for c in cases:
        if c.get("status") == "soon":
            continue
        art = Path(c["article"]).expanduser().read_text(encoding="utf-8")
        d = DIST / "work" / c["slug"]
        d.mkdir(parents=True)
        for fpath in c.get("files", []):
            shutil.copy(Path(fpath).expanduser(), d / Path(fpath).name)
        (d / "index.html").write_text(case_page(c, art), encoding="utf-8")
        jobs.append((art, c.get("t", 60), d / "thumb.jpg", Path(c["article"]).expanduser().parent))
        urls.append(f"/work/{c['slug']}/")
    asyncio.run(thumbs(jobs))
    og_src = DIST / "t" / "chronicle-essay" / "thumb.jpg"
    if og_src.exists():
        shutil.copy(og_src, DIST / "og.jpg")
    (DIST / "index.html").write_text(index_page(cards, hero, styles, cases), encoding="utf-8")
    (DIST / "themes" / "index.html").write_text(themes_page(styles), encoding="utf-8")
    (DIST / "paste" / "index.html").write_text(paste_page(), encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")
    (DIST / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                                      + "".join(f"<url><loc>{BASE}{u}</loc></url>" for u in urls) + "</urlset>\n")
    (DIST / "llms.txt").write_text(f"""# 小耳公众号SVG（xiaoer-wx-svg）· Xiaoer Omia 出品（Chronicle 重构版 · 主题作者 Cedaric）

> 免费开源的微信公众号 SVG 动效长图工具。交给 AI agent（Claude Code / Codex / Cursor），生成往下拉一屏屏长出来的纯 SVG 动效文章，推进公众号草稿箱或用粘贴台一键复制。

- 仓库与 Agent Skill：{REPO}（SKILL.md）
- 原作仓库：{UPSTREAM_REPO}
- 主题库（{len(styles)} 套可扩展风格）：{BASE}/themes/
- 粘贴台（一键复制到公众号编辑器，文章不上传）：{BASE}/paste/
- 公众号 SVG 实测规矩：{UPSTREAM_REPO}/blob/main/docs/wechat-svg-rules.md
- 模板：{", ".join(f"{n}（{BASE}/t/{s}/）" for s, n, _, _ in cards)}
""", encoding="utf-8")
    print(f"✅ {DIST}  {len(urls)} 页 · {len(styles)} 套主题")


if __name__ == "__main__":
    main()
