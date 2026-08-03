# -*- coding: utf-8 -*-
"""第 16 章 · 一维 DP。"""

TPL_A = '''\
def rob(nums):
    prev = cur = 0                          # 【骨架】cur = 前 i 间房的最优,prev = 前 i-1 间
    for x in nums:                          # 【骨架】
        prev, cur = cur, max(cur, prev + x) # 【插槽】转移:不选这间 / 选这间(+ 前前的最优)
    return cur                              # 【插槽】答案:最后一项 / 全程最大 / 计数
'''

TPL_A_TESTS = '''\
assert rob([1, 2, 3, 1]) == 4
assert rob([2, 7, 9, 3, 1]) == 12
assert rob([]) == 0
assert rob([5]) == 5


# 70 Climbing Stairs:同一个骨架,转移换成"两条路加起来"
def climb_stairs(n):
    prev, cur = 1, 1
    for _ in range(n - 1):
        prev, cur = cur, prev + cur
    return cur


assert climb_stairs(2) == 2
assert climb_stairs(3) == 3
assert climb_stairs(1) == 1


# 213 House Robber II:环形 -> 拆成两条线性,掐头和去尾各跑一次
def rob_circle(nums):
    if len(nums) == 1:
        return nums[0]
    return max(rob(nums[1:]), rob(nums[:-1]))


assert rob_circle([2, 3, 2]) == 3
assert rob_circle([1, 2, 3, 1]) == 4
assert rob_circle([1, 2, 3]) == 3
'''

TPL_B = '''\
def coin_change(coins, amount):
    INF = float("inf")
    dp = [0] + [INF] * amount               # 【骨架】dp[t] = 凑出 t 的最优值;INF = 凑不出
    for t in range(1, amount + 1):          # 【骨架】按容量从小到大填
        for c in coins:                     # 【插槽】枚举"最后一步用了哪个"
            if c <= t:                      # 【骨架】
                dp[t] = min(dp[t], dp[t - c] + 1)   # 【插槽】min 求最少 / += 求方案数
    return -1 if dp[amount] == INF else dp[amount]  # 【插槽】不可达怎么表示
'''

TPL_B_TESTS = '''\
assert coin_change([1, 3, 4], 6) == 2       # 贪心会给 3 枚(4+1+1),DP 给 2 枚(3+3)
assert coin_change([1, 2, 5], 11) == 3
assert coin_change([2], 3) == -1
assert coin_change([1], 0) == 0


# 139 Word Break:同一个骨架,dp[t] 从"最优值"换成"可达性"
def word_break(s, word_dict):
    words = set(word_dict)
    dp = [True] + [False] * len(s)
    for t in range(1, len(s) + 1):
        for w in words:
            if t >= len(w) and dp[t - len(w)] and s[t - len(w):t] == w:
                dp[t] = True
                break
    return dp[len(s)]


assert word_break("leetcode", ["leet", "code"]) is True
assert word_break("applepenapple", ["apple", "pen"]) is True
assert word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]) is False
'''

CHAPTER = dict(
    no=16,
    freq="极高",

    mental_model="**先写状态定义，再写转移。`dp[i]` 到底是「前 i 个的答案」还是"
                 "「**以 i 结尾**的答案」——这是一维 DP 唯一的分水岭，也是所有错误的源头。**",
    mental_model_body=[
        "两种定义各有主场：求「整体最优」（打家劫舍、爬楼梯、零钱兑换）用**前 i 个**，"
        "答案就是 `dp[n]`；求「必须包含某个元素」（最大子数组和、最长上升子序列）用**以 i 结尾**，"
        "答案是 `max(dp)` 而不是 `dp[n]`。取错定义，转移方程会怎么写都不顺。",
        "写完转移别急着优化。`dp[i]` 只依赖前一两项时才做滚动变量（模板 A 的 `prev`/`cur`），"
        "先把二维数组写对再压缩——面试里也建议这个顺序，省下的空间讲一句就行。",
    ],

    signals=[
        ("「有多少种方法 / 最少多少步」且答案只由前几项决定", "线性 DP（模板 A）"),
        ("「不能取相邻的两个」", "打家劫舍骨架：选它就得跳过前一个"),
        ("「凑出金额 / 能否拆分成若干段」", "完全背包式（模板 B）"),
        ("「以 i 结尾的最长 / 最大」", "状态定义必须带「以 i 结尾」，答案取 `max(dp)`"),
        ("数据规模 10⁴~10⁵ 且要最优值", "DP（回溯会超时，贪心不一定对）"),
        ("环形（首尾相接）", "拆成两条线性各跑一次（213）"),
    ],
    routing="要**方案本身**是回溯（第 09 章），要**方案数**才是 DP——第 09 章的 377 就是这个分流。"
            "每一步的最优选择显而易见、且不需要回头改，那是贪心（第 15 章）；"
            "反例见模板 B 的第一条断言。"
            "状态需要两个下标（两个序列、容量 × 物品）→ 第 17 章；"
            "「最长上升子序列」这一族虽然也是一维数组，但状态定义和转移自成一套 → 第 18 章。",
    routing_to=[9, 15, 17, 18],

    templates=[
        dict(name="模板 A · 线性 DP", note="dp[i] 只依赖前一两项",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**两个变量滚着走，每步只问选不选**。"
                  "写不顺时先摊开成完整的 `dp` 数组，确认对了再压成 `prev`/`cur`。"),
        dict(name="模板 B · 按容量填表", note="凑金额 / 能否拆分",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="外层容量、内层物品 = **完全背包**（每个物品可重复用），也是「排列数」的顺序。"
                  "反过来外层物品、内层容量才是「组合数」，两者的差别在第 17 章说清。"),
    ],

    problems=[
        dict(num=70, tier="warmup",
             note="全书最小的 DP。它的价值是让你第一次说出「`dp[i]` = 走到第 i 级的方法数」"
                  "这句话——状态定义的习惯从这里开始养。"),
        dict(num=198, tier="standard",
             note="模板 A 原题。状态定义是「前 i 间房能偷到的最多钱」，"
                  "转移是「不偷这间 = `dp[i-1]`，偷这间 = `dp[i-2] + nums[i]`」。"),
        dict(num=213, tier="standard",
             note="环形拆解的标准套路：首尾不能同时取 ⇒ 要么不要第一间，要么不要最后一间，"
                  "两次线性 DP 取较大者。同样的拆法在 337、918 里反复出现。"),
        dict(num=322, tier="standard",
             note="模板 B 原题，也是「贪心为什么不行」的标准反例（见 §2 分流条件）。"
                  "`INF` 表示不可达，最后判一次；别用 -1 当哨兵，`min` 会把它选走。"),
        dict(num=139, tier="standard",
             note="`dp[t]` 从最优值换成布尔可达性。"
                  "字典先转 `set`；被追问优化时提「按单词长度枚举而不是遍历整个字典」。"),
        dict(num=91, tier="variant",
             note="转移和爬楼梯同形（一位数 + 两位数），全部难度在 `'0'` 的边界："
                  "`'0'` 不能单独解码，`'06'` 也不是合法的两位数。写之前先把这两条列出来。"),
        dict(num=152, tier="variant",
             note="必须**同时维护最大和最小**——负数乘负数会翻身成最大。"
                  "这是「状态定义不只一个」的最好例子：一个 `dp` 数组不够用时，就开两个。"),
    ],

    pitfalls=[
        ("状态定义含糊",
         "「`dp[i]` 表示到 i 为止的结果」这种说法没有信息量。"
         "必须明确到「前 i 个」还是「以 i 结尾」，以及答案是 `dp[n]` 还是 `max(dp)`。"),
        ("答案取错位置",
         "「以 i 结尾」类的答案是 `max(dp)`。写成 `dp[-1]` 时，"
         "最大子数组和、最长上升子序列都会在「最优段不在末尾」的用例上出错。"),
        ("不可达用 -1 当哨兵",
         "322 里若把凑不出记成 -1，`min(dp[t], dp[t-c] + 1)` 会把 -1+1=0 选进来。"
         "用 `float('inf')` 或 `amount + 1`。"),
        ("急着压缩空间",
         "先写出正确的完整 `dp` 数组，再压成滚动变量。"
         "213 这类需要「两次线性」的题，压缩后更难调试。"),
        ("环形直接绕圈算",
         "首尾相接不能靠取模硬算，标准解法是拆成两条线性。"),
    ],

    quiz=[
        dict(num=746, pattern=16, options=[16, 15, 9],
             prompt="每级台阶有一个花费，每次可以走 1 或 2 级，求走到楼顶的最小花费。",
             why="一维 DP（模板 A）。`dp[i] = cost[i] + min(dp[i-1], dp[i-2])`，"
                 "和爬楼梯是同一个骨架，只是把「方法数求和」换成「花费取 min」。"),
        dict(num=518, pattern=16, options=[16, 9, 15],
             prompt="给定面额，求凑出目标金额的**组合数**（`1+2` 和 `2+1` 算同一种）。",
             why="一维 DP（模板 B 的计数版）。关键在循环顺序：**外层物品、内层容量**才是组合数；"
                 "反过来会把 `1+2` 和 `2+1` 数成两种（那是 377 排列数）。"
                 "同一个骨架，两层循环换个位置就是两道不同的题。"),
        dict(num=55, pattern=15, options=[16, 15, 17],
             prompt="数组里每个数表示在该位置最多能向前跳几步，判断能否从起点跳到终点。",
             why="**贪心，不是本章**——`dp[i] = 能否到达 i` 的写法是 O(n²) 且会超时；"
                 "只维护「目前能到的最远位置」就够，O(n)。"
                 "能一句话说清每步该选谁、且不需要回头改，优先贪心。见第 15 章。"),
    ],
)
