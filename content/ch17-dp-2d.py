# -*- coding: utf-8 -*-
"""第 17 章 · 二维 DP 与背包。"""

TPL_A = '''\
def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]          # 【骨架】多开一行一列当边界,省掉特判
    for i in range(1, m + 1):                           # 【骨架】
        for j in range(1, n + 1):                       # 【骨架】
            if a[i - 1] == b[j - 1]:                    # 【插槽】两个维度"对上了"的条件
                dp[i][j] = dp[i - 1][j - 1] + 1         # 【插槽】对上了怎么转移(走对角线)
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])  # 【插槽】没对上:各退一步取最优
    return dp[m][n]                                     # 【插槽】答案在右下角
'''

TPL_A_TESTS = '''\
assert lcs("abcde", "ace") == 3
assert lcs("abc", "abc") == 3
assert lcs("abc", "def") == 0
assert lcs("", "abc") == 0


# 62 Unique Paths:同一张表,转移换成"上面 + 左边"
def unique_paths(m, n):
    dp = [[1] * n for _ in range(m)]
    for i in range(1, m):
        for j in range(1, n):
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
    return dp[m - 1][n - 1]


assert unique_paths(3, 7) == 28
assert unique_paths(3, 2) == 3
assert unique_paths(1, 1) == 1


# 72 Edit Distance:三种操作对应三个来向
def min_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i                        # 全删
    for j in range(n + 1):
        dp[0][j] = j                        # 全插
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],        # 删
                                   dp[i][j - 1],        # 插
                                   dp[i - 1][j - 1])    # 换
    return dp[m][n]


assert min_distance("horse", "ros") == 3
assert min_distance("intention", "execution") == 5
assert min_distance("", "abc") == 3
'''

TPL_B = '''\
def can_partition(nums):
    total = sum(nums)
    if total % 2:                           # 【插槽】问题先转化成"能否凑出某个目标"
        return False
    target = total // 2
    dp = [False] * (target + 1)             # 【骨架】dp[t] = 能否恰好凑出 t
    dp[0] = True                            # 【骨架】什么都不选就能凑出 0
    for x in nums:                          # 【骨架】外层枚举物品
        for t in range(target, x - 1, -1):  # 【骨架】容量倒序 —— 保证每个物品只用一次
            dp[t] = dp[t] or dp[t - x]      # 【插槽】布尔可行性 / 计数 / 最大价值
    return dp[target]
'''

TPL_B_TESTS = '''\
assert can_partition([1, 5, 11, 5]) is True
assert can_partition([1, 2, 3, 5]) is False
assert can_partition([1, 1]) is True
assert can_partition([1]) is False


# 494 Target Sum:加减号 -> 子集和。设正号组和为 P,则 P = (sum + target) / 2
def find_target_sum_ways(nums, target):
    total = sum(nums)
    if (total + target) % 2 or abs(target) > total:
        return 0
    want = (total + target) // 2
    dp = [0] * (want + 1)
    dp[0] = 1                               # 计数版:凑出 0 有 1 种方案(什么都不选)
    for x in nums:
        for t in range(want, x - 1, -1):    # 同样倒序
            dp[t] += dp[t - x]
    return dp[want]


assert find_target_sum_ways([1, 1, 1, 1, 1], 3) == 5
assert find_target_sum_ways([1], 1) == 1
assert find_target_sum_ways([1], 2) == 0
assert find_target_sum_ways([0, 0, 0, 0, 0, 0, 0, 0, 1], 1) == 256
'''

CHAPTER = dict(
    no=17,
    freq="高",

    mental_model="**二维 DP = 两个维度各自「取到 i / 取到 j」。"
                 "01 背包是它的特例：对每个物品只问一句「选还是不选」，"
                 "压成一维之后，容量必须倒序遍历。**",
    mental_model_body=[
        "双序列题（LCS、编辑距离、正则匹配）的表格永远长一个样：`dp[i][j]` 表示"
        "「a 的前 i 个和 b 的前 j 个」的答案。**对上了走对角线，没对上各退一步**——"
        "这两句话覆盖了本章一半的题。",
        "背包的一维压缩是本章唯一需要死记的细节：**01 背包倒序、完全背包正序**。"
        "原因是倒序时 `dp[t - x]` 还停留在「上一件物品」的状态，"
        "正序时它已经被本轮更新过，等于允许同一件物品用多次。",
    ],

    signals=[
        ("「两个字符串 / 两个数组」比较、匹配、对齐", "`dp[i][j]` 双序列表（模板 A）"),
        ("「网格里从左上走到右下」（路径数 / 最小路径和）", "`dp[i][j] = 上 + 左`"),
        ("「能否把数组分成和相等的两半」", "01 背包布尔版（模板 B）"),
        ("「加减号 / 分成两组」凑出目标", "先转成子集和，再套背包（494）"),
        ("「编辑距离 / 最长公共子序列 / 通配符匹配」", "模板 A，只换「对上/没对上」的转移"),
        ("「带冷冻期 / 手续费的股票」", "状态机 DP：`dp[i][持有 or 空仓]`"),
    ],
    routing="状态只需要一个下标、且只依赖前一两项 → 第 16 章。"
            "「最长上升**子序列**」虽然也在比较元素大小，但只有一个序列、"
            "转移要回头看所有更早的元素，自成一套 → 第 18 章。"
            "要列出全部方案而不是计数 → 回溯（第 09 章）。"
            "「路径」这个词也要分三处：网格里**只能右 / 下**走 → 本章（方向受限、不可能有环，纯 DP）；"
            "能四向移动、求**最少步数** → 第 10 章的 BFS；树上的路径和 → 第 07 章的递归。",

    templates=[
        dict(name="模板 A · 双序列 / 网格 DP", note="LCS、编辑距离、路径数",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**多开一圈边界、对上走对角、没对上各退一步**。"
                  "边界怎么初始化取决于题意：路径数填 1，编辑距离填 `i` / `j`，LCS 填 0。"),
        dict(name="模板 B · 01 背包（一维）", note="选或不选，容量倒序",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="**01 背包倒序、完全背包正序**——这一行的方向就是「每件用一次」和"
                  "「每件可无限用」的全部差别，见翻车点①。"),
    ],

    problems=[
        dict(num=62, tier="warmup",
             note="最干净的二维表：`dp[i][j] = dp[i-1][j] + dp[i][j-1]`。"
                  "先用它把「多开一圈边界」的习惯建立起来，后面的题都省事。"),
        dict(num=1143, tier="standard",
             note="模板 A 原题。它是 72、583、1092 的共同母题——"
                  "把这张表画明白，剩下几道只是换转移。"),
        dict(num=416, tier="standard",
             note="模板 B 原题。转化是第一步：分成两个和相等的子集 ⇔ 能否凑出 `sum / 2`。"
                  "和为奇数直接返回 False，省一次 DP。"),
        dict(num=494, tier="standard",
             note="加减号转子集和：设正号组的和为 P，则 `P - (sum - P) = target`，"
                  "即 `P = (sum + target) / 2`。奇偶性不对或超界直接返回 0——"
                  "这两个判断漏掉就会数组越界。"),
        dict(num=309, tier="variant",
             note="状态机 DP：`hold`（持有）/ `sold`（今天刚卖）/ `rest`（空仓且非冷冻）。"
                  "画出三个状态之间的箭头再写代码，比硬推转移方程快得多。"),
        dict(num=72, tier="variant", star=True,
             note="⭐认脸。三种操作对应三个来向：删（上）、插（左）、换（对角）。"
                  "说得出这句就够。"),
    ],

    pitfalls=[
        ("背包遍历方向记反",
         "01 背包一维版容量必须**倒序**。写成正序，`[1, 5, 11, 5]` 会因为 5 被重复使用而误判。"
         "完全背包（零钱兑换）反过来正是要正序。"),
        ("循环顺序决定组合还是排列",
         "外层物品、内层容量 = **组合数**（518）；外层容量、内层物品 = **排列数**（377）。"
         "两者的代码只差一次缩进，答案完全不同。"),
        ("边界行列没初始化",
         "编辑距离的第 0 行是「全插入」、第 0 列是「全删除」，不能都填 0。"
         "多开一圈的意义就在于把边界写进表里，而不是在循环里写 `if i == 0`。"),
        ("494 忘了奇偶与越界判断",
         "`(sum + target)` 为奇数、或 `|target| > sum` 时无解。"
         "少了这两句会得到负的容量或错误答案。"),
        ("空间压缩压过头",
         "模板 A 也能压成一维（滚动一行），但得小心 `dp[i-1][j-1]` 被覆盖，"
         "需要一个临时变量存左上角。面试里先写二维，被追问再说压缩方案。"),
    ],

    quiz=[
        dict(num=64, pattern=17, options=[17, 16, 10],
             prompt="在一个数字网格里从左上走到右下，每次只能向右或向下，求路径数字和的最小值。",
             why="二维 DP（模板 A）。`dp[i][j] = grid[i][j] + min(上, 左)`，"
                 "和 62 是同一张表换了转移。看到「网格 + 只能右/下」就是二维 DP，"
                 "不是图搜索——方向受限意味着没有环，不需要 `visited`。"),
        dict(num=1049, pattern=17, options=[17, 8, 15],
             prompt="一堆石头两两相撞，剩下差值继续撞，求最后可能剩下的最小重量。",
             why="01 背包（模板 B）。把石头分成两堆、让两堆重量尽量接近 —— "
                 "即在 `sum/2` 容量内能凑出的最大重量，答案是 `sum - 2 * best`。"
                 "对比 1046（每次取最重的两块）才是堆：那道题按固定规则模拟，这道题要你自己分组。"),
        dict(num=139, pattern=16, options=[17, 16, 9],
             prompt="给一个字符串和一个词典，判断字符串能否拆成若干个词典里的单词。",
             why="**一维 DP，不是本章**——虽然出现了「字符串 + 词典」两样东西，"
                 "但状态只需要一个下标：`dp[t]` = 前 t 个字符能否拆完。"
                 "词典是候选集合不是第二个序列，凑不出第二个维度。见第 16 章。"),
    ],
)
