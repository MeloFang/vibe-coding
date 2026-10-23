#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_report.py — vibe-coding 体检 findings.json 零依赖校验器。

用法:
    python validate_report.py <findings.json>

只依赖标准库（json/re），不依赖 jsonschema 库。
按 references/report-schema.json 的规则做手工校验：
结构、必填字段、枚举、编号连续唯一、correctness+confirmed 必填 evidence。

退出码: 0 = 通过; 1 = 校验失败; 2 = 用法错误。
"""
import json
import re
import sys

CATEGORIES = {"correctness", "architecture", "decision_gap"}
VERDICTS = {"confirmed", "needs_validation", "rejected"}
RECOMMENDATIONS = {"strong", "worth_exploring", "speculative"}
EXCLUDED_KINDS = {"false_positive", "intentional"}
ISO_DT = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")

def fail(errors, path, msg):
    errors.append("%s: %s" % (path, msg))

def validate(data):
    errors = []

    if not isinstance(data, dict):
        return ["$: 顶层必须是对象"]

    if set(data) - {"meta", "findings", "excluded"}:
        fail(errors, "$", "未定义的顶层字段: %s" % sorted(set(data) - {"meta", "findings", "excluded"}))

    # meta
    meta = data.get("meta")
    if not isinstance(meta, dict):
        fail(errors, "$.meta", "缺失或不是对象")
    else:
        if set(meta) - {"repo", "generated_at", "scope", "read_only"}:
            fail(errors, "$.meta", "未定义字段: %s" % sorted(set(meta) - {"repo", "generated_at", "scope", "read_only"}))
        for k in ("repo", "generated_at", "scope"):
            if k not in meta:
                fail(errors, "$.meta", "缺必填字段 %s" % k)
            elif not isinstance(meta[k], str) or not meta[k].strip():
                fail(errors, "$.meta.%s" % k, "必须是非空字符串" % k)
        if "generated_at" in meta and isinstance(meta["generated_at"], str) and not ISO_DT.match(meta["generated_at"]):
            fail(errors, "$.meta.generated_at", "不是 ISO 8601 时间戳: %r" % meta["generated_at"])
        if "read_only" in meta and meta["read_only"] is not True:
            fail(errors, "$.meta.read_only", "体检只读声明必须为 true")

    # findings
    findings = data.get("findings")
    if not isinstance(findings, list):
        fail(errors, "$.findings", "缺失或不是数组")
        findings = []
    if not findings:
        fail(errors, "$.findings", "至少要有一条发现（或明确写 excluded 说明全部排除）")

    seen_ids = set()
    for i, f in enumerate(findings, 1):
        p = "$.findings[%d]" % (i - 1)
        if not isinstance(f, dict):
            fail(errors, p, "不是对象")
            continue
        allowed = {"id", "category", "verdict", "title", "files", "problem",
                   "evidence", "hit_count", "fix", "regression", "recommendation", "deferred"}
        extra = set(f) - allowed
        if extra:
            fail(errors, p, "未定义字段: %s" % sorted(extra))
        for k in ("id", "category", "verdict", "title", "files", "problem", "fix"):
            if k not in f:
                fail(errors, p, "缺必填字段 %s" % k)
        if "id" in f:
            if not isinstance(f["id"], int) or isinstance(f["id"], bool):
                fail(errors, p + ".id", "必须是整数")
            elif f["id"] < 1:
                fail(errors, p + ".id", "必须 >= 1")
            elif f["id"] in seen_ids:
                fail(errors, p + ".id", "编号重复: %d" % f["id"])
            else:
                seen_ids.add(f["id"])
        if f.get("category") not in CATEGORIES and "category" in f:
            fail(errors, p + ".category", "必须是 %s 之一" % sorted(CATEGORIES))
        if f.get("verdict") not in VERDICTS and "verdict" in f:
            fail(errors, p + ".verdict", "必须是 %s 之一" % sorted(VERDICTS))
        if "recommendation" in f and f["recommendation"] not in RECOMMENDATIONS:
            fail(errors, p + ".recommendation", "必须是 %s 之一" % sorted(RECOMMENDATIONS))
        if "title" in f and (not isinstance(f["title"], str) or len(f["title"]) < 4):
            fail(errors, p + ".title", "标题太短，必须说清场景(>=4字符)")
        if "problem" in f and (not isinstance(f["problem"], str) or len(f["problem"]) < 10):
            fail(errors, p + ".problem", "问题描述太短：必须给出具体场景(>=10字符)")
        if "fix" in f and (not isinstance(f["fix"], str) or len(f["fix"]) < 8):
            fail(errors, p + ".fix", "修法太含糊：必须具体到改哪几处(>=8字符)")
        if "files" in f:
            if not isinstance(f["files"], list) or not f["files"]:
                fail(errors, p + ".files", "必须是非空数组")
            elif not all(isinstance(x, str) and x.strip() for x in f["files"]):
                fail(errors, p + ".files", "每个元素必须是非空字符串(带行号)")
        # 关键业务规则：正确性缺陷且已验证 → 必须有实测证据
        if f.get("category") == "correctness" and f.get("verdict") == "confirmed":
            if not isinstance(f.get("evidence"), str) or not f["evidence"].strip():
                fail(errors, p, "correctness+confirmed 必须给 evidence（输入→实际→期望）")
        if "hit_count" in f and f["hit_count"] is not None and not isinstance(f["hit_count"], int):
            fail(errors, p + ".hit_count", "必须是整数或 null")
        if "deferred" in f and f["deferred"] is not None and not isinstance(f["deferred"], str):
            fail(errors, p + ".deferred", "必须是字符串(挂账+触发条件)或 null")

    ids = sorted(x for x in seen_ids if isinstance(x, int))
    if findings and ids and ids != list(range(1, len(ids) + 1)):
        fail(errors, "$.findings", "编号必须全局连续从 1 开始，实际: %s" % ids)

    # excluded
    excluded = data.get("excluded", [])
    if not isinstance(excluded, list):
        fail(errors, "$.excluded", "不是数组")
    else:
        for i, e in enumerate(excluded, 1):
            p = "$.excluded[%d]" % (i - 1)
            if not isinstance(e, dict):
                fail(errors, p, "不是对象")
                continue
            extra = set(e) - {"title", "reason", "kind", "checked"}
            if extra:
                fail(errors, p, "未定义字段: %s" % sorted(extra))
            for k in ("title", "reason", "kind"):
                if k not in e:
                    fail(errors, p, "缺必填字段 %s" % k)
            if "reason" in e and (not isinstance(e["reason"], str) or len(e["reason"]) < 4):
                fail(errors, p + ".reason", "必须写清为什么否(>=4字符)")
            if "kind" in e and e["kind"] not in EXCLUDED_KINDS:
                fail(errors, p + ".kind", "必须是 false_positive 或 intentional")
            if "checked" in e and not isinstance(e["checked"], bool):
                fail(errors, p + ".checked", "必须是布尔")

    # 裁定统计
    stats = {}
    for f in findings:
        if isinstance(f, dict) and "verdict" in f:
            stats[f["verdict"]] = stats.get(f["verdict"], 0) + 1
    return errors, stats

def main():
    if len(sys.argv) != 2:
        print("用法: python validate_report.py <findings.json>")
        return 2
    try:
        with open(sys.argv[1], encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as e:
        print("读取失败: %s" % e)
        return 2
    except json.JSONDecodeError as e:
        print("JSON 解析失败: %s" % e)
        return 1

    errors, stats = validate(data)
    if errors:
        print("校验失败，共 %d 处:" % len(errors))
        for e in errors:
            print("  - %s" % e)
        return 1
    print("校验通过。findings=%d, excluded=%d, 裁定分布=%s" % (
        len(data.get("findings", [])), len(data.get("excluded", [])),
        ", ".join("%s:%d" % kv for kv in sorted(stats.items())) or "无"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
