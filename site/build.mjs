#!/usr/bin/env node
/**
 * 纯 Node.js 静态站构建器（零外部依赖，可直接部署到 Vercel / Cloudflare Pages）：
 *   npm run build   (即 node site/build.mjs)
 *
 * 设计语言：Chronicle 编年体极简排版 × SVG 矢量绘图台（Vector Drafting Table）
 * 原作者：Xiaoer Omia (https://svg.xiaoeromia.com) · Chronicle 界面与主题重构：Cedaric
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const DIST = path.join(__dirname, "dist");
const DEMOS_CACHE = path.join(__dirname, "demos");
const OUT = path.join(ROOT, "out");
const STYLES_DIR = path.join(ROOT, "styles");

const BASE = "https://svg.xiaoeromia.com";
const REPO = "https://github.com/OwenCedaric/xiaoer-wx-svg";
const UPSTREAM_REPO = "https://github.com/Jane-xiaoer/xiaoer-wx-svg";
const OMIA = "https://xiaoeromia.com";

const DEMOS = [
  {
    slug: "isometric-journey",
    name: "等轴测旅程 · 3D",
    route: "等轴测旅程",
    fit: "流程、路线、链路：Z 字公路串起一站站 2.5D 小场景，零件一块块拼起来，光点沿路跑；结尾带建议卡和工具墙",
    sbPath: "templates/storyboards/等轴测-小耳的四台电脑.json",
    outname: "等轴测-小耳的四台电脑",
    t: 40,
  },
  {
    slug: "fm-laundry",
    name: "等轴测 · 产品故事（带图片帧）",
    route: "等轴测旅程",
    fit: "有真实 3D 资产或作品图的产品：浪漫开场问一句、角色说话泡泡、一站站真帧动画、作品一幅幅晾上绳子、点一下猜答案、结尾大网址",
    sbPath: "templates/storyboards/等轴测-小耳FM洗衣房.json",
    outname: "等轴测-小耳FM洗衣房",
    t: 14,
  },
  {
    slug: "product-launch",
    name: "产品发布 · 8 屏",
    route: "套模板",
    fit: "软件产品：一堆东西被吸成品牌、产品窗口长出来、数字滚动、价格卡",
    sbPath: "templates/storyboards/产品-Omia-8屏.json",
    outname: "产品-Omia-8屏",
    t: 70,
  },
  {
    slug: "hardware-app",
    name: "硬件 + App · 带互动",
    route: "套模板",
    fit: "硬件产品：账单吐出来盖章、设备蓝牙同步、点一下开会字幕循环冒出",
    sbPath: "templates/storyboards/硬件加App-录音卡-带互动.json",
    outname: "硬件加App-录音卡-带互动",
    t: 70,
  },
  {
    slug: "methodology",
    name: "方法论 · 6 屏",
    route: "套模板",
    fit: "方法、清单、教程：线稿自己画、三个大字砸下、要点卡片",
    sbPath: "templates/storyboards/方法论-番茄工作法.json",
    outname: "方法论-番茄工作法",
    t: 60,
  },
  {
    slug: "chronicle-essay",
    name: "编年体 · 8 屏全能力长文",
    route: "套模板 · Chronicle",
    fit: "深度长文与能力展示：80% 几何圆、空心描边大字、数字滚动、线稿自绘、点击揭开互动与结构化对话（主题作者：Cedaric）",
    sbPath: "templates/storyboards/编年体-深度长文示例.json",
    outname: "编年体-深度长文示例",
    t: 4.5,
  },
  {
    slug: "brand-vi",
    name: "品牌 VI · 墨黑流金",
    route: "品牌 VI / 高端发布",
    fit: "品牌发布会与 VI 手册规范：墨黑流金配色、建筑标尺测量线、线稿自绘与克制转场",
    sbPath: "templates/storyboards/品牌VI-墨黑流金示例.json",
    outname: "品牌VI-墨黑流金示例",
    t: 15,
  },
  {
    slug: "ai-agent-flow",
    name: "AI 工作流 · 改写与换肤",
    route: "套模板 · 夜紫幻境",
    fit: "AI 产品与工作流展示：终端指令打字改写、明暗扫光一键换肤、搜索高亮与待办依次打勾",
    sbPath: "templates/storyboards/AI工作流-夜紫幻境示例.json",
    outname: "AI工作流-夜紫幻境示例",
    t: 6,
  },
  {
    slug: "minimal",
    name: "最小示例 · 3 屏",
    route: "底层格式",
    fit: "直接写元素和时间轴：画圈、放大、逐字出现，适合想自己从零搭的人",
    sbPath: "templates/raw/最小示例-3屏.json",
    outname: "最小示例-3屏",
    t: 20,
  },
];

const esc = (s) =>
  String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

function previewSvg(slug) {
  const common = `viewBox="0 0 320 180" width="100%" height="100%" style="display:block" aria-hidden="true"`;
  switch (slug) {
    case "chronicle-essay":
      return `<svg ${common}>
        <circle cx="160" cy="90" r="64" fill="none" stroke="var(--line)" stroke-width="1.2" stroke-dasharray="402" stroke-dashoffset="0"/>
        <line x1="64" y1="90" x2="104" y2="90" stroke="var(--line)" stroke-width="1" stroke-dasharray="4 4"/>
        <line x1="216" y1="90" x2="256" y2="90" stroke="var(--line)" stroke-width="1" stroke-dasharray="4 4"/>
        <text x="160" y="106" text-anchor="middle" font-family="Georgia,serif" font-size="48" font-weight="700" fill="none" stroke="var(--stroke-tint)" stroke-width="1.4">静</text>
        <circle cx="160" cy="26" r="3" fill="var(--accent)"/>
      </svg>`;
    case "isometric-journey":
      return `<svg ${common}>
        <path d="M70 138 L160 96 L110 70 L235 42" fill="none" stroke="var(--line)" stroke-width="14" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M70 138 L160 96 L110 70 L235 42" fill="none" stroke="var(--bg)" stroke-width="1.5" stroke-dasharray="6 6"/>
        <polygon points="160,64 192,80 160,96 128,80" fill="var(--surface2)" stroke="var(--line)" stroke-width="1.2"/>
        <polygon points="128,80 160,96 160,122 128,106" fill="var(--fill)" stroke="var(--line)" stroke-width="1.2"/>
        <polygon points="192,80 160,96 160,122 192,106" fill="var(--bg)" stroke="var(--line)" stroke-width="1.2"/>
        <circle r="4" fill="var(--accent)">
          <animateMotion dur="3.6s" repeatCount="indefinite" path="M70 138 L160 96 L110 70 L235 42"/>
        </circle>
      </svg>`;
    case "fm-laundry":
      return `<svg ${common}>
        <path d="M36 48 Q160 66 284 48" fill="none" stroke="var(--line)" stroke-width="1.4"/>
        <rect x="74" y="54" width="44" height="58" rx="3" fill="var(--bg)" stroke="var(--line)" stroke-width="1.2"/>
        <rect x="82" y="62" width="28" height="28" fill="var(--fill)"/>
        <rect x="138" y="58" width="44" height="58" rx="3" fill="var(--surface2)" stroke="var(--accent)" stroke-width="1.4"/>
        <circle cx="160" cy="80" r="10" fill="none" stroke="var(--accent)" stroke-width="1.4"/>
        <rect x="202" y="54" width="44" height="58" rx="3" fill="var(--bg)" stroke="var(--line)" stroke-width="1.2"/>
        <rect x="108" y="128" width="104" height="26" rx="13" fill="var(--fill)" stroke="var(--line)" stroke-width="1"/>
        <circle cx="144" cy="141" r="2.5" fill="var(--accent)"/>
        <circle cx="160" cy="141" r="2.5" fill="var(--muted)"/>
        <circle cx="176" cy="141" r="2.5" fill="var(--muted)"/>
      </svg>`;
    case "product-launch":
      return `<svg ${common}>
        <rect x="52" y="34" width="216" height="112" rx="6" fill="var(--bg)" stroke="var(--line)" stroke-width="1.2"/>
        <line x1="52" y1="56" x2="268" y2="56" stroke="var(--line)" stroke-width="1"/>
        <rect x="52" y="56" width="58" height="90" fill="var(--fill)"/>
        <circle cx="66" cy="45" r="2.5" fill="var(--muted)"/>
        <circle cx="76" cy="45" r="2.5" fill="var(--muted)"/>
        <rect x="126" y="72" width="120" height="10" rx="2" fill="var(--fill)"/>
        <rect x="126" y="92" width="76" height="8" rx="2" fill="var(--accent)" opacity="0.85">
          <animate attributeName="width" values="24;116;24" dur="3.4s" repeatCount="indefinite"/>
        </rect>
        <rect x="126" y="112" width="96" height="8" rx="2" fill="var(--line)"/>
      </svg>`;
    case "hardware-app":
      return `<svg ${common}>
        <rect x="64" y="42" width="68" height="96" rx="4" fill="var(--surface2)" stroke="var(--line)" stroke-width="1.2"/>
        <line x1="78" y1="64" x2="118" y2="64" stroke="var(--line)" stroke-width="2"/>
        <line x1="78" y1="80" x2="112" y2="80" stroke="var(--line)" stroke-width="2"/>
        <rect x="78" y="98" width="38" height="18" rx="2" fill="none" stroke="var(--accent)" stroke-width="1.4"/>
        <circle cx="216" cy="90" r="14" fill="var(--fill)" stroke="var(--accent)" stroke-width="1.5"/>
        <circle cx="216" cy="90" r="28" fill="none" stroke="var(--accent)" stroke-width="1" opacity="0.5">
          <animate attributeName="r" values="16;40" dur="2.2s" repeatCount="indefinite"/>
          <animate attributeName="opacity" values="0.7;0" dur="2.2s" repeatCount="indefinite"/>
        </circle>
        <path d="M136 90 H196" stroke="var(--line)" stroke-width="1.2" stroke-dasharray="4 4"/>
      </svg>`;
    case "methodology":
      return `<svg ${common}>
        <rect x="58" y="42" width="118" height="90" fill="none" stroke="var(--line)" stroke-width="1.2" stroke-dasharray="4 3"/>
        <line x1="58" y1="28" x2="176" y2="28" stroke="var(--accent)" stroke-width="1.2"/>
        <line x1="58" y1="24" x2="58" y2="32" stroke="var(--accent)" stroke-width="1.2"/>
        <line x1="176" y1="24" x2="176" y2="32" stroke="var(--accent)" stroke-width="1.2"/>
        <path d="M74 114 L106 72 L134 94 L162 58" fill="none" stroke="var(--ink)" stroke-width="1.8" stroke-linecap="round"/>
        <g transform="translate(232 96)">
          <circle cx="0" cy="0" r="22" fill="none" stroke="var(--accent)" stroke-width="1.6" stroke-dasharray="6 4">
            <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="10s" repeatCount="indefinite"/>
          </circle>
          <circle cx="0" cy="0" r="7" fill="none" stroke="var(--ink)" stroke-width="1.4"/>
        </g>
      </svg>`;
    default:
      return `<svg ${common}>
        <circle cx="110" cy="90" r="40" fill="none" stroke="var(--line)" stroke-width="1.4"/>
        <circle cx="110" cy="90" r="22" fill="none" stroke="var(--accent)" stroke-width="1.4" stroke-dasharray="138">
          <animate attributeName="stroke-dashoffset" values="138;0;138" dur="3.6s" repeatCount="indefinite"/>
        </circle>
        <circle cx="70" cy="90" r="3" fill="var(--ink)"/>
        <circle cx="150" cy="90" r="3" fill="var(--ink)"/>
        <line x1="184" y1="74" x2="256" y2="74" stroke="var(--ink)" stroke-width="2"/>
        <line x1="184" y1="92" x2="240" y2="92" stroke="var(--muted)" stroke-width="2"/>
        <line x1="184" y1="110" x2="220" y2="110" stroke="var(--accent)" stroke-width="2"/>
      </svg>`;
  }
}

const CSS = `
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
  --c-surface2-light: #f0ede8;
  --c-surface2-dark: #282c34;
  --c-line-light: rgba(61, 68, 81, 0.20);
  --c-line-dark: rgba(210, 214, 221, 0.20);
  --c-stroke-light: rgba(61, 68, 81, 0.60);
  --c-stroke-dark: rgba(210, 214, 221, 0.60);

  --bg: var(--c-bg-light);
  --ink: var(--c-ink-light);
  --muted: var(--c-muted-light);
  --accent: var(--c-accent-light);
  --fill: var(--c-fill-light);
  --surface2: var(--c-surface2-light);
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
    --surface2: var(--c-surface2-dark);
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
    --surface2: light-dark(var(--c-surface2-light), var(--c-surface2-dark));
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
  overflow-x: clip;
}
a { color: var(--accent); text-decoration: none; }
@media (hover: hover) and (pointer: fine) {
  a:hover { text-decoration: underline; text-underline-offset: 4px; }
}
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
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  padding: 22px 0;
  border-bottom: 1px solid var(--line);
}
.brand { font-family: var(--serif); font-weight: 700; font-size: 18px; color: var(--ink); letter-spacing: 0.04em; white-space: nowrap; }
.nav-links { display: flex; align-items: center; gap: 20px; flex-wrap: wrap; }
.nav-links a { color: var(--ink); font-size: 14px; font-weight: 400; white-space: nowrap; }
.nav-links a[aria-current="page"] { color: var(--accent); font-weight: 600; }
.theme-btn {
  background: transparent;
  color: var(--muted);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 4px 10px;
  min-width: 58px;
  text-align: center;
  font-size: 12px;
  font-family: var(--mono);
  cursor: pointer;
  white-space: nowrap;
  transition: color 0.15s ease, border-color 0.15s ease;
}
@media (hover: hover) and (pointer: fine) {
  .theme-btn:hover { color: var(--ink); border-color: var(--accent); }
}
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
  white-space: nowrap;
  transition: opacity 0.15s ease, border-color 0.15s ease, color 0.15s ease;
}
.btn.ghost { background: transparent; color: var(--ink); border: 1px solid var(--line); }
.btn.active { background: var(--accent); border-color: var(--accent); color: var(--bg); }
.link-action {
  background: none;
  border: 0;
  padding: 2px 0;
  color: var(--accent);
  font-family: var(--sans);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: opacity 0.15s ease;
}
@media (hover: hover) and (pointer: fine) {
  .btn:hover { opacity: 0.85; text-decoration: none; }
  .btn.ghost:hover { border-color: var(--accent); color: var(--accent); }
  .link-action:hover { text-decoration: underline; text-underline-offset: 4px; }
}
.btn:active, .link-action:active { opacity: 0.65; }
.btn:disabled { opacity: 0.35; cursor: not-allowed; pointer-events: none; }

/* Hero + SVG Drafting Anchor */
.hero-stage {
  position: relative;
  padding-top: 64px;
  padding-bottom: 48px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) min(375px, 100%);
  gap: 56px;
  align-items: center;
}
.hero-stage > * { position: relative; z-index: 1; min-width: 0; }
.hero-stage > .hero-svg {
  position: absolute;
  left: -96px;
  top: 18px;
  width: 520px;
  height: 520px;
  pointer-events: none;
  z-index: 0;
}
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
.phone {
  width: min(375px, 100%);
  margin: 0 auto;
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
@media (hover: hover) and (pointer: fine) {
  .card:hover { border-color: var(--accent); text-decoration: none; }
}
.card-preview {
  position: relative;
  background: var(--surface2);
  border-bottom: 1px solid var(--line);
  aspect-ratio: 5 / 7;
  overflow: hidden;
  pointer-events: none;
}
.card-preview-stage {
  position: absolute;
  left: 0;
  top: 0;
  width: 1080px;
  transform-origin: top left;
}
.card-body { padding: 18px 20px 20px; flex: 1; display: flex; flex-direction: column; gap: 8px; }
.card-title { font-family: var(--serif); font-size: 20px; font-weight: 600; color: var(--ink); margin: 0; line-height: 1.35; }
.card-desc { color: var(--muted); font-size: 14px; line-height: 1.65; margin: 0; }
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
  background: var(--surface2);
  border-radius: 10px 2px 10px 10px;
}
@media (max-width: 640px) {
  .chat-box::before { display: none; }
  .bubble { max-width: 90%; }
}
.mech-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  gap: 36px;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 28px;
  background: var(--bg);
}
.mech-grid > * { min-width: 0; }
.swatches { display: flex; gap: 8px; align-items: center; }
.swatch { width: 22px; height: 22px; border-radius: 50%; border: 1px solid var(--line); }
.tags { display: flex; flex-wrap: wrap; gap: 6px; }
.tag { font-size: 12px; padding: 2px 8px; border-radius: 3px; background: var(--fill); color: var(--muted); }
.coda { margin: 96px 0 40px; text-align: center; }
.coda-row { font-family: var(--serif); font-size: 14px; letter-spacing: 0.14em; color: var(--muted); text-transform: uppercase; }
.coda-mark { font-size: clamp(64px, 10vw, 104px); margin: 20px 0; display: block; }
footer { border-top: 1px solid var(--line); margin-top: 40px; padding: 36px 0 120px; color: var(--muted); font-size: 14px; line-height: 1.85; }
.demo-grid > * { min-width: 0; }
@media (max-width: 900px) {
  .hero-stage { grid-template-columns: 1fr; padding-top: 40px; gap: 40px; }
  .hero-stage > .hero-svg { width: min(86vw, 360px); height: min(86vw, 360px); left: 50%; top: 8px; transform: translateX(-50%); }
  .three-col { grid-template-columns: 1fr !important; }
  .demo-grid { grid-template-columns: 1fr !important; }
  .mech-grid { grid-template-columns: 1fr; padding: 20px; }
}
@media (max-width: 480px) {
  .nav-links { gap: 14px; }
}
`;

const THEME_HEAD_SCRIPT = `<meta name="color-scheme" content="light dark">
<script>
try {
  const s = localStorage.getItem("color-scheme");
  if (s === "light" || s === "dark") document.querySelector('meta[name="color-scheme"]').content = s;
} catch (e) {}
</script>`;

const THEME_TOGGLE_JS = `
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
`;

const COPY_JS = `
function copyHtml(html,ok,fail){
  const done=()=>ok&&ok();
  if(navigator.clipboard&&window.ClipboardItem){
    navigator.clipboard.write([new ClipboardItem({'text/html':new Blob([html],{type:'text/html'}),'text/plain':new Blob(['请在公众号编辑器里粘贴'],{type:'text/plain'})})]).then(done,()=>legacy());
  }else legacy();
  function legacy(){const box=document.createElement('div');box.contentEditable='true';box.style.cssText='position:fixed;left:-9999px;top:0;width:375px';
    box.innerHTML=html;document.body.appendChild(box);const r=document.createRange();r.selectNodeContents(box);
    const s=getSelection();s.removeAllRanges();s.addRange(r);const k=document.execCommand('copy');s.removeAllRanges();box.remove();k?done():(fail&&fail());}
}
`;

function loadAllStyles() {
  const items = [];
  for (const route of ["motion", "iso"]) {
    const dir = path.join(STYLES_DIR, route);
    if (!fs.existsSync(dir)) continue;
    const files = fs.readdirSync(dir).filter((f) => f.endsWith(".json")).sort();
    for (const file of files) {
      const raw = JSON.parse(fs.readFileSync(path.join(dir, file), "utf-8"));
      const meta = raw.meta ?? {};
      const swatches =
        route === "motion"
          ? [raw.bg, raw.panel, raw.text, raw.grey, raw.accent]
          : [raw.bg, raw.card, raw.ink, raw.muted, raw.red];
      items.push({
        id: path.basename(file, ".json"),
        route: meta.route ?? route,
        name: meta.name ?? path.basename(file, ".json"),
        author: meta.author ?? "Xiaoer Omia",
        source: meta.source ?? "",
        mood: meta.mood ?? [],
        best_for: meta.best_for ?? "",
        visual_note: meta.visual_note ?? "",
        bg: raw.bg ?? "#fbf9f6",
        panel: raw.panel ?? raw.card ?? "#f1efec",
        ink: raw.text ?? raw.ink ?? "#3d4451",
        muted: raw.grey ?? raw.muted ?? "#757d8a",
        accent: raw.accent ?? raw.red ?? "#82a1b9",
        swatches: swatches.filter(Boolean),
        file: `styles/${route}/${file}`,
      });
    }
  }
  return items;
}

function loadDemoArticle(demo) {
  const outPath = path.join(OUT, demo.outname, "article.html");
  const cachePath = path.join(DEMOS_CACHE, `${demo.slug}.html`);
  let html = "";
  if (fs.existsSync(outPath)) {
    html = fs.readFileSync(outPath, "utf-8");
    const sbPath = path.join(ROOT, demo.sbPath);
    if (fs.existsSync(sbPath)) {
      const sb = JSON.parse(fs.readFileSync(sbPath, "utf-8"));
      if (sb.assets) {
        const mmbizPath = path.join(path.dirname(sbPath), sb.assets, "mmbiz.json");
        if (fs.existsSync(mmbizPath)) {
          const pre = sb.assets.replace(/\/+$/, "") + "/";
          const mapping = JSON.parse(fs.readFileSync(mmbizPath, "utf-8"));
          for (const [rel, url] of Object.entries(mapping)) {
            html = html.replaceAll(`href="${pre}${rel}"`, `href="${url}"`);
          }
        }
      }
    }
    fs.mkdirSync(DEMOS_CACHE, { recursive: true });
    fs.writeFileSync(cachePath, html, "utf-8");
  } else if (fs.existsSync(cachePath)) {
    html = fs.readFileSync(cachePath, "utf-8");
  }
  return html;
}

const head = (title, desc, pagePath, extra = "") => `<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
${THEME_HEAD_SCRIPT}
<meta name="referrer" content="no-referrer">
<meta name="robots" content="index,follow">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${BASE}${pagePath}">
<meta property="og:title" content="${esc(title)}"><meta property="og:description" content="${esc(desc)}">
<meta property="og:site_name" content="小耳公众号SVG · Xiaoer Omia"><meta property="og:url" content="${BASE}${pagePath}">
<style>${CSS}</style>${extra}</head><body>`;

function nav(active = "") {
  const link = (href, label, key) =>
    `<a href="${href}"${active === key ? ' aria-current="page"' : ""}>${label}</a>`;
  return `<div class="wrap"><nav>
  <a href="/" class="brand">小耳公众号SVG</a>
  <div class="nav-links">
    ${link("/#mechanism", "原理", "mechanism")}
    ${link("/#templates", "模板", "templates")}
    ${link("/themes/", "主题库", "themes")}
    ${link("/paste/", "粘贴台", "paste")}
    <a href="${REPO}">GitHub</a>
    <button class="theme-btn" id="theme-toggle" type="button">DARK</button>
  </div>
</nav></div>`;
}

const FOOT = `<div class="wrap">
<div class="coda">
  <div class="coda-row">XIAOER WX SVG · AGENT SKILL</div>
  <span class="hollow coda-mark">动</span>
  <div class="coda-row">PURE SVG · NATIVE WECHAT</div>
</div>
<footer>
  <div>原作与引擎：<a href="${OMIA}">Xiaoer Omia</a>（<a href="${UPSTREAM_REPO}">Jane-xiaoer/xiaoer-wx-svg</a>）· 主题体系与界面重构：<strong>Cedaric</strong>（<a href="${REPO}">OwenCedaric/xiaoer-wx-svg</a>）</div>
  <div style="margin-top:6px">代码 MIT 开源 · 推到草稿箱 ≠ 发布，发布永远由你自己点。</div>
</footer></div><script>${THEME_TOGGLE_JS}</script>`;

function demoPage(demo, article) {
  const title = `${demo.name} · 公众号 SVG 动效模板 · 小耳公众号SVG`;
  const desc = `${demo.name}：${demo.fit}。纯 SVG，公众号原生支持，可一键复制到公众号编辑器。`;
  const safeArt = article.replaceAll("</template", "<\\/template");
  return (
    head(title, desc, `/t/${demo.slug}/`) +
    nav("templates") +
    `<div class="wrap demo-grid" style="display:grid;grid-template-columns:385px 1fr;gap:48px;padding-top:48px;align-items:start">
  <div>
    <div class="phone"><div class="screen" id="screen"><h1>${esc(demo.name)}</h1><div class="meta">演示 · 动画从打开那一刻开始</div><div id="art"></div></div></div>
    <p style="text-align:center;margin-top:14px"><button class="btn ghost" onclick="replay()">重播</button></p>
  </div>
  <div>
    <div class="mono">${esc(demo.route)}</div>
    <h1 style="font-size:34px;margin:8px 0 12px;line-height:1.25">${esc(demo.name)}</h1>
    <p style="color:var(--muted);font-size:16px">${esc(demo.fit)}</p>
    <p style="margin:24px 0"><button class="btn" id="cp" onclick="cp()">复制这个演示到公众号</button> <span id="msg" style="color:var(--accent);margin-left:10px;font-size:14px"></span></p>
    <h3 style="margin-top:48px;font-size:20px">想用这个模板做你自己的内容</h3>
    <p style="color:var(--muted);font-size:15px">把仓库交给你的 AI agent（Claude Code、Codex、Cursor……），说：</p>
    <pre id="ask" style="white-space:pre-wrap;background:var(--fill);border:1px solid var(--line);border-radius:4px;padding:16px;font-size:13px;font-family:var(--mono);line-height:1.6">用 ${REPO} 的「${esc(demo.route)}」（照 ${esc(demo.sbPath)} 改）给我做一篇公众号 SVG 动效长图，题材是：____，资料在：____</pre>
    <p style="display:flex;align-items:center;gap:16px;flex-wrap:wrap"><button class="link-action" type="button" onclick="cpText(this)">复制这句话 →</button> <a class="link-action" href="/themes/" style="color:var(--muted)">挑选配色主题 →</a></p>
  </div>
</div>
<template id="src">${safeArt}</template>
<script>${COPY_JS}
const src=document.getElementById('src').innerHTML.trim();
function replay(){const a=document.getElementById('art');a.innerHTML='';document.getElementById('screen').scrollTop=0;requestAnimationFrame(()=>a.innerHTML=src);}
function cp(){copyHtml(src,()=>msg.textContent='已复制，去公众号编辑器里粘贴',()=>msg.textContent='复制失败，换 Chrome 再试');}
function cpText(btn){navigator.clipboard.writeText(document.getElementById('ask').textContent).then(()=>{const old=btn.textContent;btn.textContent='已复制 ✓';setTimeout(()=>btn.textContent=old,1600);});}
replay();</script>` +
    FOOT +
    "</body></html>"
  );
}

function themesPage(styles) {
  const title = "主题库 · 独立可扩展风格系统 · 小耳公众号SVG";
  const desc = "独立抽离的公众号 SVG 主题风格库：支持一键复制提示词，往 styles/ 放入 JSON 即可扩展全新风格。";
  const cards = styles
    .map((s) => {
      const sw = s.swatches
        .map((c) => `<span class="swatch" style="background:${esc(c)}" title="${esc(c)}"></span>`)
        .join("");
      const tags = s.mood.map((m) => `<span class="tag">${esc(m)}</span>`).join("");
      const routeLabel = s.route === "motion" ? "MOTION · 平面" : "ISO 3D · 等轴测";
      const promptText = `用 ${REPO} 的「${s.id}」主题（${s.route} 路线）给我做一篇公众号 SVG 动效长图，题材是：____，资料在：____`;
      return `<article class="card theme-card" data-route="${esc(s.route)}">
  <div style="background:${esc(s.bg)};color:${esc(s.ink)};padding:22px 20px;border-bottom:1px solid var(--line)">
    <div style="font-family:var(--mono);font-size:11px;letter-spacing:0.14em;color:${esc(s.accent)};text-transform:uppercase">${esc(s.id)}</div>
    <div style="font-family:var(--serif);font-size:24px;font-weight:700;margin:6px 0 8px;line-height:1.25">${esc(s.name)}</div>
    <div style="background:${esc(s.panel)};color:${esc(s.ink)};opacity:0.88;padding:10px 12px;border-radius:4px;font-size:12px;line-height:1.55">${esc(s.visual_note || s.best_for)}</div>
  </div>
  <div class="card-body">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;white-space:nowrap">
      <span class="mono">${esc(routeLabel)}</span>
      <span style="font-size:12px;color:var(--muted)">作者：${esc(s.author)}</span>
    </div>
    <div class="swatches" style="margin:4px 0">${sw}</div>
    <p class="card-desc"><strong>适用：</strong>${esc(s.best_for)}</p>
    <div class="tags">${tags}</div>
    <div style="margin-top:auto;padding-top:14px;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center;gap:12px">
      <code style="font-size:11px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0" title="${esc(s.file)}">${esc(s.file)}</code>
      <button class="link-action" type="button" onclick="copyPrompt(this)" data-prompt="${esc(promptText)}">复制提示词 →</button>
    </div>
  </div>
</article>`;
    })
    .join("");

  return (
    head(title, desc, "/themes/") +
    nav("themes") +
    `<div class="wrap" style="padding-top:56px">
  <div class="mono">STYLE REGISTRY · EXTENSIBLE</div>
  <h1 style="font-size:42px;margin:10px 0 14px;line-height:1.15">主题风格库</h1>
  <p style="max-width:680px;color:var(--muted);font-size:17px">所有主题已从渲染代码独立抽离至 <code>styles/</code> 目录。Agent 会根据你的内容自动匹配现有风格，或在现有风格不贴合时建议并生成全新风格。</p>
  <div style="display:flex;gap:10px;flex-wrap:wrap;margin:28px 0 32px" id="filters">
    <button class="btn active" type="button" data-filter="all">全部风格 (${styles.length})</button>
    <button class="btn ghost" type="button" data-filter="motion">平面信息图 · Motion</button>
    <button class="btn ghost" type="button" data-filter="iso">等轴测 3D · Iso</button>
  </div>
  <div class="grid-cards" id="theme-grid">${cards}</div>
  <div class="sec-break"><span class="wm">拓</span><h2>如何拓展一个新主题</h2></div>
  <div class="chat-box">
    <div class="bubble left"><strong>01 · 新建配置文件</strong><br>复制 <code>styles/motion/chronicle-light.json</code>（或 <code>styles/iso/paper.json</code>），修改 <code>meta</code> 适用描述与纯色色板。</div>
    <div class="bubble right"><strong>02 · 守住微信红线</strong><br>只使用纯色与透明度，不使用原生渐变、<code>filter</code> 滤镜或 <code>id</code>（详见 <code>docs/wechat-svg-rules.md</code>）。</div>
    <div class="bubble left"><strong>03 · 自动生效</strong><br>无需修改任何代码：推送到 Vercel / Cloudflare 后执行 <code>npm run build</code>，新主题就会自动出现在本页面。</div>
  </div>
</div>
<script>
document.getElementById('filters').addEventListener('click', (e) => {
  const btn = e.target.closest('button[data-filter]');
  if (!btn) return;
  const f = btn.dataset.filter;
  document.querySelectorAll('#filters button').forEach(b => { b.className = b === btn ? 'btn active' : 'btn ghost'; });
  document.querySelectorAll('.theme-card').forEach(c => { c.style.display = (f === 'all' || c.dataset.route === f) ? 'flex' : 'none'; });
});
function copyPrompt(btn) {
  navigator.clipboard.writeText(btn.dataset.prompt).then(() => {
    const old = btn.textContent; btn.textContent = '已复制 ✓'; setTimeout(() => btn.textContent = old, 1600);
  });
}
</script>` +
    FOOT +
    "</body></html>"
  );
}

function pastePage() {
  const title = "粘贴台 & 微信 SVG 体检 · 小耳公众号SVG";
  const desc = "把 AI agent 生成的公众号 SVG 动效文章放进来：自动扫描微信禁用标签与体积，预览后一键复制到公众号编辑器。";
  return (
    head(title, desc, "/paste/") +
    nav("paste") +
    `<div class="wrap" style="padding-top:32px">
<div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap;background:var(--bg);padding:14px 0;border-bottom:1px solid var(--line)">
<button class="btn" id="cp" onclick="cp()" disabled>复制到公众号</button>
<button class="btn ghost" onclick="replay()">重播</button>
<label class="btn ghost" style="cursor:pointer">打开 article.html<input type="file" accept=".html,.htm" id="file" hidden></label>
<span id="msg" style="color:var(--accent);font-size:14px"></span></div>
<div id="lint" style="display:none;margin-top:16px;padding:12px 16px;border:1px solid var(--line);background:var(--surface2);border-radius:4px;font-size:13px;line-height:1.65"></div>
<div id="drop" style="margin-top:28px;border:1px dashed var(--line);border-radius:6px;padding:64px 24px;text-align:center;color:var(--muted)">
<p style="font-size:18px;margin:0 0 10px;font-family:var(--serif);color:var(--ink)">把 agent 生成的 <b>article.html</b> 拖到这里</p>
<p style="max-width:560px;margin:0 auto;font-size:14px;line-height:1.75">自动完成体积与微信 SVG 规矩体检。或运行 <code>python3 tools/paste.py out/…/article.html</code> 自动打开本页，文章仅保留在本地浏览器，不会上传。</p></div>
<div style="display:flex;justify-content:center;margin-top:28px"><div class="phone" id="ph" style="display:none"><div class="screen" id="screen"><div id="art"></div></div></div></div>
<ol style="max-width:608px;margin:40px auto 0;font-size:15px;color:var(--muted)">
<li>确认上方 SVG 体检无拦截项，点「复制到公众号」</li><li>公众号后台 →「新的创作」→「文章」，在正文里按 Ctrl / ⌘ + V</li>
<li>填标题、上传封面，点「预览」发到手机检查，再群发</li></ol></div>
<script>${COPY_JS}
let src='';
function lintSvg(html){
  const kb=(new Blob([html]).size/1024).toFixed(1);
  const issues=[];
  if(/\\sid\\s*=/.test(html)) issues.push('包含 id=（会被微信删除）');
  if(/<filter|linearGradient|radialGradient|<clipPath|<mask|<style|<script|xlink:href/i.test(html)) issues.push('包含滤镜/渐变/clipPath/style/JS（会被微信清除）');
  if(/attributeName=["']fill-opacity["']/i.test(html)) issues.push('包含 fill-opacity 动画（微信中会导致文字隐形）');
  if(/file:\\/\\/|href="(?!https?:)[^"]+\\.(jpe?g|png|gif|webp)"/i.test(html)) issues.push('含本地图片路径（未传微信图床会丢失，需用 --push）');
  if(Number(kb)>1024) issues.push('体积超过 1MB（可能无法保存草稿）');
  const el=document.getElementById('lint');
  el.style.display='block';
  if(!issues.length){
    el.style.borderColor='var(--accent)';
    el.innerHTML='<strong style="color:var(--accent)">✓ 微信 SVG 规范体检通过</strong> · 当前体积 <code>'+kb+' KB</code> · 无禁用标签或属性。';
  }else{
    el.style.borderColor='#d9452b';
    el.innerHTML='<strong>⚠ 体检发现 '+issues.length+' 项需要注意</strong>（当前体积 <code>'+kb+' KB</code>）：'+issues.join('；')+'。';
  }
}
function show(html){src=html.trim();document.getElementById('drop').style.display='none';document.getElementById('ph').style.display='block';
  document.getElementById('cp').disabled=false;
  lintSvg(src);
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
</script>` +
    FOOT +
    "</body></html>"
  );
}

function indexPage(demos, heroArticle, styles, articlesBySlug) {
  const title = "小耳公众号SVG：让公众号文章自己动起来 · 免费开源 · Xiaoer Omia";
  const desc = "纯 SVG 公众号动效长图：往下拉一屏屏长出来，线稿自己画、数字滚动、等轴测 3D 小场景一块块拼起来。没有视频和代码，公众号原生支持。";
  const ld = JSON.stringify({
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "小耳公众号SVG（xiaoer-wx-svg）",
    applicationCategory: "DesignApplication",
    operatingSystem: "macOS, Windows, Linux",
    offers: { "@type": "Offer", price: "0", priceCurrency: "CNY" },
    url: BASE,
    sameAs: [REPO, UPSTREAM_REPO],
    publisher: { "@type": "Organization", name: "Xiaoer Omia", url: OMIA },
    description: desc,
  });

  const grid = demos
    .map(
      (d) => `<a href="/t/${esc(d.slug)}/" class="card">
  <div class="card-preview" data-t="${d.t}">
    <div class="card-preview-stage">${articlesBySlug[d.slug] || ""}</div>
  </div>
  <div class="card-body">
    <div class="mono">${esc(d.route)}</div>
    <h3 class="card-title">${esc(d.name)}</h3>
    <p class="card-desc">${esc(d.fit)}</p>
    <div style="margin-top:auto;padding-top:8px;font-size:13px;color:var(--accent)">查看实时演示 →</div>
  </div>
</a>`
    )
    .join("");

  const installCmd = "npx skills add OwenCedaric/xiaoer-wx-svg -a claude-code codex cursor -g -y";
  const ask = `用 ${REPO} 给我做一篇公众号 SVG 动效长图，题材是：____，资料在：____`;
  const safeHero = heroArticle.replaceAll("</template", "<\\/template");

  return (
    head(title, desc, "/", `<script type="application/ld+json">${ld}</script>`) +
    nav() +
    `<div class="wrap hero-stage">
  <svg class="hero-svg" viewBox="0 0 520 520" aria-hidden="true">
    <circle cx="260" cy="260" r="230" fill="none" stroke="var(--line)" stroke-width="1" stroke-dasharray="1446">
      <animate attributeName="stroke-dashoffset" from="1446" to="0" dur="1.8s" fill="freeze"/>
    </circle>
    <path d="M98 98 A230 230 0 0 1 422 98" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="460" opacity="0.75">
      <animate attributeName="stroke-dashoffset" from="460" to="0" dur="1.4s" begin="0.4s" fill="freeze"/>
    </path>
    <line x1="260" y1="16" x2="260" y2="38" stroke="var(--line)" stroke-width="1"/>
    <line x1="260" y1="482" x2="260" y2="504" stroke="var(--line)" stroke-width="1"/>
    <line x1="16" y1="260" x2="38" y2="260" stroke="var(--line)" stroke-width="1"/>
    <line x1="482" y1="260" x2="504" y2="260" stroke="var(--line)" stroke-width="1"/>
    <rect x="257" y="27" width="6" height="6" fill="var(--bg)" stroke="var(--accent)" stroke-width="1.2"/>
    <circle cx="422" cy="98" r="3" fill="var(--accent)"/>
  </svg>
  <div>
    <div class="mono">WECHAT SVG AGENT SKILL · OPEN SOURCE</div>
    <h1 style="font-size:clamp(36px,4.5vw,52px);line-height:1.15;margin:14px 0 20px">让公众号文章<br>自己动起来</h1>
    <p style="font-size:17px;color:var(--muted);max-width:480px">纯 SVG 动效长图：往下拉，一屏屏长出来。线稿自己画、数字滚动、3D 小场景一块块拼好。没有视频、没有 GIF、没有一行代码在跑，公众号原生支持。</p>
    <p style="font-size:15px;color:var(--muted);max-width:480px">交给你的 AI agent（Claude Code、Codex、Cursor……），它会先根据题材匹配或建议视觉风格，再生成、截帧自检并交付到草稿箱或粘贴台。</p>
    <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;background:var(--fill);border:1px solid var(--line);border-radius:4px;padding:10px 14px;margin:20px 0">
      <code id="install-cmd" style="font-size:12px;font-family:var(--mono);overflow-x:auto;white-space:nowrap">${esc(installCmd)}</code>
      <button class="link-action" type="button" onclick="copyEl('install-cmd', this)">复制</button>
    </div>
    <div style="display:flex;gap:10px;flex-wrap:wrap">
      <a class="btn" href="#start">开始使用</a>
      <a class="btn ghost" href="/themes/">浏览主题库 (${styles.length})</a>
      <a class="btn ghost" href="#templates">看模板</a>
    </div>
  </div>
  <div><div class="phone"><div class="screen" id="screen"><div style="display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:16px 16px 4px"><h1 style="padding:0;margin:0;font-size:16px;line-height:1.4;color:#111">小耳的四台电脑（3D版）</h1><button type="button" onclick="replayHero()" style="background:none;border:0;color:#888;font-size:12px;cursor:pointer;padding:0;white-space:nowrap">重播 ↻</button></div><div class="meta">真实演示 · 往下滑（722 个原生 SVG 动画）</div><div id="art"></div></div></div></div>
</div>

<div class="wrap">
  <div class="epigraph">“不用视频、不用 GIF、没有一行 JS——仅凭纯 SVG 原生时间轴，让公众号文章在微信里自己生长。”</div>
</div>

<div class="wrap" id="mechanism">
  <div class="sec-break"><span class="wm">理</span><h2>没有 JS，SVG 如何自己长出来</h2></div>
  <div class="mech-grid">
    <div>
      <svg viewBox="0 0 440 240" width="100%" style="display:block;border:1px solid var(--line);border-radius:4px;background:var(--surface2)" aria-label="零高容器与动态撑开画布原理图">
        <text x="16" y="26" font-family="Menlo,monospace" font-size="11" fill="var(--accent)">01 · HEIGHT: 0 CONTAINER (LONG.SVG)</text>
        <rect x="16" y="38" width="408" height="44" rx="3" fill="var(--bg)" stroke="var(--accent)" stroke-width="1.2" stroke-dasharray="4 3"/>
        <text x="28" y="64" font-family="sans-serif" font-size="12" fill="var(--ink)">整张动效长图叠在上方，初始不占文档流高度</text>
        <text x="16" y="114" font-family="Menlo,monospace" font-size="11" fill="var(--muted)">02 · SPACER SVG (&lt;animate attributeName="width"&gt;)</text>
        <rect x="16" y="126" width="140" height="60" rx="3" fill="var(--bg)" stroke="var(--line)" stroke-width="1.2">
          <animate attributeName="width" values="140;408;408;140" keyTimes="0;0.5;0.85;1" dur="5s" repeatCount="indefinite"/>
        </rect>
        <path d="M28 156 H130" stroke="var(--accent)" stroke-width="2" stroke-dasharray="6 4">
          <animate attributeName="d" values="M28 156 H130;M28 156 H392;M28 156 H392;M28 156 H130" keyTimes="0;0.5;0.85;1" dur="5s" repeatCount="indefinite"/>
        </path>
        <text x="16" y="214" font-family="sans-serif" font-size="11.5" fill="var(--muted)">随时间变宽 → 等比撑开高度 → 页面逐屏露出</text>
      </svg>
    </div>
    <div>
      <div class="mono">CORE MECHANISM · WXSVG.PY</div>
      <h3 style="font-size:24px;margin:8px 0 12px;line-height:1.3">零高容器 + 等比撑开画布</h3>
      <p style="color:var(--muted);font-size:15px;margin:0 0 12px">微信公众号会剥离所有 JS 与 <code>&lt;style&gt;</code>，但原生保留 SVG 的 <code>&lt;animate&gt;</code> 与 <code>&lt;animateTransform&gt;</code>。</p>
      <p style="color:var(--muted);font-size:15px;margin:0">引擎将长图放进 <code>height: 0</code> 容器，下方用一块透明画布按时间轴改变宽度；宽高比锁定后高度自动同步拉长，整篇文章便像胶片一样一屏屏展开。</p>
    </div>
  </div>
</div>

<div class="wrap" id="start">
  <div class="sec-break"><span class="wm">序</span><h2>三步交付</h2></div>
  <div class="three-col" style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px">
    <div class="card"><div class="card-body">
      <div class="mono">STEP 01</div><h3 class="card-title">把 Skill 交给 agent</h3>
      <pre id="ask" style="white-space:pre-wrap;font-size:12px;font-family:var(--mono);background:var(--fill);padding:10px;border-radius:4px;margin:4px 0">${esc(ask)}</pre>
      <button class="link-action" type="button" style="align-self:flex-start;margin-top:4px" onclick="copyEl('ask', this)">复制这句话 →</button>
    </div></div>
    <div class="card"><div class="card-body">
      <div class="mono">STEP 02</div><h3 class="card-title">风格路由、生成与自检</h3>
      <p class="card-desc">agent 会先扫描 <code>styles/</code> 为你推荐最契合的主题或全新风格提案，确认后生成分镜与长图并截帧自检。</p>
    </div></div>
    <div class="card"><div class="card-body">
      <div class="mono">STEP 03</div><h3 class="card-title">推草稿箱，或体检后复制</h3>
      <p class="card-desc">填了 AppID 可直接推进公众号草稿箱；不填也能用<a href="/paste/">粘贴台</a>做微信规范体检后一键复制。</p>
    </div></div>
  </div>
</div>

<div class="wrap" id="templates">
  <div class="sec-break"><span class="wm">版</span><h2>模板与矢量路线</h2></div>
  <p style="color:var(--muted);margin:0 0 28px;text-align:center">每张卡片上方均为纯矢量 SVG 实时示意：包含 Chronicle 编年体杂志长文、等轴测 3D 旅程与信息图套模板。</p>
  <div class="grid-cards">${grid}</div>
</div>

<div class="wrap">
  <div class="sec-break"><span class="wm">界</span><h2>能力边界与微信实测规矩</h2></div>
  <div class="chat-box">
    <div class="bubble left"><strong>能做到什么：</strong>5 条创作路线（套模板 / 等轴测 3D / 图片帧故事 / 品牌 VI / 视频改编）、18 种动效场景、11 套可扩展主题、点击揭开互动、本地截帧自检与微信图床上传。</div>
    <div class="bubble right"><strong>明确的能力边界：</strong>动画随打开计时，不能绑定滚动条进度；微信会删掉所有 <code>id</code>、<code>fill-opacity</code> 动画、滤镜、渐变、<code>clipPath</code>、<code>&lt;style&gt;</code> 与 JS，插音频整篇拒收；单篇需控制在 1MB 以内。</div>
  </div>
  <p style="text-align:center;margin-top:24px"><a class="btn ghost" href="${UPSTREAM_REPO}/blob/main/docs/wechat-svg-rules.md">查看完整规矩表</a></p>
</div>

<template id="src">${safeHero}</template>
<script>
const src=document.getElementById('src').innerHTML.trim();
function replayHero(){const a=document.getElementById('art');a.innerHTML='';document.getElementById('screen').scrollTop=0;requestAnimationFrame(()=>a.innerHTML=src);}
function copyEl(id,btn){const text=document.getElementById(id).textContent;navigator.clipboard.writeText(text).then(()=>{const old=btn.textContent;btn.textContent='已复制 ✓';setTimeout(()=>btn.textContent=old,1600);});}
function layoutCardPreviews(){
  document.querySelectorAll('.card-preview').forEach(box=>{
    const stage=box.querySelector('.card-preview-stage');
    if(!stage)return;
    stage.style.transform='scale('+(box.clientWidth/1080)+')';
    const t=Number(box.dataset.t||20);
    box.querySelectorAll('svg').forEach(s=>{try{s.pauseAnimations();s.setCurrentTime(t);}catch(e){}});
  });
}
addEventListener('resize',layoutCardPreviews);
replayHero();
layoutCardPreviews();
</script>
${FOOT}</body></html>`
  );
}

function main() {
  if (fs.existsSync(DIST)) fs.rmSync(DIST, { recursive: true, force: true });
  fs.mkdirSync(path.join(DIST, "paste"), { recursive: true });
  fs.mkdirSync(path.join(DIST, "themes"), { recursive: true });

  const styles = loadAllStyles();
  const urls = ["/", "/themes/", "/paste/"];
  const articlesBySlug = {};
  let heroArticle = "";

  for (const demo of DEMOS) {
    const article = loadDemoArticle(demo);
    articlesBySlug[demo.slug] = article;
    const dir = path.join(DIST, "t", demo.slug);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, "index.html"), demoPage(demo, article), "utf-8");
    urls.push(`/t/${demo.slug}/`);
    if (demo.slug === "isometric-journey" && article) heroArticle = article;
  }

  fs.writeFileSync(path.join(DIST, "index.html"), indexPage(DEMOS, heroArticle, styles, articlesBySlug), "utf-8");
  fs.writeFileSync(path.join(DIST, "themes", "index.html"), themesPage(styles), "utf-8");
  fs.writeFileSync(path.join(DIST, "paste", "index.html"), pastePage(), "utf-8");
  fs.writeFileSync(path.join(DIST, "robots.txt"), `User-agent: *\nAllow: /\nSitemap: ${BASE}/sitemap.xml\n`, "utf-8");
  fs.writeFileSync(
    path.join(DIST, "sitemap.xml"),
    `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls
      .map((u) => `<url><loc>${BASE}${u}</loc></url>`)
      .join("")}</urlset>\n`,
    "utf-8"
  );
  fs.writeFileSync(
    path.join(DIST, "llms.txt"),
    `# 小耳公众号SVG（xiaoer-wx-svg）· Xiaoer Omia 出品（Chronicle 重构版 · 主题作者 Cedaric）\n\n- 仓库：${REPO}\n- 原作：${UPSTREAM_REPO}\n- 主题库（${styles.length} 套）：${BASE}/themes/\n- 粘贴台：${BASE}/paste/\n`,
    "utf-8"
  );

  console.log(`✅ ${DIST}  ${urls.length} 页 · ${styles.length} 套主题（纯 Node 构建完成）`);
}

main();
