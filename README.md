# Chauny X Skill

一个面向个人研究工作流的 X 监控 skill，用来低成本追踪固定博主的最新帖子。

## 这是什么

`chaunyx-skill` 现在支持两种模式：

- ✅ 半自动：生成模板，你自己看页面后导入
- ✅ 全自动：自动打开固定作者主页、抓最近帖子、自动 ingest

它的核心目标仍然很明确：

- ✅ 不依赖官方 X API
- ✅ 适合只盯少量固定作者
- ✅ 支持去重、落盘、生成 Markdown 报告
- ✅ 兼容“人工整理”和“浏览器自动采集”两种工作流

## 能干什么

| 能力 | 状态 | 说明 |
| --- | --- | --- |
| 固定作者 watchlist | ✅ | 维护一组固定的 `username` |
| 人工采集后批量导入 | ✅ | 将浏览器里看到的帖子整理成 JSON 再导入 |
| 自动打开作者主页并采集 | ✅ | 使用 Playwright 自动打开并抓取固定作者最近帖子 |
| 去重 | ✅ | 按 `post_id` 去重 |
| JSONL 事件落盘 | ✅ | 方便后续做分析或二次处理 |
| Markdown 报告生成 | ✅ | 每次导入后自动更新报告 |
| 采集辅助包 | ✅ | 自动生成作者 URL、批次模板、操作清单 |
| 成本友好 | ✅ | 不依赖官方 X API 计费 |
| 广域热门发现 | ❌ | 这不是热点爬虫 |
| 自动发帖/互动 | ❌ | 永远保持只读 |

## 适合谁

- ✅ 只关注少量作者，比如 3 到 20 个
- ✅ 希望低成本持续观察某些博主
- ✅ 想先半自动，再升级成自动浏览器采集
- ✅ 更看重稳定的个人研究流程

## 工作流

| 步骤 | 你做什么 | skill 做什么 |
| --- | --- | --- |
| 1. 初始化 | 生成配置文件 | 创建默认 watchlist 配置 |
| 2. 检查配置 | 看作者列表是否正确 | 校验路径、作者数量、输出目录 |
| 3. 生成辅助包 | 一键生成采集包 | 生成 URL 列表、批次模板和清单 |
| 4. 采集帖子 | 手动复制，或运行 `auto-collect` | 自动打开作者主页并抓帖子 |
| 5. 导入批次 | 手动 `ingest` 或由 `auto-collect` 自动执行 | 去重、落 JSONL、更新 Markdown 报告 |

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
python scripts/x_manual_monitor.py auto-collect --config .\x-manual-monitor.json --browser chromium
python scripts/x_manual_monitor.py ingest .\batch.json --config .\x-manual-monitor.json
```

## 输入与输出

### 输入

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `post_id` | ✅ | X 帖子 ID |
| `author` | ✅ | 用户名 |
| `url` | ✅ | 帖子链接 |
| `published_at` | ✅ | 发布时间 |
| `text` | ✅ | 帖子正文 |
| `label` | 可选 | 展示名 |

### 输出

| 输出 | 位置 | 用途 |
| --- | --- | --- |
| 事件流 | `events/events.jsonl` | 保存结构化帖子数据 |
| 状态文件 | `state/state.json` | 记录已处理 `post_id` |
| Markdown 报告 | `reports/latest-report.md` | 快速阅读最新导入内容 |
| 采集辅助包 | `capture-pack/` | 存放作者 URL、模板、清单 |
| 自动批次 | `events/auto-batch.json` | 自动采集生成的临时批次 |

## 使用建议

- ✅ 只监控最重要的作者
- ✅ 每天 1 到 2 次自动或半自动采集
- ✅ 每次只抓最近 3 到 10 条帖子
- ✅ 先小名单验证，再扩作者数
- ✅ 页面能匿名看就不强依赖登录

## 当前限制

- ❌ 不做热门发现
- ❌ 页面结构改版时需要维护选择器
- ❌ 某些环境下匿名访问 X 可能受限

## 仓库定位

这不是一个“超级爬虫框架”，而是一个：

> 小而稳、低成本、面向固定作者 watchlist 的 X 监控 skill，并且已经从半自动升级到了浏览器自动采集版本。
