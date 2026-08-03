# -*- coding: utf-8 -*-
"""第 13 章 · 前缀和。"""

TPL_A = '''\
def build_prefix(nums):
    pre = [0] * (len(nums) + 1)             # 【骨架】长度 n+1,pre[0]=0 是哨兵
    for i, x in enumerate(nums):            # 【骨架】
        pre[i + 1] = pre[i] + x             # 【插槽】累积什么:和 / 乘积 / 异或 / 计数
    return pre

def range_sum(pre, i, j):                   # 【骨架】闭区间 [i, j]
    return pre[j + 1] - pre[i]              # 【骨架】区间 = 两个前缀之差
'''

TPL_A_TESTS = '''\
pre = build_prefix([-2, 0, 3, -5, 2, -1])
assert range_sum(pre, 0, 2) == 1
assert range_sum(pre, 2, 5) == -1
assert range_sum(pre, 0, 5) == -3
assert range_sum(pre, 3, 3) == -5
assert build_prefix([]) == [0]


# 238 Product of Array Except Self:前缀 + 后缀,不许用除法
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    for i in range(1, n):                   # 左边的乘积
        out[i] = out[i - 1] * nums[i - 1]
    right = 1
    for i in range(n - 1, -1, -1):          # 右边的乘积,边走边乘进去
        out[i] *= right
        right *= nums[i]
    return out


assert product_except_self([1, 2, 3, 4]) == [24, 12, 8, 6]
assert product_except_self([-1, 1, 0, -3, 3]) == [0, 0, 9, 0, 0]
'''

TPL_B = '''\
from collections import defaultdict

def subarray_sum_k(nums, k):
    cnt = defaultdict(int)
    cnt[0] = 1                              # 【骨架】空前缀出现过一次;漏了它就漏掉"从头开始"的子数组
    cur = ans = 0
    for x in nums:                          # 【骨架】
        cur += x                            # 【插槽】累积量:和 / 前缀和取模 / 奇偶数差
        ans += cnt[cur - k]                 # 【插槽】要找的历史值,以及答案怎么攒:计数 / 最长 / 存在性
        cnt[cur] += 1                       # 【骨架】先结算再登记,否则会用自己配自己
    return ans
'''

TPL_B_TESTS = '''\
assert subarray_sum_k([1, 1, 1], 2) == 2
assert subarray_sum_k([1, 2, 3], 3) == 2
assert subarray_sum_k([1, -1, 0], 0) == 3
assert subarray_sum_k([3], 3) == 1          # 从头开始的子数组,靠 cnt[0]=1 才数得到


# 523 Continuous Subarray Sum:累积量换成"前缀和 % k",历史值里存最早下标
def check_subarray_sum(nums, k):
    first = {0: -1}                         # 余数 -> 最早出现的下标
    cur = 0
    for i, x in enumerate(nums):
        cur = (cur + x) % k
        if cur in first:
            if i - first[cur] >= 2:         # 长度至少为 2
                return True
        else:
            first[cur] = i                  # 只记最早的,才能拿到最长的区间
    return False


assert check_subarray_sum([23, 2, 4, 6, 7], 6) is True
assert check_subarray_sum([23, 2, 6, 4, 7], 13) is False
assert check_subarray_sum([1, 0], 2) is False
assert check_subarray_sum([0, 0], 2) is True
'''

CHAPTER = dict(
    no=13,
    freq="高",

    mental_model="**前缀和把「区间和」变成两个数的差：`sum(i..j) = pre[j+1] - pre[i]`。"
                 "一旦区间和能 O(1) 拿到，问题就退化成「找一对下标」——那是第 01 章的活。**",
    mental_model_body=[
        "这两步是本章的全部：先把「区间」降维成「一对前缀」，再用哈希表回答"
        "「我要的那个前缀值，之前出现过几次 / 最早在哪」。"
        "「子数组和恰好为 K」于是变成：对每个右端点，问 `cur - k` 见过几次。",
        "累积量不必是和。**取模**后能处理「能被 K 整除」，**异或**前缀能处理「异或为 0 的子数组」，"
        "**前后缀乘积**能处理 238。骨架不动，换的只是「累积什么」和「找哪个历史值」。",
    ],

    signals=[
        ("「区间和 / 范围求和」且要**多次查询**", "预处理前缀和数组（模板 A）"),
        ("「和**恰好**为 K 的子数组个数 / 最长长度」", "前缀和 + 哈希（模板 B）"),
        ("「除自身以外数组的乘积」且不许用除法", "前缀积 × 后缀积"),
        ("「能被 K 整除的子数组」", "前缀和**取模**，同余即可整除"),
        ("「0 和 1 数量相同的最长子数组」", "把 0 记成 −1，转成「和为 0」"),
        ("二维矩阵的「子矩形和」", "二维前缀和，容斥四项"),
    ],
    routing="都带「连续子数组」四个字，分流看的是**问什么**："
            "「和**恰好**为 K」→ 本章（元素可能为负时窗口和不单调，滑窗的收缩条件无从写起；"
            "全为正数时滑窗也做得了，但前缀和一招通吃）；"
            "「和 ≥ target 的**最短**」且元素**全为正** → 滑动窗口（第 03 章）；"
            "「窗口固定大小求最值」→ 单调队列（第 04 章）。"
            "本章的哈希只是配件，主语始终是前缀和——这一点决定了你该往哪本模板里翻。",
    routing_to=[1, 3, 4],

    templates=[
        dict(name="模板 A · 前缀和数组", note="多次区间查询",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**长度 n+1、pre[0]=0、区间取两端之差**。"
                  "哨兵位省掉了所有 `i == 0` 的特判。"),
        dict(name="模板 B · 前缀和 + 哈希", note="「恰好为 K」类",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="两条铁律：**`cnt[0] = 1` 必须有**（代表空前缀），"
                  "**先结算再登记**（否则会拿自己配自己，和第 01 章模板 A 是同一条纪律）。"),
    ],

    problems=[
        dict(num=303, tier="warmup",
             note="模板 A 原题。它存在的意义就是让你记住「预处理一次，之后每次查询 O(1)」"
                  "这个交易——以及 `n + 1` 长度的哨兵位。"),
        dict(num=238, tier="standard",
             note="前缀积 + 后缀积。第二遍用一个滚动变量 `right` 就能做到 O(1) 额外空间"
                  "（输出数组不算）。被追问「有 0 怎么办」时，正是不用除法的理由。"),
        dict(num=560, tier="standard",
             note="模板 B 原题，本章最该背下来的一道。"
                  "面试高频追问：「全是正数能不能用滑窗」——能，但有负数就只能靠它。"),
        dict(num=523, tier="variant",
             note="累积量换成 `前缀和 % k`，哈希里存**最早下标**而不是次数。"
                  "两个坑：长度至少为 2，以及 `first = {0: -1}` 这个初始值。"),
    ],

    pitfalls=[
        ("忘了 `cnt[0] = 1`",
         "少了它，「从下标 0 开始的那些子数组」全部数不到。"
         "`subarray_sum_k([3], 3)` 会返回 0——模板测试里专门留了这条断言。"),
        ("先登记再结算",
         "`cnt[cur] += 1` 必须在 `ans += cnt[cur - k]` 之后。顺序反了，`k == 0` 时每个位置都会多算一次。"),
        ("下标偏移写错",
         "`pre` 长度是 `n + 1`，闭区间 `[i, j]` 的和是 `pre[j+1] - pre[i]`。"
         "把 `pre` 写成长度 `n`（`pre[i]` 表示前 i+1 项）也能做，但每道题都要重新推边界，得不偿失。"),
        ("对负数用滑窗",
         "「和为 K 的子数组」在有负数时**不能**滑窗：扩大窗口不再让和单调变大，收缩条件无从写起。"
         "这正是本章存在的理由。"),
        ("523 只判同余不判长度",
         "题目要求子数组长度至少为 2，所以哈希里要存**最早**下标并检查 `i - first[cur] >= 2`。"
         "存最新下标会把长度 1 的情况误判成 True。"),
    ],

    quiz=[
        dict(num=724, pattern=13, options=[13, 3, 2],
             prompt="找出数组中的「中心下标」：它左边所有数之和等于右边所有数之和。",
             why="前缀和。`left == total - left - nums[i]` 一次遍历即可。"
                 "看到「左边的和 / 右边的和」就是前缀和的字面形态，连哈希都不需要。"),
        dict(num=974, pattern=13, options=[13, 3, 1],
             prompt="求和能被 K 整除的连续子数组个数。",
             why="前缀和 + 哈希（模板 B），累积量换成 `前缀和 % k`："
                 "两个前缀同余，它们之间那段就能被 K 整除。"
                 "注意 Python 的 `%` 对负数已经返回非负结果，其他语言要自己修正。"),
        dict(num=643, pattern=3, hide_num=True, options=[13, 3, 4],
             prompt="求长度**恰好为 k** 的连续子数组的最大平均值。",
             why="**定长滑动窗口，不是本章**——窗口大小固定，进一个出一个就能 O(1) 维护和，"
                 "根本不需要建前缀数组。前缀和是为**任意区间**的多次查询准备的；"
                 "只查一种固定长度时它是杀鸡用牛刀。见 §2 分流条件与第 03 章模板 B。"),
    ],
)
