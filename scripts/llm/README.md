# LLM Providers Quick Start (DeepSeek via Ollama + OpenAI via LiteLLM)

This setup gives Cursor a single OpenAI-compatible endpoint that serves:
- Local DeepSeek models via Ollama: deepseek-coder, deepseek-r1
- Optional OpenAI model alias: codex (maps to OpenAI GPT model)

## Prerequisites (one-time)
- Windows 10/11
- Python 3.10+ available on PATH (python --version)

## 1) Start Ollama and pull local models
Run in PowerShell:

scripts/llm/start-ollama.ps1

What it does:
- Installs Ollama via winget (if missing)
- Starts ollama serve on http://127.0.0.1:11434
- Ensures deepseek-coder and deepseek-r1 are pulled locally

## 2) Start LiteLLM proxy (OpenAI-compatible /v1)
Optional: set your OpenAI key in this window if you want the codex alias to use OpenAI:

SET ENV in PowerShell (temporary for this window):
$env:OPENAI_API_KEY = YOUR_OPENAI_KEY_HERE

Then run:

scripts/llm/start-litellm.ps1

What it does:
- Installs litellm[proxy] (if missing)
- Creates scripts/llm/litellm.config.yaml (from example) if absent
- Starts proxy on http://127.0.0.1:4000/v1

## 3) Point Cursor to the proxy
- Cursor → Settings → Models → OpenAI custom endpoint: http://127.0.0.1:4000/v1
- Use models: deepseek-coder (code), deepseek-r1 (reasoning), codex (OpenAI; requires OPENAI_API_KEY)

## One-shot starter
Runs Ollama then LiteLLM sequentially:

scripts/llm/start-all.ps1

## Notes
- No cloud keys required to use local DeepSeek models.
- To enable the codex alias with OpenAI, set OPENAI_API_KEY before running start-litellm.ps1.
- You can edit scripts/llm/litellm.config.yaml to add more local models (e.g., qwen2.5-coder).
