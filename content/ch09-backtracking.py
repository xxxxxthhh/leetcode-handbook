# -*- coding: utf-8 -*-
"""第 09 章 · 回溯。"""

TPL_A = '''\
def subsets(nums):
    res, path = [], []                      # 【骨架】path = 当前走到哪
    def dfs(start):                         # 【插槽】start 表示"不许回头",排列题换成 used
        res.append(path[:])                 # 【插槽】何时记答案:每个节点 / 只在叶子;必须拷贝
        for i in range(start, len(nums)):   # 【骨架】枚举本层的选择
            path.append(nums[i])            # 【骨架】做选择
            dfs(i + 1)                      # 【插槽】i+1 = 每个数最多用一次;i = 可重复用
            path.pop()                      # 【骨架】撤销选择
    dfs(0)
    return res
'''

TPL_A_TESTS = '''\
assert sorted(subsets([1, 2, 3])) == sorted(
    [[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]])
assert subsets([]) == [[]]


# 39 Combination Sum:同一个数可重复选 -> 递归传 i 而不是 i+1
def combination_sum(candidates, target):
    candidates.sort()
    res, path = [], []

    def dfs(start, remain):
        if remain == 0:
            res.append(path[:])
            return
        for i in range(start, len(candidates)):
            if candidates[i] > remain:      # 排序后可以直接 break,这是最有效的剪枝
                break
            path.append(candidates[i])
            dfs(i, remain - candidates[i])
            path.pop()

    dfs(0, target)
    return res


assert sorted(combination_sum([2, 3, 6, 7], 7)) == [[2, 2, 3], [7]]
assert combination_sum([2], 1) == []


# 90 Subsets II:有重复元素 -> 排序后"同层跳过相同值"
def subsets_with_dup(nums):
    nums.sort()
    res, path = [], []

    def dfs(start):
        res.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:   # 注意是 i > start,不是 i > 0
                continue
            path.append(nums[i])
            dfs(i + 1)
            path.pop()

    dfs(0)
    return res


assert sorted(subsets_with_dup([1, 2, 2])) == sorted(
    [[], [1], [1, 2], [1, 2, 2], [2], [2, 2]])
'''

TPL_B = '''\
def permutations(nums):
    res, path = [], []
    used = [False] * len(nums)              # 【骨架】排列没有"不许回头",靠 used 防重复取
    def dfs():
        if len(path) == len(nums):          # 【插槽】终止条件 = 叶子的定义
            res.append(path[:])             # 【骨架】记答案要拷贝
            return
        for i, x in enumerate(nums):        # 【骨架】每层都从头枚举
            if used[i]:                     # 【骨架】
                continue
            used[i] = True                  # 【骨架】做选择
            path.append(x)
            dfs()                           # 【骨架】
            path.pop()                      # 【骨架】撤销选择
            used[i] = False
    dfs()
    return res
'''

TPL_B_TESTS = '''\
assert sorted(permutations([1, 2, 3])) == sorted(
    [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]])
assert permutations([1]) == [[1]]
assert permutations([]) == [[]]


# 79 Word Search:网格上的回溯 —— 标记与还原就是"做选择/撤销选择"
def exist(board, word):
    m, n = len(board), len(board[0])

    def dfs(i, j, k):
        if k == len(word):
            return True
        if not (0 <= i < m and 0 <= j < n) or board[i][j] != word[k]:
            return False
        board[i][j] = "#"                   # 做选择:占用这个格子
        found = (dfs(i + 1, j, k + 1) or dfs(i - 1, j, k + 1)
                 or dfs(i, j + 1, k + 1) or dfs(i, j - 1, k + 1))
        board[i][j] = word[k]               # 撤销选择:还原,别的路径还要用
        return found

    return any(dfs(i, j, 0) for i in range(m) for j in range(n))


b = [["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]]
assert exist(b, "ABCCED") is True
assert exist(b, "SEE") is True
assert exist(b, "ABCB") is False
assert b[0][0] == "A"                       # 还原干净了才能反复调用
'''

CHAPTER = dict(
    no=9,
    freq="高",

    mental_model="**回溯是在一棵「选择树」上做深度优先：做选择 → 递归 → 撤销选择。"
                 "三个空要填——本层有哪些选择、什么时候记答案、怎么剪枝。**",
    mental_model_body=[
        "「撤销选择」是它和普通 DFS 的唯一区别，也是它叫回溯的原因："
        "同一个 `path` 数组被所有分支共用，走完一条路必须恢复原状，"
        "否则兄弟分支拿到的是脏数据。**记答案时一定 `path[:]` 拷贝**，同理。",
        "识别它很容易：题面里有「**所有**」「列出全部方案」「有多少种走法并要求给出方案」，"
        "而且数据规模小得反常（n ≤ 20）——因为答案数量本身就是指数级的，"
        "出题人不可能给你大数据。",
    ],

    signals=[
        ("「所有子集 / 所有组合 / 所有排列」", "模板 A（组合）或模板 B（排列）"),
        ("「列出全部方案 / 打印所有路径」", "回溯，答案是方案本身而不是个数"),
        ("「在矩阵里找一个单词 / 一条路径」", "网格回溯：标记 → 递归 → 还原"),
        ("「把字符串切成若干段，每段都要满足…」", "切割型回溯，切点就是选择"),
        ("n ≤ 20 却要枚举，或明确说「保证答案不超过 X 个」", "指数级枚举被默许了"),
        ("「棋盘 / 皇后 / 数独」", "回溯 + 冲突集合剪枝"),
    ],
    routing="题目只要**方案数**、不要方案本身，几乎一定是 DP（第 16、17 章）——"
            "回溯枚举完再数一遍是指数级，DP 是多项式级。"
            "只要**最优值**（最大 / 最小）同理，先想 DP 或贪心（第 15 章）。"
            "网格上数连通块（第 10 章）用的是 DFS 但**不撤销**：格子一旦访问就永久标记，"
            "因为你不需要「换一条路再走一遍」。看到「还原现场」这个动作才是回溯。"
            "最后一个同名陷阱：「排列」这个词在第 03 章 567 也出现，但那道题问的是"
            "「s1 的某个排列是否作为子串出现」——比对字符计数即可，"
            "**真去枚举排列就爆了**。要不要真的列出方案，永远是第一道分水岭。",
    routing_to=[3, 10, 15, 16, 17],

    templates=[
        dict(name="模板 A · 组合 / 子集", note="靠 start 参数不许回头",
             code=TPL_A, tests=TPL_A_TESTS,
             foot="默写口诀：**选、递归、撤销**。`dfs(i + 1)` 每个数用一次，"
                  "`dfs(i)` 可以重复用——一个字符的差别就是 78 和 39 的差别。"),
        dict(name="模板 B · 排列", note="靠 used 数组标记占用",
             code=TPL_B, tests=TPL_B_TESTS,
             foot="排列与组合的分水岭：组合「不许回头」（`start`），排列「每层都从头选」（`used`）。"
                  "网格题（79）本质是排列型——`board[i][j] = '#'` 就是它的 `used`。"),
    ],

    problems=[
        dict(num=78, tier="warmup",
             note="模板 A 原题。子集题的答案记在**每个节点**而不是叶子——"
                  "这就是「什么时候记答案」这个插槽的第一次演示。"),
        dict(num=39, tier="standard",
             note="唯一改动：递归传 `i` 而不是 `i + 1`（同一个数可重复用）。"
                  "排序后 `if candidates[i] > remain: break` 是本章性价比最高的剪枝。"),
        dict(num=46, tier="standard",
             note="模板 B 原题。47（含重复元素的排列）在它基础上加"
                  "「同层跳过相同值且前一个未被使用」，是 90 的排列版。"),
        dict(num=90, tier="standard",
             note="去重的标准写法：**先排序**，然后 `if i > start and nums[i] == nums[i-1]: continue`。"
                  "条件是 `i > start` 不是 `i > 0`，见翻车点②——这是全章最常写错的一行。"),
        dict(num=79, tier="standard",
             note="网格回溯。就地把格子改成 `'#'` 表示占用，递归结束后**必须还原**；"
                  "不还原就变成了第 10 章的洪水填充，答案会漏。"),
        dict(num=131, tier="variant",
             note="切割型回溯：选择是「下一刀切在哪」。判回文可以先用 DP 预处理成表，"
                  "把每次 O(n) 的检查降到 O(1)——回溯 + 预处理是常见组合拳。"),
        dict(num=51, tier="variant", star=True,
             note="⭐认脸。逐行放皇后，用三个集合记列、主对角线 `r - c`、副对角线 `r + c`。"
                  "说得出这三个集合就够。"),
    ],

    pitfalls=[
        ("记答案忘了拷贝",
         "`res.append(path)` 存的是同一个列表对象的引用，回溯完它会被改空。"
         "必须 `path[:]` 或 `list(path)`。这是本章 90% 的「答案全是空数组」的原因。"),
        ("去重条件写成 `i > 0`",
         "`if i > start and nums[i] == nums[i-1]` 里的 `start` 不能换成 0。"
         "写成 `i > 0` 会把 `[1,2,2]` 里合法的 `[1,2,2]` 也剪掉——"
         "同一层的重复才要跳过，父子关系上的重复是合法的。"),
        ("撤销漏了一半",
         "做了两件事（`path.append` + `used[i] = True`）就要撤两件事。"
         "网格题里 `board[i][j] = '#'` 之后忘了还原，会让后续搜索少掉大片可用格子。"),
        ("该剪的枝不剪",
         "回溯的复杂度全靠剪枝救。排序 + 提前 `break`（39）、"
         "剩余元素不够就返回（77）、冲突集合（51）——面试里主动讲剪枝比写完更重要。"),
        ("把「要方案数」的题写成回溯",
         "见 §2 分流条件。爬楼梯、零钱兑换的方案数如果用回溯枚举，n 稍大就超时。"),
    ],

    quiz=[
        dict(num=77, pattern=9, options=[9, 16, 1],
             prompt="从 1..n 中选出所有长度为 k 的组合。",
             why="回溯（模板 A）。「所有组合」= 枚举方案本身。"
                 "剪枝点：当剩下的数不够凑满 k 个时直接返回，`range(start, n - (k - len(path)) + 2)`。"),
        dict(num=17, pattern=9, options=[9, 16, 2],
             prompt="给一串电话数字，返回它能表示的所有字母组合。",
             why="回溯。每一位数字对应一层，本层的选择列表就是这个数字映射的几个字母。"
                 "「所有组合」+ 输入长度很短（≤ 4），指数级枚举被默许。"),
        dict(num=377, pattern=16, options=[9, 16, 8],
             prompt="给一个无重复正整数数组和目标值，求**总和为目标值的组合个数**（顺序不同算不同）。",
             why="**一维 DP，不是本章**——名字里带 Combination，要的却只是**个数**。"
                 "回溯枚举完再数是指数级；`dp[t] = Σ dp[t - num]` 是 O(n·target)。"
                 "见 §2 分流条件：要方案本身才回溯，要个数就 DP。"),
    ],
)
