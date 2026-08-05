# 增量任务：为现有算法面试手册新增「附录 A · Python 刷题急救包」

> 交给已有 handbook 项目的 Claude Code。这是单页增量任务，不是重建。

## 集成要求

1. 新增一个页面「附录 A · Python 刷题急救包」，位置在导读之后、第 01 章之前；导航与全局页面计数程序化更新（禁止手改数字）。
2. 导读页加一句指引：**"太久没自己写代码 → 先完成附录 A 再进正文。"**
3. 视觉体系、dark mode 默认、组件风格与现有站点完全一致；本页 quiz 组件用"改错"题型（见规格 §4）。
4. 适用的既有质量校验必须跑：10 道题的 LeetCode 链接做"题号↔slug↔题名"三方核对；速查表内所有代码片段实际执行验证（含反例注释的正确性）；发布前站级横切检查。

## 页面完整规格

> 定位：**复健，不是学习**。读者会 Python，只是长期把写代码委托给 AI 后手感萎缩。
> 核心原则：**这一章的主体动作是打字，不是阅读**。速查部分一屏为限，练习部分才是重点。

---

## §1 先划定范围（写进开头，降低心理负担）

LeetCode Python 是整个语言的一个极小子集，约 30 个惯用法覆盖 95% 的题。

**明确不需要**：装饰器、生成器进阶、async、类型系统进阶、包管理、面向对象设计——刷题用不到，一个都不用碰。

## §2 惯用法速查（单屏，按使用频率排序）

**容器基本功**
```python
a = [0] * n                # 一维初始化
g = [[0] * n for _ in range(m)]   # 二维——注意:[[0]*n]*m 是 m 个同一引用,经典大坑
a[i:j], a[::-1]            # 切片、反转
d.get(k, 0); d[k] = d.get(k, 0) + 1   # 计数三连
s.add(x); x in s           # set:O(1) 存在性
```

**遍历三件套**
```python
for i, x in enumerate(nums): ...
for a, b in zip(xs, ys): ...
[f(x) for x in nums if cond(x)]      # 推导式
```

**排序**
```python
nums.sort()                          # 原地
sorted(pairs, key=lambda p: (p[0], -p[1]))   # 多关键字,负号降序
```

**collections + heapq 四件套**
```python
from collections import deque, Counter, defaultdict
import heapq
q = deque(); q.append(x); q.popleft()        # BFS/单调队列
Counter(s)                                    # 频次统计
defaultdict(list)                             # 建图
heapq.heappush(h, x); heapq.heappop(h)        # 最小堆;要最大堆就 push -x
```

**LeetCode 特有语法**
```python
float('inf')               # 无穷大
7 // 2, -7 // 2            # 整除向下取整:后者是 -4 不是 -3,DP 边界常见坑
class ListNode: ...        # 题目自带,会读会用即可
import sys; sys.setrecursionlimit(10**6)      # 深递归保险
```

**五个 Python 专属翻车点**（各配一行反例）
1. `[[0]*n]*m` 引用陷阱
2. 可变默认参数 `def f(x, memo={})` 跨调用共享
3. 递归里改外层变量要 `nonlocal`
4. `heapq` 只有最小堆，最大堆取负
5. 没有 `++`；`x += 1`

## §3 打字复健计划（本章主体）

**规则（加粗印在页面上）**：手打，编辑器关掉 AI 补全，每道 ≤15 分钟；卡住看速查表，不看题解；打完在 LeetCode 提交验证。

10 道复健题，每道标注它复健的惯用法，同时全部是正文各章的热身题（双重用途，做完即完成 40% 热身进度）：

| # | 题 | 复健目标 |
|---|----|---------|
| 1 | 1 Two Sum | dict 计数/查找 |
| 2 | 217 Contains Duplicate | set |
| 3 | 242 Valid Anagram | Counter |
| 4 | 125 Valid Palindrome | 字符串方法、双指针 |
| 5 | 20 Valid Parentheses | list 当栈 |
| 6 | 704 Binary Search | 下标边界 |
| 7 | 121 Best Time to Buy and Sell Stock | 单次遍历 + 打擂台 |
| 8 | 70 Climbing Stairs | dp 数组初始化 |
| 9 | 206 Reverse Linked List | ListNode、多变量赋值 |
| 10 | 104 Maximum Depth of Binary Tree | 递归 |

页面提供每题的"复健自查"折叠块（不是题解）：只列本题会用到的速查表条目编号，卡住时按图索骥。

**出口标准**：10 道全部一次提交通过（或第二次），且没有一道超时 15 分钟 → 关闭本章，进入正文第 01 章。达不到就重打不达标的题，不加新题。

## §4 交互组件

沿用系列 quiz 组件，本章题型为"改错"：展示带一个 Python 专属翻车点的代码片段（§2 的五个坑），30 秒内指出错在哪。5 题。
