# {{NAME}}

{{GOAL}}

这是全项目的中文说明书，读完这一份就够。英文版在 `README_en.md`。规则文件是 `AGENTS.md`，那是给 AI 的，英文写的；你不用读它，想管住 AI 的行为时扫一眼它的"Never violate"一节即可。

## 结构

```text
├── AIWORK —— AI 工作区，AI 可自由工作
│   ├── Prototype —— baseline 原始仓库，进来就不改，是后续一切工作的基础
│   ├── Experiment —— 实验存放处；方向由你确认，方向内 AI 自行分支
│   │   ├── data —— 高度复用的数据（拟合对象、数据集等），按类型细分；只引用不拷贝
│   │   └── environ —— 复现基底：环境/硬件记录、跨实验冻结协议、共享默认配置
│   └── Status —— 状态记录
│       ├── status_global —— 项目至今的重大节点，节点由你确认，AI 不自己加行
│       ├── agent_status_<时间>_current —— 滚动交接窗口，AI 开工读、收工写
│       ├── inter.html —— 你的一页总览：方向/实验/结论/统计 + 你自己的 note（双击即开，AI 收工刷新）
│       └── archive —— 滚出去的旧窗口，只进不改
├── REVIEW —— 你确认的节点：AI 把必要的代码与结果以快照放进这里，你在此审核（也可与 AI 共同审核）
└── HUMAN —— 审核后留下的最高净值内容；你说"放进 HUMAN"AI 才从 REVIEW 原样拷入，之后 AI 永不改动
```

文件名约定：全大写 = 区（AIWORK / REVIEW / HUMAN）；首字母大写 = 区内层（Prototype / Experiment / Status）；再往下一律小写。`AGENTS.md` 和带 `agent_` 前缀的文件是 AI 的协议文件，用英文写（LLM 的母语是英语，指令遵从更稳）；给你看的文档双语。

## 你日常只需要看四个地方

| 想知道 | 看 |
|---|---|
| 现在做到哪、下一步是什么 | `AIWORK/Status/` 里带 `_current` 的窗口 |
| 做过哪些实验、结果如何 | 双击 `AIWORK/Status/inter.html`（一页总览 + 统计表 + 你自己的 note） |
| 你确认过哪些节点 | `AIWORK/Status/status_global.md` 和 `REVIEW/` 下的快照 |
| 最终留下的高净值内容 | `HUMAN/` |

## 你需要做的事（只有四件）

1. **开新方向**：AI 想开新的顶层实验方向（`e###`）时需要你给序号点头；你没提出新方向，AI 不会自己开。
2. **确认节点**：AI 汇报结果后，你说"这个节点我确认"，AI 才会记入 `status_global` 并把必要的代码与结果快照进 REVIEW。
3. **审核与晋升**：你在 REVIEW 里审核（可让 AI 一起看），审核通过、你说"放进 HUMAN"，AI 才原样拷入 HUMAN。HUMAN 里是你最终留下的最高净值内容，不是随手笔记。
4. **初审 Prototype**：AI 拷入 baseline 原始仓库前，你确认来源和版本。

除这四件外，AI 自主。

## 界线

- REVIEW 里的是审核材料：快照附 sha256 清单，拷入后不动；想验证有没有被动过，重算哈希对清单。
- HUMAN 里的东西只经你一句话进入，之后 AI 永不修改、不删除、不"整理"；AI 可应你要求检查完整性，结论只在对话里说。
- AI 的自述不是证据，证据是快照的哈希清单和 git 历史。
- 复用数据在 `AIWORK/Experiment/data/`，冻结协议与环境记录在 `AIWORK/Experiment/environ/`，实验一律引用，不各拷一份。

## 给新会话开 agent 时

在项目目录里开任意 agent，说"读 AGENTS.md 后开始"即可。它读窗口接上进度，不需要任何导入操作。

## inter 页的几件事

- 双击 `AIWORK/Status/inter.html` 打开；下拉菜单选方向或实验，总览页点行进入。
- 笔记存在本机浏览器里，换机器不跟随。要带走：打开浏览器开发者工具控制台，跑 `copy(localStorage)` 不行的话逐条复制，或直接让 agent 从页面读。日常最简单的做法——重要的结论直接写进 `HUMAN/`，inter 笔记当草稿。
- 有实验在跑时页面顶部出现 live 标记并自动刷新，进度卡由 watcher 写入；这是瞬态信息，正式结果走 README / REVIEW。
