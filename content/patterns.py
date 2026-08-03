# -*- coding: utf-8 -*-
"""18 个模式的骨架（对应 spec/skeleton.md §5）。

这是全书唯一的「模式 → 章号 / 标题 / 文件名」映射：目录页、章页导航、
自测题的选项按钮、决策树叶子全部从这里取。章节内容文件只写内容，不重复标题，
所以「章号写错」「标题两处不一致」这类错误在结构上就不可能发生。
"""

GROUPS = [
    ("扫描与查找", "一遍扫过去就能解决的那一类", (1, 5)),
    ("链表 · 树 · 堆", "指针改写、递归填空、只关心第 K 个", (6, 8)),
    ("搜索与图", "把状态空间走一遍", (9, 12)),
    ("预处理与排序后的结构", "先加工数据，问题就变形了", (13, 15)),
    ("动态规划", "先写状态定义，再写转移", (16, 18)),
]

PATTERNS = [
    dict(no=1, slug="hash", title_zh="哈希", title_en="Hash Map / Set",
         tagline="用空间换「我见过你吗」的 O(1) 回答"),
    dict(no=2, slug="two-pointers", title_zh="双指针", title_en="Two Pointers",
         tagline="有序或对称结构里，两端 / 快慢协同收缩搜索空间"),
    dict(no=3, slug="sliding-window", title_zh="滑动窗口", title_en="Sliding Window",
         tagline="连续区间问题，右扩左缩维护一个「合法窗口」"),
    dict(no=4, slug="stack", title_zh="栈与单调栈", title_en="Stack & Monotonic Stack",
         tagline="每个元素都在找「左/右第一个比我大的人」"),
    dict(no=5, slug="binary-search", title_zh="二分查找", title_en="Binary Search",
         tagline="不止搜位置，还能搜答案本身——前提是判定函数单调"),
    dict(no=6, slug="linked-list", title_zh="链表", title_en="Linked List",
         tagline="只有指针改写和快慢指针两件事；画图 > 心算"),
    dict(no=7, slug="tree", title_zh="树的遍历与递归", title_en="Tree Traversal & Recursion",
         tagline="一切树题 =「对当前节点做什么 + 递归左右」的填空"),
    dict(no=8, slug="heap", title_zh="堆 / Top-K", title_en="Heap / Top-K",
         tagline="只关心第 K 个时，不排序，养一个大小为 K 的堆"),
    dict(no=9, slug="backtracking", title_zh="回溯", title_en="Backtracking",
         tagline="做选择 → 递归 → 撤销选择；剪枝决定生死"),
    dict(no=10, slug="graph-traversal", title_zh="图的 BFS/DFS", title_en="Graph BFS / DFS",
         tagline="网格也是图；visited 集合是命根子"),
    dict(no=11, slug="topological-sort", title_zh="拓扑排序", title_en="Topological Sort",
         tagline="「依赖关系」三个字出现就是它；入度为 0 进队列"),
    dict(no=12, slug="union-find", title_zh="并查集", title_en="Union-Find",
         tagline="动态连通性——「这俩在不在一伙」"),
    dict(no=13, slug="prefix-sum", title_zh="前缀和", title_en="Prefix Sum",
         tagline="一次预处理，之后区间和 O(1)；配哈希解「子数组和为 K」"),
    dict(no=14, slug="intervals", title_zh="区间", title_en="Intervals",
         tagline="先按起点排序，剩下的就是「重叠怎么办」"),
    dict(no=15, slug="greedy", title_zh="贪心", title_en="Greedy",
         tagline="先说出「局部最优不毁全局」的那个性质，再动手"),
    dict(no=16, slug="dp-1d", title_zh="一维 DP", title_en="1-D Dynamic Programming",
         tagline="dp[i] 只依赖前几项；先写状态定义再写转移"),
    dict(no=17, slug="dp-2d", title_zh="二维 DP 与背包", title_en="2-D DP & Knapsack",
         tagline="两个维度各自「取到 i / 容量 j」；背包 = 选或不选"),
    dict(no=18, slug="dp-subsequence", title_zh="子序列 DP", title_en="Subsequence DP (LIS)",
         tagline="LIS 两解法：O(n²) DP 与「耐心排序 + 二分」"),
]

BY_NO = {p["no"]: p for p in PATTERNS}
