#!/usr/bin/env python3
"""把 content/ 里的数据渲染成 21 页静态 HTML。

    python3 reference/build.py

设计约束（对应 CLAUDE.md 质量规则）：
  · 题名 / slug / 🔒 / 难度 一律从 data/leetcode-index.json 派生，页面上不许手写；
  · 模板代码在页面上展示的字符串，就是 run_templates.py 拿去 exec 的那一份；
  · 章节数、题目数等全局数量由 content/ 计算后注入，禁止手写；
  · 校验一律跑在渲染产物 HTML 上（见 reference/check_*.py），不是跑在这里的 dict 上。

reference/ 与 content/ 属构建期资产，随书发布无妨，但不是读者要看的页面。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import content  # noqa: E402
from reference import lcindex  # noqa: E402

CHAPTERS = content.CHAPTERS
TIERS = [
    ("warmup", "热身", "建直觉，easy 为主"),
    ("standard", "标准", "模板直接套"),
    ("variant", "变体", "模板要扭，坑的来源"),
]
TIER_ZH = {k: zh for k, zh, _ in TIERS}
FONTS = ("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700"
         "&family=Noto+Sans+SC:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap")


# ---------------------------------------------------------------- 行内标记
def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def inline(s):
    """极简行内标记：**粗体**、`代码`、[文字](链接)。先转义再套标签。"""
    out = esc(s)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", out)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return out


def highlight(code):
    """给 Python 模板上色：注释走 .cm，其中 【骨架】/【插槽】 各有专色。
    只做一件事——找出行内第一个不在引号里的 #。"""
    lines = []
    for line in code.rstrip("\n").split("\n"):
        quote = None
        cut = None
        for i, ch in enumerate(line):
            if quote:
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == "#":
                cut = i
                break
        if cut is None:
            lines.append(esc(line))
            continue
        cm = line[cut:]
        cls = "cm slot" if "【插槽】" in cm else "cm bone" if "【骨架】" in cm else "cm"
        lines.append(esc(line[:cut]) + '<span class="{}">{}</span>'.format(cls, esc(cm)))
    return "\n".join(lines)


# ---------------------------------------------------------------- 页面骨架
def page(title, desc, body, depth, extra_js=()):
    up = "../" * depth
    scripts = "".join(
        '\n<script src="{}assets/{}" defer></script>'.format(up, j) for j in extra_js)
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" type="image/svg+xml" href="{up}assets/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{fonts}" rel="stylesheet" media="print" onload="this.media='all'">
<noscript><link href="{fonts}" rel="stylesheet"></noscript>
<link rel="stylesheet" href="{up}assets/handbook.css">
<script src="{up}assets/theme.js"></script>
</head>
<body>
<button class="theme-toggle" type="button" aria-label="切换深色/浅色模式" title="切换深色/浅色模式">
  <span class="sun" aria-hidden="true">☀️</span><span class="moon" aria-hidden="true">🌙</span>
</button>
<div class="wrap">
{body}
</div>{scripts}
</body>
</html>
""".format(title=esc(title), desc=esc(desc), up=up, fonts=FONTS, body=body, scripts=scripts)


def sec(tag_zh, tag_en, h2, inner, color=None, anchor=None):
    style = ' style="background:var(--{})"'.format(color) if color else ""
    aid = ' id="{}"'.format(anchor) if anchor else ""
    return ('<section{aid}>\n  <div class="sec-tag"><span class="cell"{style}></span>'
            '<span class="lab">{en} {zh}</span></div>\n  <h2>{h2}</h2>\n{inner}\n</section>\n'
            ).format(aid=aid, style=style, en=esc(tag_en), zh=esc(tag_zh), h2=inline(h2), inner=inner)


def bars(pattern="1,2,4,6,3,5w,2f,1f"):
    """signature 母题：一排高低不一的柱子（单调栈/柱状图）。"""
    out = []
    for tok in pattern.split(","):
        cls = "h" + tok[0]
        if "w" in tok:
            cls += " w"
        if "f" in tok:
            cls += " f"
        out.append('<span class="{}"></span>'.format(cls))
    return '<div class="bars" aria-hidden="true">{}</div>'.format("".join(out))


# ---------------------------------------------------------------- 题目条目
def problem_li(p):
    meta = lcindex.get(p["num"])
    badges = ""
    if meta["paid_only"]:
        badges += '<span class="badge lock" title="LeetCode Premium 题">🔒 premium</span>'
    if p.get("star"):
        badges += '<span class="badge star" title="hard，认脸即可">⭐ 认脸</span>'
    badges += '<span class="badge diff">{}</span>'.format(meta["difficulty"])
    return ('<li>\n    <div class="p-title"><a href="{url}" target="_blank" rel="noopener">'
            '{num} {title}</a>{badges}</div>\n'
            '    <div class="p-note">{note}</div>\n  </li>').format(
        url=lcindex.url(p["num"]), num=p["num"], title=esc(meta["title"]),
        badges=badges, note=inline(p["note"]))


def quiz_block(ch):
    items = []
    for i, q in enumerate(ch["quiz"], 1):
        meta = lcindex.get(q["num"])
        label = "" if q.get("hide_num") else '<a href="{}" target="_blank" rel="noopener">{} {}</a>：'.format(
            lcindex.url(q["num"]), q["num"], esc(meta["title"]))
        opts = "".join(
            '<button class="opt" type="button" data-ch="{no}">{label}</button>'.format(
                no=o, label=esc(content.chapter_label(o))) for o in q["options"])
        items.append(
            '<article class="q" data-answer="{ans}">\n'
            '  <p class="qprompt"><span class="qtype">30 秒识别</span>Q{i} · {label}{prompt}'
            '你的第一反应是哪个模式？</p>\n'
            '  <div class="opts">{opts}</div>\n'
            '  <details><summary>看答案</summary><div class="answer"><p>{why}</p></div></details>\n'
            '</article>'.format(ans=q["pattern"], i=i, label=label,
                                prompt=inline(q["prompt"]), opts=opts, why=inline(q["why"])))
    note = ("每章自测都会**混入恰好一道非本章题**，防止「读哪章选哪章」的条件反射；"
            "题面也一律取自本章未收录的题，避免凭记忆而非凭信号作答。")
    return ('<div class="quiz">\n{}\n<p class="quiz-note">{}</p>\n</div>'
            ).format("\n".join(items), inline(note))


# ---------------------------------------------------------------- 章页
def render_chapter(ch, prev_href, prev_label, next_href, next_label):
    pat = content.pattern(ch["no"])
    n_star = sum(1 for p in ch["problems"] if p.get("star"))
    parts = [
        '<nav class="crumb"><a href="../index.html">← 目录</a> · '
        '<a href="../cheatsheet.html">决策树速查</a></nav>\n',
        '<header class="ch">\n  {bars}\n  <div class="kicker">Pattern {no:02d} · {en}</div>\n'
        '  <h1>{no:02d} {zh}\n    <span class="zh">{tagline}</span>\n  </h1>\n'
        '  <div class="meta"><span>面试频率 <b>{freq}</b></span>'
        '<span>题目 <b>{np} 道</b></span><span>模板 <b>{nt} 个</b></span>'
        '<span>⭐认脸 <b>{ns} 道</b></span></div>\n</header>\n'.format(
            bars=bars(), no=ch["no"], en=esc(pat["title_en"]), zh=esc(pat["title_zh"]),
            tagline=esc(pat["tagline"]), freq=esc(ch["freq"]),
            np=len(ch["problems"]), nt=len(ch["templates"]), ns=n_star),
    ]

    # §1
    body = '<div class="oneliner">{}</div>\n'.format(inline(ch["mental_model"]))
    body += "".join("<p>{}</p>\n".format(inline(p)) for p in ch["mental_model_body"])
    parts.append(sec("一句话心智模型", "§1 Mental Model", "先记住这一句", body, anchor="s1"))

    # §2
    rows = "".join('<tr><td>{}</td><td>{}</td></tr>'.format(inline(a), inline(b))
                   for a, b in ch["signals"])
    body = ('<div class="tbl-scroll"><table class="sig-tbl"><thead><tr><th>题面出现…</th>'
            '<th>想到</th></tr></thead><tbody>{}</tbody></table></div>\n'.format(rows))
    body += ('<div class="routing"><div class="rt-head">分流条件 · 决策树同源</div>'
             '<p>{}</p></div>\n'.format(inline(ch["routing"])))
    parts.append(sec("识别信号", "§2 Recognition Signals", "看到什么，想到本章", body, anchor="s2"))

    # §3
    body = ('<p class="legend"><i class="bone">■ 【骨架】</i> 不变，闭着眼默写　'
            '<i class="slot">■ 【插槽】</i> 随题变化，写题前先问自己填什么</p>\n')
    for t in ch["templates"]:
        body += ('<div class="tpl">\n  <div class="tpl-head">{name}<span class="note">{note}</span></div>\n'
                 '  <pre><code>{code}</code></pre>\n  <div class="tpl-foot">{foot}</div>\n</div>\n'
                 ).format(name=esc(t["name"]), note=esc(t["note"]),
                          code=highlight(t["code"]), foot=inline(t["foot"]))
    parts.append(sec("模板代码", "§3 Template", "可默写的那几行", body, anchor="s3"))

    # §4
    body = ""
    for key, zh, hint in TIERS:
        ps = [p for p in ch["problems"] if p["tier"] == key]
        if not ps:
            continue
        body += ('<div class="tier">\n  <div class="tier-head"><span class="t">{zh}</span>'
                 '<span class="d">{hint}</span><span class="c">{n} 道</span></div>\n'
                 '  <ul class="plist">\n  {items}\n  </ul>\n</div>\n').format(
            zh=zh, hint=hint, n=len(ps), items="\n  ".join(problem_li(p) for p in ps))
    parts.append(sec("题目分层", "§4 Problems", "从建直觉到扭模板", body, anchor="s4"))

    # §5
    body = '<ol class="pits">\n{}\n</ol>\n'.format("\n".join(
        '<li><span class="pt">{}</span>——{}</li>'.format(inline(t), inline(d))
        for t, d in ch["pitfalls"]))
    body += "<h3>自测 · 30 秒识别模式</h3>\n" + quiz_block(ch)
    parts.append(sec("常见翻车点 + 自测", "§5 Pitfalls & Self-check", "会写不等于不翻车",
                     body, color="warn", anchor="s5"))

    parts.append('<nav class="next">\n  {prev}\n  {next}\n</nav>\n'.format(
        prev='<a href="{}">← {}</a>'.format(prev_href, esc(prev_label)) if prev_href
             else '<span class="disabled">← 已是第一章</span>',
        next='<a href="{}">{} →</a>'.format(next_href, esc(next_label)) if next_href
             else '<span class="disabled">已是最后一章 →</span>'))

    return page("{:02d} {} · 算法面试阈值手册".format(ch["no"], pat["title_zh"]),
                pat["tagline"], "\n".join(parts), depth=1, extra_js=("quiz.js",))


# ---------------------------------------------------------------- 目录页
def render_index():
    n_ch = len(CHAPTERS)
    n_p = len(content.curated_numbers())
    n_star = sum(1 for c in CHAPTERS for p in c["problems"] if p.get("star"))
    n_lock = sum(1 for c in CHAPTERS for p in c["problems"]
                 if lcindex.get(p["num"])["paid_only"])
    n_tpl = sum(len(c["templates"]) for c in CHAPTERS)

    parts = ['<header class="book-head">\n  {bars}\n'
             '  <div class="kicker">Algorithm Interview Threshold Handbook</div>\n'
             '  <h1>算法面试阈值手册\n    <span class="zh">达到面试不翻车的水平即停</span>\n  </h1>\n'
             '  <p class="lede">18 个模式，{n_p} 道题。不追求竞赛级精通，'
             '只解决三件事：5 分钟内认出模式、25 分钟写出能跑的代码、说清复杂度。'
             '中文讲解，术语与题名保留英文原文。</p>\n'
             '  <div class="meta"><span>共 <b>导读 + {n_ch} 章 + 速查 + 错题页</b></span>'
             '<span>模板 <b>{n_tpl} 个</b></span>'
             '<span>支持 <b>深色模式 / 打印导出 PDF</b></span></div>\n</header>\n'.format(
                 bars=bars(), n_p=n_p, n_ch=n_ch, n_tpl=n_tpl)]

    parts.append('<div class="stats">\n'
                 '  <div class="stat"><div class="n">{n_ch}</div><div class="l">核心模式</div></div>\n'
                 '  <div class="stat"><div class="n">{n_p}</div><div class="l">收录题目</div></div>\n'
                 '  <div class="stat"><div class="n">{n_star}</div><div class="l">⭐ 认脸即可（不必手写）</div></div>\n'
                 '  <div class="stat"><div class="n">{n_lock}</div><div class="l">🔒 premium 题</div></div>\n'
                 '</div>\n'.format(n_ch=n_ch, n_p=n_p, n_star=n_star, n_lock=n_lock))

    parts.append('<div class="callout">\n'
                 '  <p><b>面试前一晚只翻两页。</b>先看 <a href="cheatsheet.html">决策树速查</a> '
                 '（关键词 → 模式 → 模板，单屏可打印），再看 '
                 '<a href="mistakes.html">错题登记</a> 里自己真正翻过车的那几条。'
                 '章节是平时用的，速查页才是考前用的。</p>\n'
                 '  <p>第一次读请从 <a href="chapters/00-intro.html">导读</a> 开始：'
                 '它写明了本书<b>不覆盖什么</b>，以及达标之后怎么维持。</p>\n</div>\n')

    for gi, (name, tag, (lo, hi)) in enumerate(content.GROUPS, 1):
        lis = []
        for n in range(lo, hi + 1):
            p = content.pattern(n)
            row = ('<span class="n">{no:02d}</span><span class="t">{zh}</span>'
                   '<span class="d">{tag}</span>').format(
                       no=n, zh=esc(p["title_zh"]), tag=esc(p["tagline"]))
            if n in content.WRITTEN:
                lis.append('<li><a href="chapters/{}">{}</a></li>'.format(
                    content.chapter_href(n), row))
            else:
                lis.append('<li><a aria-disabled="true" href="#">{}<span class="badge diff">'
                           '待撰写</span></a></li>'.format(row))
        parts.append('<div class="part">\n  <div class="part-head"><span class="no">Group {gi}</span>'
                     '<h2>{name}</h2><span class="tag">{tag}</span></div>\n'
                     '  <ul class="toc">\n    {lis}\n  </ul>\n</div>\n'.format(
                         gi=gi, name=esc(name), tag=esc(tag), lis="\n    ".join(lis)))

    parts.append('<div class="part">\n  <div class="part-head"><span class="no">考前</span>'
                 '<h2>速查与复盘</h2><span class="tag">面试前一晚</span></div>\n  <ul class="toc">\n'
                 '    <li><a href="cheatsheet.html"><span class="n">19</span>'
                 '<span class="t">模式决策树 / 速查表</span>'
                 '<span class="d">关键词 → 模式 → 模板索引，单屏可打印</span></a></li>\n'
                 '    <li><a href="mistakes.html"><span class="n">20</span>'
                 '<span class="t">错题登记</span>'
                 '<span class="d">题号 / 模式 / 翻车点 / 重做日期，浏览器本地保存</span></a></li>\n'
                 '  </ul>\n</div>\n')

    parts.append('<p class="quiz-note">题名、slug、难度与 🔒 标记均取自 LeetCode 官方题目索引，'
                 '抓取于 {}。</p>\n'.format(lcindex.FETCHED_AT))

    return page("算法面试阈值手册 · Algorithm Interview Threshold Handbook",
                "18 个模式覆盖面试常见题型：识别信号、可默写模板、翻车点与 30 秒识别自测。",
                "\n".join(parts), depth=0)


# ---------------------------------------------------------------- 写盘
def write(out_dir, rel, html):
    path = os.path.join(out_dir, rel)
    os.makedirs(os.path.dirname(path) or out_dir, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return rel


def main(out_dir=ROOT, quiet=False):
    written = []
    write_ = lambda rel, html: write(out_dir, rel, html)  # noqa: E731
    # 章页之间的上一页/下一页：导读 → 01 … 18 → 速查页
    nav = [(content.chapter_href(c["no"]), content.chapter_label(c["no"])) for c in CHAPTERS]
    for i, c in enumerate(CHAPTERS):
        prev = nav[i - 1] if i else ("00-intro.html", "导读")
        nxt = nav[i + 1] if i + 1 < len(nav) else ("../cheatsheet.html", "决策树速查")
        written.append(write_("chapters/" + content.chapter_href(c["no"]),
                              render_chapter(c, prev[0], prev[1], nxt[0], nxt[1])))

    written.append(write_("index.html", render_index()))

    if not quiet:
        for rel in written:
            print("  " + rel)
        print("{} 章已渲染，{} 页写出".format(len(CHAPTERS), len(written)))
        missing = [n for n in range(1, 19) if n not in content.WRITTEN]
        if missing:
            print("待撰写章节: {}".format(missing))
    return written


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=ROOT, help="输出目录（mutation test 用临时目录）")
    ap.add_argument("--quiet", action="store_true")
    main(ap.parse_args().out, ap.parse_args().quiet)
