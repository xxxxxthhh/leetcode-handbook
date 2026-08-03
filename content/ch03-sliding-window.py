# -*- coding: utf-8 -*-
"""第 03 章 · 滑动窗口。"""

TPL_A = '''\
from collections import Counter

def longest_no_repeat(s):
    cnt = Counter()                         # 【插槽】窗口状态:计数 / 和 / 去重集合
    left = best = 0                         # 【骨架】
    for right, ch in enumerate(s):          # 【骨架】右边界无脑扩
        cnt[ch] += 1                        # 【插槽】加入 s[right] 后怎么更新状态
        while cnt[ch] > 1:                  # 【插槽】"不合法"的判定 —— 整道题的灵魂
            cnt[s[left]] -= 1               # 【插槽】移出 s[left] 后怎么更新状态
            left += 1                       # 【骨架】收缩到重新合法为止
        best = max(best, right - left + 1)  # 【插槽】答案在"已经合法"之后统计
    return best
'''

TPL_A_TESTS = '''\
assert longest_no_repeat("abcabcbb") == 3
assert longest_no_repeat("bbbbb") == 1
assert longest_no_repeat("pwwkew") == 3
assert longest_no_repeat("") == 0


# 424 Longest Repeating Character Replacement:合法性换成"窗口长度 - 最多的那种字符 <= k"
def character_replacement(s, k):
    cnt = Counter()
    left = best = most = 0
    for right, ch in enumerate(s):
        cnt[ch] += 1
        most = max(most, cnt[ch])
        while (right - left + 1) - most > k:
            cnt[s[left]] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


assert character_replacement("ABAB", 2) == 4
assert character_replacement("AABABBA", 1) == 4
assert character_replacement("A", 0) == 1
'''

TPL_B = '''\
def max_fixed_window(nums, k):
    total = sum(nums[:k])                   # 【骨架】先把第一个窗口填满
    best = total                            # 【插槽】要最大 / 最小 / 全部记录下来
    for i in range(k, len(nums)):           # 【骨架】
        total += nums[i] - nums[i - k]      # 【骨架】进一个,出一个,状态 O(1) 更新
        best = max(best, total)             # 【插槽】
    return best
'''

TPL_B_TESTS = '''\
assert max_fixed_window([1, 12, -5, -6, 50, 3], 4) == 51
assert max_fixed_window([5], 1) == 5
assert max_fixed_window([-1, -2, -3], 2) == -3


# 567 Permutation in String:定长窗口 + 计数相等
def check_inclusion(s1, s2):
    from collections import Counter
    k = len(s1)
    if k > len(s2):
        return False
    need, win = Counter(s1), Counter(s2[:k])
    if win == need:
        return True
    for i in range(k, len(s2)):
        win[s2[i]] += 1
        win[s2[i - k]] -= 1
        if win[s2[i - k]] == 0:             # 减到 0 必须删键,否则字典永远不相等
            del win[s2[i - k]]
        if win == need:
            return True
    return False


assert check_inclusion("ab", "eidbaooo") is True
assert check_inclusion("ab", "eidboaoo") is False
assert check_inclusion("abc", "ab") is False
'''

CHAPTER = dict(
    no=3,
    freq="极高",

    mental_model="**窗口只做两件事：右边界无脑往外扩，扩到不合法就收左边界。"
                 "所以整道题的全部难度，都在你怎么定义「不合法」。**",
    mental_model_body=[
        "先问自己三句话，答完模板就填完了：窗口里要维护**什么状态**（计数 / 和 / 去重集合）？"
        "**什么时候算不合法**（`while` 的条件）？**答案在哪一刻统计**（收缩之后，此刻窗口一定合法）？",
        "复杂度是 O(n) 而不是 O(n²)：左指针只会向右走，两个指针各自最多走 n 步。"
        "如果你写出的收缩循环里左指针可能回退，那说明它不是滑动窗口。",
    ],

    signals=[
        ("「最长 / 最短**连续**子串 / 子数组」+ 一个约束条件", "可变窗口（模板 A）"),
        ("「至多 K 个不同字符 / 至多 K 次替换 / 至多 K 个 0」", "可变窗口，K 就是合法性阈值"),
        ("「长度恰好为 k 的子数组的最大和 / 平均值」", "定长窗口（模板 B）"),
        ("「s1 的排列是不是 s2 的子串」「找出所有 anagram 起点」", "定长窗口 + 计数相等（模板 B）"),
        ("「包含 t 中所有字符的最小子串」", "可变窗口 + 缺口计数（76 题）"),
        ("你的暴力解是「枚举所有子数组再逐个检查」", "滑窗优化信号"),
    ],
    routing="都带「连续子数组」四个字，但分流很清楚："
            "求**最值 / 长度**且约束单调 → 滑动窗口（本章）；"
            "求「和**恰好**等于 K 的个数」→ 前缀和 + 哈希（第 13 章），因为窗口和不单调、收缩条件无从写起；"
            "**窗口大小固定**且要窗口内的最大 / 最小值 → 单调队列（第 04 章）。"
            "另外，数组里有负数时「和 ≥ target 的最短子数组」也不能用滑窗——单调性没了。"
            "还有一个同名陷阱：本章的「最短」永远修饰**连续子数组**；"
            "「最短路径 / 最少步数」说的是图上的 BFS（第 07 章的层序、第 10 章的网格），两者毫无关系。",
    routing_to=[4, 7, 13],

    templates=[
        dict(name="模板 A · 可变窗口", note="覆盖本章 80% 的题",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**右扩、不合法就左缩、合法后统计**。"
                  "三个插槽依次是：状态怎么加、怎么算不合法、状态怎么减。"),
        dict(name="模板 B · 定长窗口", note="窗口大小 k 固定",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="定长窗口没有 `while` 收缩，只有「进一个、出一个」。"
                  "注意 `k > len(nums)` 时首个窗口就不成立，调用前先挡一下。"),
    ],

    problems=[
        dict(num=121, tier="warmup",
             note="严格说它是「窗口退化成一个变量」：左边界只在遇到更低价时跳过去。"
                  "放在这里是为了先建立「左边界只前进不后退」的直觉，写法上记住"
                  "`best = max(best, price - min_so_far)` 就够。"),
        dict(num=3, tier="standard",
             note="模板 A 原题。不合法 = 出现重复字符。进阶写法是 `last[ch]` 记录上次位置，"
                  "`left = max(left, last[ch] + 1)` 一步跳到位——`max` 不能省，见翻车点③。"),
        dict(num=424, tier="standard",
             note="不合法 = `窗口长度 - 出现最多的字符数 > k`。"
                  "`most` 只增不减看起来是 bug，实际不影响最终答案（窗口不会缩小，答案也就不会被高估），"
                  "这一点值得在面试里主动讲清楚。"),
        dict(num=567, tier="standard",
             note="定长窗口 + `Counter` 相等判断。坑在计数减到 0 必须 `del`，否则两个字典永远不相等——"
                  "第 01 章翻车点③的同一个坑，在这里第一次真正咬人。"),
        dict(num=76, tier="variant", star=True,
             note="⭐认脸。可变窗口的完全体：用 `missing` 计数「还差几个字符」，为 0 才收缩。"
                  "说清框架即可，不必默写。"),
    ],

    pitfalls=[
        ("答案统计的时机",
         "求**最长**时在收缩完（窗口已合法）之后统计；求**最短**时在窗口刚合法的那一刻、"
         "收缩循环**内部**统计。位置放错，最短的那类题会整体偏大。"),
        ("`while` 写成 `if`",
         "一次收缩不一定能恢复合法（例如窗口里同一个字符出现了三次）。"
         "除非你能证明每步最多违规一次，否则一律用 `while`。"),
        ("跳跃式左指针忘了 `max`",
         "3 题的进阶写法里 `left = max(left, last[ch] + 1)`；漏掉 `max`，"
         "遇到 `\"abba\"` 时左指针会**倒退**，答案偏大。"),
        ("计数字典没删空键",
         "`Counter` 减到 0 的键仍然存在，`len(cnt)` 和 `==` 都会受影响。"
         "要么 `del`，要么额外维护一个「不同字符数」。"),
        ("负数破坏单调性",
         "滑窗成立的前提是「扩大窗口让指标单调变差、收缩让它单调变好」。"
         "数组含负数时「和 ≥ target」不再单调，得换前缀和 + 单调队列或别的思路。"),
    ],

    quiz=[
        dict(num=1004, pattern=3, options=[3, 1, 15],
             prompt="数组只含 0 和 1，最多可以把 k 个 0 翻成 1，求最长的全 1 连续子数组。",
             why="滑动窗口。不合法 = 「窗口内 0 的个数 > k」，状态就一个计数器。"
                 "「最多 K 次操作」是滑窗最标准的暗号。"),
        dict(num=438, pattern=3, options=[3, 1, 2],
             prompt="找出字符串中所有「另一个串的字母异位词」的起始下标。",
             why="定长窗口（模板 B）+ 计数相等，和 567 是同一道题换了个问法："
                 "567 问存不存在，它问全部位置。窗口长度固定为模式串长度。"),
        dict(num=239, pattern=4, options=[3, 4, 8],
             prompt="窗口大小固定为 k，返回每个窗口里的**最大值**。",
             why="**单调队列，不是本章**——窗口是定长的，但要的是窗口内的最值，"
                 "而滑窗模板只会维护「和 / 计数」这类能 O(1) 增删的状态，最大值删掉后无法 O(1) 恢复。"
                 "见 §2 分流条件与第 04 章模板 B。"),
    ],
)
