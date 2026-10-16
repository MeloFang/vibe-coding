# SKILL.md 写法规范（提炼自 mattpocock/skills）

> 任何想固化为"可复用纪律"的知识，都写成一个独立技能目录 `<skill-name>/SKILL.md`。
> 来源：mattpocock/skills 的实际写法 + WorkBuddy 技能机制。

## 文件结构
```
skills/<skill-name>/
├── SKILL.md          # 必需：技能正文（含 YAML 前置）
└── references/       # 可选：示例、细节、长文档，SKILL.md 里用链接引用
    └── ...
```

## SKILL.md 前置（YAML frontmatter）—— 最关键
```yaml
---
name: <skill-name>            # 与目录名一致，kebab-case
description: <一句话触发词 + 适用场景>   # 决定何时被加载，必须写好
# 可选：disable-model-invocation: true   # 仅人工触发、AI 不自动调用时加
---
```
- **`description` 是触发词**：写清"什么时候用这个技能"（如"用户说诊断 bug / 跑 TDD 时"）。
  描述越准，技能越容易被正确加载。
- 命名只用小写 + 中划线。

## 正文写法
1. **开头一句话定位**：这个技能解决什么、对应哪个失败模式。
2. **分节 / 分阶段**，每节自包含、可独立查阅（不要写成线性小说）。
3. **给清单 / 铁律 / 反模式**：可勾选的 checklist、明确的"绝不"比散文好执行。
4. **引用参考**：长示例、代码模板放 `references/`，正文只链不堆。
5. **语言**：面向执行 Agent，指令清晰；中文项目用中文，技术词保留英文。
6. 不要有 em-dash（——）等易翻车的标点（mattpocock 的硬规，也利于中文排版）。

## 灵感：mattpocock 三个范本
- `tdd`：前置 + "什么是好测试 / 接缝 / 反模式 / 循环规则"，每节都可在循环中查。
- `diagnosing-bugs`：六阶段（建反馈环 → 复现最小化 → 假设 → 插桩 → 修复 → 清理），每阶段带 checklist。
- `grill-me`：极简，仅"调用 grilling 技能"——说明子技能可互相路由。

## 注册（WorkBuddy）
- 把技能目录放进 `~/.workbuddy/skills/`（用户级，所有项目可用）或 `<项目>/.workbuddy/skills/`（仅本项目）。
- 之后在任意任务里说"按 vibe coding 来"或让 Agent 按 description 自动匹配即可加载。
