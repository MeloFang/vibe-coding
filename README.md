# vibe-coding

> 规划驱动 + 上下文固定 + AI 结对执行 —— 开项目就走固定流程，从立项一路到验证交付，全程有一份"程序是什么 + 到哪一步 + 怎么接手"的活文档。

一个跨项目通用的 AI 结对编程工作流技能。把「让 AI 写代码」从一次性碰运气，变成一条**可审计、可复盘、可移交**的流水线。

---

## 解决什么问题

AI 结对编程最常见的五种翻车，本技能各有一道关卡挡住：

| 失败模式 | 典型症状 | 挡住它的关卡 |
|:---|:---|:---|
| **做错方向** | 代码写完了，但不是你要的东西 | ① 对齐（Grill）+ ② GitHub 查重（能抄不写） |
| **代码不对** | 看着像那么回事，一跑就崩 | ④ TDD 红在前 + 诊断六阶段 |
| **过度工程** | 简单的事写出一堆抽象和样板 | ③ 最小完整改动（决策阶梯 + Never cut） |
| **架构泥球** | 越写越乱，改一处崩三处 | 深模块词汇 + 代码库体检（带机器可读报告） |
| **项目级失控** | 做着做着忘了要做什么、接手的人看不懂 | 项目六阶段生命周期 + `HANDOFF.md` 活文档 |

---

## 核心流水线：六道关卡

每个编码任务从想法到验收，依次过六道关卡（具体规则在 `SKILL.md` 与对应 reference）：

```
① 对齐 Grill ──→ ② GitHub 查重 ──→ ③ 最小完整改动 ──→ ④ TDD 红在前 ──→ ⑤ 四段式审查 ──→ ⑥ 体检 + 机器可读报告
   问清目标/非目标    先搜现成轮子       决策阶梯选最小方案     先写失败测试        Must/Should/Nice      findings.json
   不做什么          能抄不写           Never cut 不裁剪       再写最少实现        全局编号 + Verdict     三级裁定 + 校验器
```

**关键裁决**：最小化指**实现代码最少，不是测试最少**——测试定义"完整"，阶梯定义"最小"。TDD 红在前是铁律，永不松。

外面包一层**项目六阶段生命周期**（开新项目时走）：立项（PRODUCT.md）→ 固定上下文（AGENTS/GLOSSARY/ADR）→ 规划（PLAN.md）→ 实现 → 验证（人下结论）→ 全程维护 HANDOFF.md。按规模适配：一次性脚本只走中间三步，跨会话/有人接手才走全套。

---

## 安装

用户级安装，所有项目自动可用。

### WorkBuddy

```bash
git clone https://github.com/MeloFang/vibe-coding.git ~/.workbuddy/skills/vibe-coding
```

或直接把 `vibe-coding/` 整个目录拷到 `~/.workbuddy/skills/` 下。

### 其他 Agent（通用）

技能就是一个文件夹 + 一个 `SKILL.md`，放进目标 Agent 的技能目录即可：

- Claude Code → `.claude/skills/vibe-coding/`
- Codex / Cursor / OpenCode → 对应的 skills 目录

---

## 怎么用

### 自动触发

对话里说下面任意一句，技能会被自动加载：

> 开个新项目 / 从零做一个东西 / 我要立项 / 走完整流程 / 生成产品文档 / 做到哪一步了 / 按 vibe coding 来 / 先对齐 / 烤问 / grill / **先搜 github 有没有现成轮子** / **查重** / **最小实现** / **别过度设计** / 跑 TDD / 写测试 / 诊断这个 bug / 固定上下文 / 体检架构 / 扫代码质量 / 查查有没有 bug / 交接给下个会话 / 换人接着做

### 主动指定

> 用 vibe coding 帮我开个新项目，做一个 XXX

### 典型对话

```
你：用 vibe coding 帮我开个新项目，做个批量重命名工具
我：① 立项起草 PRODUCT.md（你审改确认）→ ② 建 AGENTS.md + GLOSSARY.md
    → ③ 规划前先搜 GitHub 有没有现成轮子 → 拆步写进 PLAN.md
    → ④ 按决策阶梯做最小实现，先写失败测试（红）再写实现（绿）
    → ⑤ 对着成功标准逐条核对，你下结论 → ⑥ HANDOFF.md 更新进度

你：这个 bug 有点怪，诊断一下
我：建环 → 复现最小化 → 假设 → 插桩 → 修复 → 回归，发现必须自己实证

你：功能做完了，怎么收尾
我：验证 → 清理调试代码 → 合并 → 复盘

你：体检一下这个代码库
我：三类发现（正确性/架构/决策缺口）→ HTML 报告给你看
    + findings.json（三级裁定，validate_report.py 校验过）给机器消费
```

---

## 文件结构

```
vibe-coding/
├── SKILL.md                          # 技能主文件：路由表 + 生命周期 + 五步闭环 + 四大纪律
├── README.md                         # 本文件
└── references/
    │
    │  ── A. 立项与上下文 ──
    ├── project-lifecycle.md          # ★ 项目全生命周期（六阶段 + 规模适配）
    ├── project-docs.md               # ★ PRODUCT / PLAN / HANDOFF 三份模板
    ├── repo-setup-and-tasks.md       #   仓库初始化清单 + 任务状态机
    ├── AGENTS-template.md            #   单一文件三段式上下文模板
    ├── CONTEXT-template.md           #   共享语言 / 术语表模板
    │
    │  ── B. 动手前 ──
    ├── alignment-deep-dive.md        #   对齐深挖：设计树 + 前沿多轮追问
    ├── github-scouting.md            # ★ P1 GitHub 查重：搜现成开源、评估、决策（能抄不写）
    ├── smallest-change.md            # ★ P1 最小完整改动：决策阶梯 + Never cut + shortcut 约定
    │
    │  ── C. 实现与测试 ──
    ├── tdd-playbook.md               # ★ P0 TDD：好测试、接缝、反模式、循环规则（红在前铁律）
    ├── deep-module-design.md         #   深模块词汇：module/interface/depth/seam
    │
    │  ── D. 质量与诊断 ──
    ├── architecture-review.md        #   代码库体检：三类发现 → HTML + findings.json
    ├── report-schema.json            #   findings.json 机器可读 Schema（三级裁定）
    ├── validate_report.py            #   findings.json 零依赖校验器
    ├── test_validate_report.py       #   校验器自测（12 项断言）
    ├── diagnosing-session.md         # ★ P0 会话诊断：建环→复现→假设→修复
    │
    │  ── E. 协作与并行 ──
    ├── subagent-driven-development.md# ★ P1 子 Agent 并行开发
    ├── using-git-worktrees.md        # ★ P1 Git Worktree 隔离
    ├── requesting-code-review.md     # ★ P2 任务间审查（四段式 + Verdict）
    ├── receiving-code-review.md      # ★ P2 接收审查反馈
    │
    │  ── F. 收尾与交接 ──
    ├── finishing-branch.md           # ★ P0 分支收尾：验证→清理→合并→复盘
    ├── handoff.md                    #   临时会话交接（写系统临时目录）
    │
    │  ── G. 元规范 ──
    └── SKILL-spec.md                 #   如何写自己的新技能
```

---

## 与六个上游的关系

本技能是融合产物，只取方法论，不复制源码：

| 上游 | 贡献了什么 | 取舍 |
|:---|:---|:---|
| [tradecatlabs/vibe-coding-cn](https://github.com/tradecatlabs/vibe-coding-cn) | 规划驱动心法、道法术器、单一 `AGENTS.md` 三段式 | 全部吸收 |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 设计树对齐、GLOSSARY/ADR、TDD 垂直切片、深模块词汇、架构体检、会话交接、任务状态机、SKILL 写法规范 | 全部吸收（`CONTEXT.md` 更名为 `GLOSSARY.md`） |
| [anthropics/skills](https://github.com/anthropics/skills) | `frontend-design`：先定美学方向再写前端 | 全部吸收 |
| [obra/superpowers](https://github.com/obra/superpowers) | 7 项工程优化：会话诊断、分支收尾、子 Agent 并行、Worktree 隔离、任务间审查、接收审查、TDD 强制 | 全部吸收（references 内 7 篇为其改编） |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | 决策阶梯、Never cut 清单、shortcut 注释约定、审查四段式 + 全局编号 + Verdict | **不采纳**"trivial 改动不用测试"——TDD 红在前不变 |
| [cloudflare/security-audit-skill](https://github.com/cloudflare/security-audit-skill) | 三级裁定（confirmed / needs_validation / rejected）、机器可读报告 + schema + 校验器形态 | 只借裁定思想与产物形态；full-audit 沙盒流程未引入 |

---

## 写子技能

想把某条纪律固化成独立技能，照 `references/SKILL-spec.md` 来。核心要求：目录名与 frontmatter 的 `name` 一致（kebab-case）；**`description` 就是触发词**，写清"什么时候用"；正文是自包含的纪律参考；长示例放 `references/`。

> **优先留在本技能内**：拆出去的技能独立成目录，随"该触发时没触发"的风险。除非某条纪律自成一体且触发场景明显不同，否则不拆。

---

## 许可证

见 [LICENSE](LICENSE)。
