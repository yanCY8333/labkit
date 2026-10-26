---
name: Labkit
description: Project structure scaffold for long-running work shared by multiple agents and humans. Use when starting a new project, when taking over a project from another agent, when context may be lost, or when the user asks where to record state, hypotheses, decisions, runs, or claims. Defines a bounded, append-only, tool-agnostic layout.
---

# Labkit

本项目的记忆不依赖任何 agent 的会话上下文。所有判断必须能从仓库文件重建。

## 开工：只读这一页

按顺序读，**读完就停**：

1. `STATE.md` — 现在在哪（有上限，很快读完）
2. `CHARTER.md` — 为什么做这个项目、边界在哪
3. `LOG.md` 最后 20 行 — 刚刚发生了什么
4. `CLAIMS/INDEX.md`（若存在）— 有哪些断言、各是什么状态

到此为止。需要细节再按 `NOTES/` 或产物路径**单点打开**，不要整份通读历史。

## 三个写入口

### 动作之后 —— `LOG.md` 追加一行

```text
2026-11-02 14:20 | claude/opus | R | 跑完 4 图 fine-only 对照  out=runs/fine_only/
```

- 一行，≤240 字，不换行，不写解释性段落。
- 一个动作一行。一句话说不清，说明动作太大，先拆。
- 类型：`Q` 提问 · `T` 推理 · `D` 设计 · `R` 运行 · `F` 事实 · `X` 失败 · `H` 交接。

只记：改了文件、跑了命令、启动/结束实验、做了决定、出错。
不记：读文件、搜索、思考草稿、同一动作的多条流水账。

### 收工 —— `STATE.md` 覆盖

交接卡是**覆盖式**的，只保留当前有效状态。历史在 `LOG.md`，不在 STATE 里堆积。

至少写清：目标、当前假设、最近一次运行、下一步、阻塞。

### 结论变化 —— 追加，不覆盖

- `DECISIONS.md`：只增。
- `NOTES/THINKING.md`：假设被推翻时保留原假设，标 `❌` 并写"被什么推翻"。
- `CLAIMS/*.md`：修改结论时追加一条 `outcome`，旧值划掉保留。

## 四条硬规则

1. **STATE ≤ 60 行，LOG ≤ 40 条。** 超了先归档，不加长。
2. **每个 `out=` 必须指向真实存在的路径。** 没有产物的动作不值得记。
3. **审计层不自己造。** 用 git；不要手写"我改过什么"当作证据。
4. **事实不进 LOG。** 结算后的结论写进 `NOTES/BASE.md`，LOG 只留指针。

## 什么放哪里

| 你想写的 | 放这里 | 不该放 |
|---|---|---|
| 这个项目要回答什么 | `CHARTER.md` | README、LOG |
| 现在做到哪了 | `STATE.md` | NOTES |
| 刚做了什么 | `LOG.md` | STATE、DECISIONS |
| 我猜是什么原因 | `NOTES/THINKING.md` | BASE、LOG |
| 打算怎么验证 | `NOTES/DESIGN.md` | THINKING |
| 实际跑了什么 | `NOTES/RUNS.md` | LOG |
| 确定的事实 | `NOTES/BASE.md` | THINKING |
| 一条可证伪的断言 | `CLAIMS/Cxxx.md` | BASE |
| 以后不再讨论的选择 | `DECISIONS.md` | THINKING |

详细语义见 `references/structure.md`，写作规则见 `references/conventions.md`。

## 自检

交付或接手前问四个问题：

1. `STATE.md` 里的"下一步"，一个陌生人能直接执行吗？
2. `LOG.md` 里每条的 `out=` 都还存在吗？
3. `NOTES/BASE.md` 里每条事实都能追到产物或 claim 吗？
4. `CLAIMS/` 里有没有"跑完之后才补的判据"？判据必须是 `created` 时写的。
