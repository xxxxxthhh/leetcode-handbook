# 算法面试阈值手册

双语 HTML 电子书（中文讲解 + 英文术语/题名保留原文），dark mode 默认，可打印导出 PDF。
定位是**工具书而非阅读书**：成功标准 = 面试前一晚翻 30 分钟就够。

规格见 [`spec/skeleton.md`](spec/skeleton.md)（附录 A 另见 [`spec/appendix-a.md`](spec/appendix-a.md)），
体例基准见 [`spec/ch04-sample.md`](spec/ch04-sample.md)，构建约定见 [`CLAUDE.md`](CLAUDE.md)。

## 怎么看

直接打开 `index.html`，或起一个静态服务器：

```bash
python3 -m http.server 4173
```

## 仓库结构

```
index.html              目录页
chapters/00-intro.html  导读
chapters/appendix-a.html  附录 A · Python 刷题急救包（复健页：速查 + 10 道手打题 + 改错自测）
chapters/NN-*.html      18 个模式章（五段固定结构）
cheatsheet.html         第 19 页 · 模式决策树 / 速查表（单屏可打印）
mistakes.html           第 20 页 · 错题登记（localStorage，可退化成打印空表）
assets/                 样式与三个渐进增强脚本
data/leetcode-index.json      LeetCode 官方题目索引（裁剪到本书用到的题）
data/signal-conflicts.md      识别信号冲突汇总（构建产物，供人工审读）

content/                ← 唯一数据源
  patterns.py           18 个模式的骨架：章号 / 标题 / 文件名 / 分组 / 冲突关键词
  chNN-*.py             一章的五段内容
  appendix_a.py         附录 A：速查条目 / 翻车点 / 复健题单 / 改错自测（每条代码都带可执行验证）
  tree.py               决策树的分支结构（叶子指向章节，不重写识别信号）
  intro.py              导读正文（数字全部用占位符，构建时填）
reference/              构建期脚本，不是读者要看的页面
```

**HTML 是构建产物**：不要手改 `chapters/*.html`，改 `content/` 后重新构建。

## 构建与校验

```bash
python3 reference/check_all.py
```

这一条命令按顺序跑完：模板可运行 → 构建 22 页 → 站级校验 → mutation test。发布前必须全绿。

单独跑：

| 命令 | 做什么 |
|---|---|
| `python3 reference/fetch_lc_index.py` | 从 LeetCode 官方索引重抓题目元数据（新增题目后必跑） |
| `python3 reference/run_templates.py [章号…]` | 把每章模板原样 `exec`，再跑它的测试用例；全量跑时附录 A 的速查片段、反例与改错题证据也逐条执行 |
| `python3 reference/build.py [--out DIR]` | 渲染全部页面 |
| `python3 reference/check_site.py [--site DIR]` | 站级校验，跑在渲染产物 HTML 上 |
| `python3 reference/check_vs_spec.py` | 逐章逐层比对 `spec/skeleton.md` §5 的选题清单 |
| `python3 reference/mutation_test.py` | 往内容层注入 22 种真实错误，确认校验器都能抓到 |

## 三条设计约束

1. **题名 / slug / 难度 / 🔒 一律派生，不手写。** 全部来自 `data/leetcode-index.json`
   （LeetCode 官方索引，文件里记录了抓取日期）。「链接三方核对」是对外部权威源核对，不是自己核对自己。
2. **模板代码只存一份。** 页面上展示的字符串，就是 `run_templates.py` 拿去 `exec` 的那一份，
   所以「书上的模板跑不通」在结构上不可能发生。
3. **校验器跑在渲染产物上，mutation 打在数据层。** 否则校验的只是生成器的 happy path，
   而 mutation test 会变成空的——改数据、重新生成，校验器永远看不见差别。
   唯一的例外是速查页「关键词索引出自各章 §2」那一条：两边同源，它跑不出红，
   留着只是为了拦住「以后有人手写一份索引」，不算被 mutation 验证过的检查。

## 已知的两处与 spec 的偏差

- **题量 111 而非「约 130」。** `spec/skeleton.md` §5 的选题清单实际列出 107 个条目，
  拆开 141/142、235/236、252/253、496/503 这类合并项后是 111。数字由 `content/` 统计后注入页面，
  没有任何一处手写。
- **§4 的题目分层数量是警戒区间而非硬约束。** skeleton §4 写「热身 1 / 标准 2–3 / 变体 1–2」，
  但 §5 的实际选题里 18 章有 12 章不符合，连已获批的样章 ch04 也不符合。
  取舍：**§5 选题 + ch04 样章为准**，§4 当默认区间，越界的逐章登记进
  `reference/check_site.py` 的 `TIER_EXCEPTIONS` 并写明理由；名单以外的越界一律报错。
  `STAR_EXCEPTIONS` 同理（目前只有一条：LeetCode 已把 72 Edit Distance 从 Hard 下调为 Medium）。
