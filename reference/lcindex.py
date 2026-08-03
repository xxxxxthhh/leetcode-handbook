# -*- coding: utf-8 -*-
"""读取 data/leetcode-index.json。缺题一律硬失败，绝不静默跳过。"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "leetcode-index.json")

with open(PATH, encoding="utf-8") as _f:
    _DATA = json.load(_f)

FETCHED_AT = _DATA["fetched_at"]
_PROBLEMS = _DATA["problems"]


def get(num):
    key = str(num)
    if key not in _PROBLEMS:
        raise KeyError(
            "题号 {} 不在 data/leetcode-index.json 里；先跑 reference/fetch_lc_index.py".format(num)
        )
    return _PROBLEMS[key]


def url(num):
    return "https://leetcode.com/problems/{}/".format(get(num)["slug"])
