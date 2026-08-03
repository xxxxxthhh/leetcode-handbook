#!/usr/bin/env python3
"""站级校验：全部跑在渲染产物 HTML 上，而不是 content/ 里的 dict 上。

    python3 reference/check_site.py            # 检查仓库根目录的站点
    python3 reference/check_site.py --site DIR # 检查别处的构建产物（mutation test 用）

为什么必须校验 HTML 而不是数据：数据层「由构造保证」的东西，校验它等于校验
生成器的 happy path，读者拿到的产物反而没人管；而且那样一来 mutation test
（质量规则第 3 条）就是空的——改数据、重新生成，校验器永远看不见差别。
本文件因此只依赖三样外部真相：
  · 渲染出来的 HTML
  · data/leetcode-index.json（LeetCode 官方题目索引）
  · content/patterns.py（18 个模式的身份注册表）
"""
import argparse
import json
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from content.patterns import BY_NO, PATTERNS  # noqa: E402

with open(os.path.join(ROOT, "data", "leetcode-index.json"), encoding="utf-8") as _f:
    LC = json.load(_f)["problems"]

TIER_ORDER = ["热身", "标准", "变体"]

# ---------------------------------------------------------------------------
# §4 题目分层数量：skeleton §4 写的是 热身 1 / 标准 2–3 / 变体 1–2，但 §5 的实际
# 选题里 18 章有 12 章不符合，连已获批的样章 ch04 也不符合。取舍：§5 选题 +
# ch04 样章为准，§4 当作默认区间，逐章登记例外并写明理由。名单以外的越界一律报错，
# 防止「例外」变成沉默放行。
TIER_EXCEPTIONS = {
    4: ((2, 3, 3), "样章体例：普通栈+单调栈两条线各需一道热身；变体含 84/239 两道⭐认脸"),
}
BAND = {"热身": (1, 1), "标准": (2, 3), "变体": (1, 2)}


class Report(object):
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.notes = []

    def err(self, where, msg):
        self.errors.append("{}: {}".format(where, msg))

    def warn(self, where, msg):
        self.warnings.append("{}: {}".format(where, msg))


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


def chapter_files(site):
    d = os.path.join(site, "chapters")
    if not os.path.isdir(d):
        return []
    out = []
    for f in sorted(os.listdir(d)):
        m = re.fullmatch(r"(\d{2})-[a-z0-9-]+\.html", f)
        if m and int(m.group(1)) > 0:
            out.append((int(m.group(1)), os.path.join(d, f)))
    return out


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------- 五段结构
def check_structure(no, html, rep):
    where = "ch{:02d}".format(no)

    # 五段齐全且顺序正确
    ids = re.findall(r'<section id="(s\d)"', html)
    if ids != ["s1", "s2", "s3", "s4", "s5"]:
        rep.err(where, "五段结构不完整或顺序错乱: {}".format(ids))
        return

    if not re.search(r'<div class="oneliner">\s*\S', html):
        rep.err(where, "§1 缺少一句话心智模型")
    n_sig = len(re.findall(r"<tr><td>", html))
    if n_sig < 4:
        rep.err(where, "§2 识别信号只有 {} 行，至少 4 行".format(n_sig))
    routing = re.search(r'<div class="routing">.*?<p>(.*?)</p>', html, re.S)
    if not routing or len(strip_tags(routing.group(1)).strip()) < 10:
        rep.err(where, "§2 缺少分流条件")

    n_tpl = len(re.findall(r'<div class="tpl">', html))
    if not 1 <= n_tpl <= 2:
        rep.err(where, "§3 模板 {} 个，spec 上限 2 个".format(n_tpl))
    if "【骨架】" not in html or "【插槽】" not in html:
        rep.err(where, "§3 模板缺少【骨架】/【插槽】注释体例")

    # §4 分层：顺序 + 数量
    tiers = re.findall(r'<span class="t">(热身|标准|变体)</span>'
                       r'<span class="d">[^<]*</span><span class="c">(\d+) 道</span>', html)
    seen = [t for t, _ in tiers]
    if seen != [t for t in TIER_ORDER if t in seen]:
        rep.err(where, "§4 分层顺序错乱: {}".format(seen))
    counts = {t: int(n) for t, n in tiers}
    actual = tuple(counts.get(t, 0) for t in TIER_ORDER)
    if no in TIER_EXCEPTIONS:
        expect, reason = TIER_EXCEPTIONS[no]
        if actual != expect:
            rep.err(where, "§4 分层数量 {} 与登记的例外 {} 不符（例外理由：{}）".format(
                actual, expect, reason))
    else:
        for t, n in zip(TIER_ORDER, actual):
            lo, hi = BAND[t]
            if not lo <= n <= hi:
                rep.err(where, "§4「{}」{} 道，超出 skeleton §4 的 {}–{} 道；"
                               "若为有意取舍，请登记进 TIER_EXCEPTIONS".format(t, n, lo, hi))

    n_pit = len(re.findall(r'<li><span class="pt">', html))
    if not 3 <= n_pit <= 5:
        rep.err(where, "§5 翻车点 {} 条，spec 要求 3–5 条".format(n_pit))

    # 头部 meta 里的数字必须与页面上真实渲染的条目数一致（禁止手写数量）
    m = re.search(r"题目 <b>(\d+) 道</b>.*?模板 <b>(\d+) 个</b>.*?⭐认脸 <b>(\d+) 道</b>", html)
    if not m:
        rep.err(where, "头部 meta 缺少题目/模板/认脸计数")
    else:
        said_p, said_t, said_s = (int(x) for x in m.groups())
        real_p = len(re.findall(r'<div class="p-title">', html))
        real_s = len(re.findall(r'class="badge star"', html))
        if said_p != real_p or said_t != n_tpl or said_s != real_s:
            rep.err(where, "头部计数 (题{} 模板{} ⭐{}) 与实际渲染 (题{} 模板{} ⭐{}) 不一致".format(
                said_p, said_t, said_s, real_p, n_tpl, real_s))
        if said_p != sum(actual):
            rep.err(where, "头部题数 {} 与分层合计 {} 不一致".format(said_p, sum(actual)))


# ---------------------------------------------------------------- 自测题
def check_quiz(no, html, rep):
    where = "ch{:02d}".format(no)
    qs = re.findall(r'<article class="q" data-answer="(\d+)">(.*?)</article>', html, re.S)
    if not 2 <= len(qs) <= 3:
        rep.err(where, "§5 自测 {} 题，spec 要求 2–3 题".format(len(qs)))
    off = 0
    for ans, body in qs:
        ans = int(ans)
        opts = [int(o) for o in re.findall(r'class="opt" type="button" data-ch="(\d+)"', body)]
        if len(opts) < 3:
            rep.err(where, "自测题选项少于 3 个，识别练习失去意义")
        if ans not in opts:
            rep.err(where, "自测题正确答案 {} 不在选项 {} 里".format(ans, opts))
        if len(set(opts)) != len(opts):
            rep.err(where, "自测题选项重复: {}".format(opts))
        if not re.search(r'<details><summary>看答案</summary>.*?class="answer".*?\S', body, re.S):
            rep.err(where, "自测题缺少答案解释（无 JS / 打印时读者就看不到答案了）")
        if ans != no:
            off += 1
    if qs and off != 1:
        rep.err(where, "§5 应恰好混入 1 道非本章分流题，实际 {} 道".format(off))


# ---------------------------------------------------------------- 链接三方核对
# 题号 ↔ slug ↔ 题名 三方一致，逐条对 LeetCode 官方索引核，不对自己核。
LINK_RE = re.compile(
    r'<a href="https://leetcode\.com/problems/([a-z0-9-]+)/"[^>]*>(\d+) ([^<]+)</a>')
SLUG_RE = re.compile(r"https://leetcode\.com/problems/([a-z0-9-]+)/")
SLUG2NUM = {v["slug"]: k for k, v in LC.items()}


def check_links(no, html, rep, seen_curated):
    where = "ch{:02d}".format(no)

    # ① 页面上出现的每一个 slug 都必须真实存在——正文里顺手写的链接也不放过
    for slug in set(SLUG_RE.findall(html)):
        if slug not in SLUG2NUM:
            rep.err(where, "slug「{}」不对应任何 LeetCode 题（凭记忆手写没核对？）".format(slug))

    # ② 形如「739 Daily Temperatures」的锚文本，三方逐项核对
    for slug, num, title in LINK_RE.findall(html):
        meta = LC.get(num)
        if meta is None:
            rep.err(where, "题号 {} 不在 LeetCode 官方索引里".format(num))
            continue
        if meta["slug"] != slug:
            rep.err(where, "题 {} 的 slug 是 {}，页面写成 {}".format(num, meta["slug"], slug))
        if meta["title"] != title:
            rep.err(where, "题 {} 的官方题名是「{}」，页面写成「{}」".format(
                num, meta["title"], title))

    # 徽章必须与官方元数据一致：难度、🔒、⭐（⭐只能挂在 Hard 上）
    for block in re.findall(r'<div class="p-title">(.*?)</div>', html, re.S):
        m = LINK_RE.search(block)
        if not m:
            rep.err(where, "题目条目缺少 LeetCode 链接: {}".format(strip_tags(block)[:40]))
            continue
        num = m.group(2)
        meta = LC.get(num)
        if meta is None:
            continue
        seen_curated[num].append(no)
        locked = "badge lock" in block
        star = "badge star" in block
        diff = re.search(r'<span class="badge diff">([^<]+)</span>', block)
        if locked != meta["paid_only"]:
            rep.err(where, "题 {} 的 🔒 标记与官方 paid_only={} 不符".format(num, meta["paid_only"]))
        if not diff or diff.group(1) != meta["difficulty"]:
            rep.err(where, "题 {} 的难度徽章与官方 {} 不符".format(num, meta["difficulty"]))
        if star and meta["difficulty"] != "Hard":
            rep.err(where, "题 {} 标了 ⭐认脸 但官方难度是 {}".format(num, meta["difficulty"]))


def check_quiz_sources(no, html, rep):
    """自测题面必须取自本章未收录的题，否则读者是靠记忆而非靠信号作答。"""
    where = "ch{:02d}".format(no)
    s4 = html.split('<section id="s4">')[1].split('<section id="s5">')[0]
    s5 = html.split('<section id="s5">')[1]
    curated = {m[1] for m in LINK_RE.findall(s4)}
    for num in {m[1] for m in LINK_RE.findall(s5)}:
        if num in curated:
            rep.err(where, "自测题 {} 已在本章 §4 收录".format(num))


# ---------------------------------------------------------------- ⭐ 篇幅
def check_star_brevity(no, html, rep):
    """⭐认脸题的篇幅应短于必会题——篇幅本身是优先级信号。
    警告级：样章里 84 是刻意详讲的反例，不能做成硬规则。"""
    where = "ch{:02d}".format(no)
    star, plain = [], []
    for li in re.findall(r"<li>\s*<div class=\"p-title\">(.*?)</div>\s*"
                         r"<div class=\"p-note\">(.*?)</div>", html, re.S):
        head, note = li
        (star if "badge star" in head else plain).append(len(strip_tags(note)))
    if star and plain:
        if sum(star) / len(star) > sum(plain) / len(plain):
            rep.warn(where, "⭐认脸题平均篇幅 {:.0f} 字 > 必会题 {:.0f} 字，"
                            "确认是 84 式的刻意详讲再放行".format(
                                sum(star) / len(star), sum(plain) / len(plain)))


# ---------------------------------------------------------------- 决策树 / 速查页
def check_cheatsheet(site, rep, chapters_present):
    path = os.path.join(site, "cheatsheet.html")
    if not os.path.exists(path):
        rep.notes.append("cheatsheet.html 尚未构建")
        return
    html = read(path)
    leaves = [int(n) for n in re.findall(r'class="leaf" href="chapters/(\d{2})-', html)]
    if len(leaves) != len(set(leaves)):
        dup = sorted({n for n in leaves if leaves.count(n) > 1})
        rep.err("cheatsheet", "决策树有重复叶子: {}".format(dup))
    missing = sorted({p["no"] for p in PATTERNS} - set(leaves))
    if missing:
        rep.err("cheatsheet", "决策树未覆盖模式: {}".format(missing))
    extra = sorted(set(leaves) - {p["no"] for p in PATTERNS})
    if extra:
        rep.err("cheatsheet", "决策树叶子指向不存在的模式: {}".format(extra))

    # 速查表的识别信号必须逐条出自某章 §2，不能另写一套
    idx_rows = re.findall(r'<tr><td>(.*?)</td><td class="to">'
                          r'<a href="chapters/(\d{2})-[^"]+">[^<]*</a></td></tr>', html, re.S)
    if not idx_rows:
        rep.err("cheatsheet", "缺少关键词索引表")
    for cue, no in idx_rows:
        no = int(no)
        if no not in chapters_present:
            continue
        if strip_tags(cue).strip() not in chapters_present[no]:
            rep.err("cheatsheet", "关键词「{}」在第 {} 章 §2 里找不到同款表述".format(
                strip_tags(cue).strip()[:30], no))


# ---------------------------------------------------------------- 识别信号冲突
def collect_signals(no, html):
    s2 = html.split('<section id="s2">')[1].split('<section id="s3">')[0]
    rows = re.findall(r"<tr><td>(.*?)</td><td>(.*?)</td></tr>", s2, re.S)
    return [strip_tags(a).strip() for a, _ in rows]


KEYWORDS = ["连续子数组", "子数组", "子序列", "最大 / 最小", "区间", "有序", "第 K",
            "重复", "路径", "依赖", "连通", "最短", "组合", "排列", "回文", "窗口"]


def check_signal_conflicts(site, sig_map, routing_map, rep):
    """同一关键词指向多个模式时，相关章的分流条件必须点名对方。
    产出汇总表供人工过一遍（质量规则第 5 条要求人工审读点）。"""
    kw_map = defaultdict(set)
    for no, cues in sig_map.items():
        for cue in cues:
            for kw in KEYWORDS:
                if kw in cue:
                    kw_map[kw].add(no)
    conflicts = {k: sorted(v) for k, v in kw_map.items() if len(v) > 1}
    for kw, nos in sorted(conflicts.items()):
        for no in nos:
            others = [x for x in nos if x != no]
            routing = routing_map.get(no, "")
            named = [x for x in others
                     if "第 {:02d} 章".format(x) in routing or BY_NO[x]["title_zh"] in routing]
            if not named:
                rep.warn("ch{:02d}".format(no),
                         "关键词「{}」同时出现在第 {} 章，但本章分流条件没点名它们".format(
                             kw, others))
    out = os.path.join(site, "data", "signal-conflicts.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write("# 识别信号冲突汇总（构建产物，供人工审读）\n\n")
        f.write("由 reference/check_site.py 从各章 §2 渲染结果聚合。"
                "同一关键词落在多个模式上不是错误，但每一条都必须在分流条件里写明怎么分。\n\n")
        f.write("| 关键词 | 涉及模式 | 各章分流条件是否点名对方 |\n|---|---|---|\n")
        for kw, nos in sorted(conflicts.items()):
            cells = []
            for no in nos:
                routing = routing_map.get(no, "")
                ok = any("第 {:02d} 章".format(x) in routing or BY_NO[x]["title_zh"] in routing
                         for x in nos if x != no)
                cells.append("{:02d}{}".format(no, "✓" if ok else "✗"))
            f.write("| {} | {} | {} |\n".format(
                kw, "、".join("{:02d} {}".format(n, BY_NO[n]["title_zh"]) for n in nos),
                " ".join(cells)))
        if not conflicts:
            f.write("| — | 暂无跨章重复关键词 | — |\n")
    rep.notes.append("识别信号冲突汇总 -> data/signal-conflicts.md（{} 个跨章关键词）".format(
        len(conflicts)))


# ---------------------------------------------------------------- 主流程
def run(site):
    rep = Report()
    chs = chapter_files(site)
    if not chs:
        rep.err("site", "chapters/ 下没有任何章节页")
        return rep

    seen_curated = defaultdict(list)
    sig_map, routing_map, cue_map = {}, {}, {}
    for no, path in chs:
        html = read(path)
        check_structure(no, html, rep)
        check_quiz(no, html, rep)
        check_links(no, html, rep, seen_curated)
        check_quiz_sources(no, html, rep)
        check_star_brevity(no, html, rep)
        try:
            sig_map[no] = collect_signals(no, html)
            cue_map[no] = "\n".join(sig_map[no])
            routing_map[no] = strip_tags(
                re.search(r'<div class="routing">(.*?)</div>', html, re.S).group(1))
        except (AttributeError, IndexError):
            rep.err("ch{:02d}".format(no), "§2 识别信号表或分流条件无法解析")

    for num, nos in sorted(seen_curated.items(), key=lambda kv: int(kv[0])):
        if len(nos) > 1:
            rep.warn("site", "题 {} 在第 {} 章重复收录".format(num, nos))

    check_cheatsheet(site, rep, cue_map)
    check_signal_conflicts(site, sig_map, routing_map, rep)

    # 全局数量一律程序化统计
    n_prob = len(seen_curated)
    rep.notes.append("已构建 {} / 18 章，收录题目 {} 道，⭐认脸 {} 道，🔒 premium {} 道".format(
        len(chs), n_prob,
        sum(1 for n in seen_curated if LC[n]["difficulty"] == "Hard" and True),
        sum(1 for n in seen_curated if LC[n]["paid_only"])))
    missing = sorted({p["no"] for p in PATTERNS} - {no for no, _ in chs})
    if missing:
        rep.notes.append("待撰写章节: {}".format(missing))
    return rep


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=ROOT)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    rep = run(args.site)
    if not args.quiet:
        for n in rep.notes:
            print("note  " + n)
        for w in rep.warnings:
            print("WARN  " + w)
    for e in rep.errors:
        print("ERROR " + e)
    print("\n{} errors, {} warnings".format(len(rep.errors), len(rep.warnings)))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
