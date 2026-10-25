#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 vibe-coding 代码库体检的覆盖台账（coverage-ledger.json）。

借 cloudflare/security-audit-skill 的 coverage-ledger 思想，做双校验：

  第一道（台账自身）：本文件对 coverage-ledger.json 做良构校验
    - dimensions 是数组、id 不重复、category/severity 取值合法
    - covered_by 指向的文件确实存在（避免声明了却无依据）
    - 三个类别至少各有一条维度，否则台账本身有盲区

  第二道（可选 --findings）：把 findings.json 实际覆盖情况与台账交叉
    - 列出每个 always:true 基线维度是否被本会话覆盖
    - 未被覆盖的基线维度发出 WARN（零 bug 可能是真没有，但必须显式确认，不能默认跳过）

只依赖标准库。零依赖 = 任何环境直接跑。

用法：
    python references/validate_coverage_ledger.py references/coverage-ledger.json
    python references/validate_coverage_ledger.py references/coverage-ledger.json --findings <findings.json>
"""

import argparse
import json
import os
import sys

CATEGORIES = {"correctness", "architecture", "decision_gap"}
SEVERITIES = {"high", "medium", "low"}
REQUIRED_DIM_FIELDS = {
    "id", "name", "category", "description",
    "severity_if_skipped", "covered_by", "always",
}


def _fail(msg):
    print(f"[FAIL] {msg}")
    return False


def validate_ledger(ledger_path):
    """第一道：台账自身良构校验。返回 (ok, data)。"""
    ok = True
    try:
        with open(ledger_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 无法解析 JSON: {e}")
        return False, None

    dims = data.get("dimensions")
    if not isinstance(dims, list) or not dims:
        return _fail("缺少非空的 dimensions 数组"), None

    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(ledger_path)))
    ids = set()
    for i, d in enumerate(dims):
        where = f"dimensions[{i}]"
        if not isinstance(d, dict):
            ok = _fail(f"{where}: 不是对象"); continue
        missing = REQUIRED_DIM_FIELDS - set(d.keys())
        if missing:
            ok = _fail(f"{where}: 缺字段 {sorted(missing)}")
        did = d.get("id")
        if did in ids:
            ok = _fail(f"{where}: id 重复 {did!r}")
        ids.add(did)
        if d.get("category") not in CATEGORIES:
            ok = _fail(f"{where} (id={did}): category 非法 {d.get('category')!r}")
        if d.get("severity_if_skipped") not in SEVERITIES:
            ok = _fail(f"{where} (id={did}): severity_if_skipped 非法 {d.get('severity_if_skipped')!r}")
        if not isinstance(d.get("always"), bool):
            ok = _fail(f"{where} (id={did}): always 必须是布尔")
        cb = d.get("covered_by")
        if cb and not os.path.isfile(os.path.join(skill_root, cb)):
            ok = _fail(f"{where} (id={did}): covered_by 文件不存在 {cb!r}")

    for cat in CATEGORIES:
        if not any(d.get("category") == cat for d in dims):
            ok = _fail(f"类别 {cat} 在台账中零维度（台账自身有盲区）")

    return ok, data


def check_findings_coverage(ledger_data, findings_path):
    """第二道：findings.json 是否覆盖了台账中的基线维度。纯提示，不阻断。"""
    try:
        with open(findings_path, encoding="utf-8") as f:
            findings = json.load(f)
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] 无法解析 findings.json: {e}")
        return False

    cats_present = {d.get("category") for d in findings.get("findings", [])}
    excluded_cats = set()
    for ex in findings.get("excluded", []):
        # excluded 不强制带 category，这里仅用于软提示，缺失不计为覆盖
        if isinstance(ex, dict) and ex.get("category"):
            excluded_cats.add(ex["category"])

    baseline = [d for d in ledger_data["dimensions"] if d.get("always") is True]
    print("\n=== 基线维度覆盖检查（always:true，本会话必须显式确认）===")
    any_gap = False
    for d in baseline:
        cat = d["category"]
        covered = cat in cats_present or cat in excluded_cats
        status = "✅ 已覆盖" if covered else "⚠️  未覆盖（需显式确认本范围确实不含此风险，或在报告中写明跳过理由）"
        if not covered:
            any_gap = True
        print(f"  [{d['id']}] {d['name']}  →  {status}")
    print("\n分类发现数：")
    for cat in CATEGORIES:
        n = sum(1 for f in findings.get("findings", []) if f.get("category") == cat)
        print(f"  {cat}: {n} 条")
    if not any_gap:
        print("\n[OK] 所有基线维度本会话均有发现或已排除记录。")
    else:
        print("\n[WARN] 存在未覆盖基线维度——零 bug 可能是真的没有，但必须显式确认，不能默认跳过。")
    return True


def main():
    ap = argparse.ArgumentParser(description="校验 vibe-coding 覆盖台账")
    ap.add_argument("ledger", help="coverage-ledger.json 路径")
    ap.add_argument("--findings", help="可选：交叉校验的 findings.json 路径")
    args = ap.parse_args()

    ok, data = validate_ledger(args.ledger)
    if not ok:
        print("\n[结果] 覆盖台账校验失败。")
        sys.exit(1)

    print(f"[OK] 覆盖台账良构：{len(data['dimensions'])} 条维度，三类齐全。")

    if args.findings:
        check_findings_coverage(data, args.findings)

    print("\n[结果] 覆盖台账校验通过。")
    sys.exit(0)


if __name__ == "__main__":
    main()
