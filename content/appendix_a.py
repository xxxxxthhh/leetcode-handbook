# -*- coding: utf-8 -*-
"""附录 A · Python 刷题急救包。

定位：复健，不是学习——读者会 Python，只是长期把写代码委托给 AI 后手感萎缩。
本页主体动作是打字，不是阅读。

与各章模板同一约束：页面上展示的每一行代码，就是 run_templates.py 拿去
exec 的那一份（含注释里的反例声明）。条目契约：
  id      str   速查表编号（C/T/S/Q/L 分组 + 序号），供 §3「复健自查」引用
  code    str   页面展示的代码，单行；run=False 时只展示不执行（如 SyntaxError 反例）
  setup   str   执行 code 前的准备语句（不上页面）
  verify  str   执行 code 后的断言，逐条验证注释里的说法（含反例）

PITFALLS 的 bad 字段同 code；QUIZ 的 code 是带 bug 的展示片段，verify 里以
SNIPPET 变量拿到同一字符串，编译/执行它来证明 bug 是真的——展示与被测同源。
"""

# ---------------------------------------------------------------- §1 划定范围
INTRO = [
    "这一页做的是**复健，不是学习**：你会 Python，只是长期把写代码这件事"
    "委托给 AI 之后，手感萎缩了。所以本页的主体动作是**打字，不是阅读**——"
    "§2 的速查表是拿来**查**的，不是拿来读的；§3、§4 的练习篇幅是它的两倍，那才是重点。",
    "先把范围划死，降低心理负担：LeetCode Python 是整个语言的一个极小子集。"
    "下面 {n_entries} 条惯用法加 {n_pits} 个专属翻车点，覆盖刷题日常会碰到的绝大部分写法——"
    "每一条都在构建时实际执行验证过，**包括注释里的反例**。碰到没收录的写法很正常，"
    "查一下就行，不必回头补课。",
]

NO_NEED_LEAD = "以下内容刷题用不到，**一个都不用碰**："
NO_NEED = [
    "装饰器",
    "生成器进阶（`yield from`、协程式用法）",
    "async / await",
    "类型系统进阶（泛型、Protocol）",
    "包管理（venv / pip / poetry）",
    "面向对象设计（继承体系、魔术方法）",
]

# ---------------------------------------------------------------- §2 惯用法速查
GROUPS = [
    dict(title="容器基本功", entries=[
        dict(id="C1",
             code="a = [0] * n                          # 一维初始化：n 个 0",
             setup="n = 8",
             verify="assert a == [0, 0, 0, 0, 0, 0, 0, 0] and len(a) == n"),
        dict(id="C2",
             code="g = [[0] * n for _ in range(m)]      # 二维初始化；[[0]*n]*m 是 m 份同一引用（翻车点①）",
             setup="m, n = 3, 4",
             verify="g[0][0] = 1\n"
                    "assert g[1][0] == 0 and g[2][0] == 0   # 各行独立\n"
                    "bad = [[0] * n] * m\n"
                    "bad[0][0] = 1\n"
                    "assert bad[1][0] == 1 and bad[2][0] == 1   # 反例：改一行等于改所有行"),
        dict(id="C3",
             code="a[i:j], a[::-1]                      # 切片左闭右开；[::-1] 反转",
             setup="a = [1, 2, 3, 4, 5]\ni, j = 1, 3",
             verify="assert a[i:j] == [2, 3]            # 含 i 不含 j\n"
                    "assert a[::-1] == [5, 4, 3, 2, 1]\n"
                    "assert a == [1, 2, 3, 4, 5]        # 两者都不改原数组"),
        dict(id="C4",
             code="d[k] = d.get(k, 0) + 1               # dict 计数三连：键不存在按 0 算",
             setup="d = {}\nk = 'x'",
             verify="assert d == {'x': 1}\n"
                    "d[k] = d.get(k, 0) + 1\n"
                    "assert d[k] == 2"),
        dict(id="C5",
             code="s.add(x); x in s                     # set：O(1) 判断存在性",
             setup="s = set()\nx = 3",
             verify="assert 3 in s and 4 not in s"),
        dict(id="C6",
             code="st.append(x); st.pop()               # list 当栈：同侧进出，栈顶是 st[-1]",
             setup="st = [1]\nx = 2",
             verify="assert st == [1]                   # 刚 append 的 2 又被 pop 走了\n"
                    "st.append(9)\n"
                    "assert st[-1] == 9"),
        dict(id="C7",
             code="max(best, x), min(xs), sum(xs)       # 打擂台与聚合；max 还能带 key=",
             setup="best, x = 3, 7\nxs = [4, 1, 9]",
             verify="assert (max(best, x), min(xs), sum(xs)) == (7, 1, 14)\n"
                    "assert max(['aa', 'b'], key=len) == 'aa'"),
    ]),
    dict(title="遍历三件套", entries=[
        dict(id="T1",
             code="for i, x in enumerate(nums): ...     # 要下标也要值",
             setup="nums = [10, 20, 30]",
             verify="assert (i, x) == (2, 30)"),
        dict(id="T2",
             code="for a, b in zip(xs, ys): ...         # 并排走两个序列，短的一停全停",
             setup="xs = [1, 2, 3]\nys = [4, 5]",
             verify="assert (a, b) == (2, 5)            # 只走了两轮：短的先停"),
        dict(id="T3",
             code="out = [f(x) for x in nums if ok(x)]  # 推导式：过滤 + 变换一行完成",
             setup="f = lambda v: v * v\nok = lambda v: v % 2 == 1\nnums = [1, 2, 3]",
             verify="assert out == [1, 9]"),
    ]),
    # 组号字母只是给 §3 引用用的标签，与内容无关：W = Word（字符串）
    dict(title="字符串", entries=[
        dict(id="W1",
             code="s.lower(), c.isalnum()               # 归一化 / 判断字母数字：125 靠这两个过滤",
             setup="s = 'AbC'\nc = '!'",
             verify="assert s.lower() == 'abc'\n"
                    "assert c.isalnum() is False and 'a'.isalnum() is True"),
        dict(id="W2",
             code="''.join(chs), s.split()              # 拼接 / 按空白切分；字符串不可变，不能改单个字符",
             setup="chs = ['a', 'b', 'c']\ns = 'x  y'",
             verify="assert ''.join(chs) == 'abc' and s.split() == ['x', 'y']\n"
                    "try:\n"
                    "    s[0] = 'z'\n"
                    "except TypeError:\n"
                    "    pass\n"
                    "else:\n"
                    "    raise AssertionError('字符串应当不可变')   # 反例：想原地改字符只能先转 list"),
    ]),
    dict(title="排序", entries=[
        dict(id="S1",
             code="nums.sort()                          # 原地升序；返回 None，别写 nums = nums.sort()",
             setup="nums = [3, 1, 2]",
             verify="assert nums == [1, 2, 3]\n"
                    "assert [1].sort() is None          # 反例：接返回值只会接到 None"),
        dict(id="S2",
             code="pairs.sort(key=lambda p: (p[0], -p[1]))  # 多关键字；数值键取负 = 这一键降序",
             setup="pairs = [(1, 2), (0, 9), (1, 5)]",
             verify="assert pairs == [(0, 9), (1, 5), (1, 2)]"),
    ]),
    dict(title="collections + heapq 四件套", entries=[
        dict(id="Q1",
             code="from collections import deque, Counter, defaultdict",
             verify="assert callable(deque) and callable(Counter) and callable(defaultdict)"),
        dict(id="Q2",
             code="q = deque(); q.append(x); q.popleft()  # BFS 队列：右进左出，两头都是 O(1)",
             setup="from collections import deque\nx = 7",
             verify="assert len(q) == 0                 # 刚 append 的 7 又被 popleft 走了\n"
                    "q.append(1); q.append(2)\n"
                    "assert q.popleft() == 1            # 先进先出"),
        dict(id="Q3",
             code="Counter(s)                           # 一行频次统计，可当 dict 用",
             setup="from collections import Counter\ns = 'aab'",
             verify="assert Counter(s) == {'a': 2, 'b': 1}\n"
                    "assert Counter(s)['z'] == 0        # 不存在的键不抛错，返回 0"),
        dict(id="Q4",
             code="g = defaultdict(list); g[u].append(v)  # 建图：首次访问自动变 []",
             setup="from collections import defaultdict\nu, v = 1, 2",
             verify="assert g[1] == [2]\n"
                    "assert g[3] == []                  # 没建过的点也能直接读"),
        dict(id="Q5",
             code="heapq.heappush(h, x); heapq.heappop(h)  # 最小堆；要最大堆就 push -x，3.14 起另有 heappush_max（翻车点④）",
             setup="import heapq\nh = [5, 1]\nheapq.heapify(h)\nx = 3",
             verify="assert heapq.heappop(h) == 3       # 刚才那次 heappop 弹走了最小的 1"),
    ]),
    dict(title="LeetCode 特有语法", entries=[
        dict(id="L1",
             code="best = float('inf')                  # 打擂台初始值；负无穷 float('-inf')",
             verify="assert best > 10 ** 18 and -best == float('-inf')"),
        dict(id="L2",
             code="7 // 2, -7 // 2                      # 整除向下取整：结果是 3 和 -4（不是 -3），DP 边界常见坑",
             verify="assert (7 // 2, -7 // 2) == (3, -4)"),
        dict(id="L3",
             code="a, b = b, a + b                      # 平行赋值：右边整体先求值；链表反转 / 滚动 DP 靠它",
             setup="a, b = 0, 1",
             verify="assert (a, b) == (1, 1)"),
        dict(id="L4",
             code="class ListNode: ...                  # 题目自带的定义，会读会用即可，不用自己写",
             verify="assert isinstance(ListNode, type)"),
        dict(id="L5",
             code="import sys; sys.setrecursionlimit(10 ** 6)   # 深递归保险（树 / 图 DFS 防爆栈）",
             setup="import sys as _sys\n_orig = _sys.getrecursionlimit()",
             verify="assert sys.getrecursionlimit() == 10 ** 6\n"
                    "sys.setrecursionlimit(_orig)       # 验证完还原，别影响别的测试"),
    ]),
]

# ---------------------------------------------------------------- §2 翻车点
PITFALLS = [
    dict(id="P1", title="二维初始化的引用陷阱",
         bad="g = [[0] * n] * m        # m 行是同一个 list 的 m 个引用",
         why="改 `g[0][0]` 等于改每一行——正确写法见 C2 的列表推导。",
         setup="m, n = 3, 4",
         verify="g[0][0] = 1\nassert g[1][0] == 1 and g[2][0] == 1"),
    dict(id="P2", title="可变默认参数跨调用共享",
         bad="def f(x, memo={}): memo[x] = 1; return len(memo)",
         why="默认值只在函数**定义时**创建一次，第二次调用还是同一个 dict。"
             "要缓存就写 `memo=None`，函数体里再建。",
         verify="assert f(1) == 1\n"
                "assert f(2) == 2                       # 第二次调用看见了第一次的残留"),
    dict(id="P3", title="闭包里改外层变量要 nonlocal",
         bad="def outer():\n"
             "    cnt = 0\n"
             "    def inner():\n"
             "        cnt += 1          # 少了 nonlocal cnt\n"
             "    inner()",
         why="函数内一旦对某个名字赋值，Python 就把它当本地变量，"
             "读它就 `UnboundLocalError`。在 `inner` 开头加 `nonlocal cnt`。",
         verify="try:\n"
                "    outer()\n"
                "except UnboundLocalError:\n"
                "    pass\n"
                "else:\n"
                "    raise AssertionError('应触发 UnboundLocalError')"),
    dict(id="P4", title="heapq 默认是最小堆",
         bad="largest = heapq.heappop(h)   # 想要最大值？弹出来的偏偏是最小值",
         why="`heappop` 永远弹最小。要最大堆：push 时存 `-x`，pop 后取负还原（见 Q5）；"
             "Python 3.14 起也可用 `heappush_max` / `heappop_max`，先确认面试环境的版本。",
         setup="import heapq\nh = [5, 1, 9]\nheapq.heapify(h)",
         verify="assert largest == 1"),
    dict(id="P5", title="没有 ++ / --",
         bad="i++                       # SyntaxError；更阴险的是 ++i 合法但什么都不做",
         run=False,
         why="自增只有 `i += 1`。`++i` 是两个一元正号，静默等于 `i`，连报错都不给。",
         verify="try:\n"
                "    compile('i++', '<pit>', 'exec')\n"
                "except SyntaxError:\n"
                "    pass\n"
                "else:\n"
                "    raise AssertionError('i++ 应当是 SyntaxError')\n"
                "i = 5\n"
                "assert (++i) == 5 and i == 5           # ++i 合法、无效果，最阴险"),
]

# ---------------------------------------------------------------- §3 打字复健计划
RULES = [
    "**手打每一行**，禁止复制粘贴；",
    "**编辑器关掉 AI 补全**（Copilot / Cursor Tab / 各种 …）；",
    "每道 **≤ 15 分钟**；",
    "卡住**看速查表，不看题解**——每题下方的「复健自查」告诉你看哪几条；",
    "打完**在 LeetCode 提交验证**，不是在脑子里跑一遍。",
]

# refs 是 §2 的条目编号，构建时逐个核对存在性；
# 每题「出自正文哪一章哪一层」由 content/ 派生，不在这里手写。
# 顺序按数据结构由简到繁（数组/哈希 → 字符串 → 栈 → 二分 → DP → 链表 → 树），
# 不是正文章号顺序——页面上的说明文字必须跟这里一致。
PROBLEMS = [
    dict(num=1,   goal="dict 计数 / 查找", refs=["C4", "T1"]),
    dict(num=217, goal="set 判存在", refs=["C5"]),
    dict(num=242, goal="Counter / 手写计数", refs=["Q3", "C4"]),
    dict(num=125, goal="字符串方法、双指针", refs=["W1", "C3"]),
    dict(num=20,  goal="list 当栈", refs=["C6", "C4"]),
    dict(num=704, goal="下标边界、整除", refs=["L2"]),
    dict(num=121, goal="单次遍历 + 打擂台", refs=["L1", "C7", "T1"]),
    dict(num=70,  goal="dp 数组初始化 / 滚动变量", refs=["C1", "L3"]),
    dict(num=206, goal="ListNode、平行赋值", refs=["L4", "L3"]),
    dict(num=104, goal="递归 + 取较大者", refs=["C7", "L5"]),
]

EXIT = ("{n_prob} 道**全部一次提交通过（或第二次）**，且没有一道超过 15 分钟 → "
        "关闭本页，进入正文。达不到就重打不达标的那几道——**不加新题**。")

# ---------------------------------------------------------------- §4 改错自测
# 五题与 PITFALLS 一一对应。options 按书写顺序给出，构建时用题号做种子打乱；
# answer 是正确选项的 key。verify 在 SNIPPET（即 code 本体）上证明 bug 是真的。
#
# 选项长度必须拉平：初版四个干扰项写得比正确项短，读者不看代码、挑最长的那条就能刷分
# ——和早期「正确答案一律排第一位」是同一类缺陷，只是从位置换成了长度。
# check_site.py 的 check_appendix 同时盯位置分布与「正确项是否总是最长」。
QUIZ = [
    dict(code="rows, cols = 3, 4\n"
              "visited = [[False] * cols] * rows\n"
              "visited[0][0] = True",
         options=[
             ("a", "第 2 行：3 行其实是同一个 list，标一格等于整列都标了"),
             ("b", "第 2 行：行列写反了，应该写成 [[False] * rows] * cols"),
             ("c", "第 3 行：二维下标不能连写，要改成 visited[0, 0] 这种"),
             ("d", "没有错：这段代码建出了 3 行 4 列的独立标记表"),
         ],
         answer="a",
         why="翻车点①：`[[False]*cols]*rows` 复制的是**引用**。"
             "要 rows 份独立的行，只能用列表推导（见 C2）。",
         verify="ns = {}\n"
                "exec(SNIPPET, ns)\n"
                "assert ns['visited'][1][0] is True and ns['visited'][2][0] is True"),
    dict(code="def collect(node, acc=[]):\n"
              "    acc.append(node)\n"
              "    return acc",
         options=[
             ("a", "acc=[] 只在定义时建一次，第二次调用带着上次的结果"),
             ("b", "list 不能当参数默认值，这个函数定义时就会 TypeError"),
             ("c", "append 返回 None，第 2 行得写成 acc = acc.append(node)"),
             ("d", "没有错：每次调用都会拿到一个新的空 list"),
         ],
         answer="a",
         why="翻车点②：可变默认参数跨调用共享。习惯写法 `acc=None`，"
             "函数体里 `if acc is None: acc = []`。",
         verify="ns = {}\n"
                "exec(SNIPPET, ns)\n"
                "assert ns['collect'](1) == [1]\n"
                "assert ns['collect'](2) == [1, 2]      # 第二次调用带着上一次的结果"),
    dict(code="def count_leaves(root):\n"
              "    total = 0\n"
              "    def dfs(node):\n"
              "        if node is None:\n"
              "            return\n"
              "        if not node.left and not node.right:\n"
              "            total += 1\n"
              "        dfs(node.left)\n"
              "        dfs(node.right)\n"
              "    dfs(root)\n"
              "    return total",
         options=[
             ("a", "dfs 给 total 赋值却没写 nonlocal，碰到叶子就抛错"),
             ("b", "Python 不允许在函数里定义函数，再让它递归调用自己"),
             ("c", "not node.left 判断永远为假，得写 node.left is None"),
             ("d", "没有错：这个函数能正确数出二叉树的叶子数"),
         ],
         answer="a",
         why="翻车点③：`total += 1` 让 Python 把 total 当 dfs 的本地变量。"
             "在 dfs 开头加 `nonlocal total`，或改成 dfs 返回计数再相加。",
         verify="ns = {}\n"
                "exec(SNIPPET, ns)\n"
                "class N:\n"
                "    left = right = None\n"
                "try:\n"
                "    ns['count_leaves'](N())\n"
                "except UnboundLocalError:\n"
                "    pass\n"
                "else:\n"
                "    raise AssertionError('应触发 UnboundLocalError')"),
    dict(code="import heapq\n"
              "\n"
              "def top3(nums):\n"
              "    h = list(nums)\n"
              "    heapq.heapify(h)\n"
              "    return [heapq.heappop(h) for _ in range(3)]   # 想拿最大的 3 个",
         options=[
             ("a", "heappop 弹的是最小值，这里拿到的是最小的 3 个"),
             ("b", "heapify 建的是无序堆，取前 3 个之前必须先 sort"),
             ("c", "range(3) 少拿了一个，应该写成 range(1, 4) 才对"),
             ("d", "没有错：heapify 之后堆顶就是最大的那个元素"),
         ],
         answer="a",
         why="翻车点④：`heappop` 弹的是最小值。push 时取负、pop 后还原，"
             "或者直接 `heapq.nlargest(3, nums)`（3.14 起也可用 `heappush_max` 等，先确认环境版本）。",
         verify="ns = {}\n"
                "exec(SNIPPET, ns)\n"
                "assert ns['top3']([5, 1, 9, 7]) == [1, 5, 7]   # 拿到的是最小的 3 个"),
    dict(code="def total(nums):\n"
              "    s, i = 0, 0\n"
              "    while i < len(nums):\n"
              "        s += nums[i]\n"
              "        i++\n"
              "    return s",
         options=[
             ("a", "Python 没有 ++，i++ 是语法错误，只能写 i += 1"),
             ("b", "while 条件应写 i <= len(nums) - 1，现在会越界"),
             ("c", "s += nums[i] 不适用于 int，得写 s = s + nums[i]"),
             ("d", "没有错：这段代码能正确求出数组的和"),
         ],
         answer="a",
         why="翻车点⑤：`i++` 连运行的机会都没有——编译期就 SyntaxError。"
             "更阴险的是前缀 `++i` 合法但什么都不做。",
         verify="try:\n"
                "    compile(SNIPPET, '<quiz>', 'exec')\n"
                "except SyntaxError:\n"
                "    pass\n"
                "else:\n"
                "    raise AssertionError('i++ 应当在编译期就报 SyntaxError')"),
]


def runnable():
    """给 reference/run_templates.py 的执行清单：速查条目 + 翻车点反例 + 改错题证据。"""
    items = []
    for g in GROUPS:
        for e in g["entries"]:
            items.append(dict(label="附录A {}".format(e["id"]),
                              setup=e.get("setup", ""),
                              code=e["code"] if e.get("run", True) else "",
                              verify=e["verify"]))
    for p in PITFALLS:
        items.append(dict(label="附录A {} {}".format(p["id"], p["title"]),
                          setup=p.get("setup", ""),
                          code=p["bad"] if p.get("run", True) else "",
                          verify=p["verify"]))
    for i, q in enumerate(QUIZ, 1):
        items.append(dict(label="附录A 改错Q{}".format(i), setup="", code="",
                          verify=q["verify"], snippet=q["code"]))
    return items
