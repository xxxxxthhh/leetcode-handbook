# 算法面试阈值手册 · 全书骨架 v1

> 系列格式：双语 HTML 电子书（中文讲解 + 英文术语/题名保留原文），dark mode 默认，与 options / AI systems / CCAR 手册同一视觉体系。
> 定位：**工具书而非阅读书**。成功标准 = 面试前一晚翻 30 分钟就够。

---

## 1. 项目定位与阈值标准

本书服务于"阈值策略"：达到面试不翻车的水平即停，不追求竞赛级精通。三条可验证的达标标准，全书所有设计都为它们服务：

1. **模式识别 ≤ 5 分钟**：陌生 medium 题，5 分钟内说出所属模式和思路框架。
2. **陌生 medium 25–30 分钟写出能跑的代码**，并说出时间/空间复杂度。
3. **18 个核心模式全覆盖**（见章节清单）。

**明确不覆盖**（写进导读，作为承诺）：线段树、树状数组、KMP/后缀数组、计算几何、高级位运算、竞赛数论。

达标后的维持模式：每周 3–5 题 = 错题重做 + 随机抽模式保手感（错题登记页是输入源）。

## 2. 技术规格

- 代码语言：**Python**（模板可默写为目标，尽量短）
- 每道题直接链接 LeetCode：`https://leetcode.com/problems/{slug}/`（读者有 Premium，可含 premium 题，标注 🔒）
- 交互组件沿用系列：quiz 组件改造为 **"30 秒识别模式"题型**（给题面 → 选模式 → 解释识别信号）
- 工作流：chat 产出骨架 + 样章规格 → Claude Code 全量构建（CLAUDE.md 写入本 spec + 六条批量生产质量教训）

## 3. 页面结构（共 21 页）

| # | 页面 | 说明 |
|---|------|------|
| 00 | 导读 | 阈值策略、三条达标标准、不覆盖清单、如何使用本书、维持模式说明 |
| 01–18 | 模式章节 | 五段固定结构（见 §4） |
| 19 | 模式决策树 / 速查表 | 面试前一晚看的那一页：关键词 → 模式 → 模板索引，单屏可打印 |
| 20 | 错题登记页 | 可交互记录（localStorage 不可用则纯打印表格），字段：题号、模式、翻车点、重做日期 |

## 4. 每章五段固定结构（硬性约束，所有章节一致）

1. **一句话心智模型**：最直白的话讲透本模式。全章最先写、最反复打磨的一句。
2. **识别信号**：题面关键词 → 触发本模式的映射表（全书最值钱部分，直接服务达标标准 1）。
3. **模板代码**：一个可默写的 Python 模板；用注释标出【骨架行】（不变）与【插槽行】（随题变化）。一个模式多个子模板时上限 2 个。
4. **题目分层**：热身（easy，建直觉）1 道 → 标准（medium，模板直接套）2–3 道 → 变体（模板要扭、坑的来源）1–2 道。Hard 只做"认脸"级，标注 ⭐认脸即可。
5. **常见翻车点 + 自测**：3–5 条翻车点；自测 = 2–3 道"30 秒识别模式"题（题面来自本章未收录的同模式题）。

## 5. 章节清单与选题

题目总量约 130，NeetCode 150 为骨架并按模式重组。🔒 = premium，⭐ = hard 认脸即可。

### 01 哈希（Hash Map / Set）
心智模型方向：用空间换"我见过你吗"的 O(1) 回答。
- 热身：1 Two Sum · 217 Contains Duplicate
- 标准：242 Valid Anagram · 49 Group Anagrams · 128 Longest Consecutive Sequence
- 变体：36 Valid Sudoku

### 02 双指针
方向：有序或对称结构里，两端/快慢协同收缩搜索空间。
- 热身：125 Valid Palindrome
- 标准：167 Two Sum II · 15 3Sum · 11 Container With Most Water
- 变体：42 Trapping Rain Water ⭐

### 03 滑动窗口
方向：连续区间问题，右扩左缩维护一个"合法窗口"。
- 热身：121 Best Time to Buy and Sell Stock
- 标准：3 Longest Substring Without Repeating Characters · 424 Longest Repeating Character Replacement · 567 Permutation in String
- 变体：76 Minimum Window Substring ⭐

### 04 栈与单调栈（样章）
方向：单调栈 = 每个元素在找"左/右第一个比我大（小）的人"。
- 热身：20 Valid Parentheses · 155 Min Stack
- 标准：739 Daily Temperatures · 496 Next Greater Element I（+503 循环数组变形）
- 变体：853 Car Fleet · 84 Largest Rectangle in Histogram ⭐ · 239 Sliding Window Maximum ⭐（单调队列，注明与滑窗的交叉）

### 05 二分查找
方向：不止搜位置，还能搜答案本身——条件是判定函数单调。
- 热身：704 Binary Search
- 标准：74 Search a 2D Matrix · 153 Find Minimum in Rotated Sorted Array · 33 Search in Rotated Sorted Array
- 变体（答案二分）：875 Koko Eating Bananas · 410 Split Array Largest Sum ⭐ · 4 Median of Two Sorted Arrays ⭐

### 06 链表
方向：只有指针改写和快慢指针两件事；画图 > 心算。
- 热身：206 Reverse Linked List
- 标准：21 Merge Two Sorted Lists · 141/142 Linked List Cycle I/II · 19 Remove Nth Node From End · 143 Reorder List
- 变体：138 Copy List with Random Pointer · 146 LRU Cache · 23 Merge k Sorted Lists ⭐（与堆交叉）

### 07 树的遍历与递归
方向：一切树题 = "对当前节点做什么 + 递归左右"的填空。
- 热身：226 Invert Binary Tree · 104 Maximum Depth
- 标准：543 Diameter of Binary Tree · 110 Balanced Binary Tree · 102 Level Order Traversal · 98 Validate BST · 230 Kth Smallest in BST · 235/236 Lowest Common Ancestor
- 变体：105 Construct from Preorder & Inorder · 124 Binary Tree Maximum Path Sum ⭐ · 297 Serialize and Deserialize ⭐

### 08 堆 / Top-K
方向：只关心第 K 个时，不排序，养一个大小为 K 的堆。
- 热身：703 Kth Largest Element in a Stream
- 标准：215 Kth Largest Element in an Array · 347 Top K Frequent Elements · 973 K Closest Points to Origin
- 变体：621 Task Scheduler · 295 Find Median from Data Stream ⭐（对顶堆）

### 09 回溯
方向：做选择 → 递归 → 撤销选择；剪枝决定生死。
- 热身：78 Subsets
- 标准：39 Combination Sum · 46 Permutations · 90 Subsets II · 79 Word Search
- 变体：131 Palindrome Partitioning · 51 N-Queens ⭐

### 10 图的 BFS/DFS
方向：网格也是图；visited 集合是命根子。
- 热身：200 Number of Islands
- 标准：133 Clone Graph · 695 Max Area of Island · 994 Rotting Oranges（多源 BFS）· 130 Surrounded Regions
- 变体：417 Pacific Atlantic Water Flow · 127 Word Ladder ⭐

### 11 拓扑排序
方向："依赖关系"三个字出现就是它；入度为 0 进队列。
- 标准：207 Course Schedule · 210 Course Schedule II
- 变体：269 Alien Dictionary 🔒⭐

### 12 并查集
方向：动态连通性——"这俩在不在一伙"。
- 标准：547 Number of Provinces · 684 Redundant Connection · 261 Graph Valid Tree 🔒 · 323 Number of Connected Components 🔒
- 变体：721 Accounts Merge

### 13 前缀和
方向：区间和问题一次预处理，之后 O(1)；配哈希可解"子数组和为 K"。
- 热身：303 Range Sum Query
- 标准：238 Product of Array Except Self · 560 Subarray Sum Equals K
- 变体：523 Continuous Subarray Sum

### 14 区间
方向：先按起点排序，剩下的就是"重叠怎么办"。
- 标准：56 Merge Intervals · 57 Insert Interval · 435 Non-overlapping Intervals
- 变体：252/253 Meeting Rooms I/II 🔒

### 15 贪心
方向：能贪的题都有一个"局部最优不毁全局"的性质，先说出它再动手。
- 热身：53 Maximum Subarray（Kadane，注明与 DP 的边界）
- 标准：55 Jump Game · 45 Jump Game II · 134 Gas Station
- 变体：763 Partition Labels · 846 Hand of Straights

### 16 一维 DP
方向：dp[i] 只依赖前几项；先写状态定义再写转移。
- 热身：70 Climbing Stairs
- 标准：198 House Robber · 213 House Robber II · 322 Coin Change · 139 Word Break
- 变体：91 Decode Ways · 152 Maximum Product Subarray

### 17 二维 DP 与背包
方向：两个维度各自"取到 i / 容量 j"；背包 = 选或不选。
- 热身：62 Unique Paths
- 标准：1143 Longest Common Subsequence · 416 Partition Equal Subset Sum · 494 Target Sum
- 变体：309 Best Time with Cooldown · 72 Edit Distance ⭐认脸级讲解

### 18 子序列 DP（LIS 类）
方向：LIS 两解法——O(n²) DP 与"耐心排序 + 二分"，面试说前者写后者可加分。
- 标准：300 Longest Increasing Subsequence
- 变体：673 Number of Longest Increasing Subsequence · 354 Russian Doll Envelopes ⭐

## 6. 质量控制（写入 CLAUde.md）

沿用 AI systems 手册六条批量生产教训，另加本书专属校验器：

1. **链接校验**：所有 LeetCode 链接按"题号 ↔ slug ↔ 题名"三方一致性程序化核对，禁止凭记忆生成 slug 不核对。
2. **模板可运行**:每章 Python 模板必须附一个最小测试用例并实际执行通过。
3. **决策树完备性**：第 19 页决策树程序化核对覆盖全部 18 个模式、无重复叶子。
4. **五段结构校验**：每章程序化检查五段齐全、题目分层数量符合 §4 约束。
5. **识别信号无冲突**：全书识别信号表汇总后人工审一遍，确保同一关键词不会指向矛盾的模式（如"连续子数组"同时出现在滑窗与前缀和时，必须写清分流条件）。

## 7. 下一步

1. 样章：**第 04 章 栈与单调栈**（验证"一句话讲透 + 五段结构"的写法）
2. 样章通过后 → 打包 CLAUDE.md + 本骨架 → Claude Code 全量构建
