# -*- coding: utf-8 -*-
"""第 15 章 · 贪心。"""

TPL_A = '''\
def max_subarray(nums):
    best = cur = nums[0]                    # 【骨架】cur = 以当前元素结尾的最优值
    for x in nums[1:]:                      # 【骨架】
        cur = max(x, cur + x)               # 【插槽】决策:另起炉灶,还是接着上一段
        best = max(best, cur)               # 【插槽】答案:全局最优 / 最后一项 / 计数
    return best
'''

TPL_A_TESTS = '''\
assert max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]) == 6
assert max_subarray([1]) == 1
assert max_subarray([5, 4, -1, 7, 8]) == 23
assert max_subarray([-3, -1, -2]) == -1     # 全负:必须允许"只取一个"


# 55 Jump Game:维护的量换成"目前能到的最远位置"
def can_jump(nums):
    reach = 0
    for i, x in enumerate(nums):
        if i > reach:                       # 还没走到就已经够不着了
            return False
        reach = max(reach, i + x)
    return True


assert can_jump([2, 3, 1, 1, 4]) is True
assert can_jump([3, 2, 1, 0, 4]) is False
assert can_jump([0]) is True


# 134 Gas Station:总量决定有没有解,局部失败点决定从哪起步
def can_complete_circuit(gas, cost):
    if sum(gas) < sum(cost):
        return -1
    start = tank = 0
    for i in range(len(gas)):
        tank += gas[i] - cost[i]
        if tank < 0:                        # 从 start 出发撑不到 i+1,那么 start..i 都不行
            start, tank = i + 1, 0
    return start


assert can_complete_circuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2]) == 3
assert can_complete_circuit([2, 3, 4], [3, 4, 3]) == -1
'''

TPL_B = '''\
def partition_labels(s):
    last = {c: i for i, c in enumerate(s)}  # 【插槽】贪心依据:每个元素最后出现在哪
    out, start, end = [], 0, 0
    for i, c in enumerate(s):               # 【骨架】
        end = max(end, last[c])             # 【骨架】当前段被迫延伸到这里
        if i == end:                        # 【骨架】走到边界了,收一段
            out.append(end - start + 1)     # 【插槽】答案:段长 / 段数 / 段的内容
            start = i + 1                   # 【骨架】
    return out
'''

TPL_B_TESTS = '''\
assert partition_labels("ababcbacadefegdehijhklij") == [9, 7, 8]
assert partition_labels("eccbbbbdec") == [10]
assert partition_labels("a") == [1]


# 846 Hand of Straights:排序 + Counter 依次消费,每次从当前最小的牌起手
def is_n_straight_hand(hand, group_size):
    from collections import Counter
    if len(hand) % group_size:
        return False
    cnt = Counter(hand)
    for x in sorted(cnt):
        c = cnt[x]
        if c <= 0:
            continue
        for v in range(x, x + group_size):
            if cnt[v] < c:
                return False
            cnt[v] -= c
    return True


assert is_n_straight_hand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3) is True
assert is_n_straight_hand([1, 2, 3, 4, 5], 4) is False
'''

CHAPTER = dict(
    no=15,
    freq="高",

    mental_model="**能贪的题都有一条「局部最优不会毁掉全局最优」的性质。"
                 "先把这句话说出来，再动手——说不出来，八成该用 DP。**",
    mental_model_body=[
        "贪心的代码短得可疑：通常就是一个循环加一两个变量。难度全在**为什么对**。"
        "面试里的标准动作是三步：说出贪心性质 → 自己举一个反例试着推翻它 → 再写代码。"
        "跳过前两步直接写，写对了也说不清，写错了更找不到原因。",
        "本章第一题 53 Maximum Subarray 恰好站在贪心和 DP 的边界上："
        "`cur = max(x, cur + x)` 既能读成「要不要另起炉灶」的贪心决策，"
        "也能读成 `dp[i] = max(nums[i], dp[i-1] + nums[i])` 的状态转移。"
        "两种说法在面试里都对，能同时说出来最好。",
    ],

    signals=[
        ("「能否到达 / 最少几步到达」且每一步的选择不影响后面的结构", "维护「目前能到的最远」"),
        ("「加油站能否绕一圈」「从哪个位置出发」", "总量判可行 + 局部失败点跳过"),
        ("「划分标签 / 最少分成几段」", "先记每个元素最后出现的位置（模板 B）"),
        ("「按顺序发牌 / 分成若干连续组」", "排序 + `Counter` 依次消费"),
        ("「最大子数组和」", "Kadane：另起炉灶还是接着上一段（模板 A）"),
        ("题面在问「最优值」而你能一句话说清每步该选谁", "先试贪心，说不清就退回 DP"),
    ],
    routing="**需要回头改之前的选择**，就不是贪心而是 DP（第 16、17 章）："
            "零钱兑换（322）用面额从大到小贪心在 `coins=[1,3,4], amount=6` 上就是错的。"
            "要列出**全部方案**是回溯（第 09 章）。"
            "以区间为对象的贪心（435、452）识别信号来自「区间」这个形状，模板放在第 14 章。"
            "另外记住「连续子数组」的三岔口：求**最大和** → 本章的 Kadane；"
            "求**满足某约束的最长 / 最短** → 滑动窗口（第 03 章）；"
            "求**和恰好为 K 的个数** → 前缀和 + 哈希（第 13 章）。",

    templates=[
        dict(name="模板 A · 一路维护一个量", note="Kadane / 可达最远",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**一个 `cur` 一个 `best`，每步只问一句该不该重来**。"
                  "55、45、134 都是它换了个维护量。"),
        dict(name="模板 B · 先扫一遍再分段", note="划分 / 分组类",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="这类题的共性：**先用一次遍历拿到贪心依据**（最后出现位置、频次），"
                  "第二次遍历才做决策。一遍就想贪完通常会漏。"),
    ],

    problems=[
        dict(num=53, tier="warmup",
             note="Kadane。它同时是本章的入口和第 16 章的预告，见 §1 第二段。"
                  "全负数组是必检边界：`cur` 初值要用 `nums[0]` 而不是 0。"),
        dict(num=55, tier="standard",
             note="维护 `reach`（能到的最远下标），一旦 `i > reach` 就失败。"
                  "贪心性质：能到 i 就能到 i 之前的所有位置，所以只需要记最远的那个。"),
        dict(num=45, tier="standard",
             note="求最少步数：把「当前这一跳能覆盖的范围」当成一层，走到层边界就步数 +1。"
                  "本质是 BFS 分层的贪心写法，别和 55 的骨架混着写。"),
        dict(num=134, tier="standard",
             note="两个独立结论：总油量 < 总消耗则无解；从 start 出发在 i 处失败，"
                  "则 `start..i` 中任何一个都不能作为起点，直接跳到 `i + 1`。"
                  "两句话说清就等于做完了。"),
        dict(num=763, tier="variant",
             note="模板 B 原题。先记 `last[c]`，再扫一遍在 `i == end` 处切分。"
                  "「每个字母只能出现在一段里」这个约束直接翻译成了 `end = max(end, last[c])`。"),
        dict(num=846, tier="variant",
             note="排序后从最小的牌起手，每次必须凑满 `groupSize` 张连续的。"
                  "用 `Counter` 而不是在列表里删元素——后者是 O(n²)。"),
    ],

    pitfalls=[
        ("不证明就贪",
         "先说清「为什么局部最优不会毁掉全局」。说不出来时，把它当 DP 写，"
         "复杂度差一点但不会错。面试官问「你怎么知道这样贪是对的」时答不上来，比写慢更致命。"),
        ("Kadane 的初值",
         "`best = cur = 0` 在全负数组上会返回 0（相当于允许空子数组）。"
         "题目要求非空时必须用 `nums[0]` 起手。"),
        ("55 和 45 混用骨架",
         "「能否到达」维护一个 `reach` 就够；「最少几步」必须分层，"
         "用 `curEnd` / `farthest` 两个变量。把 45 写成 55 的样子会得到步数偏小的错误答案。"),
        ("134 只判总量",
         "总量够只说明**有解**，不告诉你从哪起步。两个结论要一起用。"),
        ("对「找零钱」类问题贪心",
         "只有在面额构成特定体系（如 1/5/10/25）时贪心才对。"
         "LeetCode 的 322 面额是任意的，必须 DP——见 §2 分流条件。"),
    ],

    quiz=[
        dict(num=455, pattern=15, options=[15, 8, 2],
             prompt="每个孩子有胃口值、每块饼干有尺寸，一块饼干最多给一个孩子，求最多能满足几个孩子。",
             why="贪心。两边都排序，用最小的饼干去满足最小的胃口。"
                 "贪心性质：把大饼干留给胃口大的孩子不会更差——这句话就是证明。"),
        dict(num=122, pattern=15, options=[15, 16, 3],
             prompt="股票可以当天买卖、交易次数不限，求最大利润。",
             why="贪心。把所有上涨段的差值加起来即可（`max(0, p[i] - p[i-1])` 求和）。"
                 "对比 121（只能买卖一次）要维护历史最低价——交易次数这个约束一放开，DP 就退化成贪心。"),
        dict(num=322, pattern=16, options=[15, 16, 9],
             prompt="给定任意面额的硬币，求凑出目标金额所需的**最少硬币数**。",
             why="**一维 DP，不是本章**——面额从大到小贪心在 `coins=[1,3,4], amount=6` 上会给出 3 枚"
                 "（4+1+1），正确答案是 2 枚（3+3）。"
                 "「贪心失效」的教科书反例，也是 §2 分流条件的由来。见第 16 章。"),
    ],
)
