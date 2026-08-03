# -*- coding: utf-8 -*-
"""第 04 章 · 栈与单调栈。内容取自 spec/ch04-sample.md（已获批样章），是全书体例基准。"""

TPL_A = '''\
def next_greater(nums):
    n = len(nums)
    ans = [-1] * n                          # 【插槽】默认值:没等到答案的人得什么
    stack = []                              # 【骨架】存下标;栈内对应值单调递减
    for i, x in enumerate(nums):            # 【骨架】
        while stack and nums[stack[-1]] < x:  # 【插槽】比较方向:< 找更大,> 找更小;带不带 = 见翻车点②
            j = stack.pop()                 # 【骨架】j 此刻等到了答案
            ans[j] = x                      # 【插槽】答案形式:值 x / 距离 i-j / 下标 i
        stack.append(i)                     # 【骨架】
    return ans
'''

TPL_A_TESTS = '''\
assert next_greater([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]
assert next_greater([]) == []
assert next_greater([3, 3, 3]) == [-1, -1, -1]   # 相等不结账,全部落到默认值


# 739 Daily Temperatures:唯一改动是插槽行的答案形式
def daily_temperatures(t):
    n = len(t)
    ans = [0] * n
    stack = []
    for i, x in enumerate(t):
        while stack and t[stack[-1]] < x:
            j = stack.pop()
            ans[j] = i - j
        stack.append(i)
    return ans


assert daily_temperatures([73, 74, 75, 71, 69, 72, 76, 73]) == [1, 1, 4, 2, 1, 1, 0, 0]


# 84 Largest Rectangle:模板 A 换方向 + 末尾哨兵强制清算
def largest_rectangle(heights):
    heights = heights + [0]
    stack, best = [], 0
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] >= h:
            j = stack.pop()
            left = stack[-1] if stack else -1
            best = max(best, heights[j] * (i - left - 1))
        stack.append(i)
    return best


assert largest_rectangle([2, 1, 5, 6, 2, 3]) == 10
assert largest_rectangle([2, 4]) == 4
'''

TPL_B = '''\
from collections import deque

def max_sliding_window(nums, k):
    q, ans = deque(), []                    # 【骨架】q 存下标,对应值单调递减,队首=窗口最大
    for i, x in enumerate(nums):
        while q and nums[q[-1]] <= x:       # 【骨架】新人把比自己弱的全部挤出去
            q.pop()
        q.append(i)
        if q[0] <= i - k:                   # 【插槽】过期条件:窗口左界怎么算
            q.popleft()
        if i >= k - 1:                      # 【插槽】何时开始产出答案
            ans.append(nums[q[0]])
    return ans
'''

TPL_B_TESTS = '''\
assert max_sliding_window([1, 3, -1, -3, 5, 3, 6, 7], 3) == [3, 3, 5, 5, 6, 7]
assert max_sliding_window([1], 1) == [1]
assert max_sliding_window([7, 6, 5, 4], 2) == [7, 6, 5]   # 全递减:队首始终是刚出窗的前一个
'''

CHAPTER = dict(
    no=4,
    freq="高",

    mental_model="**单调栈：每个元素都在找「左边或右边第一个比我大（或小）的人」；"
                 "栈里存的，是那些还没等到答案的人。**",
    mental_model_body=[
        "新元素进场时，把栈里所有「等到答案了」的人依次弹出并结账——弹出的那一刻就是它的答案揭晓的那一刻。"
        "每个元素最多进出栈一次，所以整体 O(n)，这就是它把 O(n²) 暴力扫描打下来的全部秘密。",
        "普通栈是它的退化形态：不比大小、只配对嵌套结构（括号、路径、表达式），本章热身用它找感觉。",
    ],

    signals=[
        ("「下一个更大 / 更小元素」", "单调栈（模板 A）"),
        ("「第一个比它高 / 低 / 便宜的…」", "单调栈（模板 A）"),
        ("「柱状图 / 矩形 / 最大面积」", "单调栈（模板 A + 哨兵）"),
        ("「滑动窗口的最大 / 最小值」", "单调队列（模板 B）"),
        ("括号匹配、嵌套、「撤销上一步」", "普通栈"),
        ("你写出的暴力解，内层循环在「向左/右扫，找第一个满足条件就停」", "单调栈优化信号"),
    ],
    routing="「连续子数组 + 最值」且窗口大小固定 → 单调队列；窗口不固定、条件是「和 / 种类数」 → "
            "滑动窗口（第 03 章）；「子数组和恰好为 K」 → 前缀和 + 哈希（第 13 章）。",
    routing_to=[3, 13],

    templates=[
        dict(name="模板 A · 下一个更大元素", note="覆盖本章 80% 的题",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**存下标、递减栈、弹出即结账**。"),
        dict(name="模板 B · 单调队列", note="仅 239 一题需要，认脸级",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="与模板 A 的唯一区别：窗口会从左边过期，所以要用双端队列在队首淘汰出窗的人。"),
    ],

    problems=[
        dict(num=20, tier="warmup",
             note="纯配对：左括号进栈，右括号找栈顶结账。体会「栈顶 = 最近一个未完成的事」。"),
        dict(num=155, tier="warmup",
             note="辅助栈同步记录「当前最小」。插槽思维预演：栈里存什么由问题决定。"),
        dict(num=739, tier="standard",
             note="模板 A 原题。唯一插槽改动：`ans[j] = i - j`（答案要距离，这就是为什么骨架存下标）。"),
        dict(num=496, tier="standard",
             note="模板 A + 哈希把答案映射回子数组。"),
        dict(num=503, tier="standard",
             note="循环数组变形：遍历 `2n` 次、下标取 `i % n`，其余不变。"),
        dict(num=853, tier="variant",
             note="先按位置排序算到达时间，再用栈合并车队。识别难度大于实现难度："
                  "它的「第一个追上我的人」结构藏在排序之后。"),
        dict(num=84, tier="variant", star=True,
             note="模板 A 换方向（递增栈、找两侧第一个更矮的），末尾补哨兵 0 强制清算。"
                  "见翻车点⑤，本章唯一必须掌握的 hard。"),
        dict(num=239, tier="variant", star=True,
             note="模板 B 原题，认脸即可。"),
    ],

    pitfalls=[
        ("存值还是存下标",
         "默认存下标。答案涉及距离或位置（739）时值救不了你；存下标永远能取回值，反之不行。"),
        ("严格与非严格（`<` vs `<=`）",
         "有重复元素时决定相等的人算不算「答案」。84 题里用 `>=` 弹出可以简化等高柱的处理；"
         "写题前先问一句「两个相等的元素，谁给谁结账」。"),
        ("方向记反",
         "找「更大」用递减栈，找「更小」用递增栈。记法：栈里留着的都是「还没等到更大的人」，"
         "所以他们自然从底到顶递减。"),
        ("循环数组忘了取模",
         "503 走两遍时下标必须 `i % n`，第二遍只结账、不再入栈也可以（微优化，非必须）。"),
        ("清算时机",
         "遍历结束后栈里剩下的人是「永远没等到答案的人」。要么接受默认值（739 的 0），"
         "要么补哨兵强制结账（84 的末尾 0）——忘掉这一步是 84 题 WA 的头号原因。"),
    ],

    quiz=[
        dict(num=901, pattern=4, options=[4, 3, 8],
             prompt="返回今天之前连续多少天股价 ≤ 今天。",
             why="单调栈。这是「之前第一个比我高的」的镜像问法：找到那个人，中间的天数就是答案，"
                 "所以要存下标而不是值（翻车点①）。"),
        dict(num=402, pattern=4, options=[4, 15, 9],
             prompt="删掉 k 个数字使剩下的数最小。",
             why="单调栈。维持栈内递增，遇到更小的就把前面大的弹掉——「删掉一个大的」正是弹栈动作；"
                 "贪心的直觉对，但落地结构是栈。"),
        dict(num=560, pattern=13, hide_num=True, options=[4, 3, 13],
             prompt="给定数组和整数 k，求「和恰好等于 k 的连续子数组」个数。",
             why="**前缀和 + 哈希，不是本章**——「恰好为 K」是分流关键词，见 §2 分流条件。"
                 "单调栈处理的是「比较大小」，不是「求和」。"),
    ],
)
