"""全书内容的唯一数据源。

分两层：
  · content/patterns.py —— 18 个模式的骨架（章号 / 标题 / 文件名 / 分组），
    在任何章节内容写出来之前就已完整，因此自测选项、决策树叶子、目录都能引用它；
  · content/chNN-*.py  —— 一章的五段内容，导出名为 CHAPTER 的 dict，只写内容不写标题。

渲染、校验、决策树、识别信号索引、题目计数全部从这里派生，任何数字都不许在别处手写。

CHAPTER 字段约定
----------------
no            int    章号 1..18，必须能在 patterns.py 里找到
freq          str    面试出现频率：极高 / 高 / 中
mental_model  str    §1 一句话心智模型（渲染进 .oneliner，支持行内标记）
mental_model_body  list[str]  §1 后续段落
signals       list[(cue, to)]  §2 识别信号表：题面出现… → 想到…
routing       str    §2 分流条件段落，决策树与冲突检查都读它
routing_to    list[int]        分流指向的章号，供「识别信号无冲突」校验
templates     list[dict]  §3 模板：name / note / code / tests / foot
                         code 是页面上展示的字符串本体，tests 直接在 exec(code)
                         后的命名空间里跑——展示的代码与被测的代码同源。
problems      list[dict]  §4 题目：num / tier / note / star
                         tier ∈ warmup | standard | variant
                         star=True 表示 ⭐认脸级（校验器会核对它确实是 Hard）
                         🔒 与难度不手写，一律从 LeetCode 官方索引派生
pitfalls      list[(title, body)]   §5 翻车点 3–5 条
quiz          list[dict]  §5 自测：num / pattern / prompt / options / why
                         pattern = 该题真正所属章号；options = 备选章号列表
                         hide_num=True 时不显示题号（避免直接剧透答案）
"""
import importlib
import os
import re

from content.patterns import BY_NO, GROUPS, PATTERNS  # noqa: F401

_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_chapters():
    names = sorted(
        f[:-3] for f in os.listdir(_DIR)
        if re.fullmatch(r"ch\d{2}-[a-z0-9-]+\.py", f)
    )
    out = [importlib.import_module("content." + n).CHAPTER for n in names]
    out.sort(key=lambda c: c["no"])
    return out


CHAPTERS = _load_chapters()
WRITTEN = {c["no"] for c in CHAPTERS}


def chapter(no):
    for c in CHAPTERS:
        if c["no"] == no:
            return c
    raise KeyError("第 {} 章尚未撰写".format(no))


def pattern(no):
    return BY_NO[no]


def chapter_href(no):
    p = BY_NO[no]
    return "{:02d}-{}.html".format(p["no"], p["slug"])


def chapter_label(no):
    p = BY_NO[no]
    return "{:02d} {}".format(p["no"], p["title_zh"])


def problem_numbers():
    """全书引用到的 LeetCode 题号（题目分层 + 自测题），供索引裁剪与链接校验。"""
    nums = set()
    for c in CHAPTERS:
        nums.update(p["num"] for p in c["problems"])
        nums.update(q["num"] for q in c["quiz"])
    return sorted(nums)


def curated_numbers():
    """只算题目分层里的正式收录题（自测题不计入书目题量）。"""
    nums = set()
    for c in CHAPTERS:
        nums.update(p["num"] for p in c["problems"])
    return sorted(nums)
