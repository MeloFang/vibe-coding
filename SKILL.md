---
name: vibe-coding
description: Vibe Coding + Real Engineering 工作流，从立项到交付的完整项目流程 + 单功能编码闭环。当用户说"开个新项目 / 从零做一个东西 / 我要立项 / 走完整流程 / 生成产品文档 / 建项目文档 / 做到哪一步了 / 交接给下个会话"，或想用 AI 做项目/功能、写代码、调试、重构、体检架构、查 bug，或说"按 vibe coding 来 / 先对齐 / 烤问 / grill / 跑 TDD / 写测试 / 诊断这个 bug / 固定上下文 / 体检架构 / 扫代码质量 / 查查有没有 bug / 换人接着做"时使用。融合 vibe-coding-cn（规划驱动、道法术器、单一 AGENTS.md）、mattpocock/skills（设计树对齐、GLOSSARY/ADR、TDD 垂直切片、深模块设计、代码库体检、会话交接、仓库初始化、任务状态机）与 anthropics/skills（frontend-design）。
---

# Vibe Coding + Real Engineering

用 AI 结对编程把想法做成**可维护**代码。核心一句话：**规划驱动 + 上下文固定 + AI 结对执行**，用真工程纪律防止 AI 失控。

**这是一个一站式技能**：从立项、产品文档、固定上下文、规划，到实现、验证、架构体检和跨会话续接，全在本技能内。

> 完整说明、安装与用法见同目录 `README.md`。

## 何时走哪条道

| 用户说的话 | 你该走什么 |
|:---|:---|
| **"开个新项目" / "从零做一个东西" / "我要立项"** | **走项目全生命周期**（下方第1 节），别直接跳进编码 |
| **"做个功能" / "写个脚本" / "加个模块"** | 走五步闭环（下方第 2 节） |
| **"体检架构" / "扫代码质量" / "查查有没有 bug"** | 走 `references/architecture-review.md` |
| "交接 / 换人接着做 / 切会话" | 走 `references/handoff.md` |

## 路由表：你要做什么 → 读哪个 reference

| 你要做的 | 读这个 |
|:---|:---|
| **开新项目，从立项走到交付** | `references/project-lifecycle.md` ★主干道 |
| **要一份项目文档模板**（产品/计划/续接） | `references/project-docs.md` ★ |
| 仓库初始化、任务状态流转 | `references/repo-setup-and-tasks.md` |
| 轻量需求对齐（问 4 条就够） | 直接用下方「对齐清单」，不用开文件 |
| 复杂需求、多轮追问、烤问 | `references/alignment-deep-dive.md` |
| 写测试、TDD 循环、审查实现 | `references/tdd-playbook.md` ★含强制机制 |
| 设计/重构模块、审查代码质量 | `references/deep-module-design.md` |
| **代码库体检**（找 bug / 浅模块 / 决策缺口 → HTML 报告） | `references/architecture-review.md` |
| **会话出问题了，诊断一下** | `references/diagnosing-session.md` ★P0 |
| **功能做完了，怎么收尾** | `references/finishing-branch.md` ★P0 |
| **用子 Agent 并行实现** | `references/subagent-driven-development.md` ★P1 |
| **git worktree 隔离开发** | `references/using-git-worktrees.md` ★P1 |
| **任务间审查**（每个任务完成后审查） | `references/requesting-code-review.md` ★P2 |
| **接收审查反馈**（如何响应审查意见） | `references/receiving-code-review.md` ★P2 |
| 跨会话/跨人接力（生成交接文档） | `references/handoff.md` |
| 建 `AGENTS.md`（三段式多模型上下文） | `references/AGENTS-template.md` |
| 建术语表 / ADR | `references/CONTEXT-template.md` |
| 把纪律固化成自己的新技能 | `references/SKILL-spec.md` |

---

## 1. 项目全生命周期（开新项目时走这条）

从零做一个项目时，最容易出的错不是代码写错，而是**做着做着忘了要做什么**。固定流程保证：**每个阶段都有一份落盘产物，任何人都能从文件判断现在在哪。**

```
① 立项与产品文档  →  ② 固定上下文  →  ③ 规划  →  ④ 实现  →  ⑤ 验证
                     PRODUCT.md        AGENTS.md   PLAN.md   代码      验收
                                        GLOSSARY.md          测试
                       └── ⑥ 续接文档 HANDOFF.md（全程维护，每个阶段都更新）
```

| 阶段 | 产物 | 出口条件 |
|:---|:---|:---|
| ① **立项与产品文档** | `PRODUCT.md` | 成功标准可验证 + **用户确认**（未确认不许进下一阶段） |
| ② **固定上下文** | `AGENTS.md` + `GLOSSARY.md` + `docs/adr/` | 新 Agent 读完这两份就能开工，不用问基础问题 |
| ③ **规划** | `PLAN.md` | 每步带验收信号，粒度一天左右，只写指令不写实现 |
| ④ **实现** | 代码 + 测试 | 红→绿走完，状态已更新 |
| ⑤ **验证** | 验收记录 | 对着 `PRODUCT.md` 成功标准逐条核对，**人来下结论** |
| ⑥ **续接文档** | `HANDOFF.md` | **从①就建，每阶段更新**；讲清"这程序是什么 / 到哪一步 / 怎么接手" |

**每阶段的详细做法**（含阶段出口检查项）见 `references/project-lifecycle.md`。
**三份文档的模板**见 `references/project-docs.md`。

### 规模适配

| 规模 | 走哪些 | 产物 |
|:---|:---|:---|
| 一次性脚本（<半天） | ②③④，①②③ 口头确认 | 代码 + 测试 |
| 单个功能（1–3 天） | ②③④⑤ + 简版 `HANDOFF.md` | AGENTS + PLAN + 进度 |
| 完整项目（>1 周） | **全六阶段** | PRODUCT + AGENTS + GLOSSARY + ADR + PLAN + HANDOFF |

判断标准：**会不会跨越会话？会不会有别人接手？** 会 → 走全流程。

**但产品文档（①）永远值得写**，哪怕三行字——它是"为什么要做这件事"的唯一记录。

---

## 2. 五步闭环（单个功能的编码内核）

1. **对齐（Grill）** —— 动手前先把"要做什么、不做什么"问清楚。最贵的失败是做错方向。
2. **固定上下文** —— 把结论写进 `AGENTS.md` / `GLOSSARY.md` / `docs/adr/`，让每轮有据可依（不靠聊天记录记忆）。
3. **规划** —— 拆成小步、每步带验收（测试或明确信号），只写指令不写实现。
4. **分步实现** —— 一次只改一个模块 / 一步，跑验证；代码一多就切会话（必要时用 `references/handoff.md` 交接）。
5. **复盘** —— 验证通过再继续；更新上下文 / 进度；可复盘的提交。

## 道法术器（心法，来自 vibe-coding-cn）

- **道（原则）**：规划就是一切；上下文是第一性（垃圾进垃圾出）；奥卡姆剃刀、帕累托、逆向思考；先结构后代码。
- **法（方法）**：一句话目标 + 非目标；能抄不写（先问有没有现成仓库 / 库）；接口先行、实现后补；一次只改一个模块；文档即上下文。
- **术（技巧）**：明确"能改什么 / 不能改什么"；Debug 只给"预期 vs 实际 + 最小复现"；测试交给 AI 但断言人审；代码一多就切会话。
- **器（工具）**：复杂任务选第一梯队模型；Claude Code / Codex / Cursor / WorkBuddy 等 CLI 优先；tmux 多会话、Ollama 本地模型等。

## 四大纪律（对应四大失败模式）

| 失败模式 | 纪律 | 怎么落地 |
|---|---|---|
| 没做对事（对齐缺失） | **Grill 对齐** | 开工前多轮盘问目标 / 非目标 / 约束；轻量任务用下方四条清单，复杂需求走 `alignment-deep-dive.md` |
| 太啰嗦 / 术语乱 | **共享语言** | 建 `GLOSSARY.md` 固化领域词汇 + ADR 记录决策，命名一致、省 token |
| 代码不对（缺反馈环） | **TDD + 诊断** | 红→绿→重构，垂直切片；硬 bug 走诊断六阶段（建环→复现最小化→假设→插桩→修复→回归） |
| 架构泥球 | **架构卫生** | 用深模块词汇（module/interface/depth/seam/adapter/leverage/locality）审查；删除测试辨别浅模块；全库体检走 `architecture-review.md` |

### 对齐清单（Grill）—— 动手前逐项问到清楚
- 这次要交付的**目标**是什么？**非目标**（明确不做）是什么？
- 技术栈 / 约束 / 已有代码在哪里？
- 验收标准是什么（怎么算"做对了"）？
- 风险点 / 不确定项有哪些？

轻量任务用上面四条就够。**复杂需求别只问一轮**——按"设计树 + 前沿"多轮追问，详见 `references/alignment-deep-dive.md`（含每轮提问格式、事实 vs 决策分工、边问边沉淀术语表与 ADR 的门槛）。

### 反馈环（TDD / 诊断）铁律
- **红在前**：先写失败测试 / 失败信号，再写最少代码让它绿；不预支未来测试。
- **只在预先约定的接缝上测**：写测试前先跟用户确认要测哪些接缝，没确认的接缝不写测试。
- **期望值必须来自独立真相源**：不能用代码同样的算法把期望值算出来（同义反复测试按构造就成立，永远测不出东西）。
- **垂直切片，不要水平**：一个测试 → 一个实现 → 重复；别先把测试全写完再写实现（那是在测想象中的行为）。
- **诊断先建环**：硬 bug 第一步是造一个"能红、确定、秒级、可无人跑"的反馈环；没有环就别着急假设。完整六阶段：建环 → 复现最小化 → 假设 → 插桩 → 修复 → 回归。
- **一次一片**：一个边界、一个测试、一次最小实现。

TDD 完整方法论（好测试的标准、接缝、三个反模式、循环规则）见 `references/tdd-playbook.md`。

## 上下文与项目文档约定（单一真相源）

> **术语表约定**：上游 `mattpocock/skills` 已把 `CONTEXT.md` 约定更名为 **`GLOSSARY.md`**。新项目一律用 `GLOSSARY.md`；已有项目若是 `CONTEXT.md`，改名或在开头注明即可，两种名字都能识别，但同一项目内不要混用。

**项目级文档**（开项目时建，模板见 `references/project-docs.md`）：

| 文件 | 回答什么 | 谁写 |
|:---|:---|:---|
| `PRODUCT.md` | 这个程序解决什么问题、成功标准、范围边界 | Agent 起草，**用户审改** |
| `PLAN.md` | 拆成哪些步骤、每步验收信号、当前状态 | Agent |
| `HANDOFF.md` | **这程序是什么 / 做到哪一步 / 后续怎么接手** | Agent，**每阶段更新** |

**上下文文件**：

- **`AGENTS.md`（根目录，单一文件）**：同时承载 AGENTS / CLAUDE / GEMINI 三种 Agent 上下文（vibe-coding-cn 的做法：一份文件三段式，免去多份不同步）。内容含：项目结构、构建 / 测试命令、编码风格与命名、测试 / 提交规范、架构总览、工作流。模板见 `references/AGENTS-template.md`。
- **`GLOSSARY.md`**（旧名 `CONTEXT.md`）：项目专属领域词汇与共享语言。术语表里**不许有实现细节**——它是术语表，不是规格说明书。模板见 `references/CONTEXT-template.md`。
- **`docs/adr/`（ADR）**：记录"难以逆转 + 无上下文会困惑 + 源于真实权衡"的决策（三个条件全中才写）。决策定型当场落盘，不要攒。
- **`docs/handoff/`（会话交接，临时）**：跨 Agent 接力的**单次**交接文档，写进系统临时目录，不落仓库——别污染长期文档。格式见 `references/handoff.md`。

> 分工：`HANDOFF.md` 是**项目级长期活文档**（讲清程序是什么、进度、怎么接手）；`docs/handoff/` 的是**单次会话临时交接**。两者别混。

## 来源与深读
本技能提炼自三个开源项目，需深读时按需克隆（技能本身已自包含，不依赖本地副本）：

- **`vibe-coding-cn`**（规划驱动、道法术器、单一 `AGENTS.md` 模式）：原仓 [`tradecatlabs/vibe-coding-cn`](https://github.com/tradecatlabs/vibe-coding-cn)（曾用 `tukuaiai/vibe-coding-cn`，已重定向），重点看 `AGENTS.md`、`i18n/zh/prompts/`、`i18n/zh/skills/`。
- **`mattpocock/skills`**（*Skills For Real Engineers*）：提供本技能大部分方法论内核——设计树对齐（`grilling` / `grill-me` / `grill-with-docs`）、共享语言与领域模型（`domain-modeling`）、TDD 垂直切片（`tdd`）、深模块设计词汇（`codebase-design`）、架构体检（`improve-codebase-architecture`）、会话交接（`handoff`）、仓库初始化（`setup-matt-pocock-skills`）、任务状态机（`triage`）、SKILL.md 写法规范。
- **`anthropics/skills`**（`frontend-design`）：让 Agent 先定美学方向再写前端，拒绝通用 AI 味设计。

> 本仓库只融合方法论，未复制三者源码或资产。

## 写子技能的规范（SKILL.md）
若要把某条纪律固化成**自己的独立技能**，遵循 mattpocock 的写法：YAML 前置含 `name` + `description`（description 即触发词 / 适用场景，写好它才能被正确加载）；正文是"自包含的纪律参考"，用分阶段 / 分节、每节可独立查；可配 `references/` 放示例与细节。规范见 `references/SKILL-spec.md`。

> 注意：拆出去的技能会独立成一个目录，随"该触发时没触发"的风险。**除非某条纪律自成一体且触发场景明显不同，否则优先留在本技能的 `references/` 里**（就像 `handoff`、`architecture-review`、`repo-setup-and-tasks` 这样）。
