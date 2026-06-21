---
name: openrouter-pdf-extract
description: Extract text from PDF files using OpenRouter multimodal models. Use when the user wants to convert a PDF document to plain text, extract structured content from product lists, invoices, or reports, or process large PDF files programmatically. Default model is google/gemini-2.5-flash-lite (native PDF input, 1M context, $0.10/M — 12× cheaper than GLM 5.2 for this task).
---

# OpenRouter PDF Text Extraction

Extract text from PDF files using Gemini Flash Lite or any OpenRouter model with `file` input support.

## Prerequisites

`OPENROUTER_API_KEY` must be set.

## Usage

```bash
# Basic: print extracted text to stdout
python ~/.claude/skills/openrouter-pdf-extract/scripts/extract_pdf.py "document.pdf"

# Save to file
python ~/.claude/skills/openrouter-pdf-extract/scripts/extract_pdf.py "document.pdf" --output extracted.txt

# Higher quality for complex layouts
python ~/.claude/skills/openrouter-pdf-extract/scripts/extract_pdf.py "document.pdf" \
  --model google/gemini-2.5-flash --output extracted.txt
```

## Model Choice

| Model | Context | Cost (input/M) | Notes |
|---|---|---|---|
| `google/gemini-2.5-flash-lite` | 1M | $0.10 | Default. Native PDF input. Best cost/quality for extraction. |
| `google/gemini-2.5-flash` | 1M | $0.30 | Higher quality for complex layouts, multi-column, or tables. |

Use `openrouter-model-advisor` with `--mode long-context` to get a current price comparison.

## Options

```
pdf                  Path to the PDF file (required)
--model <id>         OpenRouter model ID (default: google/gemini-2.5-flash-lite)
--output / -o <path> Output file — defaults to stdout if omitted
--prompt <text>      Custom extraction prompt
--max-tokens <n>     max_tokens (default: 32000; increase if finish_reason=length)
--json               Also save raw JSON response beside the output file
```

## API Notes

- PDF is sent as `data:application/pdf;base64,...` in a `file` content block.
- Large PDFs (30+ pages) may take 30–120 seconds.
- If `finish_reason=length`: increase `--max-tokens` (try 64000 for very long documents).
- The model must support `file` input modality — check with `openrouter-model-advisor`.
