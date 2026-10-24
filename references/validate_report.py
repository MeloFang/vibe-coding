#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""validate_report.py — vibe-coding 体检 findings.json 零依赖校验器 + repair receipt。

用法:
    python validate_report.py <findings.json>            # 校验；失败时落 <file>.receipt.json
    python validate_report.py <findings.json> --json     # receipt 打到 stdout
    python validate_report.py <findings.json> --repair   # 只做「有边界的自动修复」，通过才原子替换
    python validate_report.py <findings.json> --no-receipt

只依赖标准库（json/re/os/shutil），不依赖 jsonschema 库。
按 references/report-schema.json 的规则做手工校验：
结构、必填字段、枚举、编号连续唯一、correctness+confirmed 必填 evidence。

── repair receipt（借鉴 tt-a1i/archify）──────────────────────────────
archify: "Validate — bundled validators and layout rules check the source;
          failures identify the exact local repair in machine-readable JSON."
搬到这里的意思是：**校验失败不能只打一句人话**，要产出一份机器可读的收据，
每条问题都指明「精确的局部修复」（exact local repair）：

    path      出问题的精确位置（JSON 指针风格）
    rule      触发的规则号
    found     实际值
    expected  允许的值/形态
    repair    精确到「改哪一处的什么」的动作指令（人/Agent 照着改即可）
    auto      是否属于「有边界的自动修复」（bounded auto-repair）

并沿用 archify 的两条交付纪律：
    · 只有通过的产物才原子替换目标（os.replace），失败保留 last-good（.bak）
    · 自动修复限定在「确定性、无歧义、不丢信息」的范围内 —— 目前只有 id 重编号

退出码: 0 = 通过; 1 = 校验失败（或自动修复后仍失败）; 2 = 用法错误。
"""
import copy
import json
import os
import re
import shutil
import sys

CATEGORIES = {"correctness", "architecture", "decision_gap"}
VERDICTS = {"confirmed", "needs_validation", "rejected"}
RECOMMENDATIONS = {"strong", "worth_exploring", "speculative"}
EXCLUDED_KINDS = {"false_positive", "intentional"}
ISO_DT = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?")

RECEIPT_KIND = "vibe-coding-findings-repair"


class Issue(object):
    """一条 repair receipt 条目。str() 仍是人话，方便直接 print / 旧断言兼容。"""

    __slots__ = ("path", "rule", "found", "expected", "repair", "auto")

    def __init__(self, path, rule, found, expected, repair, auto=False):
        self.path = path
        self.rule = rule
        self.found = found
        self.expected = expected
        self.repair = repair
        self.auto = auto

    def __str__(self):
        return "%s [%s] %s" % (self.path, self.rule, self.repair)

    def __repr__(self):
        return "<Issue %s %s>" % (self.rule, self.path)

    def to_dict(self):
        return {
            "path": self.path,
            "rule": self.rule,
            "found": self.found,
            "expected": self.expected,
            "repair": self.repair,
            "auto": self.auto,
        }


def _brief(v, n=40):
    """把 found 值压成可放进 JSON 又不会爆掉的短串。"""
    try:
        s = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
    except (TypeError, ValueError):
        s = repr(v)
    if len(s) > n:
        s = s[:n] + "…"
    return s


def fail(errors, path, rule, found, expected, repair, auto=False):
    errors.append(Issue(path, rule, _brief(found), expected, repair, auto))


def validate(data):
    errors = []

    if not isinstance(data, dict):
        return [Issue("$", "root.type", type(data).__name__, "object",
                      "顶层必须是对象")], {}

    if set(data) - {"meta", "findings", "excluded"}:
        fail(errors, "$", "root.fields", sorted(set(data) - {"meta", "findings", "excluded"}),
             "只能是 meta / findings / excluded",
             "删掉未定义的顶层字段: %s" % ", ".join(sorted(set(data) - {"meta", "findings", "excluded"})))

    # meta
    meta = data.get("meta")
    if not isinstance(meta, dict):
        fail(errors, "$.meta", "meta.type", _brief(meta), "object", "缺失或不是对象，补一个 meta 对象")
    else:
        if set(meta) - {"repo", "generated_at", "scope", "read_only"}:
            fail(errors, "$.meta", "meta.fields", sorted(set(meta) - {"repo", "generated_at", "scope", "read_only"}),
                 "只能是 repo / generated_at / scope / read_only",
                 "删掉 meta 里未定义的字段: %s" % ", ".join(sorted(set(meta) - {"repo", "generated_at", "scope", "read_only"})))
        for k in ("repo", "generated_at", "scope"):
            if k not in meta:
                fail(errors, "$.meta", "meta.required", None, "字符串 repo/generated_at/scope",
                     "补上必填字段 meta.%s" % k)
            elif not isinstance(meta[k], str) or not meta[k].strip():
                fail(errors, "$.meta.%s" % k, "meta.nonempty", _brief(meta[k]), "非空字符串",
                     "把 meta.%s 写成非空字符串" % k)
        if "generated_at" in meta and isinstance(meta["generated_at"], str) and not ISO_DT.match(meta["generated_at"]):
            fail(errors, "$.meta.generated_at", "meta.iso8601", meta["generated_at"], "YYYY-MM-DDTHH:MM(:SS)",
                 "把 generated_at 改成 ISO 8601，如 2026-10-24T10:30:00")
        if "read_only" in meta and meta["read_only"] is not True:
            fail(errors, "$.meta.read_only", "meta.read_only", _brief(meta["read_only"]), "true",
                 "read_only 必须为 true（体检只读声明）。若你确实改过代码，就别出体检报告")

    # findings
    findings = data.get("findings")
    if not isinstance(findings, list):
        fail(errors, "$.findings", "findings.type", _brief(findings), "数组", "缺失或不是数组，补一个 findings 数组")
        findings = []
    if not findings:
        fail(errors, "$.findings", "findings.nonempty", 0, "至少 1 条",
             "至少要有一条发现；若确实全排除，写进 excluded 并说明")

    seen_ids = set()
    for i, f in enumerate(findings, 1):
        p = "$.findings[%d]" % (i - 1)
        if not isinstance(f, dict):
            fail(errors, p, "finding.type", _brief(f), "对象", "这条发现不是对象，改成对象或删掉")
            continue
        allowed = {"id", "category", "verdict", "title", "files", "problem",
                   "evidence", "hit_count", "fix", "regression", "recommendation", "deferred"}
        extra = set(f) - allowed
        if extra:
            fail(errors, p, "finding.fields", sorted(extra), "只允许 %s" % ", ".join(sorted(allowed)),
                 "删掉未定义字段 %s（或改名为标准字段）" % ", ".join(sorted(extra)))
        for k in ("id", "category", "verdict", "title", "files", "problem", "fix"):
            if k not in f:
                fail(errors, p, "finding.required", None, "必填 %s" % k,
                     "补上必填字段 %s" % k)
        if "id" in f:
            if not isinstance(f["id"], int) or isinstance(f["id"], bool):
                fail(errors, p + ".id", "id.type", _brief(f["id"]), "整数",
                     "把 id 写成整数")
            elif f["id"] < 1:
                fail(errors, p + ".id", "id.min", f["id"], ">= 1",
                     "id 从 1 开始")
            elif f["id"] in seen_ids:
                # 重复 → 与「全局连续」一起由 ids.sequential 一次性重编号解决
                fail(errors, p + ".id", "id.duplicate", f["id"], "全局唯一",
                     "与前面某条 id 重复；整体重编号 1..N 即可（--repair 可自动做）",
                     auto=True)
            else:
                seen_ids.add(f["id"])
        if f.get("category") not in CATEGORIES and "category" in f:
            fail(errors, p + ".category", "category.enum", _brief(f["category"]), " / ".join(sorted(CATEGORIES)),
                 "把 category 改成三者之一")
        if f.get("verdict") not in VERDICTS and "verdict" in f:
            fail(errors, p + ".verdict", "verdict.enum", _brief(f["verdict"]), " / ".join(sorted(VERDICTS)),
                 "把 verdict 改成 confirmed / needs_validation / rejected 之一")
        if "recommendation" in f and f["recommendation"] not in RECOMMENDATIONS:
            fail(errors, p + ".recommendation", "recommendation.enum", _brief(f["recommendation"]),
                 " / ".join(sorted(RECOMMENDATIONS)),
                 "把 recommendation 改成 strong / worth_exploring / speculative 之一")
        if "title" in f and (not isinstance(f["title"], str) or len(f["title"]) < 4):
            fail(errors, p + ".title", "title.len", _brief(f["title"]), ">= 4 字符且说清场景",
                 "标题写清场景（如「空密码直接放行」），不要用泛词")
        if "problem" in f and (not isinstance(f["problem"], str) or len(f["problem"]) < 10):
            fail(errors, p + ".problem", "problem.len", _brief(f["problem"]), ">= 10 字符的具体场景",
                 "problem 写具体场景：什么输入/情况下导致什么结果")
        if "fix" in f and (not isinstance(f["fix"], str) or len(f["fix"]) < 8):
            fail(errors, p + ".fix", "fix.len", _brief(f["fix"]), ">= 8 字符且具体到改哪几处",
                 "fix 写到「改哪个文件哪几行、换成什么顺序」，不许只写「重构」")
        if "files" in f:
            if not isinstance(f["files"], list) or not f["files"]:
                fail(errors, p + ".files", "files.type", _brief(f["files"]), "非空数组",
                     "files 至少给一个文件（带行号）")
            elif not all(isinstance(x, str) and x.strip() for x in f["files"]):
                fail(errors, p + ".files", "files.items", _brief(f["files"]), "非空字符串且带行号",
                     "files 每项写成 src/xx.py:45 这种带行号的形式")
        # 关键业务规则：正确性缺陷且已验证 → 必须有实测证据
        if f.get("category") == "correctness" and f.get("verdict") == "confirmed":
            if not isinstance(f.get("evidence"), str) or not f["evidence"].strip():
                fail(errors, p, "evidence.required", None, "输入→实际→期望",
                     "correctness+confirmed 必须给 evidence（输入→实际→期望），否则降级为 needs_validation")
        if "hit_count" in f and f["hit_count"] is not None and not isinstance(f["hit_count"], int):
            fail(errors, p + ".hit_count", "hit_count.type", _brief(f["hit_count"]), "整数或 null",
                 "hit_count 写成整数或 null")
        if "deferred" in f and f["deferred"] is not None and not isinstance(f["deferred"], str):
            fail(errors, p + ".deferred", "deferred.type", _brief(f["deferred"]), "字符串或 null",
                 "deferred 写成「挂账原因 + 触发条件」字符串或 null")

    ids = sorted(x for x in seen_ids if isinstance(x, int))
    if findings and ids and ids != list(range(1, len(ids) + 1)):
        fail(errors, "$.findings", "ids.sequential", ids, "1..N 全局连续",
             "把 findings 按当前顺序重编号为 1..%d（--repair 可自动做）" % len(findings),
             auto=True)

    # excluded
    excluded = data.get("excluded", [])
    if not isinstance(excluded, list):
        fail(errors, "$.excluded", "excluded.type", _brief(excluded), "数组", "excluded 不是数组")
    else:
        for i, e in enumerate(excluded, 1):
            p = "$.excluded[%d]" % (i - 1)
            if not isinstance(e, dict):
                fail(errors, p, "excluded.type", _brief(e), "对象", "这条 excluded 不是对象")
                continue
            extra = set(e) - {"title", "reason", "kind", "checked"}
            if extra:
                fail(errors, p, "excluded.fields", sorted(extra), "只允许 title/reason/kind/checked",
                     "删掉 excluded 里未定义的字段 %s" % ", ".join(sorted(extra)))
            for k in ("title", "reason", "kind"):
                if k not in e:
                    fail(errors, p, "excluded.required", None, "必填 %s" % k,
                         "补上必填字段 %s" % k)
            if "reason" in e and (not isinstance(e["reason"], str) or len(e["reason"]) < 4):
                fail(errors, p + ".reason", "excluded.reason.len", _brief(e["reason"]), ">= 4 字符",
                     "reason 写清为什么否（前提不成立 / 刻意设计）")
            if "kind" in e and e["kind"] not in EXCLUDED_KINDS:
                fail(errors, p + ".kind", "excluded.kind.enum", _brief(e["kind"]),
                     "false_positive / intentional",
                     "kind 改成 false_positive（误报）或 intentional（刻意设计）")
            if "checked" in e and not isinstance(e["checked"], bool):
                fail(errors, p + ".checked", "excluded.checked.type", _brief(e["checked"]), "布尔",
                     "checked 写成 true/false（是否真的查证过）")

    # 裁定统计
    stats = {}
    for f in findings:
        if isinstance(f, dict) and "verdict" in f:
            stats[f["verdict"]] = stats.get(f["verdict"], 0) + 1
    return errors, stats


# ── 有边界的自动修复（bounded auto-repair） ──────────────────────────
# 判据：确定性、无歧义、不丢信息。目前只开放一条：id 全局重编号。
def auto_repair(data):
    """返回 (新数据, 已应用动作列表)。只改允许自动修的地方，其余原样保留。"""
    out = copy.deepcopy(data)
    applied = []
    findings = out.get("findings")
    if isinstance(findings, list) and findings:
        old = [f.get("id") for f in findings if isinstance(f, dict)]
        for n, f in enumerate(findings, 1):
            if isinstance(f, dict):
                f["id"] = n
        applied.append({
            "rule": "ids.sequential",
            "action": "把 findings[*].id 按当前顺序重编号为 1..%d" % len(findings),
            "before": old,
            "after": list(range(1, len(findings) + 1)),
        })
    return out, applied


def build_receipt(src, status, issues, applied=None, last_good=None, data=None):
    return {
        "receipt": RECEIPT_KIND,
        "source": src,
        "generated_at": _now(),
        "status": status,                      # passed / failed / repaired / needs_manual_edit
        "last_good": last_good,                # archify: failures keep the last-good artifact
        "counts": {
            "issues": len(issues),
            "auto_fixable": sum(1 for i in issues if i.auto),
            "applied": len(applied or []),
            "findings": len(data.get("findings", [])) if isinstance(data, dict) else 0,
            "excluded": len(data.get("excluded", []) or []) if isinstance(data, dict) else 0,
        },
        "issues": [i.to_dict() for i in issues],
        "applied": applied or [],
    }


def _now():
    import datetime
    return datetime.datetime.now().replace(microsecond=0).isoformat()


def print_issues(issues):
    auto = [i for i in issues if i.auto]
    manual = [i for i in issues if not i.auto]
    print("校验失败，共 %d 处（可自动修 %d 处，需手工改 %d 处）:" % (len(issues), len(auto), len(manual)))
    for i in issues:
        tag = "auto " if i.auto else "edit "
        print("  [%s] %s" % (tag.rstrip(), i))
        print("         found=%s | expected=%s" % (i.found, i.expected))
    if auto:
        print("\n可自动修（确定性、不丢信息）: 加 --repair 由校验器代劳")
    if manual:
        print("需你或 Agent 手工改: 按上面 repair 字段的指令定点改，无关结构别动")


def main():
    args = [a for a in sys.argv[1:]]
    flags = {a for a in args if a.startswith("--")}
    positional = [a for a in args if not a.startswith("--")]
    if len(positional) != 1 or (flags - {"--json", "--repair", "--no-receipt"}):
        print("用法: python validate_report.py <findings.json> [--json] [--repair] [--no-receipt]")
        return 2
    src = positional[0]

    try:
        with open(src, encoding="utf-8") as fh:
            data = json.load(fh)
    except OSError as e:
        print("读取失败: %s" % e)
        return 2
    except json.JSONDecodeError as e:
        print("JSON 解析失败: %s" % e)
        return 1

    receipt_path = src + ".receipt.json"

    def write_receipt(rec):
        if "--no-receipt" in flags:
            return None
        with open(receipt_path, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=2)
        return receipt_path

    errors, stats = validate(data)

    if not errors:
        rec = build_receipt(src, "passed", [], data=data)
        print("校验通过。findings=%d, excluded=%d, 裁定分布=%s" % (
            len(data.get("findings", [])), len(data.get("excluded", []) or []),
            ", ".join("%s:%d" % kv for kv in sorted(stats.items())) or "无"))
        write_receipt(rec)
        return 0

    # 自动修复路径（archify: 只有通过的产物才原子替换目标）
    if "--repair" in flags:
        fixable = [i for i in errors if i.auto]
        if not fixable:
            print("没有可自动修的项（%d 处都需手工改），原文件未改动。" % len(errors))
            print_issues(errors)
            rp = write_receipt(build_receipt(src, "needs_manual_edit", errors, data=data))
            if rp:
                print("\nrepair receipt → %s" % rp)
            return 1
        new_data, applied = auto_repair(data)
        left, _ = validate(new_data)
        if left:
            # 自动修复后仍不过 → 保留 last-good，绝不落盘半成品
            print("自动修复后仍有 %d 处未通过，已放弃替换，原文件保持不变。" % len(left))
            print_issues(left)
            rp = write_receipt(build_receipt(src, "needs_manual_edit", left, applied, data=data))
            if rp:
                print("\nrepair receipt → %s" % rp)
            return 1
        last_good = src + ".bak"
        shutil.copy2(src, last_good)
        tmp = src + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(new_data, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, src)                     # 原子替换
        print("自动修复 %d 处并通过复检，已原子替换 %s（last-good 备份 → %s）" % (
            len(applied), src, last_good))
        for a in applied:
            print("  · %s: %s" % (a["rule"], a["action"]))
        rp = write_receipt(build_receipt(src, "repaired", [], applied, last_good, new_data))
        if rp:
            print("repair receipt → %s" % rp)
        return 0

    print_issues(errors)
    rp = write_receipt(build_receipt(src, "failed", errors, data=data))
    if rp:
        print("\nrepair receipt → %s" % rp)
    if "--json" in flags:
        print(json.dumps(build_receipt(src, "failed", errors, data=data),
                         ensure_ascii=False, indent=2))
    return 1


if __name__ == "__main__":
    sys.exit(main())
