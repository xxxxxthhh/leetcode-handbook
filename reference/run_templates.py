#!/usr/bin/env python3
"""模板可运行校验：把每章模板代码原样 exec，再在同一命名空间里跑它的测试用例。

    python3 reference/run_templates.py
    python3 reference/run_templates.py 4      # 只跑第 4 章

页面上展示的代码字符串就是这里被执行的那一份（content 里只存一份），
所以「书上的模板跑不通」这件事在结构上不可能发生——除非测试用例本身漏了。
"""
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import content  # noqa: E402


def run(only=None):
    failed = 0
    total = 0
    for ch in content.CHAPTERS:
        if only and ch["no"] not in only:
            continue
        for tpl in ch["templates"]:
            total += 1
            ns = {}
            label = "ch{:02d} · {}".format(ch["no"], tpl["name"])
            try:
                exec(compile(tpl["code"], "<{} code>".format(label), "exec"), ns)
                exec(compile(tpl["tests"], "<{} tests>".format(label), "exec"), ns)
            except Exception:
                failed += 1
                print("FAIL  " + label)
                traceback.print_exc()
            else:
                n_assert = tpl["tests"].count("assert ")
                print("ok    {}  ({} 条断言)".format(label, n_assert))
    print("\n{} 个模板，{} 个失败".format(total, failed))
    return failed


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]} or None
    sys.exit(1 if run(only) else 0)
