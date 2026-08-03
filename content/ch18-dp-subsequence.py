# -*- coding: utf-8 -*-
"""第 18 章 · 子序列 DP（LIS 类）。"""

TPL_A = '''\
def length_of_lis(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)                    # 【骨架】dp[i] = **以 i 结尾**的最长长度
    for i in range(len(nums)):              # 【骨架】
        for j in range(i):                  # 【骨架】回头看所有更早的元素
            if nums[j] < nums[i]:           # 【插槽】能否接在 j 后面:严格上升 / 非降 / 整除
                dp[i] = max(dp[i], dp[j] + 1)   # 【插槽】接上之后怎么更新
    return max(dp)                          # 【插槽】答案在所有结尾里取最大,不是 dp[-1]
'''

TPL_A_TESTS = '''\
assert length_of_lis([10, 9, 2, 5, 3, 7, 101, 18]) == 4
assert length_of_lis([0, 1, 0, 3, 2, 3]) == 4
assert length_of_lis([7, 7, 7, 7]) == 1
assert length_of_lis([]) == 0


# 673 Number of LIS:再开一个 count 数组,分"更长"和"等长"两种情况
def find_number_of_lis(nums):
    n = len(nums)
    if not n:
        return 0
    dp, cnt = [1] * n, [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if dp[j] + 1 > dp[i]:       # 发现更长的 -> 长度更新,方案数继承
                    dp[i], cnt[i] = dp[j] + 1, cnt[j]
                elif dp[j] + 1 == dp[i]:    # 等长的另一条路 -> 方案数累加
                    cnt[i] += cnt[j]
    best = max(dp)
    return sum(c for d, c in zip(dp, cnt) if d == best)


assert find_number_of_lis([1, 3, 5, 4, 7]) == 2
assert find_number_of_lis([2, 2, 2, 2, 2]) == 5
'''

TPL_B = '''\
import bisect

def length_of_lis_fast(nums):
    tails = []                              # 【骨架】tails[k] = 长度为 k+1 的上升子序列的最小结尾
    for x in nums:                          # 【骨架】
        i = bisect.bisect_left(tails, x)    # 【插槽】bisect_left 严格上升;bisect_right 允许相等
        if i == len(tails):                 # 【骨架】比所有结尾都大 -> 接出更长的一条
            tails.append(x)
        else:
            tails[i] = x                    # 【骨架】否则用它替换掉那个更大的结尾
    return len(tails)                       # 【插槽】只有长度可信,tails 本身不是某条 LIS
'''

TPL_B_TESTS = '''\
assert length_of_lis_fast([10, 9, 2, 5, 3, 7, 101, 18]) == 4
assert length_of_lis_fast([0, 1, 0, 3, 2, 3]) == 4
assert length_of_lis_fast([7, 7, 7, 7]) == 1
assert length_of_lis_fast([]) == 0

import random                               # 与模板 A 的 O(n^2) 版交叉验证


def _slow_lis(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


random.seed(18)
for _ in range(200):
    a = [random.randint(0, 20) for _ in range(random.randint(0, 30))]
    assert length_of_lis_fast(a) == _slow_lis(a)


# 354 Russian Doll Envelopes:宽升序、**宽相同时高降序**,再对高求 LIS
def max_envelopes(envelopes):
    envelopes.sort(key=lambda e: (e[0], -e[1]))
    return length_of_lis_fast([h for _, h in envelopes])


assert max_envelopes([[5, 4], [6, 4], [6, 7], [2, 3]]) == 3
assert max_envelopes([[1, 1], [1, 1], [1, 1]]) == 1
'''

CHAPTER = dict(
    no=18,
    freq="中",

    mental_model="**LIS 的状态定义是「以 i 结尾的最长上升子序列」——「以 i 结尾」这四个字是全章的钥匙。"
                 "O(n²) 是两层循环回头看；O(n log n) 是用一个 tails 数组做二分。**",
    mental_model_body=[
        "面试的标准打法：**先讲 O(n²) 的状态定义与转移，再说「还能用耐心排序 + 二分做到 "
        "O(n log n)」，然后写后者**。只写快的说不清来龙去脉，只写慢的显得没准备。",
        "`tails` 那个数组必须讲清楚一件事：`tails[k]` 是「长度为 k+1 的上升子序列中最小的结尾」，"
        "**它本身通常不是任何一条真实的 LIS**——只有它的长度是对的。"
        "面试官很爱追问这一点，答不上来会被认为是背的。",
    ],

    signals=[
        ("「最长上升 / 递增**子序列**」（不要求连续）", "LIS（模板 A 或 B）"),
        ("「最长数对链 / 俄罗斯套娃信封」", "先排序，再对另一个维度求 LIS"),
        ("「最长可整除子集 / 最长字符串链」", "排序后把「能否接上」换成整除 / 差一个字母"),
        ("「有多少个最长上升子序列」", "再开一个 `count` 数组（673）"),
        ("「最少用几个不升序列覆盖」", "Dilworth 定理，答案等于 LIS 长度"),
        ("「子序列」+「最长 / 最多」且只有一个序列", "本章；两个序列是第 17 章的 LCS"),
    ],
    routing="**连续**才是滑动窗口（第 03 章）或前缀和（第 13 章），"
            "**子序列**（可以跳着取）才是本章——这两个字是最关键的分流点。"
            "只求「最大和的连续子数组」是 Kadane（第 15 章）。"
            "两个序列之间的公共子序列（LCS）是第 17 章的双序列表；"
            "本章只有一个序列，转移要回头看所有更早的元素。",
    routing_to=[3, 13, 15, 17],

    templates=[
        dict(name="模板 A · O(n²) LIS", note="先能讲清它，再谈优化",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**以 i 结尾、回头看 j、能接就接、答案取 max(dp)**。"
                  "「以 i 结尾」决定了答案是 `max(dp)` 而不是 `dp[-1]`。"),
        dict(name="模板 B · 耐心排序 + 二分", note="O(n log n)，面试主推",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="严格上升用 `bisect_left`（相等的会被替换掉），"
                  "允许相等用 `bisect_right`。一个字母的差别，354 就靠它。"),
    ],

    problems=[
        dict(num=300, tier="standard",
             note="本章的母题。两种解法都要会：先讲 O(n²) 的状态定义，再写 O(n log n)。"
                  "本章刻意没有热身题——300 之前没有更简单的 LIS 可讲。"),
        dict(num=673, tier="variant",
             note="在模板 A 上再挂一个 `cnt` 数组，分「发现更长」（方案数继承）和"
                  "「等长的另一条路」（方案数累加）两种情况。"
                  "两种情况写反是唯一的坑，模板测试里留了 `[2,2,2,2,2]` 这条断言。"),
        dict(num=354, tier="variant", star=True,
             note="⭐认脸。宽升序、**宽相同时高降序**，然后对高求 LIS。"
                  "高要降序是为了让同宽的信封无法互相嵌套——说得出这一句就够。"),
    ],

    pitfalls=[
        ("答案写成 `dp[-1]`",
         "状态是「以 i 结尾」，最优的那条未必在末尾结束。必须 `max(dp)`。"),
        ("把 `tails` 当成 LIS 本身",
         "`tails` 只保证长度正确，内容通常不是任何一条真实的上升子序列。"
         "要还原具体序列得额外记前驱下标。"),
        ("`bisect_left` 和 `bisect_right` 用反",
         "严格上升用 `bisect_left`；写成 `bisect_right`，`[7,7,7,7]` 会返回 4 而不是 1。"),
        ("354 排序时高也用升序",
         "宽相同的信封若按高升序排，它们之间会被当成可嵌套，答案偏大。"
         "必须高降序。"),
        ("把「连续子数组」当子序列做",
         "LIS 允许跳着取，`[10, 9, 2, 5, 3, 7]` 的答案是 3（2, 3, 7）而不是相邻的那段。"
         "读题时先确认要不要连续，见 §2 分流条件。"),
    ],

    quiz=[
        dict(num=368, pattern=18, options=[18, 9, 17],
             prompt="从一组互不相同的正整数里，选出最大的子集，使其中任意两个数都能互相整除。",
             why="LIS 变体（模板 A）。先排序，把「能否接在 j 后面」的条件从 `nums[j] < nums[i]` "
                 "换成 `nums[i] % nums[j] == 0`，骨架一行没动。"
                 "要返回子集本身，所以还得记前驱下标。"),
        dict(num=1048, pattern=18, options=[18, 17, 1],
             prompt="若在字符串 A 中插入一个字母能得到 B，则 A 是 B 的前身。求最长的词链长度。",
             why="LIS 变体。按**长度**排序后，「能否接上」变成「删掉一个字母是否相等」。"
                 "用哈希表按「前身」直接转移比两层循环更快，但状态定义还是「以某个词结尾的最长链」。"),
        dict(num=53, pattern=15, options=[18, 15, 3],
             prompt="求**连续**子数组的最大和。",
             why="**贪心 / Kadane，不是本章**——「连续」两个字直接排除了子序列 DP。"
                 "LIS 要回头看所有更早的元素（O(n²)），而连续的只需要看前一个"
                 "（`cur = max(x, cur + x)`，O(n)）。见 §2 分流条件与第 15 章。"),
    ],
)
