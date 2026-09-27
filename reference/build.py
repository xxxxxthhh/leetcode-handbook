#!/usr/bin/env python3
"""把 content/ 里的数据渲染成 22 页静态 HTML。

    python3 reference/build.py

设计约束（对应 CLAUDE.md 质量规则）：
  · 题名 / slug / 🔒 / 难度 一律从 data/leetcode-index.json 派生，页面上不许手写；
  · 模板代码在页面上展示的字符串，就是 run_templates.py 拿去 exec 的那一份；
  · 章节数、题目数等全局数量由 content/ 计算后注入，禁止手写；
  · 校验一律跑在渲染产物 HTML 上（见 reference/check_*.py），不是跑在这里的 dict 上。

reference/ 与 content/ 属构建期资产，随书发布无妨，但不是读者要看的页面。
"""
import hashlib
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


def shuffled_options(q):
    """选项顺序必须打乱：内容里选项是「本章优先」手写的，直接渲染的话正确答案
    会长期落在第一个（分流题落在第二个），读者点第一个按钮就能刷分，
    「30 秒识别」就退化成猜位置了。

    用题号做种子 + md5 排序，保证同一道题每次构建顺序都一样（diff 干净），
    又与作者的书写顺序无关。check_site.py 会核对全书答案位置的分布不退化。"""
    return sorted(q["options"],
                  key=lambda o: hashlib.md5("{}:{}".format(q["num"], o).encode()).hexdigest())


def quiz_block(ch):
    items = []
    for i, q in enumerate(ch["quiz"], 1):
        meta = lcindex.get(q["num"])
        label = "" if q.get("hide_num") else '<a href="{}" target="_blank" rel="noopener">{} {}</a>：'.format(
            lcindex.url(q["num"]), q["num"], esc(meta["title"]))
        opts = "".join(
            '<button class="opt" type="button" data-ch="{no}">{label}</button>'.format(
                no=o, label=esc(content.chapter_label(o))) for o in shuffled_options(q))
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


# ---------------------------------------------------------------- 附录 A
APX_HREF = "appendix-a.html"
APX_LABEL = "附录 A · Python 刷题急救包"


def appendix_shuffled_options(i, options):
    """与 shuffled_options 同一理由：内容里选项是「正确项优先」手写的，直接渲染
    正确答案会长期落在第一个。独立成函数是为了让 mutation test 能打桩——
    章节那条 mutation 打的是 shuffled_options，够不着这里。"""
    return sorted(options,
                  key=lambda o: hashlib.md5("A{}:{}".format(i, o[0]).encode()).hexdigest())


def appendix_quiz_block(apx):
    """「30 秒改错」题型：带 bug 的代码片段 + 4 个说法选项。
    沿用章节自测的 .q/.opt/data-answer 结构，quiz.js 无需改动；
    选项顺序与章节自测同理必须打乱（题号做种子，构建可复现）。"""
    items = []
    for i, q in enumerate(apx.QUIZ, 1):
        opts = appendix_shuffled_options(i, q["options"])
        buttons = "".join(
            '<button class="opt" type="button" data-ch="{}">{}</button>'.format(k, esc(t))
            for k, t in opts)
        items.append(
            '<article class="q" data-answer="{ans}">\n'
            '  <p class="qprompt"><span class="qtype">30 秒改错</span>Q{i} · '
            '这段代码里埋了一个 Python 专属的坑——错在哪？</p>\n'
            '  <pre><code>{code}</code></pre>\n'
            '  <div class="opts">{buttons}</div>\n'
            '  <details><summary>看答案</summary><div class="answer"><p>{why}</p></div></details>\n'
            '</article>'.format(ans=q["answer"], i=i, code=highlight(q["code"]),
                                buttons=buttons, why=inline(q["why"])))
    note = ("{} 道改错题与 §2 的 {} 个翻车点一一对应；每段代码的 bug 都在构建时"
            "实际执行证明过是真的。选项顺序构建时打乱，别背位置。").format(
                len(apx.QUIZ), len(apx.PITFALLS))
    return '<div class="quiz">\n{}\n<p class="quiz-note">{}</p>\n</div>'.format(
        "\n".join(items), inline(note))


def render_appendix():
    from content import appendix_a as apx

    entry_group = {}
    for g in apx.GROUPS:
        for e in g["entries"]:
            entry_group[e["id"]] = g["title"]

    # 每题「出自正文哪一章哪一层」从 content 派生；重复收录时取章号最小的一处
    tier_of = {}
    for c in CHAPTERS:
        for p in c["problems"]:
            tier_of.setdefault(p["num"], (c["no"], p["tier"]))

    st = dict(
        n_entries=len(entry_group),
        n_pits=len(apx.PITFALLS),
        n_prob=len(apx.PROBLEMS),
        n_quiz=len(apx.QUIZ),
        n_warm_total=sum(1 for c in CHAPTERS for p in c["problems"] if p["tier"] == "warmup"),
        n_warm_rehab=sum(1 for p in apx.PROBLEMS
                         if tier_of.get(p["num"], (0, ""))[1] == "warmup"),
    )
    st["warm_pct"] = round(100 * st["n_warm_rehab"] / st["n_warm_total"])

    parts = [
        '<nav class="crumb"><a href="../index.html">← 目录</a> · 附录 A</nav>\n',
        '<header class="ch">\n  {bars}\n  <div class="kicker">Appendix A · Python Rehab Kit</div>\n'
        '  <h1>附录 A Python 刷题急救包\n    <span class="zh">复健，不是学习——主体动作是打字</span>\n  </h1>\n'
        '  <div class="meta"><span>惯用法 <b>{n_entries} 条</b></span>'
        '<span>翻车点 <b>{n_pits} 个</b></span><span>复健题 <b>{n_prob} 道</b></span>'
        '<span>改错自测 <b>{n_quiz} 题</b></span></div>\n</header>\n'.format(bars=bars(), **st),
    ]

    # §1 划定范围
    body = "".join("<p>{}</p>\n".format(inline(p.format(**st))) for p in apx.INTRO)
    body += "<p>{}</p>\n".format(inline(apx.NO_NEED_LEAD))
    body += '<div class="callout no">\n<ul>\n{}\n</ul>\n</div>\n'.format(
        "\n".join("  <li>{}</li>".format(inline(x)) for x in apx.NO_NEED))
    parts.append(sec("划定范围", "§1 Scope", "复健，不是学习", body, color="warn", anchor="s1"))

    # §2 惯用法速查
    body = ('<p class="legend">按使用频率排序。编号（C1、W1、Q5…）供 §3 的'
            '「复健自查」引用，点编号可跳回。</p>\n')
    for g in apx.GROUPS:
        lines = []
        for e in g["entries"]:
            lines.append('<span class="eid" id="e-{0}">{0}</span>  {1}'.format(
                e["id"], highlight(e["code"])))
        body += ('<div class="tpl">\n  <div class="tpl-head">{name}</div>\n'
                 '  <pre><code>{code}</code></pre>\n</div>\n').format(
                     name=esc(g["title"]), code="\n".join(lines))
    body += "<h3>五个 Python 专属翻车点</h3>\n"
    body += '<ol class="pits">\n{}\n</ol>\n'.format("\n".join(
        '<li><span class="pt">{title}</span>——{why}\n'
        '<pre><code><span class="eid" id="e-{pid}">{pid}</span>  {bad}</code></pre></li>'.format(
            pid=p["id"], title=inline(p["title"]), why=inline(p["why"]),
            bad=highlight(p["bad"]))
        for p in apx.PITFALLS))
    parts.append(sec("惯用法速查", "§2 Cheat Sheet", "拿来查的，不是拿来读的", body, anchor="s2"))

    # §3 打字复健计划
    body = ('<div class="callout">\n<p><b>规则，一条都别放水：</b></p>\n<ul>\n{}\n</ul>\n</div>\n'
            ).format("\n".join("  <li>{}</li>".format(inline(r)) for r in apx.RULES))
    body += ("<p>{}</p>\n".format(inline(
        "{n_prob} 道复健题，每道标注它复健的惯用法。它们同时全部收录在正文各章"
        "（其中 {n_warm_rehab} 道是热身层）——**双重用途**：打完这一页，"
        "全书 {n_warm_total} 道热身题你已经完成了 {warm_pct}%。".format(**st))))
    lis = []
    for p in apx.PROBLEMS:
        meta = lcindex.get(p["num"])
        badges = ""
        if meta["paid_only"]:
            badges += '<span class="badge lock" title="LeetCode Premium 题">🔒 premium</span>'
        badges += '<span class="badge diff">{}</span>'.format(meta["difficulty"])
        src = tier_of.get(p["num"])
        if src:
            badges += '<span class="badge src">正文 {:02d} · {}</span>'.format(
                src[0], TIER_ZH[src[1]])
        refs = []
        for r in p["refs"]:
            if r not in entry_group and not any(x["id"] == r for x in apx.PITFALLS):
                raise ValueError("附录 A：题 {} 引用了不存在的速查条目 {}".format(p["num"], r))
            refs.append('<a href="#e-{0}"><code>{0}</code></a>'.format(r))
        lis.append(
            '<li>\n    <div class="p-title"><a href="{url}" target="_blank" rel="noopener">'
            '{num} {title}</a>{badges}</div>\n'
            '    <div class="p-note">复健目标：{goal}</div>\n'
            '    <details><summary>复健自查（卡住再点开，不是题解）</summary>'
            '<div class="answer rehab-refs"><p>本题用到：{refs}——逐条对着敲；'
            '还是卡，回 §2 看整组，仍然不看题解。</p></div></details>\n  </li>'.format(
                url=lcindex.url(p["num"]), num=p["num"], title=esc(meta["title"]),
                badges=badges, goal=inline(p["goal"]), refs="、".join(refs)))
    body += ('<div class="tier">\n  <div class="tier-head"><span class="t">复健题单</span>'
             '<span class="d">按数据结构由简到繁，全部手打</span><span class="c">{} 道</span></div>\n'
             '  <ul class="plist">\n  {}\n  </ul>\n</div>\n').format(
                 len(apx.PROBLEMS), "\n  ".join(lis))
    body += ('<div class="routing"><div class="rt-head">出口标准 · Exit Criteria</div>'
             '<p>{}</p></div>\n'.format(inline(apx.EXIT.format(**st))))
    parts.append(sec("打字复健计划", "§3 Typing Rehab", "本页的主体：手打这 {} 道".format(
        st["n_prob"]), body, anchor="s3"))

    # §4 改错自测
    body = ('<p>给你一段带 bug 的代码，30 秒内指出错在哪。'
            '五段代码分别踩了 §2 的五个翻车点。</p>\n') + appendix_quiz_block(apx)
    parts.append(sec("自测 · 30 秒改错", "§4 Self-check", "看得出坑，才算复健完成",
                     body, color="warn", anchor="s4"))

    parts.append('<nav class="next">\n  <a href="00-intro.html">← 00 导读</a>\n'
                 '  <a href="{}">{} →</a>\n</nav>\n'.format(
                     content.chapter_href(1), esc(content.chapter_label(1))))

    return page("附录 A Python 刷题急救包 · 算法面试阈值手册",
                "太久没自己写代码的复健页：惯用法速查（逐条执行验证）+ 10 道手打复健题 + 30 秒改错自测。",
                "\n".join(parts), depth=1, extra_js=("quiz.js",))


# ---------------------------------------------------------------- 全书统计
def stats():
    """全局数量一律在这里算一次，页面上任何数字都从这里取，禁止手写。"""
    return dict(
        n_ch=len(CHAPTERS),
        n_prob=len(content.curated_numbers()),
        n_tpl=sum(len(c["templates"]) for c in CHAPTERS),
        n_star=sum(1 for c in CHAPTERS for p in c["problems"] if p.get("star")),
        n_lock=sum(1 for c in CHAPTERS for p in c["problems"]
                   if lcindex.get(p["num"])["paid_only"]),
        n_pit=sum(len(c["pitfalls"]) for c in CHAPTERS),
        n_quiz=sum(len(c["quiz"]) for c in CHAPTERS),
        n_assert=sum(t["tests"].count("assert ") for c in CHAPTERS for t in c["templates"]),
    )


# ---------------------------------------------------------------- 导读页
def render_intro():
    from content import intro
    st = stats()

    def fill(s):
        return inline(s.format(**st))

    parts = ['<nav class="crumb"><a href="../index.html">← 目录</a> · 导读</nav>\n',
             '<header class="ch">\n  {bars}\n  <div class="kicker">Chapter 00 · How to Use</div>\n'
             '  <h1>00 导读\n    <span class="zh">达到面试不翻车的水平即停</span>\n  </h1>\n'
             '  <div class="meta"><span>模式 <b>{n_ch} 个</b></span>'
             '<span>题目 <b>{n_prob} 道</b></span><span>模板 <b>{n_tpl} 个</b></span>'
             '<span>翻车点 <b>{n_pit} 条</b></span></div>\n</header>\n'.format(
                 bars=bars(), **st)]

    for i, s in enumerate(intro.SECTIONS, 1):
        body = "".join("<p>{}</p>\n".format(fill(p)) for p in s.get("paras", []))
        if "cards" in s:
            body += '<div class="stats">\n{}\n</div>\n'.format("\n".join(
                '  <div class="stat"><div class="n">{}</div><div class="l">{}</div></div>'.format(
                    fill(n), fill(t)) for n, t in s["cards"]))
        if "nolist" in s:
            # 引导句已经说了「本书明确不覆盖：」，这里不再重复一遍标题
            body += ('<div class="callout no">\n<ul>\n{}\n</ul>\n</div>\n'
                     ).format("\n".join("  <li>{}</li>".format(fill(x)) for x in s["nolist"]))
        if "list" in s:
            body += "<ul>\n{}\n</ul>\n".format(
                "\n".join("  <li>{}</li>".format(fill(x)) for x in s["list"]))
        if "table" in s:
            head, rows = s["table"]
            body += ('<div class="tbl-scroll"><table><thead><tr>{}</tr></thead><tbody>{}'
                     '</tbody></table></div>\n').format(
                "".join("<th>{}</th>".format(esc(h)) for h in head),
                "".join("<tr>{}</tr>".format(
                    "".join("<td>{}</td>".format(fill(c)) for c in r)) for r in rows))
        body += "".join("<p>{}</p>\n".format(fill(p)) for p in s.get("tail", []))
        parts.append(sec(s["tag"][1], s["tag"][0], s["h2"], body,
                         color="warn" if "nolist" in s else None, anchor="s{}".format(i)))

    parts.append('<nav class="next">\n  <a href="../index.html">← 目录</a>\n'
                 '  <a href="{}">{} →</a>\n</nav>\n'.format(APX_HREF, esc(APX_LABEL)))

    return page("00 导读 · 算法面试阈值手册",
                "阈值策略、三条达标标准、明确不覆盖的内容、怎么用这本书、达标之后怎么维持。",
                "\n".join(parts), depth=1)


# ---------------------------------------------------------------- 速查页
def render_cheatsheet():
    from content import tree as tree_mod
    st = stats()

    # ① 决策树：分支条件由 content/tree.py 定，叶子指向章节页
    lines = []
    for gi, (name, sub, leaves) in enumerate(tree_mod.TREE):
        last_group = gi == len(tree_mod.TREE) - 1
        lines.append('<span class="node">{}<b>{}</b>　<span class="cue">{}</span></span>'.format(
            "└─ " if last_group else "├─ ", esc(name), esc(sub)))
        for li, (cond, no) in enumerate(leaves):
            stem = "　 " if last_group else "│  "
            branch = "└─ " if li == len(leaves) - 1 else "├─ "
            lines.append('<span class="node">{}{}<span class="cond">{}</span>'
                         '　→　<a class="leaf" href="chapters/{}">{}</a></span>'.format(
                             stem, branch, inline(cond), content.chapter_href(no),
                             esc(content.chapter_label(no))))
    tree_html = '<div class="tree">{}</div>'.format("<br>\n".join(lines))

    # ② 关键词索引：直接汇总各章 §2，不另写一套（分流条件与各章 §2 天然一致）
    rows = []
    for c in CHAPTERS:
        for cue, _to in c["signals"]:
            rows.append((cue, c["no"]))
    rows.sort(key=lambda r: (r[1], r[0]))
    idx_html = ('<div class="tbl-scroll"><table class="idx-tbl"><thead><tr>'
                '<th>题面出现…</th><th>去哪一章</th></tr></thead><tbody>{}</tbody></table></div>'
                ).format("".join(
                    '<tr><td>{}</td><td class="to"><a href="chapters/{}">{}</a></td></tr>'.format(
                        inline(cue), content.chapter_href(no), esc(content.chapter_label(no)))
                    for cue, no in rows))

    # ③ 同名陷阱：跨章重复的关键词，和校验器共用 patterns.KEYWORDS
    kw_map = {}
    for c in CHAPTERS:
        for cue, _to in c["signals"]:
            for kw in content.KEYWORDS:
                if kw in cue:
                    kw_map.setdefault(kw, set()).add(c["no"])
    traps = sorted(((k, sorted(v)) for k, v in kw_map.items() if len(v) > 1),
                   key=lambda kv: (-len(kv[1]), kv[0]))
    trap_html = ('<div class="tbl-scroll"><table><thead><tr><th>同一个词</th>'
                 '<th>可能是这几个模式</th></tr></thead><tbody>{}</tbody></table></div>'
                 ).format("".join(
                     '<tr><td><b>{}</b></td><td>{}</td></tr>'.format(
                         esc(kw), "　".join(
                             '<a href="chapters/{}">{}</a>'.format(
                                 content.chapter_href(n), esc(content.chapter_label(n)))
                             for n in nos))
                     for kw, nos in traps))

    # ④ 模板口诀：从各章模板的 foot 里抽「默写口诀：**…**」，抽不到就退回模板副标题
    mn_rows = []
    for c in CHAPTERS:
        for t in c["templates"]:
            m = re.search(r"默写口诀：\*\*(.+?)\*\*", t["foot"])
            mn_rows.append((c["no"], t["name"], m.group(1) if m else t["note"]))
    mn_html = ('<div class="tbl-scroll"><table><thead><tr><th>模式</th><th>模板</th>'
               '<th>默写口诀 / 用途</th></tr></thead><tbody>{}</tbody></table></div>'
               ).format("".join(
                   '<tr><td><a href="chapters/{}">{}</a></td><td>{}</td><td>{}</td></tr>'.format(
                       content.chapter_href(no), esc(content.chapter_label(no)),
                       esc(name), inline(mn))
                   for no, name, mn in mn_rows))

    parts = ['<nav class="crumb"><a href="index.html">← 目录</a> · 面试前一晚看这页</nav>\n',
             '<header class="ch">\n  {bars}\n  <div class="kicker">Page 19 · Decision Tree &amp; Cheat Sheet</div>\n'
             '  <h1>19 模式决策树 / 速查表\n    <span class="zh">关键词 → 模式 → 模板口诀</span>\n  </h1>\n'
             '  <div class="meta"><span>模式 <b>{n_ch} 个</b></span>'
             '<span>识别信号 <b>{n_sig} 条</b></span><span>模板 <b>{n_tpl} 个</b></span>'
             '<span>直接 <b>打印成一页带走</b></span></div>\n</header>\n'.format(
                 bars=bars(), n_sig=len(rows), **st)]

    parts.append(sec("决策树", "§1 Decision Tree", "拿到题先问「数据长什么样」",
                     tree_html + '<p>叶子恰好 {} 个，与 {} 个模式一一对应——'
                                 '构建时程序化核对过覆盖率与唯一性。</p>\n'.format(
                                     st["n_ch"], st["n_ch"]), anchor="s1"))
    parts.append(sec("同名陷阱", "§2 Same Word, Different Pattern",
                     "这些词出现时，别急着下结论",
                     trap_html + '<p>这张表由各章 §2 的识别信号跨章聚合而成；'
                                 '每一对都在相关章节的<b>分流条件</b>里写明了怎么分。</p>\n',
                     color="warn", anchor="s2"))
    parts.append(sec("关键词索引", "§3 Signal Index", "全书识别信号，按模式排列",
                     idx_html, anchor="s3"))
    parts.append(sec("模板口诀", "§4 Template Index", "考前只需要扫这一列",
                     mn_html, anchor="s4"))

    parts.append('<nav class="next">\n  <a href="chapters/{}">← {}</a>\n'
                 '  <a href="mistakes.html">20 错题登记 →</a>\n</nav>\n'.format(
                     content.chapter_href(18), esc(content.chapter_label(18))))

    return page("19 模式决策树 / 速查表 · 算法面试阈值手册",
                "关键词 → 模式 → 模板口诀，单屏可打印的考前速查页。",
                "\n".join(parts), depth=0)


# ---------------------------------------------------------------- 错题登记页
def render_mistakes():
    st = stats()
    opts = "".join('<option value="{}">{}</option>'.format(
        esc(content.chapter_label(p["no"])), esc(content.chapter_label(p["no"])))
        for p in content.PATTERNS)

    form = ('<form id="log-form" class="log-form">\n'
            '  <div><label for="f-num">题号 / 题名</label>'
            '<input id="f-num" name="num" required placeholder="例如 84 Largest Rectangle"></div>\n'
            '  <div><label for="f-pattern">模式</label>'
            '<select id="f-pattern" name="pattern">{opts}</select></div>\n'
            '  <div><label for="f-why">翻车点</label>'
            '<input id="f-why" name="why" placeholder="例如 忘了末尾补哨兵"></div>\n'
            '  <div><label for="f-redo">重做日期</label>'
            '<input id="f-redo" name="redo" type="date"></div>\n'
            '  <div><button class="btn" type="submit">登记</button></div>\n'
            '</form>\n'
            '<div class="log-actions"><button id="log-clear" class="btn ghost" type="button">'
            '清空全部</button></div>\n').format(opts=opts)

    # 空白行单独放一个 tbody：有记录时在屏幕上隐藏，但打印时永远保留，
    # 这样「没有 JS / 隐私模式」和「打印出来手写补充」两种用法都成立。
    blank = "".join('<tr class="blank-rows"><td></td><td></td><td></td><td></td><td></td></tr>'
                    for _ in range(8))
    table = ('<div class="tbl-scroll"><table id="log-tbl"><thead><tr>'
             '<th>题号 / 题名</th><th>模式</th><th>翻车点</th><th>重做日期</th><th></th>'
             '</tr></thead><tbody id="log-body"></tbody><tbody id="log-blank">{}</tbody>'
             '</table></div>\n'
             '<p id="log-empty" class="log-empty">还没有记录。'
             '刷题时每翻一次车就登记一条——这一页是维持模式的输入源。</p>\n').format(blank)

    parts = ['<nav class="crumb"><a href="index.html">← 目录</a> · 错题登记</nav>\n',
             '<header class="ch">\n  {bars}\n  <div class="kicker">Page 20 · Mistake Log</div>\n'
             '  <h1>20 错题登记\n    <span class="zh">只记翻车点，不记题解</span>\n  </h1>\n'
             '  <div class="meta"><span>存在 <b>浏览器本地</b></span>'
             '<span>不上传 <b>任何服务器</b></span>'
             '<span>可 <b>直接打印成空白表格</b></span></div>\n</header>\n'.format(bars=bars())]

    body = ('<p>错题登记只写三样东西：<b>哪道题、属于哪个模式、当时错在哪一步</b>。'
            '不要抄题解——抄了你也不会再看。翻车点写得越具体越好，'
            '「忘了末尾补哨兵」比「没做出来」有用一百倍。</p>\n'
            '<p>记录保存在你自己浏览器的 localStorage 里，不会上传到任何地方；'
            '换浏览器或清缓存就没了，重要的话请截图或打印。'
            '隐私模式下 localStorage 不可用，本页会自动退化成一张可以打印出来手写的空表。</p>\n'
            '<p id="log-unavailable" hidden class="log-empty">'
            '当前浏览器不允许本地存储，登记表单已隐藏。下方空表可直接打印。</p>\n'
            + form + table)
    parts.append(sec("登记表", "§1 Log", "每翻一次车，记一条", body, anchor="s1"))

    body2 = ('<p>达标之后进入维持模式：<b>每周 3–5 题，一半来自这一页</b>。'
             '隔一周重做，重点不是「这次做出来了」，而是<b>当时那个翻车点还会不会再犯</b>。</p>\n'
             '<p>如果同一个模式在这里出现了三次以上，别再刷题了——'
             '回去重读那一章的 §1 和 §3，问题多半出在心智模型而不是手速。'
             '全书 {n_pit} 条翻车点就是照这个思路整理的。</p>\n'
             '<p>面试前一晚：先看 <a href="cheatsheet.html">决策树速查</a>，'
             '再看这一页里你自己的记录。这两页加起来 30 分钟，足够了。</p>\n'
             ).format(**st)
    parts.append(sec("怎么用它", "§2 Maintenance", "它是维持模式的输入源", body2, anchor="s2"))

    parts.append('<nav class="next">\n  <a href="cheatsheet.html">← 19 模式决策树 / 速查表</a>\n'
                 '  <span class="disabled">已是最后一页 →</span>\n</nav>\n')

    return page("20 错题登记 · 算法面试阈值手册",
                "记录题号、模式、翻车点与重做日期；浏览器本地保存，也可打印成空白表格。",
                "\n".join(parts), depth=0, extra_js=("mistakes.js",))


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
             '  <div class="meta"><span>共 <b>导读 + 附录 + {n_ch} 章 + 速查 + 错题页</b></span>'
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
                 '它写明了本书<b>不覆盖什么</b>，以及达标之后怎么维持。'
                 '太久没自己写代码 → 先完成 <a href="chapters/appendix-a.html">'
                 '附录 A · Python 刷题急救包</a> 再进正文。</p>\n</div>\n')

    parts.append('<div class="part">\n  <div class="part-head"><span class="no">开始之前</span>'
                 '<h2>导读与复健</h2><span class="tag">按需，进正文前</span></div>\n  <ul class="toc">\n'
                 '    <li><a href="chapters/00-intro.html"><span class="n">00</span>'
                 '<span class="t">导读</span>'
                 '<span class="d">阈值策略、三条达标标准、明确不覆盖的内容</span></a></li>\n'
                 '    <li><a href="chapters/appendix-a.html"><span class="n">附 A</span>'
                 '<span class="t">Python 刷题急救包</span>'
                 '<span class="d">太久没自己写代码 → 惯用法速查 + 10 道手打复健题</span></a></li>\n'
                 '  </ul>\n</div>\n')

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

    parts.append('<p class="quiz-note">同系列：面试里被问到「设计一个 Agent」，见 '
                 '<a href="https://xxxxxthhh.github.io/agent-interview-handbook/">Agent 设计面试手册</a>'
                 '——同样是考前用的工具书，练的是限时交卷与逐层追问。</p>\n')

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
    # 章页之间的上一页/下一页：导读 → 附录 A → 01 … 18 → 速查页
    nav = [(content.chapter_href(c["no"]), content.chapter_label(c["no"])) for c in CHAPTERS]
    for i, c in enumerate(CHAPTERS):
        prev = nav[i - 1] if i else (APX_HREF, APX_LABEL)
        nxt = nav[i + 1] if i + 1 < len(nav) else ("../cheatsheet.html", "决策树速查")
        written.append(write_("chapters/" + content.chapter_href(c["no"]),
                              render_chapter(c, prev[0], prev[1], nxt[0], nxt[1])))

    written.append(write_("chapters/00-intro.html", render_intro()))
    written.append(write_("chapters/" + APX_HREF, render_appendix()))
    written.append(write_("cheatsheet.html", render_cheatsheet()))
    written.append(write_("mistakes.html", render_mistakes()))
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
