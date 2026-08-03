# -*- coding: utf-8 -*-
"""第 12 章 · 并查集。"""

TPL_A = '''\
class DSU:
    def __init__(self, n):
        self.p = list(range(n))             # 【骨架】一开始每个点自成一伙
        self.size = [1] * n                 # 【骨架】按大小合并,防止退化成长链
        self.count = n                      # 【插槽】要顺手维护的量:连通块数 / 每块大小

    def find(self, x):
        while self.p[x] != x:               # 【骨架】
            self.p[x] = self.p[self.p[x]]   # 【骨架】路径压缩:顺手把爷爷认成爸爸
            x = self.p[x]                   # 【骨架】
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:                        # 【插槽】已在一伙 -> 这条边会成环
            return False
        if self.size[ra] < self.size[rb]:   # 【骨架】小的挂到大的下面
            ra, rb = rb, ra
        self.p[rb] = ra                     # 【骨架】
        self.size[ra] += self.size[rb]      # 【骨架】
        self.count -= 1                     # 【插槽】
        return True
'''

TPL_A_TESTS = '''\
d = DSU(5)
assert d.union(0, 1) is True
assert d.union(1, 2) is True
assert d.union(0, 2) is False              # 已经在一伙 -> 成环
assert d.find(0) == d.find(2)
assert d.find(0) != d.find(3)
assert d.count == 3                         # {0,1,2} {3} {4}


# 547 Number of Provinces:一条边一条边合并,最后看还剩几伙
def find_circle_num(is_connected):
    n = len(is_connected)
    d = DSU(n)
    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                d.union(i, j)
    return d.count


assert find_circle_num([[1, 1, 0], [1, 1, 0], [0, 0, 1]]) == 2
assert find_circle_num([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) == 3


# 684 Redundant Connection:union 第一次返回 False 的那条边就是多余的
def find_redundant(edges):
    d = DSU(len(edges) + 1)
    for a, b in edges:
        if not d.union(a, b):
            return [a, b]
    return []


assert find_redundant([[1, 2], [1, 3], [2, 3]]) == [2, 3]
assert find_redundant([[1, 2], [2, 3], [3, 4], [1, 4], [1, 5]]) == [1, 4]


# 261 Graph Valid Tree:树 = 恰好 n-1 条边 + 全连通(等价于合并过程中不成环)
def valid_tree(n, edges):
    if len(edges) != n - 1:
        return False
    d = DSU(n)
    return all(d.union(a, b) for a, b in edges)


assert valid_tree(5, [[0, 1], [0, 2], [0, 3], [1, 4]]) is True
assert valid_tree(5, [[0, 1], [1, 2], [2, 3], [1, 3], [1, 4]]) is False
'''

CHAPTER = dict(
    no=12,
    freq="中",

    mental_model="**并查集只回答一个问题：这俩在不在一伙。"
                 "它维护的是「动态」连通性——边一条条加进来，你随时能问。**",
    mental_model_body=[
        "两个动作：`find`（一路往上找老大，顺手做**路径压缩**）和 `union`（小的挂到大的下面）。"
        "两个优化都加上之后，单次操作近似 O(1)，代码一共十来行，属于必须能默写的那一档。",
        "它相对第 10 章 DFS 的独门优势有两个：**边是动态给的**（DFS 得每次重跑），"
        "以及 **`union` 返回 False 就等于发现了环**——684、261 全靠这一行。",
    ],

    signals=[
        ("「有多少个连通分量 / 省份 / 朋友圈 / 组」", "边全合并完，看还剩几伙"),
        ("「加上这条边会不会形成环」", "`union` 返回 False 的那一刻（684）"),
        ("「判断这张图是不是一棵树」", "边数 == n−1 且合并全程不成环（261）"),
        ("「把有共同元素的集合归并」（账户、邮箱、字符串）", "先把元素映射成整数 id，再合并（721）"),
        ("边是一条条**流进来**的，中途还要回答问题", "并查集；DFS 得每来一条边重跑一次"),
        ("「等式约束是否自洽」（a==b, b!=c）", "先合并所有相等，再检查不等（990）"),
    ],
    routing="**静态**无向图数连通块，第 10 章的 DFS 更直接、也更好写；"
            "并查集的价值在「动态」和「成环检测」这两件事上。"
            "图是**有向**的、问的是顺序或循环依赖 → 拓扑排序（第 11 章）："
            "并查集没有方向概念，`union(a, b)` 和 `union(b, a)` 完全等价。"
            "带权最短路属于 Dijkstra，本书不覆盖。",
    routing_to=[10, 11],

    templates=[
        dict(name="模板 A · 并查集", note="本章唯一模板，十行必须能默写",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**find 一路压缩、union 小挂大、返回 False 即成环**。"
                  "`count` 顺手维护，连通块数就不用最后再数一遍。"),
    ],

    problems=[
        dict(num=547, tier="standard",
             note="模板 A 原题：全部边合并完，`count` 就是答案。"
                  "面试里说得出「DFS 也能做，我选并查集是因为它顺手给出块数」即可。"),
        dict(num=684, tier="standard",
             note="`union` **第一次**返回 False 的那条边就是答案。"
                  "题目要求返回最后出现的那条，而按顺序合并天然满足——这一点值得主动说明。"),
        dict(num=261, tier="standard",
             note="树的两个充要条件：边数恰好 `n - 1`，且合并过程中一次环都没成。"
                  "少判任何一个都会漏用例（`n-1` 条边但有环 ⇒ 必然不连通）。"),
        dict(num=323, tier="standard",
             note="547 的邻接表版本，输入从矩阵换成 `edges`。"
                  "两道题一起做，能确认你写的模板对输入形式不敏感。"),
        dict(num=721, tier="variant",
             note="并查集用在**字符串**上的标准做法：邮箱 → 整数 id 的映射表，"
                  "同一个账户里的所有邮箱两两（其实只需和第一个）合并，最后按根分组再排序。"
                  "实现比思路长，是本章唯一的工程量。"),
    ],

    pitfalls=[
        ("忘了路径压缩",
         "只写 `while p[x] != x: x = p[x]` 而不改 `p[x]`，最坏退化成 O(n) 的长链。"
         "`self.p[x] = self.p[self.p[x]]` 这一行不能省。"),
        ("合并方向随手写",
         "不按大小（或秩）合并，配上没有压缩就是 O(n)。两个优化至少要有一个，"
         "面试里建议两个都写——一共多两行。"),
        ("`union` 的返回值没用起来",
         "684、261、990 全靠「返回 False 说明已同组」。"
         "把 `union` 写成没有返回值的过程，这几道题就得另外再判一次环。"),
        ("261 只判连通不判边数",
         "`n` 个点、`n` 条边且连通，那是有环的图不是树。两个条件缺一不可。"),
        ("字符串直接当下标",
         "721 这类题必须先建 `{邮箱: id}` 映射。"
         "把 `p` 换成字典虽然也能跑，但 `size` 数组和路径压缩都要跟着改写，容易出错。"),
    ],

    quiz=[
        dict(num=990, pattern=12, options=[12, 11, 1],
             prompt="给一组形如 `a==b`、`a!=b` 的等式，判断它们能否同时成立。",
             why="并查集。先把所有 `==` 合并成组，再逐条检查 `!=` 的两端是否落在同一组。"
                 "「约束是否自洽」= 连通性问题，两遍扫描解决。"),
        dict(num=839, pattern=12, options=[12, 10, 9],
             prompt="若两个字符串相等，或交换其中两个字母后相等，则它们相似。求相似字符串的组数。",
             why="并查集。两两判断相似（O(n²·len)）后合并，最后数连通块。"
                 "「归组 / 有多少组」是并查集最直白的暗号，和 547 是同一道题换了个判定条件。"),
        dict(num=207, pattern=11, options=[12, 11, 10],
             prompt="共 n 门课，给出若干「先修 A 才能修 B」的关系，判断能否修完所有课。",
             why="**拓扑排序，不是本章**——边是**有向**的。"
                 "并查集里 `union(a, b)` 和 `union(b, a)` 完全等价，天生表达不了「谁在谁前面」，"
                 "自然也判不出有向环。见 §2 分流条件。"),
    ],
)
