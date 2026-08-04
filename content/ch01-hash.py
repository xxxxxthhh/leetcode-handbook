# -*- coding: utf-8 -*-
"""第 01 章 · 哈希。"""

TPL_A = '''\
def two_sum(nums, target):
    seen = {}                               # 【骨架】值 -> 下标,记录"我来过"
    for i, x in enumerate(nums):            # 【骨架】
        need = target - x                   # 【插槽】"另一半"怎么算
        if need in seen:                    # 【骨架】先查后存,否则会拿自己配自己
            return [seen[need], i]          # 【插槽】答案形式:下标对 / 计数 / True
        seen[x] = i                         # 【骨架】
    return []
'''

TPL_A_TESTS = '''\
assert two_sum([2, 7, 11, 15], 9) == [0, 1]
assert two_sum([3, 2, 4], 6) == [1, 2]
assert two_sum([3, 3], 6) == [0, 1]        # 重复值:先查后存才不会返回 [0, 0]
assert two_sum([1], 2) == []
'''

TPL_B = '''\
from collections import defaultdict

def group_by_signature(words):
    buckets = defaultdict(list)             # 【骨架】签名 -> 同组成员
    for w in words:                         # 【骨架】
        key = tuple(sorted(w))              # 【插槽】签名怎么算:排序 / 计数向量 / 归一化
        buckets[key].append(w)              # 【骨架】
    return list(buckets.values())           # 【插槽】要分组本身 / 组数 / 最大的那组
'''

TPL_B_TESTS = '''\
got = sorted(sorted(g) for g in group_by_signature(
    ["eat", "tea", "tan", "ate", "nat", "bat"]))
assert got == [["ate", "eat", "tea"], ["bat"], ["nat", "tan"]]
assert group_by_signature([]) == []
assert group_by_signature(["a", "a"]) == [["a", "a"]]
'''

CHAPTER = dict(
    no=1,
    freq="极高",

    mental_model="**哈希表就一句话：花 O(n) 的空间，把「我见过你吗」变成 O(1) 的回答。**",
    mental_model_body=[
        "写题时你真正在做的动作只有三种：**见过没有**（`set`）、**见过几次**（`Counter`）、"
        "**见过的东西挂在哪**（`dict` → 下标 / 列表）。先想清楚要问哪一种，代码几乎是自动的。",
        "它的典型用法是把一层循环换成一次查表：暴力解里那个「回头去前面找有没有某个数」的内层循环，"
        "就是哈希表的入口。代价是内存，以及**顺序信息全丢了**——需要顺序的题（第 K 大、区间和）得另找工具。",
    ],

    signals=[
        ("「是否存在 / 有没有重复 / 出现过吗」", "`set`"),
        ("「出现次数 / 频率 / 众数 / anagram」", "`Counter`"),
        ("「两数之和 / 配对 / 补数」且数组**无序**", "`dict` 存「我需要的另一半」（模板 A）"),
        ("「分组 / 归类 / 把同类放一起」", "`dict[签名] → list`（模板 B）"),
        ("题目要求 O(n)，而你的暴力解是两层循环在「回头找」", "哈希把内层循环换成一次查表"),
        ("「最长连续序列」但**不要求元素相邻**", "`set` + 只从序列起点向右扩"),
    ],
    routing="同样是「两数之和」，数组**无序**才用哈希；**已排序**就该用双指针（第 02 章），"
            "省掉 O(n) 空间。「子数组和恰好为 K」表面像哈希，实际主语是前缀和（第 13 章），"
            "哈希只是配件。「频率最高的 K 个」先用 Counter 数完，选 K 个的动作属于堆（第 08 章）。",

    templates=[
        dict(name="模板 A · 配对", note="边走边问「另一半来过吗」",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**先查后存**。顺序反了，`[3,3]` 这种用例会拿自己配自己。"),
        dict(name="模板 B · 分组", note="给每个元素算一个签名",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="全部难度都在**签名怎么设计**：字母排序、26 维计数向量、"
                  "行列宫编号……骨架一个字都不用改。"),
    ],

    problems=[
        dict(num=1, tier="warmup",
             note="模板 A 原题。面试里它的价值不在题本身，而在你能否一口说出「为什么先查后存」。"),
        dict(num=217, tier="warmup",
             note="`set` 的最小用法。顺手记住变体：`len(set(nums)) < len(nums)` 一行解决。"),
        dict(num=242, tier="standard",
             note="`Counter(s) == Counter(t)`。面试官常追问排序解法 O(n log n) 与计数解法 O(n) 的取舍，"
                  "以及 Unicode 字符集下 26 长度数组会失效。"),
        dict(num=49, tier="standard",
             note="模板 B 原题。签名用 `tuple(sorted(w))` 或 26 维计数元组——"
                  "后者 O(n·k)，前者 O(n·k log k)，说得出这个差别就够了。"),
        dict(num=128, tier="standard",
             note="全章最值得琢磨的一道：把数组塞进 `set`，**只从「左边没有邻居」的数开始向右扩**。"
                  "这一条剪枝把 O(n²) 压回 O(n)，见翻车点④。"),
        dict(num=36, tier="variant",
             note="签名思维的另一面：一个格子同时属于行、列、宫三个 `set`，"
                  "用 `(i // 3, j // 3)` 当宫的键。骨架不变，键变了。"),
    ],

    pitfalls=[
        ("先查后存的顺序",
         "模板 A 里 `if need in seen` 必须在 `seen[x] = i` 之前。反过来写，`[3,3]` target=6 会返回 `[0,0]`。"),
        ("存值还是存下标",
         "题目要下标就存下标，要判断存在用 `set` 就够。别默认写 `dict`——`set` 的意图更清楚，"
         "读代码的人一眼知道你不关心位置。"),
        ("`Counter` 的删空问题",
         "滑动窗口里用 `Counter` 当窗口状态时，减到 0 的键**不会自动消失**，"
         "`len(cnt)` 会把它算进去。要么 `del`，要么另外维护一个「不同字符数」。"
         "（`==` 比较是个例外：Python 3.10 起它会忽略零计数，细节见第 03 章翻车点④。）"),
        ("128 从每个数往两边扩",
         "对每个数都向左右扩展是 O(n²)（退化用例：`[1,2,3,...,n]`）。"
         "正确写法是先判断 `x - 1 not in s`，只有序列起点才进入扩展循环。"),
        ("不可哈希的键",
         "`list` 不能当键，`tuple` 可以；`dict` 不能，`frozenset` 可以。分组题里签名一律用元组。"),
    ],

    quiz=[
        dict(num=383, pattern=1, options=[1, 3, 15],
             prompt="判断能否用杂志上的字母拼出勒索信（每个字母只能用一次）。",
             why="哈希。「每个字母只能用一次」= 计数比较，`Counter(note) <= Counter(magazine)`。"
                 "看到「次数够不够」就是 Counter，不是滑窗——它根本不要求连续。"),
        dict(num=219, pattern=1, options=[1, 2, 13],
             prompt="判断数组中是否存在两个相同的数，且它们的下标之差不超过 k。",
             why="哈希。存「值 → 最近一次出现的下标」，边走边比较距离，一次遍历。"
                 "题面里的 k 是个障眼法：要问的是「见过吗」，"
                 "不是「区间和」也不是「有序数组里的一对」。"),
        dict(num=88, pattern=2, hide_num=True, options=[1, 2, 13],
             prompt="给两个**已排序**的数组，把第二个合并进第一个（原地，第一个数组尾部有足够空位）。",
             why="**双指针，不是本章**——数组已排序，用哈希既浪费空间又丢掉顺序这个最有价值的条件。"
                 "见 §2 分流条件：有序是双指针的入场券（第 02 章）。"),
    ],
)
