# -*- coding: utf-8 -*-
"""第 08 章 · 堆 / Top-K。"""

TPL_A = '''\
import heapq

def kth_largest(nums, k):
    heap = []                               # 【骨架】小顶堆,堆顶是这 K 个里最小的那个
    for x in nums:                          # 【骨架】
        heapq.heappush(heap, x)             # 【插槽】入堆的键:值 / 频次 / 距离的相反数
        if len(heap) > k:                   # 【骨架】超员就把最弱的踢出去
            heapq.heappop(heap)             # 【骨架】
    return heap[0]                          # 【插槽】答案:第 K 大 / 整个 K 集合
'''

TPL_A_TESTS = '''\
assert kth_largest([3, 2, 1, 5, 6, 4], 2) == 5
assert kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4) == 4
assert kth_largest([1], 1) == 1


# 347 Top K Frequent:键换成 (频次, 值),骨架一行没动
def top_k_frequent(nums, k):
    from collections import Counter
    heap = []
    for val, c in Counter(nums).items():
        heapq.heappush(heap, (c, val))
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted(v for _, v in heap)


assert top_k_frequent([1, 1, 1, 2, 2, 3], 2) == [1, 2]
assert top_k_frequent([1], 1) == [1]


# 973 K Closest Points:键换成"距离的相反数",于是踢掉的正好是最远的
def k_closest(points, k):
    heap = []
    for x, y in points:
        heapq.heappush(heap, (-(x * x + y * y), x, y))
        if len(heap) > k:
            heapq.heappop(heap)
    return sorted([x, y] for _, x, y in heap)


assert k_closest([[1, 3], [-2, 2]], 1) == [[-2, 2]]
assert k_closest([[3, 3], [5, -1], [-2, 4]], 2) == [[-2, 4], [3, 3]]
'''

TPL_B = '''\
import heapq

class MedianFinder:
    def __init__(self):
        self.lo = []                        # 【骨架】大顶堆(存相反数),装较小的一半
        self.hi = []                        # 【骨架】小顶堆,装较大的一半

    def add(self, x):
        heapq.heappush(self.lo, -x)                        # 【骨架】先无脑进左边
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   # 【骨架】把左边最大的让给右边
        if len(self.hi) > len(self.lo):                    # 【插槽】平衡策略:允许谁多一个
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def median(self):
        if len(self.lo) > len(self.hi):     # 【插槽】奇数个时中位数在较长的那边
            return float(-self.lo[0])
        return (-self.lo[0] + self.hi[0]) / 2
'''

TPL_B_TESTS = '''\
mf = MedianFinder()
mf.add(1)
assert mf.median() == 1.0
mf.add(2)
assert mf.median() == 1.5
mf.add(3)
assert mf.median() == 2.0
mf.add(4)
assert mf.median() == 2.5

mf2 = MedianFinder()
for v in [5, 15, 1, 3]:
    mf2.add(v)
assert mf2.median() == 4.0
'''

CHAPTER = dict(
    no=8,
    freq="高",

    mental_model="**只关心第 K 个的时候不要排序：养一个大小为 K 的堆，让不够格的自动掉出去。**",
    mental_model_body=[
        "方向最容易记反，记住这一句就够：**求第 K 大，用大小为 K 的小顶堆**。"
        "堆顶是这 K 个里最小的，也就是全局第 K 大；新来的数比堆顶大才有资格挤掉它。"
        "求第 K 小就整体取相反数，别去手写大顶堆——Python 的 `heapq` 只有小顶堆。",
        "复杂度是 O(n log K) 而不是排序的 O(n log n)。K 很小时差距巨大，"
        "而且它**天然支持数据流**：数字一个个来，你随时能回答，排序做不到这件事。",
    ],

    signals=[
        ("「第 K 大 / 第 K 小」且数组**无序**", "大小为 K 的堆（模板 A）"),
        ("「前 K 个高频 / 最接近原点的 K 个点」", "模板 A，只换入堆的键"),
        ("「数据流 / 不断插入，随时要回答」", "堆（排序做不到，因为数据没有终点）"),
        ("「合并 K 个有序链表 / 数组」", "堆里放 K 个当前头，弹一个补一个"),
        ("「动态中位数」", "对顶堆（模板 B）"),
        ("「每次取出当前最大的，处理完再放回去」", "堆（621 任务调度、1046 碰撞石头）"),
    ],
    routing="「前 K 个高频」要先用 `Counter` 数出频次（第 01 章）再用堆选 K 个——"
            "哈希负责统计，堆负责挑选，两步不要混。"
            "数组**已排序**时第 K 大就是一个下标，别掏堆；给的是 **BST** 时中序走到第 K 个即可"
            "（第 07 章）——「第 K」这三个字本身不构成用堆的理由，**无序**才是；"
            "「固定窗口内的最大值」要的是**过期淘汰**，那是单调队列（第 04 章）不是堆；"
            "「第 K 小的距离 / 乘积」这类答案是数值的，回到答案二分（第 05 章）。"
            "只要一次的第 K 大且允许平均 O(n)，快速选择（quickselect）也是标准答案。",
    routing_to=[1, 4, 5],

    templates=[
        dict(name="模板 A · 大小为 K 的堆", note="覆盖本章 80% 的题",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**入堆、超员、踢堆顶**。换题只改一件事——"
                  "**入堆的键**（值 / 频次 / 距离的相反数）。"),
        dict(name="模板 B · 对顶堆", note="仅动态中位数需要，认脸级",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="两个堆的不变式：`lo` 全体 ≤ `hi` 全体，且 `len(lo) - len(hi) ∈ {0, 1}`。"
                  "「先进左边、再让给右边、右边多了再还回来」这三步能保证不变式恒成立。"),
    ],

    problems=[
        dict(num=703, tier="warmup",
             note="模板 A 的类封装版，把「数据流」这件事具象化：构造时先灌一遍，"
                  "之后每次 `add` 都是「入堆 + 超员就踢」。"),
        dict(num=215, tier="standard",
             note="模板 A 原题。面试标准答法是先说堆 O(n log K)，再补一句"
                  "「要平均 O(n) 就用快速选择」——两个都说得出才算完整。"),
        dict(num=347, tier="standard",
             note="`Counter` + 堆的组合。`heapq.nlargest(k, cnt, key=cnt.get)` 一行也行，"
                  "但要能说出它内部就是这个堆。桶排序 O(n) 解法是加分项。"),
        dict(num=973, tier="standard",
             note="入堆的键换成距离的相反数（求最近的 K 个 = 踢掉最远的）。"
                  "别开平方，比较平方距离就够——省一次浮点运算，也避免精度问题。"),
        dict(num=621, tier="variant",
             note="堆解法是「每轮取出剩余最多的几种任务」，直观但啰嗦；"
                  "面试更爱听 `(maxCount - 1) * (n + 1) + 同频次任务数` 这个数学公式。"
                  "两种都准备，先讲公式再说堆。"),
        dict(num=295, tier="variant", star=True,
             note="⭐认脸。模板 B 原题，说清两个堆的不变式即可。"),
    ],

    pitfalls=[
        ("方向记反",
         "求第 K **大**用**小**顶堆。反过来（大顶堆存 K 个）踢掉的是最大的，答案全错。"
         "记法：堆顶是「守门员」，它守的是第 K 名这道门。"),
        ("Python 没有大顶堆",
         "一律取相反数入堆，出堆再取回来。对顶堆里 `lo` 存的是负值，"
         "`-self.lo[0]` 才是真正的最大值——这一步漏掉是 295 最常见的 bug。"),
        ("元组入堆的次级比较",
         "`(freq, val)` 里 `freq` 相同时会去比 `val`。如果 `val` 是不可比较的对象"
         "（如自定义类、字典），会直接抛 `TypeError`。塞一个序号当 tie-breaker。"),
        ("`heapify` 与逐个 push 的差别",
         "`heapq.heapify(list)` 是 O(n)，逐个 `heappush` 是 O(n log n)。"
         "已经拿到全量数据时用前者；数据流场景只能用后者。"),
        ("K 等于 n 时堆没意义",
         "K 接近 n 时 O(n log K) 已退化到 O(n log n)，直接排序更省事。"
         "面试里主动说这句，说明你知道自己在优化什么。"),
    ],

    quiz=[
        dict(num=1046, pattern=8, options=[8, 15, 4],
             prompt="每次取出最重的两块石头相撞，剩下的差值放回去，求最后剩下的重量。",
             why="堆。「每次取当前最大、处理完再放回去」是堆的标准句式。"
                 "Python 里全部取负入小顶堆即可。排序做不到——每撞一次集合就变了。"),
        dict(num=692, pattern=8, options=[8, 1, 5],
             prompt="返回出现频率前 K 高的单词，频率相同的按字典序排。",
             why="`Counter` + 堆（模板 A）。频率相同按字典序，正是「元组入堆的次级比较」"
                 "那条翻车点的实战：入堆键写成 `(freq, 反向的字典序)` 才能一次排对。"),
        dict(num=658, pattern=5, options=[8, 5, 2],
             prompt="给一个**已排序**数组和目标值 x，找出最接近 x 的 k 个数。",
             why="**二分 / 双指针，不是本章**——看到「k 个最接近」手就想去掏堆，"
                 "但数组已排序，答案必然是一段**连续区间**，二分找左边界即可，O(log n)。"
                 "堆要先把 n 个元素全扫一遍（O(n log k)），等于把题目给的「有序」这个"
                 "最强条件原样扔掉。见 §2 分流条件。"),
    ],
)
