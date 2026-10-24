#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_validate_report.py — validate_report.py 的自测（零依赖，直接断言跑）。

覆盖两部分：
  1–12  原有结构校验断言
  13–18 repair receipt（借鉴 archify）与有边界自动修复
"""
import copy
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_report import validate, Issue, auto_repair, build_receipt

HERE = os.path.dirname(os.path.abspath(__file__))

def valid_doc():
    return {
        "meta": {
            "repo": "demo",
            "generated_at": "2026-10-23T09:44:00",
            "scope": "src/",
            "read_only": True,
        },
        "findings": [
            {
                "id": 1, "category": "correctness", "verdict": "confirmed",
                "title": "空密码直接放行",
                "files": ["src/auth.py:45"],
                "problem": "密码为空字符串时判断顺序错误，返回通过",
                "evidence": "输入 password='' → 实际: 通过 → 期望: 拒绝",
                "hit_count": 0,
                "fix": "把空值校验移到哈希比较之前",
                "regression": "重跑 tests/test_auth.py 全部用例",
                "recommendation": "strong",
            },
            {
                "id": 2, "category": "architecture", "verdict": "needs_validation",
                "title": "重复实现的配置加载",
                "files": ["src/conf.py:12", "src/conf2.py:8"],
                "problem": "同一概念两处实现且风格不同，读代码要在两个文件间跳",
                "fix": "合并到 src/conf.py，删掉 conf2.py",
                "recommendation": "worth_exploring",
            },
        ],
        "excluded": [
            {"title": "疑似双重缓存", "reason": "查证后 load() 返回同一 dict，前提不成立",
             "kind": "false_positive", "checked": True},
        ],
    }

def expect(errors, want_err, label):
    has = bool(errors)
    if has != want_err:
        print("FAIL %s: errors=%s" % (label, errors[:3]))
        return False
    print("pass %s" % label)
    return True

ok = True
# 1. 合法文档通过
e, s = validate(valid_doc())
ok &= expect(e, False, "1 合法文档")
# 2. 裁定统计
ok &= (s == {"confirmed": 1, "needs_validation": 1}) or (print("FAIL stats", s) or False)
print("pass 2 裁定统计")

# 3. correctness+confirmed 缺 evidence → 报错
d = valid_doc(); del d["findings"][0]["evidence"]
ok &= expect(validate(d)[0], True, "3 confirmed 缺 evidence")

# 4. id 不连续 → 报错
d = valid_doc(); d["findings"][1]["id"] = 5
ok &= expect(validate(d)[0], True, "4 id 不连续")

# 5. id 重复 → 报错
d = valid_doc(); d["findings"][1]["id"] = 1
ok &= expect(validate(d)[0], True, "5 id 重复")

# 6. verdict 非法 → 报错
d = valid_doc(); d["findings"][0]["verdict"] = "maybe"
ok &= expect(validate(d)[0], True, "6 非法 verdict")

# 7. 未定义顶层字段 → 报错
d = valid_doc(); d["extra"] = 1
ok &= expect(validate(d)[0], True, "7 未定义顶层字段")

# 8. read_only=False → 报错
d = valid_doc(); d["meta"]["read_only"] = False
ok &= expect(validate(d)[0], True, "8 read_only 必须 true")

# 9. fix 太含糊 → 报错
d = valid_doc(); d["findings"][1]["fix"] = "重构"
ok &= expect(validate(d)[0], True, "9 fix 含糊")

# 10. needs_validation 不要求 evidence（通过）
d = valid_doc(); d["findings"][1]["evidence"] = None if "evidence" in d["findings"][1] else d["findings"][1].get("evidence")
ok &= expect(validate(d)[0], False, "10 needs_validation 无 evidence 可过")

# 11. schema 文件本身是合法 JSON 且版本字段齐
with open(os.path.join(HERE, "report-schema.json"), encoding="utf-8") as f:
    sch = json.load(f)
ok &= ("$defs" in sch and "finding" in sch["$defs"]) or (print("FAIL schema") or False)
print("pass 11 schema 可解析")

# 12. 空 findings → 报错（体检必须有产出或全排除说明）
d = valid_doc(); d["findings"] = []
ok &= expect(validate(d)[0], True, "12 空 findings")

# 13. 每条错误都是 receipt 条目：带 path / rule / repair，且 str() 仍是人话
d = valid_doc(); d["findings"][0]["verdict"] = "maybe"
errs = validate(d)[0]
ok &= all(isinstance(e, Issue) and e.path and e.rule and e.repair for e in errs) or (
    print("FAIL 13 receipt 条目字段", errs[:2]) or False)
ok &= all(isinstance(str(e), str) and str(e) for e in errs) or (
    print("FAIL 13b str() 兼容") or False)
print("pass 13 receipt 条目字段完整 + str() 兼容")

# 14. 自动修标记：只有 id 类问题标 auto=True，语义类问题不标
d = valid_doc(); d["findings"][1]["id"] = 5
errs = validate(d)[0]
ok &= any(e.rule == "ids.sequential" and e.auto for e in errs) or (
    print("FAIL 14a ids.sequential 应可自动修", [str(e) for e in errs]) or False)
d = valid_doc(); d["findings"][0]["verdict"] = "maybe"
errs = validate(d)[0]
ok &= not any(e.auto for e in errs) or (print("FAIL 14b 语义错误不应自动修") or False)
print("pass 14 auto 标记只对确定性修复生效")

# 15. auto_repair 重编号后复检通过（有边界自动修复的收敛性）
d = valid_doc(); d["findings"][1]["id"] = 5
fixed, applied = auto_repair(d)
left, _ = validate(fixed)
ok &= (not left) or (print("FAIL 15 自动修复后仍有错", [str(e) for e in left]) or False)
ok &= applied and applied[0]["rule"] == "ids.sequential" or (print("FAIL 15b applied 为空") or False)
print("pass 15 auto_repair 重编号后通过复检")

# 16. 自动修复不动无关结构（archify: unrelated structure stays stable）
d = valid_doc(); d["findings"][1]["id"] = 5
snapshot = copy.deepcopy(d["findings"][0])
fixed, _ = auto_repair(d)
ok &= (fixed["findings"][0] == snapshot) or (print("FAIL 16 自动修复动了无关字段") or False)
print("pass 16 自动修复不动无关结构")

# 17. receipt 结构可序列化且字段齐（机器可读）
errs = validate(valid_doc())[0]
rec = build_receipt("findings.json", "passed", errs, data=valid_doc())
ok &= (rec["receipt"] == "vibe-coding-findings-repair" and
       {"source", "status", "counts", "issues", "applied"} <= set(rec)) or (
    print("FAIL 17 receipt 顶层字段", sorted(rec)) or False)
json.dumps(rec, ensure_ascii=False)  # 必须可序列化
print("pass 17 receipt 可序列化且字段齐")

# 18. 语义类问题无法自动修 → auto_repair 后再校验仍报错（保证不会误放行）
d = valid_doc(); del d["findings"][0]["evidence"]
fixed, applied = auto_repair(d)
left, _ = validate(fixed)
ok &= bool(left) or (print("FAIL 18 缺 evidence 不该被自动修掉") or False)
ok &= any(e.rule == "evidence.required" for e in left) or (
    print("FAIL 18b 未报出 evidence.required") or False)
print("pass 18 语义问题不被自动修复误放行")

print("\n%s" % ("ALL PASS" if ok else "SOME FAILED"))
sys.exit(0 if ok else 1)
