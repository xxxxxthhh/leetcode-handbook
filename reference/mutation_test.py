#!/usr/bin/env python3
"""Mutation test：往内容层注入错误，确认校验器真的抓得到（质量规则第 3 条）。

    python3 reference/mutation_test.py

做法：在内存里改 content 的数据 → 重新渲染到临时目录 → 跑 check_site
→ 断言出现了预期的错误信息。「校验器跑绿了」本身不算证据，得先证明它会红。
每条 mutation 都对应一个真实会犯的错，不是为了凑数的合成错误。
"""
import copy
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import content  # noqa: E402
from content import appendix_a, intro, tree  # noqa: E402
from reference import build, check_site  # noqa: E402


def build_site(out):
    """渲染到临时目录，并把 assets/ 一起带过去——否则站内链接检查会把
    「临时目录里没有样式表」误报成死链。临时站点必须是真站点的忠实副本。"""
    build.main(out, quiet=True)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(out, "assets"))


def m_wrong_slug(chs):
    """凭记忆手写 slug：把注释里的链接写成 daily-temperature（少个 s）。"""
    ch = next(c for c in chs if c["no"] == 4)
    ch["problems"][2]["note"] += (
        " 参见 [739 Daily Temperatures](https://leetcode.com/problems/daily-temperature/)。")


def m_wrong_title(chs):
    """手写题名与官方不符。"""
    ch = next(c for c in chs if c["no"] == 4)
    ch["problems"][2]["note"] += (
        " 参见 [739 Daily Temperature](https://leetcode.com/problems/daily-temperatures/)。")


def m_star_on_medium(chs):
    """给一道 Medium 挂 ⭐认脸。"""
    next(c for c in chs if c["no"] == 4)["problems"][2]["star"] = True


def m_tier_out_of_band(chs):
    """变体多塞一道，越过登记的例外。"""
    ch = next(c for c in chs if c["no"] == 4)
    ch["problems"].append(dict(num=20, tier="variant", note="重复塞进来的题"))


def m_no_offchapter_quiz(chs):
    """自测题全都指向本章，分流题丢了。"""
    for q in next(c for c in chs if c["no"] == 4)["quiz"]:
        q["pattern"] = 4
        q["options"] = [4, 3, 13]


def m_quiz_from_own_chapter(chs):
    """自测题面用了本章已收录的题。"""
    ch = next(c for c in chs if c["no"] == 4)
    ch["quiz"][0]["num"] = 739


def m_too_few_pitfalls(chs):
    next(c for c in chs if c["no"] == 4)["pitfalls"] = [("只剩一条", "不够 3 条")]


def m_three_templates(chs):
    ch = next(c for c in chs if c["no"] == 4)
    ch["templates"] = ch["templates"] + [dict(ch["templates"][0], name="模板 C · 多余")]


def m_missing_routing(chs):
    next(c for c in chs if c["no"] == 4)["routing"] = ""


def m_quiz_answer_not_in_options(chs):
    next(c for c in chs if c["no"] == 4)["quiz"][0]["options"] = [3, 13, 8]


def m_answer_always_first(chs):
    """选项不打乱、正确答案一律排在第一个（这正是被 advisor 抓到的原始缺陷）。"""
    build.shuffled_options = lambda q: (
        [q["pattern"]] + [o for o in q["options"] if o != q["pattern"]])


def m_dangling_pitfall_ref(chs):
    """删掉一条翻车点，但正文里「见翻车点⑤」的交叉引用还在（编号最容易悬空的场景）。"""
    ch = next(c for c in chs if c["no"] == 4)
    ch["pitfalls"] = ch["pitfalls"][:4]


def m_tree_duplicate_leaf(chs):
    """决策树里两条分支指向同一章（改章号时最容易犯）。"""
    tree.TREE[1][2][0] = (tree.TREE[1][2][0][0], 1)


def m_tree_missing_pattern(chs):
    """决策树漏掉一个模式。"""
    del tree.TREE[2][2][0]


def m_dead_internal_link(chs):
    """正文里链到一个不存在的页面。"""
    intro.SECTIONS[0]["tail"] = ["详见 [某个不存在的页](../nonexistent.html)。"]


def m_appendix_wrong_slug(chs):
    """附录 A 复健目标里凭记忆手写链接：two-sums（多个 s）。"""
    appendix_a.PROBLEMS[0] = dict(
        appendix_a.PROBLEMS[0],
        goal=appendix_a.PROBLEMS[0]["goal"]
        + " 参见 [1 Two Sum](https://leetcode.com/problems/two-sums/)。")


def m_appendix_problem_not_curated(chs):
    """附录 A 混进一道正文没收录的题，「双重用途」承诺失效。
    挑官方索引里有、但正文各章都没收录的题号（各章自测题即是）。"""
    curated = {str(p["num"]) for c in chs for p in c["problems"]}
    num = next(int(n) for n in check_site.LC if n not in curated)
    appendix_a.PROBLEMS.append(dict(num=num, goal="混进来的题", refs=[]))


def m_appendix_quiz_answer_missing(chs):
    """附录 A 改错题的正确答案 key 不在选项里。"""
    appendix_a.QUIZ[0] = dict(appendix_a.QUIZ[0], answer="z")


def m_appendix_answer_always_first(chs):
    """附录 A 选项不打乱：正确项一律排第一。章节那条 mutation 打的是
    build.shuffled_options，够不着附录自己的打乱函数——这条补上。"""
    build.appendix_shuffled_options = lambda i, options: (
        sorted(options, key=lambda o: o[0] != "a"))


def m_appendix_answer_always_longest(chs):
    """附录 A 四个干扰项都写得比正确项短：读者挑最长的那条就能刷分。
    这是位置偏置的孪生缺陷，位置类检查看不见它。"""
    for i, q in enumerate(appendix_a.QUIZ):
        appendix_a.QUIZ[i] = dict(q, options=[
            (k, t if k == q["answer"] else t[:8]) for k, t in q["options"]])


def m_appendix_quiz_no_code(chs):
    """附录 A 改错题只剩选项、没有代码片段——「改错」无从改起。"""
    appendix_a.QUIZ[:] = [dict(q, code="") for q in appendix_a.QUIZ]


def m_appendix_header_count_stale(chs):
    """删掉一道复健题，但头部 meta 的计数没跟着变（手写数量的经典后果）。
    这里模拟的是「有人把计数从派生改回硬编码」：渲染后 meta 与实际条目数不符。"""
    orig = build.render_appendix

    def patched():
        html = orig()
        return html.replace("复健题 <b>10 道</b>", "复健题 <b>12 道</b>")
    build.render_appendix = patched


MUTATIONS = [
    ("链接 slug 凭记忆手写", m_wrong_slug, "slug 是"),
    ("链接题名与官方不符", m_wrong_title, "官方题名是"),
    ("⭐认脸挂在 Medium 上", m_star_on_medium, "官方难度是"),
    ("题目分层数量越界", m_tier_out_of_band, "与登记的例外"),
    ("自测缺少非本章分流题", m_no_offchapter_quiz, "恰好混入 1 道非本章分流题"),
    ("自测题取自本章已收录题", m_quiz_from_own_chapter, "已在本章 §4 收录"),
    ("翻车点不足 3 条", m_too_few_pitfalls, "翻车点"),
    ("模板超过 2 个", m_three_templates, "模板 3 个"),
    ("§2 缺少分流条件", m_missing_routing, "缺少分流条件"),
    ("自测正确答案不在选项里", m_quiz_answer_not_in_options, "不在选项"),
    ("正确答案一律排第一个", m_answer_always_first, "读者靠位置就能猜对"),
    ("翻车点交叉引用悬空", m_dangling_pitfall_ref, "但该章只有"),
    ("决策树两条分支同一章", m_tree_duplicate_leaf, "重复叶子"),
    ("决策树漏掉一个模式", m_tree_missing_pattern, "未覆盖模式"),
    ("正文链到不存在的页", m_dead_internal_link, "死链"),
    ("附录A slug 凭记忆手写", m_appendix_wrong_slug, "slug 是"),
    ("附录A 混入未收录题", m_appendix_problem_not_curated, "未在正文任何一章收录"),
    ("附录A 答案不在选项里", m_appendix_quiz_answer_missing, "不在选项"),
    ("附录A 正确答案一律排第一", m_appendix_answer_always_first, "读者靠位置就能猜对"),
    ("附录A 正确答案一律最长", m_appendix_answer_always_longest, "挑最长的就能猜对"),
    ("附录A 改错题没有代码", m_appendix_quiz_no_code, "缺少代码片段"),
    ("附录A 头部计数写死", m_appendix_header_count_stale, "头部复健题计数"),
]


def run_one(name, mutate, expect):
    original = content.CHAPTERS
    orig_shuffle = build.shuffled_options
    orig_tree = copy.deepcopy(tree.TREE)
    orig_intro = copy.deepcopy(intro.SECTIONS)
    orig_apx_problems = copy.deepcopy(appendix_a.PROBLEMS)
    orig_apx_quiz = copy.deepcopy(appendix_a.QUIZ)
    orig_apx_shuffle = build.appendix_shuffled_options
    orig_render_apx = build.render_appendix
    tmp = tempfile.mkdtemp(prefix="mut-")
    try:
        mutated = copy.deepcopy(original)
        mutate(mutated)
        content.CHAPTERS = mutated
        build.CHAPTERS = mutated
        content.WRITTEN = {c["no"] for c in mutated}
        build_site(tmp)
        # 校验器读的是渲染产物；官方索引仍从仓库读，外部真相不参与 mutation
        rep = check_site.run(tmp)
        hit = [e for e in rep.errors if expect in e]
        ok = bool(hit)
        print("{}  {:<24} {}".format("caught " if ok else "MISSED ", name,
                                     hit[0] if ok else "期望包含「{}」的错误，实际: {}".format(
                                         expect, rep.errors or "无任何错误")))
        return ok
    finally:
        content.CHAPTERS = original
        build.CHAPTERS = original
        content.WRITTEN = {c["no"] for c in original}
        build.shuffled_options = orig_shuffle
        tree.TREE[:] = orig_tree
        intro.SECTIONS[:] = orig_intro
        appendix_a.PROBLEMS[:] = orig_apx_problems
        appendix_a.QUIZ[:] = orig_apx_quiz
        build.appendix_shuffled_options = orig_apx_shuffle
        build.render_appendix = orig_render_apx
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    # 前提：未变异的站点必须是干净的，否则「抓到错误」可能只是本来就有的错
    base = tempfile.mkdtemp(prefix="mut-base-")
    try:
        build_site(base)
        rep = check_site.run(base)
        if rep.errors:
            print("基线就不干净，先修好再跑 mutation test:")
            for e in rep.errors:
                print("  " + e)
            return 1
    finally:
        shutil.rmtree(base, ignore_errors=True)

    missed = 0
    for name, fn, expect in MUTATIONS:
        if not run_one(name, fn, expect):
            missed += 1
    print("\n{} 条注入，{} 条没被抓住".format(len(MUTATIONS), missed))
    return 1 if missed else 0


if __name__ == "__main__":
    sys.exit(main())
