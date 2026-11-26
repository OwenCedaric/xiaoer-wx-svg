"""Chronicle 深度定制杂志长文场景库。

主题作者：Cedaric（基于 Chronicle Design System 深度定制）
特点：
  1. 极简克制：单一中性底色 + 单一雾霾蓝强调色，无物理投影、无网格底纹。
  2. 字体极性：衬线体（Serif）负责标题、引语与空心描边大字；无衬线细体（Light 300）负责左对齐长文叙事。
  3. 留白即节奏：大尺度垂直留白、80% 视口几何锚点圆、虚线章节分隔与结构化双人对话。

场景列表：
  chronicle_hero      开场屏：80% 几何细线圆 + 空心描边大字 + 衬线标题与副标
  chronicle_epigraph  章节与长文屏：虚线章节分隔（带淡水印）+ 居中引语 + 左对齐细体叙事
  chronicle_chat      结构化对话屏：中央竖轴 + 左右交替气泡（左线框、右淡底）
  chronicle_coda      极简落版屏：上下衬线框行 + 巨型空心描边收尾字符
"""
from html import escape

from scenes import CN, MONO, SCREEN, W, anim, draw, fade, fit, n, op, rise, slide_in, text, text_w, typed

SERIF = "'Songti SC', 'Noto Serif CJK SC', 'STSong', Georgia, serif"


NO_HEAD = "，。、：；！？）」』”’,.;:!?)%"


def _wrap_lines(s, size, maxw, font=CN):
    """按字符宽度折行，保留显式换行，标点不落行首。"""
    out = []
    for para in str(s).split("\n"):
        if not para:
            out.append("")
            continue
        cur, cw = "", 0.0
        for ch in para:
            w = size if ord(ch) > 0x2E7F else (size * 0.32 if ch == " " else size * 0.56)
            if cur and cw + w > maxw and ch not in NO_HEAD:
                out.append(cur)
                cur, cw = ch, w
            else:
                cur += ch
                cw += w
        if cur:
            out.append(cur)
    return out


def _hollow_text(x, y, s, size, color, weight=700, anchor="middle", font=SERIF, stroke_w=2, stroke_op=0.6):
    """Chronicle 空心描边大字（仅用纯色 stroke + fill='none'，微信原生支持）。"""
    return (f'<text x="{n(round(x, 1))}" y="{n(round(y, 1))}" font-size="{n(round(size, 1))}" '
            f'fill="none" stroke="{color}" stroke-width="{n(stroke_w)}" stroke-opacity="{n(stroke_op)}" '
            f'font-weight="{weight}" text-anchor="{anchor}" font-family="{font}">{escape(str(s))}</text>')


# ---------------------------------------------------------------- chronicle_hero
def chronicle_hero(d, y, t, th):
    """开场屏：80% 几何细线圆 + 空心描边大字 + 衬线主标题 + 左对齐导语。"""
    out = []
    tx, g, a, ln = th["text"], th["grey"], th["accent"], th["line"]
    cx, cy = W / 2, y + SCREEN / 2

    # 80vmin 几何锚点圆（1080 * 0.8 = 864，半径 432）
    r = 432
    circle_d = f"M{cx - r} {cy}a{r} {r} 0 1 0 {2 * r} 0a{r} {r} 0 1 0 {-2 * r} 0"
    out.append(draw(circle_d, t, 1.4, ln, width=2, glow=False))

    # 顶栏小字
    if d.get("kicker"):
        k_el = (f'<text x="110" y="{y + 180}" font-size="24" fill="{a}" font-weight="600" '
                f'letter-spacing="4" font-family="{MONO}">{escape(d["kicker"].upper())}</text>')
        out.append(fade(k_el, t + 0.3, 0.6))

    # 空心描边巨字（居中偏上）
    mark = d.get("mark", "序")
    mark_size = fit(mark, 260, 760, SERIF, floor=0.45)
    out.append(fade(_hollow_text(cx, cy - 110, mark, mark_size, tx, weight=700, stroke_w=2.5, stroke_op=0.55), t + 0.5, 0.9))

    # 主标题（衬线加粗，左对齐或居中）
    title = d.get("title", "")
    if title:
        t_lines = _wrap_lines(title, 68, 860, SERIF)[:2]
        for i, line in enumerate(t_lines):
            out.append(rise(text(110, cy + 120 + i * 92, line, 68, tx, 700, "start", SERIF, maxw=860), t + 1.0 + i * 0.25, 0.7, 45))

    # 副标 / 导语（无衬线 Light 300，左对齐，1.85 倍行距）
    sub_y = cy + 120 + len(_wrap_lines(title, 68, 860, SERIF)[:2]) * 92 + 56
    if d.get("subtitle"):
        s_lines = _wrap_lines(d["subtitle"], 34, 860, CN)[:3]
        for i, line in enumerate(s_lines):
            out.append(rise(text(110, sub_y + i * 63, line, 34, g, 300, "start", CN, maxw=860), t + 1.6 + i * 0.2, 0.7, 35))

    # 底部作者/元信息标记
    meta_line = d.get("meta", "")
    if meta_line:
        out.append(fade(text(110, y + SCREEN - 140, meta_line, 24, g, 400, "start", MONO, maxw=860), t + 2.4, 0.6))

    return out, 7.6


# ---------------------------------------------------------------- chronicle_epigraph
def chronicle_epigraph(d, y, t, th):
    """章节与长文屏：虚线章节分隔（带淡水印）+ 居中引语 + 左对齐细体叙事。"""
    out = []
    tx, g, a, ln = th["text"], th["grey"], th["accent"], th["line"]

    # 1. Section Break（虚线 + 水印 + 衬线标题）
    sec = d.get("section")
    cur_y = y + 230
    if sec:
        wm = d.get("watermark") or sec[0]
        wm_el = (f'<text x="540" y="{cur_y + 70}" font-size="220" fill="{tx}" opacity="0.04" '
                 f'font-weight="700" text-anchor="middle" font-family="{SERIF}">{escape(wm)}</text>')
        out.append(fade(wm_el, t + 0.1, 0.8))

        tw = min(text_w(sec, 48, SERIF), 520)
        lx1, lx2 = 110, 540 - tw / 2 - 40
        rx1, rx2 = 540 + tw / 2 + 40, 970
        if lx2 > lx1 + 20:
            l_line = f'<line x1="{lx1}" y1="{cur_y}" x2="{lx2:.0f}" y2="{cur_y}" stroke="{ln}" stroke-width="2" stroke-dasharray="8 8"/>'
            r_line = f'<line x1="{rx1:.0f}" y1="{cur_y}" x2="{rx2}" y2="{cur_y}" stroke="{ln}" stroke-width="2" stroke-dasharray="8 8"/>'
            out.append(fade(l_line + r_line, t + 0.2, 0.6))

        out.append(rise(text(540, cur_y + 16, sec, 48, tx, 700, "middle", SERIF, maxw=560), t + 0.3, 0.7, 30))
        cur_y += 210

    # 2. Epigraph（居中引语，大留白隔离）
    epi = d.get("epigraph")
    t_epi = t + 0.9
    if epi:
        e_lines = _wrap_lines(epi, 34, 760, SERIF)[:3]
        for i, line in enumerate(e_lines):
            el = (f'<text x="540" y="{cur_y + i * 58}" font-size="34" fill="{g}" font-style="italic" '
                  f'font-weight="400" text-anchor="middle" font-family="{SERIF}">{escape(line)}</text>')
            out.append(fade(el, t_epi + i * 0.2, 0.7))
        cur_y += len(e_lines) * 58 + 150

    # 3. Symbolic Keyword（可选：衬线加粗 + 字距 + 强调色）
    t_body = t_epi + 0.9
    if d.get("keyword"):
        kw_el = (f'<text x="110" y="{cur_y}" font-size="32" fill="{a}" font-weight="600" '
                 f'letter-spacing="4" font-family="{SERIF}">{escape(d["keyword"])}</text>')
        out.append(slide_in(kw_el, t_body, -30, 0.6))
        cur_y += 88

    # 4. Narrative Body（严格左对齐、Light 300、1.85 倍行距）
    paras = d.get("paragraphs", [])
    if isinstance(paras, str):
        paras = [paras]
    step_t = t_body + 0.3
    for p_idx, para in enumerate(paras[:3]):
        p_lines = _wrap_lines(para, 34, 860, CN)
        for l_idx, line in enumerate(p_lines):
            if cur_y + l_idx * 63 > y + SCREEN - 140:
                break
            out.append(rise(text(110, cur_y + l_idx * 63, line, 34, tx, 300, "start", CN, maxw=860),
                            step_t + l_idx * 0.14, 0.65, 28))
        cur_y += len(p_lines) * 63 + 64
        step_t += 0.6 + len(p_lines) * 0.14

    dur = max(7.5, step_t - t + 1.4)
    return out, dur


# ---------------------------------------------------------------- chronicle_chat
def chronicle_chat(d, y, t, th):
    """结构化对话屏：中央竖轴 + 左右交替气泡（左底色细边框、右 8% 淡底无边框）。"""
    out = []
    tx, g, a, ln, bg, pan = th["text"], th["grey"], th["accent"], th["line"], th["bg"], th["panel"]

    # 顶部标题
    cur_y = y + 190
    if d.get("kicker"):
        out.append(fade(text(110, cur_y, d["kicker"], 24, a, 600, "start", MONO, maxw=860), t + 0.1, 0.5))
        cur_y += 64
    if d.get("title"):
        out.append(rise(text(110, cur_y, d["title"], 52, tx, 700, "start", SERIF, maxw=860), t + 0.25, 0.65, 35))
        cur_y += 110

    # 中央 1px 竖轴
    axis_top = cur_y
    axis_bot = y + SCREEN - 200
    out.append(draw(f"M540 {axis_top}V{axis_bot}", t + 0.4, 1.0, ln, width=2, glow=False))

    messages = d.get("messages", [])[:5]
    msg_y = axis_top + 40
    t_msg = t + 0.7

    for idx, msg in enumerate(messages):
        side = msg.get("side", "left" if idx % 2 == 0 else "right")
        speaker = msg.get("speaker", "")
        content = msg.get("text", "")
        lines = _wrap_lines(content, 30, 580, CN)[:4]
        lh = 52
        pad_x, pad_y = 36, 32
        max_lw = max((text_w(l, 30, CN) for l in lines), default=120)
        bw = min(max(max_lw + pad_x * 2, 240), 700)
        bh = len(lines) * lh + pad_y * 2 - 12

        if msg_y + bh > axis_bot:
            break

        if side == "left":
            bx = 110
            # 左气泡：Base Surface 背景 + 细边框 + 2px 左上尖角视觉标记
            bub = [
                f'<rect x="{bx}" y="{msg_y}" width="{bw:.0f}" height="{bh}" rx="18" fill="{bg}" stroke="{ln}" stroke-width="2"/>',
                f'<rect x="{bx}" y="{msg_y}" width="18" height="18" rx="2" fill="{bg}" stroke="{ln}" stroke-width="2"/>',
                f'<rect x="{bx + 2}" y="{msg_y + 2}" width="20" height="20" fill="{bg}"/>',
            ]
            dx_anim = -40
        else:
            bx = 970 - bw
            # 右气泡：Subtle Fill 8% 淡底 + 无边框
            bub = [
                f'<rect x="{bx:.0f}" y="{msg_y}" width="{bw:.0f}" height="{bh}" rx="18" fill="{pan}"/>',
                f'<rect x="{bx + bw - 18:.0f}" y="{msg_y}" width="18" height="18" rx="2" fill="{pan}"/>',
            ]
            dx_anim = 40

        if speaker:
            sp_x = bx if side == "left" else 970
            sp_anchor = "start" if side == "left" else "end"
            out.append(fade(text(sp_x, msg_y - 16, speaker, 22, g, 600, sp_anchor, SERIF, maxw=400), t_msg, 0.45))

        for li, line in enumerate(lines):
            bub.append(text(bx + pad_x, msg_y + pad_y + 28 + li * lh, line, 30, tx, 300, "start", CN, maxw=bw - pad_x * 2))

        out.append(slide_in("".join(bub), t_msg + 0.1, dx_anim, 0.6))
        msg_y += bh + (68 if speaker else 44)
        t_msg += 1.05

    if d.get("caption"):
        out.append(fade(text(110, y + SCREEN - 120, d["caption"], 26, g, 300, "start", CN, maxw=860), t_msg + 0.4, 0.6))

    return out, max(8.0, t_msg - t + 1.6)


# ---------------------------------------------------------------- chronicle_coda
def chronicle_coda(d, y, t, th):
    """极简落版屏：上下衬线框行 + 巨型空心描边字符 + 底部注记。"""
    out = []
    tx, g, a, ln = th["text"], th["grey"], th["accent"], th["line"]
    cx, cy = W / 2, y + SCREEN / 2

    top_row = d.get("top", "")
    if top_row:
        el = (f'<text x="540" y="{cy - 280}" font-size="28" fill="{g}" font-weight="400" '
              f'letter-spacing="8" text-anchor="middle" font-family="{SERIF}">{escape(top_row)}</text>')
        out.append(fade(el, t + 0.2, 0.7))

    # 巨型空心描边字符
    mark = d.get("mark", "终")
    mark_size = fit(mark, 240, 720, SERIF, floor=0.4)
    out.append(fade(_hollow_text(cx, cy + 70, mark, mark_size, tx, weight=700, stroke_w=2.5, stroke_op=0.6), t + 0.6, 0.9))

    bot_row = d.get("bottom", "")
    if bot_row:
        el = (f'<text x="540" y="{cy + 270}" font-size="28" fill="{g}" font-weight="400" '
              f'letter-spacing="6" text-anchor="middle" font-family="{SERIF}">{escape(bot_row)}</text>')
        out.append(fade(el, t + 1.1, 0.7))

    # 分隔短线 + 强调色网址/署名
    out.append(draw(f"M480 {cy + 360}H600", t + 1.5, 0.6, ln, width=2, glow=False))
    if d.get("url"):
        out.append(typed(540, cy + 430, d["url"], 26, t + 1.8, a, step=0.05, font=MONO, weight=400, maxw=860))

    note = d.get("note", "")
    if note:
        out.append(fade(text(540, y + SCREEN - 140, note, 24, g, 300, "middle", CN, maxw=860), t + 2.4, 0.6))

    return out, 7.2


SCENES = {
    "chronicle_hero": chronicle_hero,
    "chronicle_epigraph": chronicle_epigraph,
    "chronicle_chat": chronicle_chat,
    "chronicle_coda": chronicle_coda,
}
