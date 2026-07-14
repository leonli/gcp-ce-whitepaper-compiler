---
name: gcp-ce-whitepaper-compiler
description: >-
  将包含 Mermaid 系统架构图、复杂的 Markdown 表格与公文样式的技术方案白皮书，直接调用本地 Google Chrome 内核极速编译为企业级的高精排版 PDF 文档。内置 GCP Customer Engineer (CE) 官方品牌美学（Google Sans + Roboto + Unicode 中文字体栈、25mm/20mm 黄金边距、代码自动换行防截断、内联 Base64 图表防 CORS 拦截）。当用户需要输出技术架构白皮书、解决方案指南、POC 总结报告或将 Markdown 转为高质量 PDF 时触发本技能。
---

# GCP CE Whitepaper Compiler

## Overview
本技能是一个完全独立的本地命令行工具套件，专门为 Google Cloud Customer Engineer (CE) 及架构师群体量身打造。它能一键将编写好的 Markdown 技术方案（包含 Mermaid 架构图、数据表格、提示框 Alert 等）转化为排版严谨、符合 GCP 品牌美学的高规格 PDF 文档。

核心排版与技术特性：
- **GCP 品牌美学字体栈**：英文与数字优先匹配 `Google Sans` 与 `Roboto`，中文无缝回退至 `Arial Unicode MS` 及标准 Unicode 字体，完美解决无头浏览器 PDF 导出中文字体丢字与空缺问题。
- **公文级黄金边距**：严格锁定上下 25mm、左右 20mm 的标准化留白，段落两端对齐（Justify）。
- **Retina 3x 矢量/高清图表内联**：调用 Mermaid CLI 把图表超采样渲染为 PNG，并自动转化为 `data:image/png;base64` 内联字符串，彻底绕过 Chrome 本地文件跨域（CORS）沙盒安全拦截。
- **智能折行与溢出防护**：对 `<pre>` 和 `<code>` 块加持强制自动断行（`pre-wrap`），防止长行 SQL 或 Python 代码在静态 PDF 中截断。
- **零容忍报错中断 (Fail Loudly)**：发现内核缺失或图表语法渲染失败时立刻打印原始堆栈并以 Exit Code 1 退出，绝不输出残缺半成品。

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

## Utility Scripts (if CLI-based)
### compile_whitepaper.py
核心编译驱动工具，集成图表解析、Base64 编解码、CSS 样式组装与 Chrome 无头内核调起。

#### 参数详解
- `input_md` (必选 positional): 输入的 Markdown 文件路径。
- `-o, --output` (可选): 指定输出 PDF 的完整路径。未提供时默认在工作目录下生成与源文件同名的 `.pdf`。
- `--chrome-path` (可选): 指定浏览器可执行文件的绝对路径。例如在 Linux 环境可指定 `--chrome-path /usr/bin/chromium`。
- `--keep-temp` (可选): 调试模式。指定后不会清理自动生成的临时文件夹（内含中间 Markdown、Base64 图表与合并后的单文件 HTML），方便排查排版细节。

#### 使用示例
```bash
# 标准调用
python3 /Users/lileon/.gemini/skills/gcp-ce-whitepaper-compiler/scripts/compile_whitepaper.py design_doc.md

# 自定义浏览器路径并保留调试文件
python3 /Users/lileon/.gemini/skills/gcp-ce-whitepaper-compiler/scripts/compile_whitepaper.py design_doc.md --chrome-path "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge" --keep-temp
```

## Rate Limiting (if applicable)
本套件不调用任何远程有速率限制的 HTTP API，所有运算、图形渲染与 PDF 构建完全在本机离线运行，无速率限制。

## Common Mistakes
1. **环境环境变量或路径缺失**：如提示 `npx executable not found` 或 `Could not locate Google Chrome`，请检查当前 Shell 环境的 PATH 或通过 `export CHROME_PATH=/your/path` 声明内核位置。
2. **在 Mermaid 图表子图中书写特殊未包裹字符**：如果在 Mermaid 的 `subgraph ID [标题(含括号)]` 中未使用双引号包裹或嵌入了未转义的 `<br>`，会导致图表编译失败。请务必使用 `subgraph ID ["标题 (含括号)"]` 的规范语法。
3. **在 CSS 中滥用苹果私有系统字体**：如果自定义或修改样式表时为中文字体声明了 `-apple-system` 或特定的 `-Semibold` 粗体映射，会导致 macOS 底层沙盒阻止 TrueType 字体子集嵌入，造成输出 PDF 时中文空白。请务必使用通用 `sans-serif` 与原生的单体字库库名称（如 `Arial Unicode MS`, `PingFang SC`）。
