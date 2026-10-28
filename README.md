# labkit

一个给人 + AI 共用的项目骨架。开新项目时把 `seed/` 整份拷过去，填几个 token，改一个文件名，项目就长好了。之后不管换模型、换客户端、对话被压缩成什么样子，新来的 agent 读项目里的 `AGENTS.md` 就能接上。

结构长在 `seed/` 里，它就是未来项目的样子：

```text
AIWORK/      AI 的工作区，随便写
  Prototype/   baseline 原始仓库，拷进来就不动
  Experiment/  一个实验一个目录，README 头部几行是给人看的
    data/      高度复用的数据池，按类型细分，引用不拷贝
    environ/   复现基底：环境记录、冻结协议、共享默认配置
  Status/      交接窗口 + 全局节点 + inter 总览页 + 归档
REVIEW/      人确认节点后 AI 放入的代码与结果快照，人在此审核
HUMAN/       审核后晋升的最高净值内容，只经人一句话进入
```

语言分工：AI 读的（`AGENTS.md` 和所有 `agent_` 前缀文件）是英文——LLM 的母语是英语；人读的说明书双语（生成的项目根目录有 `README.md` 跳板 + `README_zh.md` + `README_en.md`）。

命名约定：区全大写，区内层首字母大写，再往下一律小写。没有脚本：建实验、打快照、校验哈希、刷新 inter 全是 agent 照规则手工做的。

## 怎么用（对 agent 说）

```text
读 <本仓库路径>/AGENTS.md，给目标 <一句话> 生成一个项目到 <路径>
```

生成协议见本仓库 `AGENTS.md`（很短）。

## 设计要点（为什么长这样）

- **三区权限**：AIWORK AI 可写（开新方向要人点头）；REVIEW 只进快照、进后不改（sha256 清单作证）；HUMAN 只经人一句话晋升。AI 的自述不是证据——证据是哈希清单和 git 历史。
- **记录 append-only**：结论被推翻 = 原处划掉旧值追加新值；流水只有六种动作（N 新建 / R 运行 / F 修正 / M 节点 / P 晋升 / X 失败），讨论和推理永远不进流水。
- **判据先于结果**：实验 criteria 在第一次运行前写死，否则结论只能记 inconclusive。
- **真实时间戳**：机器时钟、含秒、带 UTC 偏移，不凑整不编造。
- **inter.html**：`AIWORK/Status/` 下的自包含总览页——方向/实验/结论/统计/逐 bench 表 + 人的本机笔记；跑动实验由 watcher 刷 live 区，页面自动重载。

License: MIT（见 `LICENSE`）。
