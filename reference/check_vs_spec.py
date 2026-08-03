#!/usr/bin/env python3
"""选题与 spec 的一致性核对：content/ 收录的题目必须逐章、逐层对得上
spec/skeleton.md §5 的选题清单。

    python3 reference/check_vs_spec.py

这一条是「站级横切检查」（质量教训 6）：18 章分五批写完，最容易发生的漂移
就是某一章顺手多收了一道、或把某道题挪到了别的层。程序化对一遍，
比逐章回读靠谱。合并项（141/142、235/236、252/253、496+503）在这里自动拆开。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import content  # noqa: E402

TIER_ZH = {"warmup": "热身", "standard": "标准", "variant": "变体"}


def parse_spec():
    path = os.path.join(ROOT, "spec", "skeleton.md")
    with open(path, encoding="utf-8") as f:
        body = f.read().split("## 5. 章节清单与选题")[1].split("## 6.")[0]
    out = {}
    for block in re.split(r"\n### ", body)[1:]:
        head = block.splitlines()[0]
        no = int(re.match(r"(\d+)", head).group(1))
        tiers = {}
        for line in block.splitlines():
            m = re.match(r"- (热身|标准|变体)(（[^）]*）)?：(.*)", line)
            if m:
                # 题号一律是 1–4 位整数；合并项 141/142、+503 都会被拆出来
                tiers[m.group(1)] = [int(x) for x in re.findall(r"\b\d{1,4}\b", m.group(3))]
        out[no] = tiers
    return out


def main():
    spec = parse_spec()
    errors = []
    n_spec = n_book = 0

    for ch in content.CHAPTERS:
        no = ch["no"]
        want = spec.get(no)
        if want is None:
            errors.append("第 {} 章在 spec §5 里找不到".format(no))
            continue
        got = {}
        for p in ch["problems"]:
            got.setdefault(TIER_ZH[p["tier"]], []).append(p["num"])

        for tier in ("热身", "标准", "变体"):
            w, g = want.get(tier, []), got.get(tier, [])
            n_spec += len(w)
            n_book += len(g)
            extra = sorted(set(g) - set(w))
            missing = sorted(set(w) - set(g))
            if extra:
                errors.append("ch{:02d} {}：书里多出 {}".format(no, tier, extra))
            if missing:
                errors.append("ch{:02d} {}：spec 有但书里没有 {}".format(no, tier, missing))

        # 层次挪动：题在本章但落到了别的层
        flat_want = {n: t for t, ns in want.items() for n in ns}
        flat_got = {n: t for t, ns in got.items() for n in ns}
        for n in set(flat_want) & set(flat_got):
            if flat_want[n] != flat_got[n]:
                errors.append("ch{:02d}：题 {} 在 spec 里是「{}」，书里放在「{}」".format(
                    no, n, flat_want[n], flat_got[n]))

    print("spec §5 条目 {} 个（拆开合并项后），书里收录 {} 道".format(n_spec, n_book))
    for e in errors:
        print("ERROR " + e)
    print("\n{} errors".format(len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
