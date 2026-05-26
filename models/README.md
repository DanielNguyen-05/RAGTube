# Models Directory

This directory stores model checkpoints and embeddings used by the system.

## Structure

- `checkpoints/` — Fine-tuned LLM/embedding model checkpoints (if applicable)
- `embeddings/` — Pre-computed or cached embedding matrices
- `README.md` — This file

## Current Setup

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (auto-downloaded from HuggingFace)
- **VLM**: `FPT.AI-KIE-v1.7` (called via API, no local checkpoint)
- **LLM**: `Llama-3.3-70B-Instruct` (called via API, no local checkpoint)

## Future Use Cases

If fine-tuning embeddings or hosting local LLMs:
```
models/
  ├── checkpoints/
  │   ├── embedding_finetuned_v1/
  │   │   ├── config.json
  │   │   ├── pytorch_model.bin
  │   │   └── tokenizer.json
  │   └── embedding_finetuned_v2/
  └── embeddings/
      └── cache_1928_chunks.npy
```

