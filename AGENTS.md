# labkit — meta 骨架仓库

这个仓库不是项目，是**生成项目**的骨架。这里没有实验，不要在这里干活。

## 用户给一个初始目标时

把 `seed/` 整份拷到目标路径（含 `.gitignore`），然后：

- 在 `AGENTS.md`、`README.md`、`README_zh.md`、`README_en.md`、`AIWORK/Status/inter.html`、`AIWORK/Status/status_global.md`、`AIWORK/Status/agent_status_current.md` 里替换：`{{NAME}}` → 项目名，`{{GOAL}}` → 用户的目标原句，`{{DATE}}` → 今天日期，`{{DATETIME}}` → 当前时间。
- 把 `agent_status_current.md` 改名为 `agent_status_<yyyyMMddTHHmm>_current.md`。
- `git init`，首次提交。git 身份没配就告诉用户设一次，文件照常生成。
- 自查一遍：除了 `AIWORK/Experiment/agent_template.md`，别处不能有 `{{` 残留。

做完把生成路径和下一步告诉用户。不要写任何脚本，这几步手工做完就是几分钟的事。

## 改这套骨架时

直接改 `seed/`，它就是未来项目的样子，改完即所见。规则要改就改 `seed/AGENTS.md`，别在别处另立说法。新文件除非有明确的规则约束它，否则不加。这里永远不写脚本。
