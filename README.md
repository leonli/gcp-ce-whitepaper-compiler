# GCP CE Whitepaper Compiler

A robust, local command-line toolkit tailored for Google Cloud Customer Engineers (CEs) and Architects. It transforms Markdown technical design documents (featuring Mermaid architecture diagrams, tables, and alerts) into highly polished, enterprise-grade PDF whitepapers that adhere to the official GCP brand aesthetics.

## Key Features

- **GCP Brand Typography**: Utilizes `Google Sans` and `Roboto` for English/numeric characters, with a seamless fallback to `Arial Unicode MS` (and standard Unicode) to prevent missing Chinese glyphs in headless Chrome exports.
- **Enterprise-Grade Layout**: Enforces strict margins (25mm top/bottom, 20mm left/right) and justified paragraphs for a professional "whitepaper" look.
- **High-Resolution Inline Diagrams**: Uses the Mermaid CLI to render charts into high-res PNGs. These are then converted to Base64 data URIs and embedded directly into the HTML to bypass Chrome's local CORS restrictions.
- **Smart Code Wrapping**: Applies `pre-wrap` to `<pre>` and `<code>` blocks, ensuring long SQL queries or Python scripts are never truncated off-page.
- **Fail Loudly**: Built-in strict error handling. If the browser engine is missing or a Mermaid diagram fails to render, it immediately exits (Code 1) to prevent generating incomplete documents.

## Prerequisites

- `python3` (Standard library only; no `pip` dependencies required)
- `node` / `npx` (Required for `@mermaid-js/mermaid-cli` and `marked` execution)
- **Google Chrome** or **Chromium** (Automatically detected on macOS; for other platforms, set the `CHROME_PATH` environment variable)

## Usage

You can use the script on any `.md` file in your workspace.

```bash
# Compile a markdown document into a PDF in the same directory
python3 scripts/compile_whitepaper.py architecture_plan.md

# Specify a custom output path
python3 scripts/compile_whitepaper.py architecture_plan.md -o ./dist/GCP_Solution_Whitepaper.pdf
```

## CLI Arguments

- `input_md` (Required): The path to your input Markdown file.
- `-o, --output` (Optional): The full output path for the PDF.
- `--chrome-path` (Optional): Explicit path to your Chrome/Chromium binary.
- `--keep-temp` (Optional): Debugging mode. Retains the temporary folder containing intermediate HTML and Base64 images.

## Common Issues & Troubleshooting

- **"npx executable not found"** or **"Could not locate Google Chrome"**: Verify your system's PATH or explicitly set `export CHROME_PATH=/your/chrome/path`.
- **Mermaid Compilation Errors**: Ensure labels with special characters (like parentheses) within a `subgraph` are quoted. E.g., use `subgraph ID ["Label (extra)"]` instead of `subgraph ID [Label (extra)]`.
- **Missing Chinese Text in PDF**: Do not map Chinese fonts to Apple proprietary fonts like `-apple-system` or `-Semibold`, as the macOS sandbox blocks their embedding during the PDF print phase. Always stick to generic `sans-serif` or explicit names like `Arial Unicode MS`.

## License
Apache-2.0
