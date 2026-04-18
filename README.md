# Chauny X Skill

一个面向个人研究工作流的 X 监控 skill，用来低成本追踪固定博主的最新帖子。

## 这是什么

`chaunyx-skill` 是一个浏览器驱动、人工节奏的 X 作者监控工具。

它的设计目标很明确：

- ✅ 不依赖官方 X API
- ✅ 适合只盯少量固定作者
- ✅ 支持去重、落盘、生成 Markdown 报告
- ✅ 适合“人工浏览器采集 + 本地整理”的研究流程
- ✅ 支持生成采集辅助包

## 能干什么

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 固定作者 watchlist | ✅ | 维护一组固定的 `username` |
| 人工采集后批量导入 | ✅ | 将浏览器里看到的帖子整理成 JSON 再导入 |
| 去重 | ✅ | 按 `post_id` 去重 |
| JSONL 事件落盘 | ✅ | 方便后续做分析或二次处理 |
| Markdown 报告生成 | ✅ | 每次导入后自动更新报告 |
| 采集辅助包 | ✅ | 自动生成作者 URL、批次模板、操作清单 |
| 成本友好 | ✅ | 不依赖官方 X API 计费 |
| 广域热门发现 | ❌ | 这不是热点爬虫 |
| 自动发帖/互动 | ❌ | 永远保持只读 |
| 大规模后台常驻抓取 | ❌ | 不面向高频无人值守 |

## 适合谁

- ✅ 只关注少量作者，比如 3 到 20 个
- ✅ 希望低成本持续观察某些博主
- ✅ 可以接受“人工打开主页 + 半自动整理”
- ✅ 更看重稳定的个人研究流程
- ✅ 想把内容沉淀成自己的 Markdown / JSON 数据资产

## 工作流

| 步骤 | 你做什么 | skill 做什么 |
| --- | --- | --- |
| 1. 初始化 | 生成配置文件 | 创建默认 watchlist 配置 |
| 2. 检查配置 | 看作者列表是否正确 | 校验路径、作者数量、输出目录 |
| 3. 生成辅助包 | 一键生成采集包 | 生成 URL 列表、批次模板和清单 |
| 4. 浏览器采集 | 打开作者主页，复制最近帖子 | 不直接抓浏览器，只接收标准 JSON |
| 5. 导入批次 | 运行 `ingest` | 去重、落 JSONL、更新 Markdown 报告 |

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| `SKILL.md` | Skill 触发说明与执行指南 |
| `README.md` | 仓库级说明文档 |
| `agents/openai.yaml` | Skill UI 元数据 |
| `scripts/x_manual_monitor.py` | 主执行脚本 |
| `references/workflow.md` | 工作流解释和操作建议 |

## 命令

```powershell
python scripts/x_manual_monitor.py init --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py check --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py make-batch-template .\batch.json --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py make-capture-pack .\capture-pack --config .\x-manual-monitor.json
python scripts/x_manual_monitor.py ingest .\batch.json --config .\x-manual-monitor.json
```

## 输入格式

每条帖子都需要这些字段：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `post_id` | ✅ | X 帖子 ID |
| `author` | ✅ | 用户名 |
| `url` | ✅ | 帖子链接 |
| `published_at` | ✅ | 发布时间 |
| `text` | ✅ | 帖子正文 |
| `label` | 可选 | 展示名 |

## 输出结果

| 输出 | 位置 | 用途 |
| --- | --- | --- |
| 事件流 | `events/events.jsonl` | 保存结构化帖子数据 |
| 状态文件 | `state/state.json` | 记录已处理 `post_id` |
| Markdown 报告 | `reports/latest-report.md` | 快速阅读最新导入内容 |
| 采集辅助包 | `capture-pack/` | 存放作者 URL、模板、清单 |

## 使用建议

- ✅ 只监控最重要的作者
- ✅ 每天 1 到 2 次人工采集
- ✅ 每次只看最近 3 到 10 条帖子
- ✅ 统一存成 JSON 再导入
- ✅ 优先使用 `make-capture-pack`

## 当前限制

- ❌ 不直接控制浏览器
- ❌ 不自动提取帖子
- ❌ 不做热门发现

## 仓库定位

这不是一个“超级爬虫框架”，而是一个：

> 小而稳、低成本、面向个人研究的 X 作者监控 skill。
