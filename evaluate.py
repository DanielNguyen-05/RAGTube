"""
Đánh giá chỉ số Recall@K và MRR cho RAG pipeline.

Cách xác định relevance: sample thứ i của tài liệu X được sinh từ chunk thứ i
của tài liệu X (khớp 1:1 theo thứ tự). Đây là nhãn chính xác, không fuzzy.

Chạy: python evaluate.py [--k 1 3 5] [--top-n 10]
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

CHUNKS_DIR = Path("data/processed/chunks")
STRUCTURED_DIR = Path("data/processed/structured")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_all_chunks() -> Tuple[List[Document], Dict[str, List[int]]]:
    """Return (docs, doc_key -> ordered chunk_ids)."""
    docs: List[Document] = []
    doc_chunk_ids: Dict[str, List[int]] = {}

    for chunks_file in sorted(CHUNKS_DIR.glob("*_chunks.json")):
        data = json.loads(chunks_file.read_text(encoding="utf-8"))
        doc_key = chunks_file.stem.replace("_chunks", "")
        doc_chunk_ids[doc_key] = []

        for chunk in data["chunks"]:
            unique_id = f"{doc_key}__c{chunk['chunk_id']}"
            docs.append(Document(
                page_content=chunk["content"],
                metadata={
                    "uid": unique_id,
                    "doc_key": doc_key,
                    "chunk_id": chunk["chunk_id"],
                    "page": chunk["page"],
                },
            ))
            doc_chunk_ids[doc_key].append(chunk["chunk_id"])

    return docs, doc_chunk_ids


def load_all_samples(doc_chunk_ids: Dict[str, List[int]]) -> List[Dict]:
    """Return list of {question, relevant_uid, doc_key}."""
    samples: List[Dict] = []

    for struct_file in sorted(STRUCTURED_DIR.glob("*_structured.json")):
        data = json.loads(struct_file.read_text(encoding="utf-8"))
        doc_key = struct_file.stem.replace("_structured", "")
        chunk_ids = doc_chunk_ids.get(doc_key, [])

        for i, sample in enumerate(data["samples"]):
            relevant_uid = f"{doc_key}__c{chunk_ids[i]}" if i < len(chunk_ids) else None
            samples.append({
                "question": sample["question"],
                "relevant_uid": relevant_uid,
                "doc_key": doc_key,
            })

    return samples


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(
    vector_db: FAISS,
    samples: List[Dict],
    k_values: List[int],
    top_n: int,
) -> Tuple[Dict[str, float], Dict[str, Dict]]:
    """
    Returns:
        overall  : {metric_name -> value}
        per_doc  : {doc_key -> {metric_name -> value}}
    """
    mrr_sum = 0.0
    recall_hits = {k: 0 for k in k_values}

    per_doc_mrr: Dict[str, float] = {}
    per_doc_hits: Dict[str, Dict[int, int]] = {}
    per_doc_count: Dict[str, int] = {}

    n = len(samples)
    t0 = time.time()

    for idx, sample in enumerate(samples):
        retrieved = vector_db.similarity_search(sample["question"], k=top_n)
        target = sample["relevant_uid"]
        doc_key = sample["doc_key"]

        # Find rank of relevant chunk (None = not found in top_n)
        rank = next(
            (j + 1 for j, doc in enumerate(retrieved)
             if doc.metadata.get("uid") == target),
            None,
        )

        rr = (1.0 / rank) if rank is not None else 0.0
        mrr_sum += rr

        for k in k_values:
            if rank is not None and rank <= k:
                recall_hits[k] += 1

        # Per-document accumulators
        per_doc_mrr[doc_key] = per_doc_mrr.get(doc_key, 0.0) + rr
        per_doc_count[doc_key] = per_doc_count.get(doc_key, 0) + 1
        if doc_key not in per_doc_hits:
            per_doc_hits[doc_key] = {k: 0 for k in k_values}
        for k in k_values:
            if rank is not None and rank <= k:
                per_doc_hits[doc_key][k] += 1

        if (idx + 1) % 200 == 0 or (idx + 1) == n:
            elapsed = time.time() - t0
            print(f"  [{idx+1:4d}/{n}]  "
                  f"MRR={mrr_sum/(idx+1):.4f}  "
                  f"Recall@{max(k_values)}={recall_hits[max(k_values)]/(idx+1):.4f}  "
                  f"({elapsed:.1f}s)")

    overall: Dict[str, float] = {"MRR": mrr_sum / n}
    for k in k_values:
        overall[f"Recall@{k}"] = recall_hits[k] / n

    per_doc: Dict[str, Dict] = {}
    for dk, count in per_doc_count.items():
        per_doc[dk] = {"MRR": per_doc_mrr[dk] / count}
        for k in k_values:
            per_doc[dk][f"Recall@{k}"] = per_doc_hits[dk][k] / count

    return overall, per_doc


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def print_results(overall: Dict[str, float], per_doc: Dict[str, Dict], k_values: List[int]) -> None:
    sep = "=" * 62

    # Per-document table
    col_metrics = ["MRR"] + [f"Recall@{k}" for k in k_values]
    header = f"{'Document':<28}" + "".join(f"{m:>10}" for m in col_metrics)
    print(f"\n{sep}")
    print("PER-DOCUMENT BREAKDOWN")
    print(sep)
    print(header)
    print("-" * len(header))
    for dk in sorted(per_doc):
        row = f"{dk:<28}" + "".join(f"{per_doc[dk][m]:>10.4f}" for m in col_metrics)
        print(row)

    # Overall
    print(f"\n{sep}")
    print("OVERALL RESULTS  (combined index, cross-document retrieval)")
    print(sep)
    for m in col_metrics:
        print(f"  {m:<12} {overall[m]:.4f}")
    print(sep)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG Recall@K and MRR.")
    parser.add_argument("--k", nargs="+", type=int, default=[1, 3, 5],
                        help="K values for Recall@K (default: 1 3 5)")
    parser.add_argument("--top-n", type=int, default=10,
                        help="Max rank to consider for MRR (default: 10)")
    args = parser.parse_args()

    k_values: List[int] = sorted(set(args.k))
    top_n: int = max(max(k_values), args.top_n)

    # 1. Load chunks
    print("\nLoading chunks ...")
    docs, doc_chunk_ids = load_all_chunks()
    print(f"  {len(docs)} chunks from {len(doc_chunk_ids)} documents")

    # 2. Load samples
    print("Loading evaluation samples ...")
    samples = load_all_samples(doc_chunk_ids)
    print(f"  {len(samples)} samples")

    # 3. Build FAISS index
    print(f"Building FAISS index  (model: {EMBEDDING_MODEL}) ...")
    t0 = time.time()
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vector_db = FAISS.from_documents(docs, embeddings)
    print(f"  Done in {time.time() - t0:.1f}s")

    # 4. Evaluate
    print(f"\nEvaluating {len(samples)} queries  (top_n={top_n}, k={k_values}) ...")
    overall, per_doc = evaluate(vector_db, samples, k_values, top_n)

    # 5. Print
    print_results(overall, per_doc, k_values)


if __name__ == "__main__":
    main()
