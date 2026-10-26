# 采用指南

## 五分钟起步

```powershell
# 1. 复制模板
$dst = "D:\spaceEXP\<新项目>"
New-Item -ItemType Directory -Force "$dst\NOTES","$dst\archive" | Out-Null
Copy-Item D:\spaceEXP\labkit\templates\*.md $dst\
Copy-Item D:\spaceEXP\labkit\templates\NOTES\*.md "$dst\NOTES\"
Copy-Item D:\spaceEXP\labkit\templates\archive\*.md "$dst\archive\"

# 2. 科研项目再加 CLAIMS
New-Item -ItemType Directory -Force "$dst\CLAIMS" | Out-Null
Copy-Item D:\spaceEXP\labkit\templates\CLAIMS\*.md "$dst\CLAIMS\"

# 3. 填 CHARTER，然后在 STATE 写第一张交接卡
```

### 可选：注册成 agent 技能

`SKILL.md` 是给 agent 的入口说明。若希望客户端自动发现它：

```powershell
New-Item -ItemType Directory -Force "$dst\.agents\skills\labkit" | Out-Null
Copy-Item D:\spaceEXP\labkit\SKILL.md "$dst\.agents\skills\labkit\"
```

OpenCode 会扫描 `.agents/skills`；其他客户端可用各自的 skills 目录或直接指向 `AGENTS.md`。
不注册也不影响使用——`AGENTS.md` 已经包含了协议要点。

```powershell
git init
git add .
git commit -m "chore: 采用 labkit v0.1 结构"
```

填 CHARTER 这一步不要跳过：空模板没有价值，一份填好的 CHARTER 比十个规范文件重要。

## 三档起步

不要一上来就全用。按项目实际需要选：

| 档位 | 文件 | 适用 |
|---|---|---|
| **最小** | CHARTER + STATE | 单人、两周内结束、不需要交接 |
| **标准** | 上面 + LOG + DECISIONS + NOTES/RUNS | 会被别人接手，或换 agent |
| **完整** | 上面 + NOTES 全部 + CLAIMS | 科研、需要可追溯的结论 |

先按最小档跑一周。如果一周内没打开过 STATE，说明这个项目不需要 labkit，删掉即可；
如果打开过，说明该升档。

## 迁移已有项目

以 `D:\spaceEXP\superINR\research\` 为例，逐个映射：

| 已有文件 | 迁移到 | 说明 |
|---|---|---|
| `research/README.md` | `AGENTS.md` | 使用协议 → 入口协议 |
| `research/BASE.md` | `NOTES/BASE.md` | 几乎原样；把散文结论改成一行的 ✅/◐/❌ + 来源 |
| `research/THINKING.md` | `NOTES/THINKING.md` | 几乎原样；补上缺"会推翻它"的条目 |
| `research/DESIGN.md` | `NOTES/DESIGN.md` | 把"判定规则"提到执行之前写的那几条固定下来 |
| `research/RUNS.md` | `NOTES/RUNS.md` | 保留；把内嵌数字改为指向 `results.csv` |
| — | `CLAIMS/` | 新增。把 BASE 里最关键的 3–5 条改写成带判据的断言 |
| `research/logbook/` | 删除 | 那份 CLI 是"判定机制"思路，与本骨架冲突 |

迁移时**不要**重写内容。只做三件事：换位置、加状态标记、把长段落拆成一行一条。

## 迁移检查表

- [ ] `CHARTER.md` 只有一个问题，且能被证伪或明确完成
- [ ] `STATE.md` 的"下一步"陌生人能直接执行
- [ ] `NOTES/BASE.md` 每条事实都有 `[[Cxxx]]` 或 `out=` 来源
- [ ] `NOTES/BASE.md` 保留了所有 ❌ 条目
- [ ] `NOTES/THINKING.md` 每条都有"什么会推翻它"
- [ ] `NOTES/RUNS.md` 的 `out=` 路径全部真实存在
- [ ] `CLAIMS/` 每条断言的 `created` 早于或等于其证据产物的日期
- [ ] `DECISIONS.md` 每条都写了代价
- [ ] 没有任何文件超过 `references/conventions.md` 里的上限

最后一条最重要：**上限是这套结构唯一真正起作用的部分**。

## 与现有工具的关系

labkit 不替代任何东西，只规定位置：

| 你已有的 | labkit 怎么处理 |
|---|---|
| `batch.json` / 队列状态 | 原样保留，`RUNS.md` 里引用其路径 |
| `results.csv` | 原样保留，是证据层 |
| 训练脚本、配置 | 原样保留；提交它们，不提交产物 |
| `AGENTS.md` | 升级为入口协议（本项目已有则合并，不要新建第二份） |
| `CLAUDE.md` | 若已存在，改成指向 `AGENTS.md` 的一行 |
| 已有 README 里的进度记录 | 移入 `STATE.md`，README 只留"这是什么" |

## 多人 / 多 agent 并行

labkit 用 `STATE.md` 的 `owner` / `lease_until` 做**软锁**：不阻止操作，只告知。

实践建议：

1. 一个 agent 只改自己新建的文件。
2. 共享文件（`BASE.md`、`DECISIONS.md`）只追加或整段替换，不要同时编辑同一段。
3. 超过 90 分钟没有更新的 `owner` 视为失效，下一个 agent 直接接管并在 LOG 记一行。
4. 真冲突时以 `LOG.md` 的写入顺序为准——这也是为什么要"动作之后立刻记一行"。

## 不适用的情况

- 一次性脚本、探索两小时的实验：直接写 README，别用。
- 已有成熟项目管理（issue tracker + 完整 CI）：labkit 只补 `CHARTER` 和 `STATE`。
- 需要强合规审计（GxP、金融）：labkit 是轻量约定，不满足法规级要求。
