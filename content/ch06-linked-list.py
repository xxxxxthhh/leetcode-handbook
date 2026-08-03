# -*- coding: utf-8 -*-
"""第 06 章 · 链表。"""

TPL_A = '''\
def reverse_list(head):
    prev, cur = None, head                  # 【骨架】prev 是已反转部分的头
    while cur:                              # 【骨架】
        nxt = cur.next                      # 【骨架】先记住 next —— 全章第一守则
        cur.next = prev                     # 【插槽】改指针:反转 / 断开 / 指向别处
        prev, cur = cur, nxt                # 【骨架】两个指针一起前进
    return prev                             # 【插槽】答案:新头 / 新尾 / 一段的两端
'''

TPL_A_TESTS = '''\
class ListNode:                             # LeetCode 会替你定义,本地测试自己补一个
    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def to_list(node):
    out = []
    while node:
        out.append(node.val)
        node = node.next
    return out


assert to_list(reverse_list(build([1, 2, 3, 4, 5]))) == [5, 4, 3, 2, 1]
assert to_list(reverse_list(build([1]))) == [1]
assert reverse_list(None) is None


# 141/142:快慢指针判环 + 找入口
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow is fast:                    # 相遇 -> 有环
            p = head
            while p is not slow:            # 头和相遇点同速前进,交点就是入口
                p, slow = p.next, slow.next
            return p
    return None


a, b, c = ListNode(3), ListNode(2), ListNode(0)
d = ListNode(-4)
a.next, b.next, c.next, d.next = b, c, d, b
assert detect_cycle(a) is b
assert detect_cycle(build([1, 2])) is None
'''

TPL_B = '''\
def merge_two(a, b):
    dummy = tail = ListNode()               # 【骨架】哨兵头,省掉"第一个节点"的特判
    while a and b:                          # 【骨架】
        if a.val <= b.val:                  # 【插槽】选谁接上来的条件
            tail.next, a = a, a.next        # 【骨架】接上 + 被选中的一方前进
        else:
            tail.next, b = b, b.next        # 【骨架】
        tail = tail.next                    # 【骨架】
    tail.next = a or b                      # 【插槽】收尾:剩下的一整段直接挂上
    return dummy.next                       # 【骨架】哨兵的下一个才是真头
'''

TPL_B_TESTS = '''\
class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt


def build(vals):
    head = None
    for v in reversed(vals):
        head = ListNode(v, head)
    return head


def to_list(node):
    out = []
    while node:
        out.append(node.val)
        node = node.next
    return out


assert to_list(merge_two(build([1, 2, 4]), build([1, 3, 4]))) == [1, 1, 2, 3, 4, 4]
assert to_list(merge_two(build([]), build([0]))) == [0]
assert merge_two(None, None) is None


# 19 Remove Nth From End:同一个哨兵骨架,快指针先走 n+1 步
def remove_nth(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n + 1):                  # +1 是为了让 slow 停在待删节点的前一个
        fast = fast.next
    while fast:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next
    return dummy.next


assert to_list(remove_nth(build([1, 2, 3, 4, 5]), 2)) == [1, 2, 3, 5]
assert to_list(remove_nth(build([1]), 1)) == []
assert to_list(remove_nth(build([1, 2]), 2)) == [2]
'''

CHAPTER = dict(
    no=6,
    freq="高",

    mental_model="**链表题只有两件事：改指针，和跑指针。"
                 "改指针之前一定先把 `next` 存下来；跑指针靠一快一慢制造出位置差。**",
    mental_model_body=[
        "改指针类（反转、合并、删除、重排）的通用保险是**哨兵节点** `dummy`："
        "它让「头节点也可能被删 / 被换」这个特判彻底消失，代码短一半、bug 少一半。",
        "跑指针类（找中点、判环、倒数第 n 个）本质是第 02 章的快慢指针，只是数据结构换成了链表。"
        "**画图，不要心算**——三个节点、两轮循环，纸上画一遍比在脑子里推十遍准。",
    ],

    signals=[
        ("「反转 / 翻转链表（或其中一段）」", "三指针改写（模板 A）"),
        ("「合并两个有序链表」「删除倒数第 n 个」", "哨兵 + 双指针（模板 B）"),
        ("「找中点 / 判断有环 / 环的入口」", "快慢指针，快的每次两步"),
        ("「重排 / 判回文链表」", "找中点 → 反转后半 → 交替拼接，三个已知动作的组合"),
        ("「带随机指针的深拷贝」", "哈希表：旧节点 → 新节点（第 01 章的映射思维）"),
        ("「O(1) 时间的 get 和 put」", "哈希表 + 双向链表（146 LRU）"),
    ],
    routing="快慢指针与第 02 章同源，区别只是数组能随机访问、链表只能顺着走。"
            "「合并 **K** 个有序链表」的主语已经不是链表而是**堆**（第 08 章）——"
            "两个链表用双指针，K 个链表要的是「当前最小的头节点」这种 Top-K 结构。"
            "「链表排序」考的是归并思路，不在阈值范围内。",
    routing_to=[2, 8],

    templates=[
        dict(name="模板 A · 反转", note="改指针类的地基",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**存 next、改指向、双双前进**。"
                  "反转一段（92、25）时骨架不变，只是循环跑固定次数、并在两端重新接线。"),
        dict(name="模板 B · 哨兵 + 双指针", note="合并 / 删除类",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="只要题目里「头节点可能被改动」，第一行就写 `dummy`。"
                  "最后 `return dummy.next`，不是 `return head`。"),
    ],

    problems=[
        dict(num=206, tier="warmup",
             note="模板 A 原题。递归写法也要会说：`reverse(head.next)` 之后"
                  "`head.next.next = head; head.next = None`，栈深度 O(n) 是它的代价。"),
        dict(num=21, tier="standard",
             note="模板 B 原题。收尾那行 `tail.next = a or b` 是链表相对数组的便宜："
                  "剩下的一整段不用逐个搬。"),
        dict(num=141, tier="standard",
             note="快慢指针判环。为什么快指针走两步就一定能追上：每轮差距缩小 1，环内必然相遇。"),
        dict(num=142, tier="standard",
             note="141 的进阶：相遇后**从头和从相遇点同速前进，交点即入口**。"
                  "结论要背，推导（设环前长 a、环长 b）能讲一遍更好。"),
        dict(num=19, tier="standard",
             note="哨兵 + 快指针先走 `n + 1` 步。为什么是 `n + 1` 而不是 `n`："
                  "要让 `slow` 停在待删节点的**前一个**。"),
        dict(num=143, tier="standard",
             note="三个已知动作的拼装：找中点（快慢）→ 反转后半（模板 A）→ 交替合并。"
                  "本章最能体现「链表题是动作的组合」的一道。"),
        dict(num=138, tier="variant",
             note="哈希映射旧 → 新，两遍扫描：第一遍建节点，第二遍接 `next` 和 `random`。"
                  "O(1) 空间的原地交织解法是加分项，不是必需品。"),
        dict(num=146, tier="variant",
             note="哈希表 + 双向链表。面试里可以提 `OrderedDict` 一行搞定，"
                  "但**必须能手写双向链表版本**——考的就是这个。"),
        dict(num=23, tier="variant", star=True,
             note="⭐认脸。K 路归并：堆里放 K 个头节点，见第 08 章。"),
    ],

    pitfalls=[
        ("先改指针，再想起要 next",
         "`cur.next = prev` 之后原来的 `cur.next` 就永远找不回来了。"
         "任何改指针的循环，第一行都应该是 `nxt = cur.next`。"),
        ("不用哨兵",
         "头节点可能被删（19）、可能被换（21、203）。没有 `dummy` 就得为「删的是头」单独写一段，"
         "这段代码是链表题最常见的漏写。"),
        ("快指针的循环条件",
         "`while fast and fast.next` 缺一不可：只判 `fast` 会在 `fast.next.next` 处崩，"
         "只判 `fast.next` 会在链表为空时崩。"),
        ("环入口结论记成「相遇点就是入口」",
         "相遇点在环内但通常不是入口。必须再走一轮同速追赶（见 142）。"),
        ("双向链表忘了断两头",
         "146 里删除节点要同时修 `prev.next` 和 `next.prev`，只改一边会留下悬挂引用，"
         "表现为容量统计对不上。"),
    ],

    quiz=[
        dict(num=83, pattern=6, options=[6, 1, 2],
             prompt="删除**已排序**链表中所有重复的节点，每个值只保留一个。",
             why="链表。改指针类，`cur.next = cur.next.next` 跳过重复即可，连哨兵都不需要"
                 "（头节点一定保留）。用 `set` 去重也能过，但那是数组思维，浪费了「已排序」。"),
        dict(num=287, pattern=6, options=[6, 1, 5],
             prompt="长度 n+1 的数组，元素都在 1..n 之间，找出那个重复的数（不能改数组、只能用 O(1) 空间）。",
             why="链表的快慢指针。把 `i -> nums[i]` 看成链表的 next，重复的数就是**环的入口**，"
                 "142 原样套用。这是本章最值得认脸的一道——它长得完全不像链表题。"
                 "（允许用哈希时当然是第 01 章。）"),
        dict(num=155, pattern=4, options=[6, 4, 1],
             prompt="设计一个栈，`push` / `pop` / `top` / `getMin` 全部 O(1)。",
             why="**栈，不是本章**——同样是「设计一个数据结构」，146 LRU 要的是"
                 "「按访问顺序淘汰」所以需要双向链表，而这道要的是「随时取当前最小」，"
                 "辅助栈同步记录即可。设计题不都是链表题，看它要维护的到底是什么顺序。"),
    ],
)
