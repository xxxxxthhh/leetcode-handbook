# -*- coding: utf-8 -*-
"""第 10 章 · 图的 BFS/DFS。"""

TPL_A = '''\
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))

def num_islands(grid):
    if not grid or not grid[0]:
        return 0
    m, n = len(grid), len(grid[0])

    def dfs(i, j):
        if not (0 <= i < m and 0 <= j < n):     # 【骨架】先越界,再看内容
            return
        if grid[i][j] != "1":                   # 【插槽】什么格子该走
            return
        grid[i][j] = "0"                        # 【骨架】立刻标记已访问,否则会来回死循环
        for di, dj in DIRS:                     # 【骨架】
            dfs(i + di, j + dj)                 # 【骨架】

    count = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1":               # 【插槽】什么算一个新的连通块
                count += 1
                dfs(i, j)
    return count
'''

TPL_A_TESTS = '''\
g1 = [list("11110"), list("11010"), list("11000"), list("00000")]
assert num_islands(g1) == 1

g2 = [list("11000"), list("11000"), list("00100"), list("00011")]
assert num_islands(g2) == 3

assert num_islands([]) == 0


# 695 Max Area of Island:同一个骨架,把"计数"换成"返回面积"
def max_area_of_island(grid):
    m, n = len(grid), len(grid[0])

    def dfs(i, j):
        if not (0 <= i < m and 0 <= j < n) or grid[i][j] != 1:
            return 0
        grid[i][j] = 0
        return 1 + sum(dfs(i + di, j + dj) for di, dj in DIRS)

    return max((dfs(i, j) for i in range(m) for j in range(n)), default=0)


assert max_area_of_island([[1, 1, 0], [1, 0, 0], [0, 0, 1]]) == 3
assert max_area_of_island([[0, 0], [0, 0]]) == 0
'''

TPL_B = '''\
from collections import deque

def rotting_oranges(grid):
    m, n = len(grid), len(grid[0])
    q, fresh = deque(), 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                q.append((i, j))            # 【插槽】所有起点一次性入队 —— 多源的全部秘密
            elif grid[i][j] == 1:
                fresh += 1                  # 【插槽】终止条件要盯的量
    steps = 0
    while q and fresh:                      # 【骨架】
        for _ in range(len(q)):             # 【骨架】先固定这一层,层数就是步数
            i, j = q.popleft()              # 【骨架】
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                x, y = i + di, j + dj
                if 0 <= x < m and 0 <= y < n and grid[x][y] == 1:
                    grid[x][y] = 2          # 【骨架】入队时就标记,不能等出队再标
                    fresh -= 1
                    q.append((x, y))        # 【骨架】
        steps += 1                          # 【插槽】答案:层数 / 每个点的距离
    return -1 if fresh else steps
'''

TPL_B_TESTS = '''\
assert rotting_oranges([[2, 1, 1], [1, 1, 0], [0, 1, 1]]) == 4
assert rotting_oranges([[2, 1, 1], [0, 1, 1], [1, 0, 1]]) == -1
assert rotting_oranges([[0, 2]]) == 0
assert rotting_oranges([[0]]) == 0
'''

CHAPTER = dict(
    no=10,
    freq="极高",

    mental_model="**网格就是图：每个格子是点，上下左右是边。"
                 "`visited` 决定你会不会死循环，用队列还是栈决定你先看近的还是先看深的。**",
    mental_model_body=[
        "选 BFS 还是 DFS，只看一个问题：**要不要「最少步数」**。要，就必须 BFS——"
        "队列一层一层往外扩，第一次碰到目标时的层数就是最短距离；不要，两个都行，"
        "DFS 的递归写法通常更短。",
        "`visited` 的标记时机是本章头号 bug 来源：**入队时就标记**，不是出队时。"
        "出队才标记的话，同一个格子会被多个邻居重复入队，轻则变慢，重则超时。",
    ],

    signals=[
        ("「岛屿 / 连通块 / 区域 / 省份的个数」", "洪水填充，一次 DFS 吃掉一整块（模板 A）"),
        ("「最少步数 / 最短路径 / 最少几轮」（边权都是 1）", "BFS，层数就是答案（模板 B）"),
        ("「同时从多个点开始扩散」（腐烂的橘子、着火）", "多源 BFS：所有起点一次性入队"),
        ("「被包围的区域 / 流向两个大洋」", "**反向**从边界出发扩散，比正向判断简单得多"),
        ("「克隆图 / 深拷贝一张图」", "DFS + 哈希表映射旧节点 → 新节点"),
        ("给的是 `edges` 数组而不是网格", "先建邻接表 `defaultdict(list)`，再套同一套骨架"),
    ],
    routing="要枚举**所有路径**并在回来时还原现场，那是回溯（第 09 章）——"
            "本章的格子一旦标记就永久标记，绝不还原，这是两者最省事的分辨方法。"
            "题面出现「先修课 / 依赖 / 顺序」→ 拓扑排序（第 11 章）；"
            "只问「这两个点连不连通」且边是**动态加进来**的 → 并查集（第 12 章）——"
            "静态图数连通块用本章更直接。边有权重的最短路属于 Dijkstra，本书不覆盖。",
    routing_to=[9, 11, 12],

    templates=[
        dict(name="模板 A · 网格 DFS", note="连通块 / 洪水填充",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**越界就回、不该走就回、进来先标记、再走四个方向**。"
                  "数个数、求面积、求周长都只改最后的返回值。"),
        dict(name="模板 B · 多源 BFS", note="最少步数",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="两个关键点：**所有起点一次性入队**（多源和单源的唯一区别），"
                  "以及 `for _ in range(len(q))` 固定住这一层——层数就是步数。"),
    ],

    problems=[
        dict(num=200, tier="warmup",
             note="模板 A 原题。就地把 `'1'` 改成 `'0'` 当作 `visited`；"
                  "面试官说不许改输入时，换成一个 `visited` 集合即可。"),
        dict(num=133, tier="standard",
             note="DFS + `old → new` 哈希映射。映射必须**在递归之前**写入，"
                  "否则环会让你无限递归——这是它和普通 DFS 唯一的区别。"),
        dict(num=695, tier="standard",
             note="模板 A 换返回值：从「计数」变成「返回本块面积」。"
                  "`1 + sum(四个方向的 dfs)` 这一行把递归的合并写法演示得很干净。"),
        dict(num=994, tier="standard",
             note="模板 B 原题。多源 BFS 的教科书题：所有烂橘子先入队，"
                  "再用 `fresh` 计数判断最后有没有剩下够不到的。"),
        dict(num=130, tier="standard",
             note="反向思维：不去找「被包围的 O」，而是从**边界的 O** 出发标记所有安全的，"
                  "剩下的就是被包围的。正向判断需要回溯，反向只要一次遍历。"),
        dict(num=417, tier="variant",
             note="130 的双向版：从太平洋边界和大西洋边界各做一次反向扩散（水往高处走），"
                  "取两个集合的交集。识别难度大于实现难度。"),
        dict(num=127, tier="variant", star=True,
             note="⭐认脸。把单词看成点、差一个字母看成边，就是无权图最短路 → BFS。"
                  "说得出「用 `*` 通配建桶来找邻居」这个优化即可。"),
    ],

    pitfalls=[
        ("出队时才标记 visited",
         "同一个格子会被四个邻居各入队一次。正确做法是**入队的那一刻就标记**。"
         "网格题里表现为超时，图题里表现为重复计数。"),
        ("越界检查放在取值之后",
         "`grid[i][j] != '1' and 0 <= i < m` 会先崩在越界索引上。"
         "顺序永远是：先边界，后内容。"),
        ("多源 BFS 只入队了一个起点",
         "994、286 这类题必须把**全部**起点先塞进队列再开始循环。"
         "逐个起点跑单源 BFS 是 O(k·mn)，多源是 O(mn)。"),
        ("BFS 忘了固定层大小",
         "要「第几步」就必须 `for _ in range(len(q))`，和第 07 章层序是同一条。"
         "只要距离不要步数时，可以改成把 `(点, 距离)` 一起入队。"),
        ("大网格上递归 DFS 爆栈",
         "1000×1000 的全 `'1'` 网格，递归深度可达 10⁶。"
         "面试里提一句「必要时改成显式栈的迭代 DFS 或 BFS」是加分点。"),
    ],

    quiz=[
        dict(num=733, pattern=10, options=[10, 9, 12],
             prompt="从某个像素出发，把所有与它四连通且同色的像素改成新颜色。",
             why="图的 DFS/BFS（模板 A）。这就是洪水填充的原型，200 数岛屿是它的计数版。"
                 "注意新旧颜色相同时要提前返回，否则死循环。"),
        dict(num=1091, pattern=10, options=[10, 9, 5],
             prompt="0/1 矩阵里从左上角走到右下角（可走八个方向），求最短路径长度。",
             why="BFS（模板 B）。「最短」+ 边权都是 1 = BFS，层数就是答案。"
                 "DFS 也能遍历，但要枚举所有路径再取最小，指数级。八方向只是把 `DIRS` 换成 8 个。"),
        dict(num=207, pattern=11, options=[10, 11, 12],
             prompt="共 n 门课，给出若干「先修 A 才能修 B」的关系，判断能否修完所有课。",
             why="**拓扑排序，不是本章**——题面里的「先修 / 依赖」是拓扑的专属暗号。"
                 "它确实用 BFS 队列，但队列里放的是**入度为 0** 的点，不是「所有邻居」；"
                 "要判的是有没有环，不是能不能走到。见第 11 章。"),
    ],
)
