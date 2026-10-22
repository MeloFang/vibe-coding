# GitHub 开源查重 · 能抄不写

动手写第一行实现代码之前，先确认「这个东西是不是已经有人做好了」。这是 `法` 层「能抄不写」的**强制落地**——不查就动手，算违反纪律。

## 什么时候必须查

- 任何**新功能 / 新项目**，进入 ④ 实现 之前；
- 尤其是一开始就冒出「这个应该有现成的吧」的直觉时；
- 连「一次性脚本」也建议花 30 秒搜一下（很可能直接 `pip install` / `npm i` 解决，根本不用写）。

> 已经确认要自研的场景（如纯业务私有逻辑），也要在 `HANDOFF.md` 或 `AGENTS.md` 留一句「已检索，无合适现成（检索词：…）」，避免下个会话又搜一遍。

## 怎么搜（按优先级）

1. **gh CLI（若已登录）**
   ```bash
   gh search repos "<关键词>" --sort stars --limit 10 --language <语言可省>
   gh search repos "<关键词>" --sort stars --limit 10 --web   # 开浏览器看详情
   ```
2. **GitHub API（无需登录，沙盒直连可用）**
   ```bash
   curl -s "https://api.github.com/search/repositories?q=<query>&sort=stars&order=desc&per_page=10"
   ```
   重点读返回的字段：`items[].stargazers_count` / `language` / `pushed_at` / `license.spdx_id` / `description`。
3. **WebSearch / WebFetch** —— 兜底，用于中文生态、小众库、或需要对比评测时。

## 检索词怎么造

- **中英双语 + 同义词**：同一功能用「pdf 表格提取 / extract tables from pdf / tabula 替代」多组试；
- **技术栈限定**：`q=markdown editor language:typescript`、`q=llm agent framework`；
- **组合「功能 + 语言 / 框架」** 比单关键词命中率高得多；
- 用 `topic:` 过滤：`q=topic:rag topic:python`。

## 对每个候选，只看 4 件事

| 维度 | 看什么 | 红线 |
|---|---|---|
| **星标量级** | <1k 谨慎，1k–10k 可用，>10k 优先 | 太低且久不更新 → 不如自己写 |
| **是否在维护** | `pushed_at` 距今、近月 commit 数 | 半年以上没动 + 无人修 issue → 慎入 |
| **许可证** | `license.spdx_id` | 单位 / 商用避开 GPL / AGPL 强 Copyleft；拿不准先标红 |
| **是否真解决同一问题** | 读 README + 一眼架构 | 标题像、实际偏 → 不算 |

## 决策（三选一，写进规划）

- **能用现成** → 优先 `fork` 或作为依赖引入，**不要自己写**；在 `PLAN.md` 标注「复用 X，不造轮子」。
- **能借鉴** → 只抄思路 / 算法 / 配置，不搬代码；标注借鉴来源。
- **确实没有** → 自己写，但**在 `HANDOFF.md` / `AGENTS.md` 记一句「已检索 GitHub，无合适现成（检索词：…）」**，防止重复劳动。

## 产出格式（一句话结论即可）

```
【开源检索】功能：<要做的事>
候选：<repo A>（<stars>，<license>，<最近提交>）、<repo B>…
决定：复用 A / 借鉴 B 的 X / 自研（已记录检索词）
```

## 纪律红线

- 动手写实现代码前**必须**走这一步；跳过 = 违反「能抄不写」。
- 单位 / 商用场景：**许可证合规优先于一切**；拿不准先标红，问清楚再引入。
- 不要把「标题相似」算作「能解决同一问题」——以 README + 实际用法为准。
