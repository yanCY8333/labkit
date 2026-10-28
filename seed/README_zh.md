# {{NAME}}

{{GOAL}}

规则文件是 `AGENTS.md`（AI 的，英文）。不必阅读，如需阅读可以优先 Never violate 一节。

## 结构

```text
AIWORK/      AI 的工作区，随便写
  Prototype/   baseline 原始仓库，进来就不改
  Experiment/  实验；方向由你确认，方向内 AI 自行分支
    data/      高度复用的数据，按类型细分，引用不拷贝
    environ/   环境/硬件记录、冻结协议、共享默认配置
  Status/      交接窗口 + 全局节点 + inter 总览页 + 归档
REVIEW/      你确认的节点，AI 放快照进来，你在此审核
HUMAN/       审核后晋升的高净值内容，你说"放进 HUMAN"才进入
```

命名：区全大写，区内层首字母大写，再往下一律小写。AI 的协议文件（AGENTS.md、agent_ 前缀）用英文写。

## 结构介绍

当前任务在 `AIWORK/Status/` 里带 `_current` 的窗口，包括以往实验、结果等可以快捷查找查看，在`AIWORK/Status/inter.html`。确认过的 milestone 节点：`status_global.md` + `REVIEW/` 下的快照

真正经由人工审核后的的内容：`HUMAN/`

## 使用方法

1. 开新方向：AI 想开顶层方向（e###）时需要人类确认；
2. 确认节点：人类提出“从普通实验定格为 milestone”，AI 才记入 status_global 并把代码与结果快照进 REVIEW，这里不指的是任意实验，而是 milestone 级别的；
3. 审核晋升：人类在 REVIEW 里审（可让 AI 一起看），说"放进 HUMAN"才拷入；
4. 初审 Prototype：AI 拷入 baseline 前，人类确认来源和版本

其余 AI 自主。

## 界线

- REVIEW 拷入后不改，附 sha256 清单；被动过就重算哈希对清单
- HUMAN 里的东西 AI 永不修改
- AI 的自述不是证据，证据是哈希清单和 git 历史

## 开新会话

在项目目录里开任意 agent，说"读 AGENTS.md 后开始"。

## inter 页

- 笔记存在本机浏览器，换机器不跟随；重要的结论直接写 HUMAN/
- 有实验在跑时页面自动刷新，进度由 watcher 写入；正式结果走 README / REVIEW
