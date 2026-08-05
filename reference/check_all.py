#!/usr/bin/env python3
"""一条命令跑完整条流水线。发布前必须全绿。

    python3 reference/check_all.py

顺序是有讲究的：
  1. 模板可运行  —— 书上印的代码先得跑通，不然后面校验的是错的东西
  2. 构建        —— 重新渲染，保证校验器看到的是最新产物
  3. 站级校验    —— 链接三方核对、五段结构、决策树、识别信号冲突、站内死链
  4. mutation    —— 证明上一步的校验器真的会红，而不是形同虚设
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STEPS = [
    ("模板可运行", ["python3", "reference/run_templates.py"]),
    ("构建 22 页", ["python3", "reference/build.py", "--quiet"]),
    ("选题对 spec", ["python3", "reference/check_vs_spec.py"]),
    ("站级校验", ["python3", "reference/check_site.py"]),
    ("mutation test", ["python3", "reference/mutation_test.py"]),
]


def main():
    failed = []
    for name, cmd in STEPS:
        print("\n{}\n== {} ==\n{}".format("=" * 60, name, "=" * 60))
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode:
            failed.append(name)
    print("\n" + "=" * 60)
    if failed:
        print("失败: {}".format("、".join(failed)))
        return 1
    print("全部通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
