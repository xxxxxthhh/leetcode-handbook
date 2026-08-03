#!/usr/bin/env python3
"""从 LeetCode 官方题目索引抓取本书引用到的题目元数据，裁剪后落盘。

    python3 reference/fetch_lc_index.py                    # 联网抓取
    python3 reference/fetch_lc_index.py --dump path.json   # 用已下载的全量 dump

产物 data/leetcode-index.json 是「链接三方核对」的权威源：题号 ↔ slug ↔ 题名
不再靠记忆生成，🔒（premium）与难度也从这里派生而非手写。
只保留本书用到的题，并记录抓取日期——本系列对时效性数据一律标注时间。
"""
import argparse
import datetime
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from content import problem_numbers  # noqa: E402

API = "https://leetcode.com/api/problems/all/"
OUT = os.path.join(ROOT, "data", "leetcode-index.json")
LEVELS = {1: "Easy", 2: "Medium", 3: "Hard"}


def load_dump(path):
    if path:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    req = urllib.request.Request(API, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", help="已下载的 api/problems/all/ 全量 JSON")
    args = ap.parse_args()

    raw = load_dump(args.dump)
    by_id = {}
    for p in raw["stat_status_pairs"]:
        by_id[p["stat"]["frontend_question_id"]] = p

    wanted = problem_numbers()
    missing = [n for n in wanted if n not in by_id]
    if missing:
        sys.exit("官方索引里找不到题号: {}".format(missing))

    index = {}
    for n in wanted:
        p = by_id[n]
        index[str(n)] = {
            "title": p["stat"]["question__title"],
            "slug": p["stat"]["question__title_slug"],
            "paid_only": bool(p["paid_only"]),
            "difficulty": LEVELS[p["difficulty"]["level"]],
        }

    out = {
        "source": API,
        "fetched_at": datetime.date.today().isoformat(),
        "total_problems_on_leetcode": raw["num_total"],
        "problems": index,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    print("wrote {} problems -> {}".format(len(index), os.path.relpath(OUT, ROOT)))


if __name__ == "__main__":
    main()
