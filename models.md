# Recommended Local Models

| # | Name | Params | Quant | Bit | K-type | Size (approx) | Use case | Link |
|---|------|--------|-------|-----|--------|------|----------|------|
| 1 | Meta-Llama-3.1-8B-Instruct (MaziyarPanahi) | 8B | Q4_K_M | 4 | K-M | ~4.9 GB | General chat, reasoning, agents | [HF](https://huggingface.co/MaziyarPanahi/Meta-Llama-3.1-8B-Instruct-GGUF) |
| 2 | Needle (Cactus Compute) | 26M | N/A (custom) | fp16 | N/A | ~50 MB | Tiny tool/function-calling model | [HF](https://huggingface.co/Cactus-Compute/needle) |
| 3 | Qwen3-8B | 8B | Q4_K_M | 4 | K-M | ~5.0 GB | All-rounder, thinking mode, agents | [HF](https://huggingface.co/unsloth/Qwen3-8B-GGUF) |
| 4 | Qwen3-4B | 4B | Q4_K_M | 4 | K-M | ~2.5 GB | Fast general use on low VRAM | [HF](https://huggingface.co/unsloth/Qwen3-4B-GGUF) |
| 5 | Qwen3-1.7B | 1.7B | Q4_K_M | 4 | K-M | ~1.1 GB | Potato PC, quick tasks | [HF](https://huggingface.co/unsloth/Qwen3-1.7B-GGUF) |
| 6 | Qwen2.5-Coder-7B-Instruct | 7B | Q4_K_M | 4 | K-M | ~4.7 GB | Coding, debugging | [HF](https://huggingface.co/bartowski/Qwen2.5-Coder-7B-Instruct-GGUF) |
| 7 | DeepSeek-R1-Distill-Qwen-7B | 7B | Q4_K_M | 4 | K-M | ~4.7 GB | Step-by-step reasoning, math | [HF](https://huggingface.co/bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF) |
| 8 | Mistral-7B-Instruct-v0.3 | 7B | Q4_K_M | 4 | K-M | ~4.4 GB | Chat, function calling | [HF](https://huggingface.co/bartowski/Mistral-7B-Instruct-v0.3-GGUF) |
| 9 | Gemma-3-4B-it | 4B | Q4_K_M | 4 | K-M | ~2.5 GB | Chat plus image understanding | [HF](https://huggingface.co/unsloth/gemma-3-4b-it-GGUF) |
| 10 | Gemma-3-12B-it | 12B | Q4_K_M | 4 | K-M | ~7.3 GB | Higher quality, needs CPU offload | [HF](https://huggingface.co/unsloth/gemma-3-12b-it-GGUF) |
| 11 | Llama-3.2-3B-Instruct | 3B | Q4_K_M | 4 | K-M | ~2.0 GB | Light chat, summarizing | [HF](https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF) |
| 12 | Llama-3.2-1B-Instruct | 1B | Q8_0 | 8 | none | ~1.3 GB | Very low-end hardware, testing | [HF](https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF) |
| 13 | Phi-3.5-mini-instruct | 3.8B | Q4_K_M | 4 | K-M | ~2.4 GB | Reasoning on small hardware | [HF](https://huggingface.co/bartowski/Phi-3.5-mini-instruct-GGUF) |
| 14 | Qwen3-14B | 14B | Q4_K_M | 4 | K-M | ~9.0 GB | Stronger quality, heavy offload | [HF](https://huggingface.co/unsloth/Qwen3-14B-GGUF) |
| 15 | nomic-embed-text-v1.5 | 137M | Q8_0 | 8 | none | ~0.15 GB | Embeddings for RAG | [HF](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5-GGUF) |

## Notes

- **Needle** uses a custom architecture, so it won't load in llama.cpp, Ollama or LM Studio. It runs through its own code from the repo, so treat it separately from the GGUF models.
- **Sizes are approximate.** Check the repo's Files tab for exact numbers, since they vary slightly by repo.
- **Quant guide:** `K_S` is smaller with slightly lower quality, `K_M` is the best balance, and `K_L` is bigger with slightly higher quality. Q4_K_M is the usual sweet spot.
- **Fit on an RTX 3050 (6 GB):** models up to about 5 GB (rows 1, 3 to 9, 11, 13) should fit fully in VRAM. Rows 10 and 14 will spill into system RAM and run slower.
- **For RAG and agents:** pair #3 or #1 as the LLM with #15 for embeddings, and use #2 as a tiny tool-calling layer.