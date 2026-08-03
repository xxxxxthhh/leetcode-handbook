# -*- coding: utf-8 -*-
"""第 07 章 · 树的遍历与递归。"""

TPL_A = '''\
def max_depth(root):
    if not root:                            # 【骨架】空节点的答案 —— 递归的地基
        return 0                            # 【插槽】空树返回什么
    left = max_depth(root.left)             # 【骨架】
    right = max_depth(root.right)           # 【骨架】
    return 1 + max(left, right)             # 【插槽】当前节点怎么合并左右的返回值
'''

TPL_A_TESTS = '''\
class TreeNode:                             # LeetCode 会替你定义,本地测试自己补一个
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def build(vals):
    """按 LeetCode 层序数组建树,None 表示空位。"""
    if not vals:
        return None
    root = TreeNode(vals[0])
    q, i = [root], 1
    while q and i < len(vals):
        node = q.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root


assert max_depth(build([3, 9, 20, None, None, 15, 7])) == 3
assert max_depth(build([])) == 0
assert max_depth(build([1])) == 1


# 543 Diameter:返回值(深度)不是答案(直径),答案挂在外面
def diameter(root):
    best = 0

    def depth(node):
        nonlocal best
        if not node:
            return 0
        l, r = depth(node.left), depth(node.right)
        best = max(best, l + r)             # 经过当前节点的路径长度
        return 1 + max(l, r)                # 返回给父亲的仍然是深度

    depth(root)
    return best


assert diameter(build([1, 2, 3, 4, 5])) == 3
assert diameter(build([1, 2])) == 1


# 98 Validate BST:带着上下界往下递归,只比父节点是不够的
def is_valid_bst(root, lo=float("-inf"), hi=float("inf")):
    if not root:
        return True
    if not lo < root.val < hi:
        return False
    return (is_valid_bst(root.left, lo, root.val)
            and is_valid_bst(root.right, root.val, hi))


assert is_valid_bst(build([2, 1, 3])) is True
assert is_valid_bst(build([5, 1, 4, None, None, 3, 6])) is False
assert is_valid_bst(build([5, 4, 6, None, None, 3, 7])) is False   # 只比父节点会漏掉的用例
'''

TPL_B = '''\
from collections import deque

def level_order(root):
    if not root:
        return []
    q, out = deque([root]), []              # 【骨架】
    while q:                                # 【骨架】
        size = len(q)                       # 【骨架】先固定这一层的人数,再开始出队
        level = []                          # 【插槽】这一层要收集什么
        for _ in range(size):               # 【骨架】
            node = q.popleft()              # 【骨架】
            level.append(node.val)          # 【插槽】
            if node.left:
                q.append(node.left)         # 【骨架】
            if node.right:
                q.append(node.right)        # 【骨架】
        out.append(level)                   # 【插槽】每层一组 / 只要最后一层 / 只要层数
    return out
'''

TPL_B_TESTS = '''\
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def build(vals):
    if not vals:
        return None
    root = TreeNode(vals[0])
    q, i = [root], 1
    while q and i < len(vals):
        node = q.pop(0)
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            q.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            q.append(node.right)
        i += 1
    return root


assert level_order(build([3, 9, 20, None, None, 15, 7])) == [[3], [9, 20], [15, 7]]
assert level_order(build([])) == []
assert level_order(build([1])) == [[1]]
'''

CHAPTER = dict(
    no=7,
    freq="极高",

    mental_model="**一切树题都是同一个填空：对当前节点做什么，加上递归左右孩子。"
                 "动手前只需回答一句——这个递归函数的返回值代表什么？**",
    mental_model_body=[
        "把「返回值的含义」写在纸上（深度？子树是否合法？子树的最大路径和？），"
        "剩下的三件事会自动落位：空节点返回什么（地基）、怎么合并左右的返回值（当前节点做什么）、"
        "答案是不是就是根节点的返回值。",
        "最容易卡住的一类是**返回值 ≠ 答案**：543 的返回值是深度、答案是直径；"
        "124 的返回值是「向上贡献的单边路径和」、答案是「经过某点的整条路径和」。"
        "这类题一律用 `nonlocal best` 把答案挂在递归外面。",
    ],

    signals=[
        ("「深度 / 高度 / 直径 / 是否平衡」", "后序递归，返回值是深度（模板 A）"),
        ("「层 / 每一层 / 最短路径 / 右视图」", "BFS 队列，按层出队（模板 B）"),
        ("「BST」+「第 K 小 / 有序输出」", "中序遍历天然升序"),
        ("「验证 BST」", "带上下界递归，不能只和父节点比"),
        ("「最近公共祖先 LCA」", "后序：左右都非空则当前就是答案；BST 可用值域直接下降"),
        ("「前序 + 中序构造」「序列化 / 反序列化」", "用中序定位划分点 / 前序 + 空标记"),
    ],
    routing="要**枚举所有路径 / 所有方案**并且需要撤销选择，那是回溯（第 09 章），"
            "树只是它的递归载体。网格和邻接表上的 BFS/DFS 属于第 10 章——"
            "区别在于树没有环、不需要 `visited`，一旦要判重就说明你面对的是图。"
            "「层序」和「多源最短步数」共用队列骨架，但树的层序不需要 `visited`。"
            "还有一个同名陷阱：树里说「有序」指的是 **BST 的中序**，"
            "和有序数组（第 05 章的二分）、有序链表（第 06 章的合并）不是一回事——"
            "BST 的有序性藏在结构里，你得走一遍中序才能看见它。",
    routing_to=[5, 6, 9, 10],

    templates=[
        dict(name="模板 A · 递归三问", note="覆盖本章绝大多数题",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**空的返回什么、左右各要什么、当前怎么合**。"
                  "返回值和答案不是一回事时，答案用 `nonlocal` 挂在外面。"),
        dict(name="模板 B · 层序 BFS", note="凡是带「层」字的题",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="`size = len(q)` 这一行是全部：先固定住这一层有几个人，"
                  "再开始出队，否则新入队的下一层会混进来。"),
    ],

    problems=[
        dict(num=226, tier="warmup",
             note="模板 A 的最小形态：当前节点交换左右，再递归。"
                  "「对当前节点做什么 + 递归左右」这句话的字面演示。"),
        dict(num=104, tier="warmup",
             note="模板 A 原题。它的返回值恰好就是答案，是理解「返回值 ≠ 答案」之前最好的对照组。"),
        dict(num=543, tier="standard",
             note="第一道返回值 ≠ 答案的题：返回深度，答案是 `l + r` 的最大值。"
                  "见 §1 第二段与翻车点①。"),
        dict(num=110, tier="standard",
             note="朴素写法对每个节点都算一次深度是 O(n²)。"
                  "正解让 `depth` 返回 `-1` 表示「已经不平衡」，一次遍历搞定——剪枝藏在返回值里。"),
        dict(num=102, tier="standard",
             note="模板 B 原题。107（自底向上）把结果 `reverse` 即可，"
                  "199（右视图）取每层最后一个，都是同一个骨架。"),
        dict(num=98, tier="standard",
             note="必须带 `(lo, hi)` 上下界往下传。只比父节点的写法会放过 "
                  "`[5,4,6,null,null,3,7]` 这种用例——模板测试里专门留了这条断言。"),
        dict(num=230, tier="standard",
             note="BST 中序遍历是升序，走到第 K 个就返回。"
                  "面试常追问「频繁查询怎么办」：答案是节点里维护子树大小。"),
        dict(num=235, tier="standard",
             note="BST 版 LCA：两个值都比当前小就往左，都比当前大就往右，"
                  "否则当前节点就是分叉点。不需要递归回溯，一路向下即可。"),
        dict(num=236, tier="standard",
             note="普通二叉树版 LCA：后序递归，左右子树的返回值都非空 → 当前节点就是 LCA。"
                  "和 235 放在一起看，能清楚感受到「BST 这个条件值多少钱」。"),
        dict(num=105, tier="variant",
             note="前序的第一个是根，在中序里找到它就切开了左右子树。"
                  "用哈希表存「值 → 中序下标」把每次查找降到 O(1)，否则是 O(n²)。"),
        dict(num=124, tier="variant", star=True,
             note="⭐认脸。返回值是「向上贡献的单边路径和」（负数截断成 0），答案用 `nonlocal` 记。"
                  "543 想明白了，这道只是把「长度」换成「和」。"),
        dict(num=297, tier="variant", star=True,
             note="⭐认脸。前序 + 空节点占位符即可还原。说得出「为什么需要空标记」就够。"),
    ],

    pitfalls=[
        ("返回值和答案混为一谈",
         "543 / 124 / 110 都是这一类。写之前先说一句「这个函数返回的是 X」，"
         "如果答案不是 X，就必须另开一个 `nonlocal` 变量。"),
        ("验证 BST 只比父节点",
         "`node.left.val < node.val` 只保证局部有序。必须把祖先施加的上下界一路传下去。"),
        ("层序忘了先取 `len(q)`",
         "循环里直接 `while q` 逐个出队，会把下一层的节点混进当前层。"
         "凡是要「按层」的输出，第一行永远是 `size = len(q)`。"),
        ("平衡判断退化成 O(n²)",
         "在 `is_balanced` 里对每个节点调用 `depth`，最坏是 O(n²)。"
         "用「返回 -1 表示已失衡」把两件事合并成一次遍历。"),
        ("递归深度",
         "退化成链的树（1e5 个节点）会爆 Python 默认递归上限。"
         "面试里提一句「必要时改迭代或调 `setrecursionlimit`」是加分项。"),
    ],

    quiz=[
        dict(num=572, pattern=7, options=[7, 1, 9],
             prompt="判断一棵树是不是另一棵树的子树。",
             why="树的递归。外层递归找候选根，内层递归判「两棵树是否完全相同」——"
                 "两个模板 A 嵌套。看到「结构相同」就该想到 `isSame(a, b)` 这个经典返回值。"),
        dict(num=199, pattern=7, options=[7, 10, 9],
             prompt="从右侧看一棵二叉树，返回从上到下能看到的节点值。",
             why="层序 BFS（模板 B）。每层只取最后一个，`size = len(q)` 那行的直接应用。"
                 "「右视图 / 每层最大值 / 层平均数」全是同一道题换皮。"),
        dict(num=200, pattern=10, options=[7, 10, 9],
             prompt="给一个由 '1'（陆地）和 '0'（水）组成的网格，数出岛屿的个数。",
             why="**图的 BFS/DFS，不是本章**——网格是图不是树，会绕回来，所以必须有 `visited`"
                 "（或就地改成 '0'）。树的递归之所以不用判重，是因为树天然无环。见第 10 章。"),
    ],
)
