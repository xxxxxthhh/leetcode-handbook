# -*- coding: utf-8 -*-
"""第 11 章 · 拓扑排序。"""

TPL_A = '''\
from collections import deque

def topo_order(n, prerequisites):
    graph = [[] for _ in range(n)]          # 【骨架】邻接表:a -> b 表示"修完 a 才能修 b"
    indeg = [0] * n                         # 【骨架】入度 = 还欠几个前置
    for b, a in prerequisites:              # 【插槽】题目给的是 [课, 先修课],方向别搞反
        graph[a].append(b)
        indeg[b] += 1
    q = deque(i for i in range(n) if not indeg[i])   # 【骨架】所有零依赖的先入队
    order = []
    while q:                                # 【骨架】
        cur = q.popleft()                   # 【骨架】
        order.append(cur)                   # 【插槽】答案:顺序本身 / 只要个数
        for nxt in graph[cur]:              # 【骨架】
            indeg[nxt] -= 1                 # 【骨架】它少欠一个了
            if not indeg[nxt]:              # 【骨架】欠债清零才有资格入队
                q.append(nxt)               # 【骨架】
    return order if len(order) == n else [] # 【插槽】出队数 < n 就是有环
'''

TPL_A_TESTS = '''\
assert topo_order(2, [[1, 0]]) == [0, 1]
assert topo_order(2, [[1, 0], [0, 1]]) == []          # 互为前置 -> 有环
assert topo_order(1, []) == [0]

order = topo_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])
pos = {c: i for i, c in enumerate(order)}
assert len(order) == 4
assert pos[0] < pos[1] and pos[0] < pos[2]
assert pos[1] < pos[3] and pos[2] < pos[3]

# 207 Course Schedule:只要判断能不能修完
def can_finish(n, prerequisites):
    return len(topo_order(n, prerequisites)) == n


assert can_finish(2, [[1, 0]]) is True
assert can_finish(2, [[1, 0], [0, 1]]) is False
assert can_finish(5, []) is True                      # 孤立点也必须算进入度表
'''

CHAPTER = dict(
    no=11,
    freq="高",

    mental_model="**「依赖」两个字出现就是它：把入度为 0 的点放进队列，"
                 "出队一个就给它的后继减一个入度，减到 0 再入队。**",
    mental_model_body=[
        "判环不需要额外逻辑：**能出队的点数少于总点数，剩下的就卡在环里**。"
        "这一条让「能不能修完所有课」和「给出一种修课顺序」变成同一段代码，只是返回值不同。",
        "全章唯一的难点其实是**建图方向**。LeetCode 给的 `[b, a]` 意思是「修 b 之前要先修 a」，"
        "所以边是 `a → b`、`indeg[b] += 1`。方向反了代码照样能跑，只是答案整个是倒的。",
    ],

    signals=[
        ("「先修课 / 前置条件 / 依赖关系」", "拓扑排序，入度为 0 进队列"),
        ("「编译顺序 / 任务调度顺序 / 打包顺序」", "同上，问的是一种合法线性序"),
        ("「判断有没有循环依赖 / 能不能全部完成」", "拓扑 + 计数判环"),
        ("「输出**任意一种**合法顺序」", "拓扑（答案不唯一正是它的特征）"),
        ("「根据给定的单词序推字母表顺序」", "先从相邻单词比出边，再拓扑（269）"),
        ("图是**有向**的且要问顺序", "拓扑；无向图问连通性是第 12 章"),
    ],
    routing="同样用队列，第 10 章的 BFS 队列里放的是「所有未访问的邻居」，"
            "本章队列里放的是「入度已清零的点」——**入度**这两个字是分界线。"
            "判环也要分清：**有向**图判环用拓扑（本章），**无向**图判环用并查集"
            "（第 12 章，`union` 返回 False 即成环）或 DFS 记父节点。"
            "只要遍历、不问顺序，回到第 10 章。",
    routing_to=[10, 12],

    templates=[
        dict(name="模板 A · Kahn 入度法", note="本章唯一模板",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**建图数入度、零入度入队、出队减邻居、计数判环**。"
                  "DFS 三色法（白/灰/黑）也能做，但入度法更好写也更好讲，阈值内只需要这一个。"),
    ],

    problems=[
        dict(num=207, tier="standard",
             note="模板 A 原题，只取「出队个数是否等于 n」。"
                  "面试里被问「怎么证明这样就能判环」时答：入度永远清不了零的点，必然互相欠着。"),
        dict(num=210, tier="standard",
             note="和 207 同一段代码，返回 `order` 而不是布尔值。"
                  "两道题放一起就是本章的全部内容——这也是本章刻意没有热身题的原因。"),
        dict(num=269, tier="variant", star=True,
             note="⭐认脸。难点全在**建图**：逐对比较相邻单词，第一个不同的字母给出一条边，"
                  "之后照套模板。"),
    ],

    pitfalls=[
        ("建图方向反了",
         "`[b, a]` 是「先修 a 才能修 b」，边必须是 `a → b`。"
         "反了之后 207 依然返回 True（有向无环图反向仍无环），但 210 的顺序整个是倒的。"),
        ("孤立点漏进入度表",
         "入度数组必须按 `n` 开满，没有任何依赖的课也要以 0 入度进队列。"
         "只遍历 `prerequisites` 建表，会漏掉从未出现过的课号。"),
        ("用异常或染色去判环",
         "拓扑判环只需要 `len(order) == n` 这一句。写成递归 DFS 再捕获「重复访问」，"
         "既长又容易把「本次路径上」和「以前访问过」搞混。"),
        ("以为拓扑序唯一",
         "同时有多个零入度点时，顺序取决于出队次序。题目说「返回任意一种」就是这个意思；"
         "要求字典序最小时把队列换成小顶堆（第 08 章）。"),
    ],

    quiz=[
        dict(num=2115, pattern=11, options=[11, 10, 12],
             prompt="给一批菜谱、各自的原料表和你手上的现有原料，求最终能做出哪些菜"
                    "（一道菜也可以是另一道菜的原料）。",
             why="拓扑排序。「A 是 B 的原料」就是一条有向边，手上的现有原料是入度为 0 的起点，"
                 "能被剥出来的菜就是做得成的。题面把「依赖」换了个说法而已——"
                 "认出**有向依赖**这四个字，模板一行不用改。"),
        dict(num=802, pattern=11, options=[11, 10, 12],
             prompt="有向图中，从某点出发的所有路径最终都能走到终点（出度为 0 的点），求所有这样的安全点。",
             why="拓扑排序。把图**反向**后，出度为 0 就变成入度为 0，"
                 "能被剥掉的点就是安全的，剥不掉的卡在环里。「反向建图」是拓扑题的常见变形。"),
        dict(num=547, pattern=12, options=[11, 12, 10],
             prompt="给一个 n×n 的矩阵表示城市之间是否直接相连，求「省份」（连通块）的个数。",
             why="**并查集，不是本章**——图是**无向**的，问的是「谁和谁在一伙」而不是「谁在谁前面」。"
                 "无向图没有入度这个概念，拓扑排序无从谈起。见 §2 分流条件与第 12 章。"),
    ],
)
