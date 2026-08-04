# -*- coding: utf-8 -*-
"""第 02 章 · 双指针。"""

TPL_A = '''\
def two_sum_sorted(nums, target):
    l, r = 0, len(nums) - 1                 # 【骨架】两端起步
    while l < r:                            # 【骨架】相遇即结束
        cur = nums[l] + nums[r]             # 【插槽】当前候选的度量:和 / 面积 / 是否相等
        if cur == target:                   # 【插槽】命中条件
            return [l, r]                   # 【插槽】答案形式
        if cur < target:                    # 【插槽】谁动:小了就让左边变大
            l += 1                          # 【骨架】
        else:
            r -= 1                          # 【骨架】
    return []
'''

TPL_A_TESTS = '''\
assert two_sum_sorted([2, 7, 11, 15], 9) == [0, 1]
assert two_sum_sorted([1, 2, 3, 4, 6], 10) == [3, 4]
assert two_sum_sorted([1, 2], 4) == []
assert two_sum_sorted([], 0) == []


# 15 3Sum:排序 + 固定一个 + 相向双指针,难点全在去重
def three_sum(nums):
    nums.sort()
    res, n = [], len(nums)
    for i in range(n - 2):
        if i and nums[i] == nums[i - 1]:    # 固定位去重
            continue
        if nums[i] > 0:
            break
        l, r = i + 1, n - 1
        while l < r:
            s = nums[i] + nums[l] + nums[r]
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                res.append([nums[i], nums[l], nums[r]])
                l += 1
                while l < r and nums[l] == nums[l - 1]:   # 命中后左指针去重
                    l += 1
                r -= 1
    return res


assert three_sum([-1, 0, 1, 2, -1, -4]) == [[-1, -1, 2], [-1, 0, 1]]
assert three_sum([0, 0, 0, 0]) == [[0, 0, 0]]
assert three_sum([1, 2, 3]) == []


# 11 Container With Most Water:度量换成面积,移动规则换成"短板先动"
def max_area(height):
    l, r, best = 0, len(height) - 1, 0
    while l < r:
        best = max(best, (r - l) * min(height[l], height[r]))
        if height[l] < height[r]:
            l += 1
        else:
            r -= 1
    return best


assert max_area([1, 8, 6, 2, 5, 4, 8, 3, 7]) == 49
assert max_area([1, 1]) == 1
'''

TPL_B = '''\
def remove_val(nums, val):
    slow = 0                                # 【骨架】slow = 下一个要写入的位置
    for fast in range(len(nums)):           # 【骨架】fast 负责看,slow 负责写
        if nums[fast] != val:               # 【插槽】保留条件:去重 / 非零 / 满足谓词
            nums[slow] = nums[fast]         # 【骨架】
            slow += 1                       # 【骨架】
    return slow                             # 【插槽】答案:新长度 / 就地改好的数组
'''

TPL_B_TESTS = '''\
a = [3, 2, 2, 3]
assert remove_val(a, 3) == 2 and a[:2] == [2, 2]
b = [0, 1, 2, 2, 3, 0, 4, 2]
assert remove_val(b, 2) == 5 and b[:5] == [0, 1, 3, 0, 4]
assert remove_val([], 1) == 0
'''

CHAPTER = dict(
    no=2,
    freq="极高",

    mental_model="**双指针的前提是「移动一步能一次排除掉一整批候选」——有序给了相向指针这个权力，"
                 "速度差给了快慢指针这个权力。**",
    mental_model_body=[
        "相向双指针为什么对：数组有序时，`nums[l] + nums[r]` 太小，那么 `nums[l]` 配右边任何数都太小，"
        "**这一整行候选一次性作废**，`l` 才敢往前走。任何相向双指针题，你都应该能说出这句"
        "「作废了谁」——说不出来就是在碰运气。",
        "同向快慢指针是另一件事：一个负责看、一个负责写（原地覆盖），或者一个走两步、一个走一步"
        "（找中点、判环）。它不要求有序，要求的是**两个指针的相对关系本身就是答案**。",
    ],

    signals=[
        ("「已排序数组」+ 找一对 / 三个数满足条件", "相向双指针（模板 A）"),
        ("「回文 / 对称 / 首尾比较」", "相向双指针（模板 A）"),
        ("「容器 / 面积 / 两根柱子」", "相向 + 短板先动（模板 A 的度量换成面积）"),
        ("「原地去重 / 移除元素 / 把某类挪到前面」", "同向快慢（模板 B）"),
        ("「3Sum / 4Sum / 最接近的三数之和」", "排序 + 固定 k−2 个 + 相向"),
        ("链表「找中点 / 判环 / 倒数第 n 个」", "快慢指针，模板在第 06 章"),
    ],
    routing="「两数之和」在**无序**数组上是哈希（第 01 章），排序后才轮到双指针——"
            "如果题目没给有序、也不允许排序（要原下标），就别硬套。"
            "「连续子数组满足某条件」左右指针都从左端出发、且窗口内状态要维护，那是滑动窗口"
            "（第 03 章），不是相向双指针。",

    templates=[
        dict(name="模板 A · 相向双指针", note="覆盖 167 / 15 / 11 / 125",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**两端起步、小了动左、大了动右**。"
                  "换题时只改三个插槽：度量是什么、命中条件是什么、谁该动。"),
        dict(name="模板 B · 同向快慢", note="原地覆盖类",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="记住分工：**fast 负责看，slow 负责写**。"
                  "返回值是新长度，`nums[slow:]` 之后的内容按题目要求可以是任何值。"),
    ],

    problems=[
        dict(num=125, tier="warmup",
             note="相向双指针的最小形态。真正的坑在预处理：`isalnum()` 过滤 + `lower()`，"
                  "别先拼出一个干净字符串再比较——面试官想看的是 O(1) 空间。"),
        dict(num=167, tier="standard",
             note="模板 A 原题（注意题目返回的是 1-indexed）。"
                  "被问「为什么不用哈希」时答：数组有序，双指针 O(1) 空间且不需要额外查表。"),
        dict(num=15, tier="standard",
             note="排序 + 固定第一个数 + 相向。**去重是全题唯一难点**，见翻车点①；"
                  "`nums[i] > 0` 时提前 break 是常见加分点。"),
        dict(num=11, tier="standard",
             note="度量从「和」换成「面积」。核心是证明「移动短板」不会漏掉答案："
                  "移动长板，宽必减、高不可能超过原短板，面积一定不增——说出这句就过关了。"),
        dict(num=42, tier="variant", star=True,
             note="⭐认脸。一句话：每格存水 = 左右最大值中较小者 − 自身高度。"
                  "说得出这句，再指一下单调栈解法（第 04 章）就够。"),
    ],

    pitfalls=[
        ("3Sum 的三处去重",
         "固定位 `if i and nums[i] == nums[i-1]: continue`；命中后左指针跳过重复；右指针同理。"
         "只写一处就会出现重复三元组——这是 3Sum 最常见的 WA。"),
        ("`while l < r` 还是 `l <= r`",
         "要一对**不同**元素用 `<`；在有序数组上二分式地找单个位置才可能用 `<=`。"
         "回文判断用 `<` 即可，中间那个字符不需要和自己比。"),
        ("排序破坏原下标",
         "题目要返回**原始下标**时（如第 01 章的 1 Two Sum）不能排序，只能哈希。"
         "3Sum 之所以能排序，是因为它要的是值不是下标。"),
        ("短板先动写反",
         "11 题里必须移动**较短**的那根。写成移动较长的，样例 `[1,8,6,2,5,4,8,3,7]` 会给出 8 而不是 49。"),
    ],

    quiz=[
        dict(num=977, pattern=2, options=[2, 1, 3],
             prompt="给一个**已排序**（含负数）的数组，返回每个数平方后的有序数组。",
             why="双指针。平方后最大值只可能出现在两端，所以从两端向中间收、**从后往前填结果**。"
                 "看到「已排序」+「结果也要有序」就该想到相向指针，而不是排序后再排一次。"),
        dict(num=26, pattern=2, options=[2, 1, 4],
             prompt="在已排序数组上原地去重，返回去重后的长度。",
             why="双指针（模板 B）。保留条件从 `!= val` 换成 `!= nums[slow-1]`，骨架一行没变。"
                 "用 `set` 也能去重，但破坏顺序、且不是原地。"),
        dict(num=209, pattern=3, hide_num=True, options=[2, 3, 13],
             prompt="给定正整数数组和 target，求和 ≥ target 的**最短连续子数组**长度。",
             why="**滑动窗口，不是本章**——两个指针都从左端出发、右扩左缩，窗口内要维护「当前和」这个状态。"
                 "相向双指针从两端起步、不维护状态，是完全不同的两件事。见第 03 章。"),
    ],
)
