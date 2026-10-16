# Git Worktrees 隔离：并行开发不冲突

> 触发说法："开个新功能" / "并行开发" / "隔离变更" / "用 worktree" / "多 Agent 协作"

**铁律**：每个功能独立 worktree，**不干扰 main 分支**，清理方便。

---

## 为什么用 worktrees

| 问题 | 传统分支 | worktree |
|------|----------|----------|
| **切换上下文** | `git checkout` 丢未提交 | 独立工作区，不切换 |
| **并行开发** | 容易冲突 | 物理隔离 |
| **测试干扰** | 同目录可能污染 | 完全隔离 |
| **清理成本** | 删除分支 + 恢复文件 | `git worktree remove` |

**核心优势**：
- 每个功能独立工作区（不同目录）
- 同时开发多个功能不冲突
- 随时可放弃（直接删除 worktree）
- 不污染主仓库

---

## 流程

```
① 创建 worktree  →  ② 验证基线  →  ③ 开发  →  ④ 收尾清理
```

| 步骤 | 产物 | 出口条件 |
|:---|:---|:---|
| ① **创建 worktree** | 独立工作区 | 新分支已创建 |
| ② **验证基线** | 测试报告 | 全量测试绿 |
| ③ **开发** | 代码 + 测试 + 提交 | 功能完成 |
| ④ **收尾清理** | 合并/PR/删除 | worktree 已删除 |

---

## 步骤①：创建 worktree

### 命令

```bash
# 语法
git worktree add -b <branch-name> <worktree-path>

# 示例：创建功能分支
git worktree add -b feature/user-login ../worktrees/user-login

# 示例：创建实验分支
git worktree add -b experimental/new-arch ../worktrees/new-arch
```

### 路径约定

| 类型 | 路径 | 说明 |
|------|------|------|
| **功能分支** | `../worktrees/feature-<name>` | 重要功能 |
| **实验分支** | `../worktrees/experimental-<name>` | 实验性功能 |
| **修复分支** | `../worktrees/fix-<name>` | Bug 修复 |

**注意**：
- worktree 路径**不要放在仓库内**（避免 git 嵌套）
- 统一放在 `../worktrees/` 目录
- 命名清晰（功能名/日期/作者）

### 输出格式

```markdown
## Worktree 创建

**分支**: feature/user-login

**路径**: ../worktrees/user-login

**时间**: 2026-10-16 20:00

**目的**: 开发用户登录功能，隔离 main 分支
```

---

## 步骤②：验证基线

**目标**：确认 worktree 创建后测试全绿。

### 命令

```bash
cd ../worktrees/user-login

# 运行全量测试
pytest  # 或项目测试命令

# 确认构建
npm run build  # 或项目构建命令
```

### 输出格式

```markdown
## 基线验证

**测试**: [x] 全量测试绿（128/128）

**构建**: [x] 构建通过

**备注**: 无
```

---

## 步骤③：开发

**纪律**：
- 在 worktree 内实现功能
- 每步提交（小步快跑）
- 更新 PLAN.md 状态
- 更新 HANDOFF.md 进度

### 命令

```bash
cd ../worktrees/user-login

# 开发...

# 提交
git add -A
git commit -m "feat: 实现用户登录验证"

# 更新状态
# 编辑 PLAN.md / HANDOFF.md
```

### 多 Agent 协作

| Agent | worktree | 职责 |
|-------|----------|------|
| Agent-A | `../worktrees/feature-login` | 登录功能 |
| Agent-B | `../worktrees/feature-register` | 注册功能 |
| Agent-C | `../worktrees/feature-profile` | 用户资料 |

**同步点**：
- 所有 worktree 完成后
- 集成测试
- 合并到 main

### 输出格式

```markdown
## 开发进度

**提交 1**: `feat: 实现用户登录验证` (abc123)

**提交 2**: `test: 添加登录测试` (def456)

**PLAN.md**: Step 3.2 [x] 完成

**HANDOFF.md**: 已更新
```

---

## 步骤④：收尾清理

**走 `finishing-branch.md` 流程**，决定去向。

### 去向 4 选项

| 选项 | 操作 | 清理命令 |
|------|------|----------|
| **Merge** | 合并到 main | `git worktree remove <path>` |
| **PR** | 创建 PR，保留分支 | 保留 worktree 直到 PR 合并 |
| **Keep** | 标记 experimental | 保留 worktree，定期清理 |
| **Discard** | 删除分支 | `git branch -D <branch>` + `git worktree remove <path>` |

### 清理命令

```bash
# Merge 后清理
git worktree remove ../worktrees/user-login

# PR 合并后清理
git worktree remove ../worktrees/user-login
git branch -d feature/user-login

# Discard 清理
git branch -D experimental/new-arch
git worktree remove ../worktrees/new-arch
```

### 输出格式

```markdown
## 收尾清理

**去向**: Merge

**清理操作**:
- [x] 已合并到 main
- [x] worktree 已删除
- [x] HANDOFF.md 已更新

**备注**: 无
```

---

## Worktree 管理

### 查看 worktrees

```bash
# 查看所有 worktrees
git worktree list

# 输出示例
/home/user/project              main
/home/user/worktrees/feature-1  feature/user-login
/home/user/worktrees/feature-2  feature/user-register
```

### 清理废弃 worktrees

```bash
# 查看过期 worktrees（超过 7 天未修改）
find ../worktrees -type d -mtime +7

# 逐个清理
git worktree remove <path>
```

### 输出格式

```markdown
## Worktree 清单

| 分支 | 路径 | 创建时间 | 状态 |
|------|------|----------|------|
| feature/login | ../worktrees/user-login | 2026-10-16 | 开发中 |
| feature/register | ../worktrees/user-register | 2026-10-15 | 待合并 |
| experimental/arch | ../worktrees/new-arch | 2026-10-10 | 待清理 |

**过期 worktrees**: 1（experimental/arch，超过 7 天）
```

---

## 与其他流程的衔接

- **创建 worktree** → 走 `project-lifecycle.md` 阶段③规划
- **开发** → 走五步闭环（对齐→固定→规划→实现→复盘）
- **子 Agent 驱动** → 走 `subagent-driven-development.md`（多 Agent 多 worktree）
- **收尾** → 走 `finishing-branch.md`（Merge/PR/Keep/Discard）
- **清理** → 更新 HANDOFF.md 记录

---

## 常见错误

| 错误 | 症状 | 修复 |
|------|------|------|
| **worktree 放在仓库内** | git 嵌套，混乱 | 移到 `../worktrees/` |
| **命名不清晰** | 不知道哪个是哪个 | 用 `feature-<name>` / `experimental-<name>` |
| **忘记清理** | worktrees 堆积 | 定期 `git worktree list` 检查 |
| **Discard 不删分支** | 分支污染 | `git branch -D` + `git worktree remove` |
| **PR 合并后保留** | 分支冗余 | PR 合并后立刻删除 |

---

## 最佳实践

### ✅ 好的实践

- worktree 路径统一 `../worktrees/<name>`
- 命名清晰 `feature-login` / `experimental-arch`
- 每步提交，信息清晰
- 收尾立刻清理
- 定期清理过期 worktrees

### ❌ 坏的实践

- worktree 放在仓库内
- 命名随意 `test` / `temp`
- 开发完不清理
- PR 合并后保留分支
- 过期 worktrees 堆积

---

## 输出格式（完整报告）

```markdown
# Git Worktree 开发报告

**功能**: 用户登录

**Worktree 路径**: ../worktrees/feature-login

**分支**: feature/user-login

---

## ① 创建

**时间**: 2026-10-16 20:00

**命令**: `git worktree add -b feature/user-login ../worktrees/feature-login`

---

## ② 基线验证

**测试**: [x] 全量测试绿（128/128）

**构建**: [x] 构建通过

---

## ③ 开发

**提交 1**: `feat: 实现用户登录验证` (abc123)

**提交 2**: `test: 添加登录测试` (def456)

**提交 3**: `docs: 更新 API 文档` (ghi789)

**PLAN.md**: Step 3.2 [x] 完成

---

## ④ 收尾

**去向**: Merge

**清理**:
- [x] 已合并到 main
- [x] worktree 已删除
- [x] HANDOFF.md 已更新

---

## 检查清单

- [x] worktree 路径正确
- [x] 基线验证通过
- [x] 每步提交清晰
- [x] PLAN.md 已更新
- [x] 收尾清理完成
```

---

## 检查清单（打印版）

```
Git Worktree 检查清单

[ ] ① 创建 worktree
    [ ] 路径 `../worktrees/<name>`
    [ ] 分支命名 `feature-<name>` / `experimental-<name>`
    [ ] 创建记录落盘

[ ] ② 基线验证
    [ ] 全量测试绿
    [ ] 构建通过
    [ ] 验证记录落盘

[ ] ③ 开发
    [ ] 每步提交
    [ ] 提交信息清晰
    [ ] PLAN.md 已更新
    [ ] HANDOFF.md 已更新

[ ] ④ 收尾清理
    [ ] 去向决定（Merge/PR/Keep/Discard）
    [ ] 清理操作完成
    [ ] worktree 已删除
    [ ] HANDOFF.md 已更新
```

---

> **注意**：worktree 是**隔离变更**的工具，不是"临时目录"。每个 worktree 都应对应一个清晰的功能/实验，收尾时必须决定去向（Merge/PR/Keep/Discard），不许"先放着"。
