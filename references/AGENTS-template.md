# AGENTS.md 模板（单一文件，三段式多模型上下文）

> 用法：放进项目根目录。一份文件同时喂 AGENTS / Claude / Gemini 等所有编码 Agent，
> 免去维护多份（CLAUDE.md / GEMINI.md）不同步的麻烦。来源：vibe-coding-cn 的
> 合并式写法 + 通用工程规范。以下内容按需删改，`<...>` 替换为项目实际值。

---

# Repository Guidelines（通用 Agent 规则）

## Project Structure & Module Organization
- 根目录：`README.md` 给全貌，`Makefile` / `package.json` 封装日常命令，`LICENSE` 载协议。保持根扁平，避免巨石文件。
- 文档与代码分离：代码在 `src/`，文档在 `docs/`，提示词 / 技能在 `prompts/`、`skills/`。
- 备份 / 构建产物不入库（写进 `.gitignore`）。

## Build, Test, and Development Commands
- `<构建命令，如 npm run build>`
- `<测试命令，如 npm test / pytest>`
- `<lint 命令，如 markdownlint / eslint>`

## Coding Style & Naming Conventions
- 文字层（注释 / 日志 / 文档）：`<中文 / 英文>`；代码符号统一英文、语义直白，不用晦涩缩写。
- 缩进：空格缩进（2 或 4，选定后不混用）；行宽 ≤ 120 列；Git diff 可读性优先。
- 设计品味：优先消除分支与重复；函数单一职责且短小；跨模块接口保持稳定的签名。
- 依赖管理：新增库记录安装方式、最小版本、来源与"为什么需要"。

## Testing Guidelines
- 引入代码至少提供最小可复现测试；推荐 `pytest` / 框架自带测试，文件命名 `test_*.py`，red-green-refactor 循环。
- 文档 / 提示词改动：提交前跑 lint；涉及数据附最小输入 / 输出样例。

## Commit & Pull Request Guidelines
- Commit 遵循 Conventional Commits：`feat|fix|docs|chore|refactor|test: scope – summary`。
- PR 必填：变更摘要、动机 / 关联 Issue、测试与验证步骤。

## Security & Configuration Tips
- 运行脚本前确认输出目录不覆盖私有数据；外部依赖来源可追溯，第三方脚本标许可证。

## Architecture Overview & Workflow
- 工作流：规划 → 上下文固定 → 分步实现 → 自测 → 复盘，对应资产在 `docs/`、`prompts/`、`skills/`。
- 设计决策 / 目录变动后，同步修订本文件，确保团队共享同一真相源。

---

# CLAUDE.md（Claude 系列模型专用段）

This file provides guidance to Claude series models when working with code in this repository.
（可直接复用上方 Repository Guidelines 的要点，按需补充 Claude 专属约定。）

## Key Commands
（同上方 Build/Test，列出最常用 2-3 条。）

## Architecture & Structure
（列出核心目录与"为什么这样分"，便于新会话快速建立心智模型。）

---

# GEMINI.md（Gemini 等模型专用段）

## 项目概述
本项目目标：`<一句话>`。核心理念：`<规划驱动 / 模块化>`。

## 技术栈
`<语言 / 框架 / 关键依赖>`。

## 文件结构
（精简树，标注每个顶层目录职责；详见上方 Project Structure。）

---

# CONTEXT.md（项目共享领域语言 / 术语表，另见 references/CONTEXT-template.md）
- `<术语>`：`<含义>`（团队黑话、缩写、模块语义统一在此定义，命名一致、省 token）
