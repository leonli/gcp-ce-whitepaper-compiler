#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""CLI script for compiling Markdown with Mermaid diagrams to publication-grade PDFs."""

import argparse
import base64
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def find_chrome(custom_path=None):
  """Locates Google Chrome or Chromium executable with strict fail-loudly handling."""
  candidates = []
  if custom_path:
    candidates.append(custom_path)
  elif "CHROME_PATH" in os.environ:
    candidates.append(os.environ["CHROME_PATH"])
  else:
    # Standard macOS paths
    candidates.extend([
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
    ])

  for path in candidates:
    if os.path.isfile(path) and os.access(path, os.X_OK):
      return path

  print(
      "ERROR: Could not locate Google Chrome or Chromium executable.",
      file=sys.stderr,
  )
  print(
      "Please install Google Chrome or specify its exact path using"
      " --chrome-path or the CHROME_PATH environment variable.",
      file=sys.stderr,
  )
  sys.exit(1)


def find_npx():
  """Locates npx executable."""
  npx_path = shutil.which("npx")
  if not npx_path:
    # Check standard nvm / node paths on macOS
    for p in [
        "/usr/local/bin/npx",
        "/opt/homebrew/bin/npx",
        os.path.expanduser("~/.nvm/versions/node/$(ls -t ~/.nvm/versions/node 2>/dev/null | head -n 1)/bin/npx"),
    ]:
      if os.path.exists(p):
        return p
    print("ERROR: npx executable not found in PATH.", file=sys.stderr)
    print(
        "Please ensure Node.js and NPM/npx are installed and accessible.",
        file=sys.stderr,
    )
    sys.exit(1)
  return npx_path


def main():
  parser = argparse.ArgumentParser(
      description=(
          "Compile Markdown with Mermaid diagrams into GCP CE brand PDF"
          " whitepapers."
      )
  )
  parser.add_argument(
      "input_md", help="Path to the input Markdown source file (.md)"
  )
  parser.add_argument(
      "-o",
      "--output",
      help=(
          "Path for the output PDF file (defaults to same name as input in"
          " current directory)"
      ),
  )
  parser.add_argument(
      "--chrome-path",
      help="Custom path to Google Chrome / Chromium executable",
  )
  parser.add_argument(
      "--keep-temp",
      action="store_true",
      help="Retain temporary build files (HTML and images) for debugging",
  )

  args = parser.parse_args()

  input_path = pathlib.Path(args.input_md).resolve()
  if not input_path.exists() or not input_path.is_file():
    print(
        f"ERROR: Input file does not exist or is not a file: {input_path}",
        file=sys.stderr,
    )
    sys.exit(1)

  if args.output:
    output_path = pathlib.Path(args.output).resolve()
  else:
    output_path = pathlib.Path.cwd() / f"{input_path.stem}.pdf"

  chrome_exec = find_chrome(args.chrome_path)
  npx_exec = find_npx()

  # Find built-in whitepaper.css relative to this script
  script_dir = pathlib.Path(__file__).resolve().parent
  css_path = script_dir.parent / "resources" / "whitepaper.css"
  if not css_path.exists():
    print(f"ERROR: Built-in stylesheet not found at: {css_path}", file=sys.stderr)
    sys.exit(1)

  with open(css_path, "r", encoding="utf-8") as f:
    css_content = f.read()

  # Create workspace
  temp_dir = pathlib.Path(tempfile.mkdtemp(prefix="gcp_ce_whitepaper_"))
  try:
    print(f"[{input_path.name}] Step 1/4: Extracting and compiling Mermaid diagrams...")
    temp_md = temp_dir / "stage1.md"
    
    mmdc_cmd = [
        npx_exec, "-y", "@mermaid-js/mermaid-cli@latest",
        "-i", str(input_path),
        "-o", str(temp_md),
        "-e", "png",
        "-s", "3",
        "-b", "white"
    ]
    
    res = subprocess.run(mmdc_cmd, cwd=str(temp_dir), capture_output=True, text=True)
    if res.returncode != 0:
      print("ERROR: Mermaid diagram compilation failed!", file=sys.stderr)
      print(res.stderr or res.stdout, file=sys.stderr)
      sys.exit(1)

    # Inline all generated PNG images as Base64 Data URIs to bypass Chrome file:// CORS policy
    print(f"[{input_path.name}] Step 2/4: Inlining images and converting Markdown to HTML...")
    if not temp_md.exists():
      temp_md = input_path

    with open(temp_md, "r", encoding="utf-8") as f:
      md_text = f.read()

    for img_file in temp_dir.glob("*.png"):
      with open(img_file, "rb") as f_img:
        b64_data = base64.b64encode(f_img.read()).decode("utf-8")
      data_uri = f"data:image/png;base64,{b64_data}"
      md_text = md_text.replace(f"./{img_file.name}", data_uri)
      md_text = md_text.replace(img_file.name, data_uri)

    temp_md_inlined = temp_dir / "stage2_inlined.md"
    with open(temp_md_inlined, "w", encoding="utf-8") as f:
      f.write(md_text)

    # Convert to HTML via marked
    temp_body_html = temp_dir / "body.html"
    marked_cmd = [
        npx_exec, "-y", "marked@latest",
        "-i", str(temp_md_inlined),
        "-o", str(temp_body_html)
    ]
    res_marked = subprocess.run(marked_cmd, cwd=str(temp_dir), capture_output=True, text=True)
    if res_marked.returncode != 0:
      print("ERROR: Markdown to HTML conversion failed!", file=sys.stderr)
      print(res_marked.stderr or res_marked.stdout, file=sys.stderr)
      sys.exit(1)

    with open(temp_body_html, "r", encoding="utf-8") as f:
      body_content = f.read()

    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{input_path.stem}</title>
<style>
{css_content}
</style>
</head>
<body>
{body_content}
</body>
</html>
"""
    temp_full_html = temp_dir / "whitepaper_full.html"
    with open(temp_full_html, "w", encoding="utf-8") as f:
      f.write(full_html)

    print(f"[{input_path.name}] Step 3/4: Rendering PDF via Google Chrome engine...")
    chrome_cmd = [
        chrome_exec,
        "--headless",
        "--disable-gpu",
        "--allow-file-access-from-files",
        f"--print-to-pdf={output_path}",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"file://{temp_full_html}"
    ]
    res_chrome = subprocess.run(chrome_cmd, capture_output=True, text=True)
    if res_chrome.returncode != 0:
      print("ERROR: Google Chrome PDF rendering failed!", file=sys.stderr)
      print(res_chrome.stderr or res_chrome.stdout, file=sys.stderr)
      sys.exit(1)

    if not output_path.exists() or os.path.getsize(output_path) == 0:
      print("ERROR: Output PDF was not generated or is empty.", file=sys.stderr)
      sys.exit(1)

    print(f"[{input_path.name}] Step 4/4: Done!")
    print(f"Success! Data written to: {output_path} ({os.path.getsize(output_path)} bytes)")

  finally:
    if args.keep_temp:
      print(f"Debug: Temporary build files preserved at: {temp_dir}")
    else:
      shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
  main()
