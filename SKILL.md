---
name: gcp-ce-whitepaper-compiler
description: >-
  将包含 Mermaid 系统架构图、复杂的 Markdown 表格与公文样式的技术方案白皮书，直接调用本地 Google Chrome 内核极速编译为企业级的高精排版 PDF 文档。内置 GCP Customer Engineer (CE) 官方品牌美学（Hiragino Sans GB 优先中文字体栈、18pt 磅礴气场演示/演讲级公文字号、零额外间距排版、公文黄金边距、多行代码模块化排版、内联 Base64 图表防 CORS 拦截）。当用户需要输出技术架构白皮书、解决方案指南、POC 总结报告或将 Markdown 转为高质量 PDF 时触发本技能。
---

# GCP CE Whitepaper Compiler

## Overview
本技能是一个完全独立的本地命令行工具套件，专门为 Google Cloud Customer Engineer (CE) 及架构师群体量身打造。它能一键将编写好的 Markdown 技术方案（包含 Mermaid 架构图、数据表格、提示框 Alert 等）转化为排版严谨、符合 GCP 品牌美学的高规格 PDF 文档。

核心排版与技术特性（V10 黄金公文/演讲演示标准）：
- **GCP 品牌与视网膜中文字体栈**：优先选用原生视网膜级中文字体 `Hiragino Sans GB` (冬青黑体) 与 `PingFang SC` (苹方黑体)，并严格搭配 `letter-spacing: normal !important` 零额外字间距排版，彻底解决中英文混排时的间隙散乱与无头浏览器丢字空白问题。
- **18pt 磅礴气场演示/演讲级字号与节奏**：正文采用 `18pt` (行高 1.8) 宏伟演示规格，一至三级标题分别锁定为 `34pt` / `24pt` / `20pt`，代码块为 `15pt`，表格与内联代码为 `15.5pt`。保证在 A4 High-Res 静态文档及高清大屏演示中字字如巨擘、威慑力拉满、极度醒目易读。
- **零头尾干净输出 (`--no-pdf-header-footer`)**：驱动 Chrome 无头内核时强制追加 `--no-pdf-header-footer` 与 `--print-to-pdf-no-header` 双重消隐参数，自动斩除系统注入的日期、页码与本地 HTML 文件路径 URL。
- **多行复杂命令行“步骤-代码对 (Modular Step-Code Pairs)”排版规范**：严格禁止将多步长命令塞入单一庞大 `<pre>` 黑框。要求分切为结构清晰的独立步骤（如 `**步骤 1：...**`）配套专属小巧代码框，并借助 `\` 折行缩进对齐，彻底消除中折乱码与分页孤白。
- **公文级黄金边距**：严格锁定上下 25mm、左右 20mm 的标准化留白。
- **Retina 3x 矢量/高清图表内联**：调用 Mermaid CLI 把图表超采样渲染为 PNG，并自动转化为 `data:image/png;base64` 内联字符串，彻底绕过 Chrome 本地文件跨域（CORS）沙盒安全拦截。

## Dependencies
- **系统工具依赖**：
  - `python3` (标准库驱动，无第三方 pip 依赖)
  - `node` / `npx` (用于自动拉取并执行 `@mermaid-js/mermaid-cli` 与 `marked`)
  - `Google Chrome` / `Chromium` 浏览器内核（默认探测 macOS 标准应用程序目录，或通过 `CHROME_PATH` 环境变量指定）

## Quick Start
在任何含有 `.md` 文件的项目目录下，通过终端调用本技能自带的脚本：

```bash
# 将架构设计文档编译为同名的 PDF 文件
python3 /Users/lileon/.gemini/skills/gcp-ce-whitepaper-compiler/scripts/compile_whitepaper.py architecture_plan.md

# 指定输出的 PDF 物理路径
python3 /Users/lileon/.gemini/skills/gcp-ce-whitepaper-compiler/scripts/compile_whitepaper.py architecture_plan.md -o ./dist/GCP_Solution_Whitepaper.pdf
```

## Markdown 编撰规范与最佳实践 (CE Best Practices)

为保证经由本套件编译出的 PDF 能够达到最高企业级公文排版水准，编撰 Markdown 源码时务必遵循以下准则：

1. **复杂 Shell/参数操作必须模块化处理 (Modular Code Blocks)**：
   - 如果遇到包含多个逻辑步骤（如 `gcloud` 导出 -> `jq` 清洗 -> `gcloud` 创建 -> `gcloud` 解绑/绑定）的配置指南，切勿全部堆砌在同一个 ` ```bash ` 长代码块中。
   - 应将其切分为独立的步骤标题（例如：`**步骤 1：导出现有权限清单**`），正文简述逻辑后，紧跟该步专属的 1~3 行代码框。
   - 所有超过 70 字符的长命令或 JSON 过滤表达式，必须按语义拆行并追加 `\` 连接符缩进对齐，防止 PDF 输出时发生中折。

2. **架构图注与防跨页保护 (`page-break-inside`)**：
   - 两段正文或表格间插入 Mermaid 架构图时，应控制图表横向跨度（样式库默认限制最大宽度 `75%~78%`）。
   - 图表正下方应搭配规范的图注说明，例如 `<div class="caption">图 1：多云异构环境下的凭据隔离与权限逃逸路径 (Ref: b/534639686)</div>`。

3. **表格内容与换行限制**：
   - 表格单元格默认启用 `word-break: normal; overflow-wrap: break-word;`。对于 API 权限名称（如 `serviceusage.services.enable`），会自动在 `.` 处折行而不会切断英文单词。

## Utility Scripts
### compile_whitepaper.py
核心编译驱动工具，集成图表解析、Base64 编解码、CSS 样式组装与 Chrome 无头内核调起。

#### 参数详解
- `input_md` (必选 positional): 输入的 Markdown 文件路径。
- `-o, --output` (可选): 指定输出 PDF 的完整路径。未提供时默认在工作目录下生成与源文件同名的 `.pdf`。
- `--chrome-path` (可选): 指定浏览器可执行文件的绝对路径。例如在 Linux 环境可指定 `--chrome-path /usr/bin/chromium`。
- `--keep-temp` (可选): 调试模式。指定后不会清理自动生成的临时文件夹（内含中间 Markdown、Base64 图表与合并后的单文件 HTML），方便排查排版细节。

## Common Mistakes
1. **中英文字体字间距拉扯或留白**：切勿在 `whitepaper.css` 里为 `body` 或 `p` 声明正的 `letter-spacing`（如 `0.015em`）配合 `text-align: justify`，否则 `PingFang SC` 与 `Hiragino Sans GB` 中文字字之间的方正密合度会被强行拉宽撕裂。必须保持 `letter-spacing: normal !important` 与左对齐。
2. **忽略 `--no-pdf-header-footer` 导致页眉页尾超链接污染**：调用 Chrome `--headless --print-to-pdf` 时如果只传 `--print-to-pdf-no-header`，部分高版本 Chromium 内核依然会打印日期和 HTML 本地路径。必须同时传递 `--no-pdf-header-footer`。
3. **在 Mermaid 图表子图中书写特殊未包裹字符**：如果在 Mermaid 的 `subgraph ID [标题(含括号)]` 中未使用双引号包裹或嵌入了未转义的 `<br>`，会导致图表编译失败。请务必使用 `subgraph ID ["标题 (含括号)"]` 的规范语法。
