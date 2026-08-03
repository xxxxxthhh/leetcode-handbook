# -*- coding: utf-8 -*-
"""第 05 章 · 二分查找。"""

TPL_A = '''\
def lower_bound(nums, target):
    lo, hi = 0, len(nums)                   # 【骨架】左闭右开,hi 取"越界位置"
    while lo < hi:                          # 【骨架】区间空了就停
        mid = (lo + hi) // 2                # 【骨架】
        if nums[mid] < target:              # 【插槽】判定:成立说明 mid 太靠左
            lo = mid + 1                    # 【骨架】mid 已被排除
        else:
            hi = mid                        # 【骨架】mid 可能就是答案,不能排除
    return lo                               # 【插槽】答案:第一个满足条件的下标
'''

TPL_A_TESTS = '''\
assert lower_bound([1, 3, 5, 6], 5) == 2
assert lower_bound([1, 3, 5, 6], 2) == 1
assert lower_bound([1, 3, 5, 6], 7) == 4    # 全都不满足 -> 落在越界位置
assert lower_bound([], 1) == 0


# 704 Binary Search:在 lower_bound 之上补一次"到底有没有"
def search(nums, target):
    i = lower_bound(nums, target)
    return i if i < len(nums) and nums[i] == target else -1


assert search([-1, 0, 3, 5, 9, 12], 9) == 4
assert search([-1, 0, 3, 5, 9, 12], 2) == -1


# 153 Find Minimum in Rotated Sorted Array:判定换成"和右端比"
def find_min(nums):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] > nums[hi]:            # 最小值一定在右半
            lo = mid + 1
        else:
            hi = mid
    return nums[lo]


assert find_min([3, 4, 5, 1, 2]) == 1
assert find_min([4, 5, 6, 7, 0, 1, 2]) == 0
assert find_min([11, 13, 15, 17]) == 11
'''

TPL_B = '''\
def min_feasible(lo, hi, ok):
    while lo < hi:                          # 【骨架】二分的是"答案区间",不是数组
        mid = (lo + hi) // 2                # 【骨架】
        if ok(mid):                         # 【插槽】判定函数:mid 这个答案够用吗
            hi = mid                        # 【骨架】够用,试试更小的
        else:
            lo = mid + 1                    # 【骨架】不够用,答案必须更大
    return lo                               # 【插槽】最小的可行答案
'''

TPL_B_TESTS = '''\
# 875 Koko Eating Bananas:答案区间是速度 1..max(piles),判定是"h 小时内吃得完吗"
def min_eating_speed(piles, h):
    return min_feasible(1, max(piles),
                        lambda k: sum(-(-p // k) for p in piles) <= h)


assert min_eating_speed([3, 6, 7, 11], 8) == 4
assert min_eating_speed([30, 11, 23, 4, 20], 5) == 30
assert min_eating_speed([30, 11, 23, 4, 20], 6) == 23


# 410 Split Array Largest Sum:答案区间是 max(nums)..sum(nums),判定是"能否切成 <= m 段"
def split_array(nums, m):
    def ok(cap):
        parts, cur = 1, 0
        for x in nums:
            if cur + x > cap:
                parts, cur = parts + 1, x
            else:
                cur += x
        return parts <= m
    return min_feasible(max(nums), sum(nums), ok)


assert split_array([7, 2, 5, 10, 8], 2) == 18
assert split_array([1, 2, 3, 4, 5], 2) == 9
assert split_array([1, 4, 4], 3) == 4
'''

CHAPTER = dict(
    no=5,
    freq="极高",

    mental_model="**二分不是在数组里找数，是在一串「前面全 False、后面全 True」的判定结果上找那道分界线。"
                 "数组有序，只是这条性质最常见的来源。**",
    mental_model_body=[
        "所以写二分前先把问题翻译成一个**布尔判定函数** `ok(x)`，再确认它单调："
        "一旦某个 x 成立，比它大的全都成立。翻译不出这个函数，就说明这题不是二分。",
        "想通这一层，「答案二分」就不再是新技巧：数组二分的 `ok(i)` 是 `nums[i] >= target`，"
        "答案二分的 `ok(k)` 是「速度 k 够不够快」——判定函数换了，骨架一模一样。",
    ],

    signals=[
        ("「已排序数组里找目标 / 插入位置 / 第一个大于 X 的」", "边界二分（模板 A）"),
        ("「旋转有序数组」", "二分 + 先判断哪半是有序的"),
        ("「最小的最大值」「最大的最小值」「最少需要多少天 / 多快」", "答案二分（模板 B）"),
        ("「能否在 X 之内完成」这种问句本身", "它就是判定函数 `ok(X)`"),
        ("数据规模到 10⁹ 但答案是个整数", "在答案区间上二分，log 级别的判定次数"),
        ("「两个有序数组的中位数 / 第 K 小」", "二分划分位置（认脸级）"),
    ],
    routing="有序数组里找**一对**数是双指针（第 02 章），找**一个**位置才是二分。"
            "「第 K 大」如果数组无序、且没有可二分的判定量，那是堆或快速选择（第 08 章）；"
            "但「第 K 小的距离 / 第 K 小的乘积」这类**答案本身是数值**的题，反而回到答案二分；"
            "而「BST 里的第 K 小」根本不用二分，中序遍历走到第 K 个就是（第 07 章）。"
            "顺带把「有序」这个词的三种含义分清："
            "有序**数组**找位置 → 本章；有序**链表**合并 → 哨兵 + 双指针（第 06 章）；"
            "**BST** 的中序天然有序 → 第 07 章。判断标准始终是同一个：能不能写出单调的 `ok(x)`。",
    routing_to=[2, 6, 7, 8],

    templates=[
        dict(name="模板 A · 边界二分", note="lower_bound 一个顶三个",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**左闭右开、`lo = mid + 1` / `hi = mid`、返回 `lo`**。"
                  "只要判定函数单调，这个骨架不会死循环，因为每轮区间必然缩小。"),
        dict(name="模板 B · 答案二分", note="判定函数才是题目本身",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="把 `ok` 写成独立函数，面试时先讲 `ok` 再讲二分——"
                  "面试官要听的是**你为什么确信它单调**。"),
    ],

    problems=[
        dict(num=704, tier="warmup",
             note="标准二分。建议直接用模板 A 的写法而不是 `lo <= hi` 那一套，"
                  "全书统一一个边界约定，考场上少一个出错来源。"),
        dict(num=74, tier="standard",
             note="把 m×n 矩阵当成长度 m·n 的有序数组，下标映射 `divmod(mid, n)`。"
                  "识别信号是「每行有序且下一行首元素大于上一行末元素」。"),
        dict(num=153, tier="standard",
             note="判定换成「`nums[mid]` 和右端比」。为什么和右端比而不是左端："
                  "旋转之后右端点一定落在「较小的那一段」里，比较结果才单调；"
                  "没有旋转时右端就是最大值，条件恒不成立，`hi` 一路收到 0，答案照样对。"),
        dict(num=33, tier="standard",
             note="153 的进阶：先判断哪半有序，再看 target 在不在那半的区间里。"
                  "写不顺时的降级方案：先用 153 找到旋转点，再对两段各做一次标准二分。"),
        dict(num=875, tier="variant",
             note="答案二分入门题。`ok(k) = 以速度 k 吃完所需小时数 <= h`，区间 `[1, max(piles)]`。"
                  "向上取整用 `-(-p // k)`，别用浮点。"),
        dict(num=410, tier="variant", star=True,
             note="⭐认脸。`ok(cap) = 按 cap 贪心切分后段数 <= m`，区间 `[max(nums), sum(nums)]`。"
                  "认出「最小化最大值」这五个字即可。"),
        dict(num=4, tier="variant", star=True,
             note="⭐认脸。二分较短的那个数组的**划分位置**。面试遇到先说 O(m+n) 归并解法。"),
    ],

    pitfalls=[
        ("开闭区间不统一",
         "`hi = len(nums)`（右开）配 `hi = mid`；`hi = len(nums) - 1`（右闭）配 `hi = mid - 1`。"
         "混着写是死循环和差一错误的头号来源。全书统一用左闭右开。"),
        ("判定函数不单调",
         "答案二分的前提是「x 可行则 x+1 也可行」。写不出这句话就别二分——"
         "例如「恰好等于 K」这类非单调条件，二分给出的结果没有意义。"),
        ("`ok` 的方向反了",
         "求**最小可行**时 `ok` 成立要 `hi = mid`；求**最大可行**时要把判定取反或改成 "
         "`lo = mid`（此时 `mid` 必须上取整，否则死循环）。拿不准就一律转化成「求最小」。"),
        ("旋转数组有重复元素",
         "`[1,1,1,0,1]` 这种输入下 `nums[mid] == nums[hi]` 无法判断哪半有序，"
         "只能 `hi -= 1` 退化到 O(n)。面试被追问时要说得出这个边界。"),
    ],

    quiz=[
        dict(num=1011, pattern=5, options=[5, 15, 3],
             prompt="传送带每天最多装 cap 重量，货物必须按顺序装运，求 D 天内运完的最小 cap。",
             why="答案二分（模板 B）。「最小的最大装载量」+「能否在 D 天内完成」——"
                 "判定函数直接写在题面里了。区间是 `[max(weights), sum(weights)]`，和 410 是同一道题。"),
        dict(num=162, pattern=5, options=[5, 2, 4],
             prompt="数组中相邻元素不相等，返回任意一个「比左右邻居都大」的位置。",
             why="二分。数组**没有排序**也能二分：`nums[mid] < nums[mid+1]` 说明右边一定存在峰值，"
                 "这个判定是单调的。它是「有序才能二分」这个误解的最好解药。"),
        dict(num=215, pattern=8, hide_num=True, options=[5, 8, 1],
             prompt="在一个**无序**数组里找第 K 大的元素。",
             why="**堆 / 快速选择，不是本章**——数组无序，也写不出关于下标的单调判定函数。"
                 "养一个大小为 K 的小顶堆即可，见第 08 章。"
                 "对照 162：能不能二分，看的是有没有单调判定，不是看数组长什么样。"),
    ],
)
