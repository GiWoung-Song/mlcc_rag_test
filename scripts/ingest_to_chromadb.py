#!/usr/bin/env python3
"""Ingest MLCC catalog JSONL chunks into ChromaDB.

Usage:
    python scripts/ingest_to_chromadb.py                    # ingest (skip existing)
    python scripts/ingest_to_chromadb.py --reset            # delete collection and re-ingest
    python scripts/ingest_to_chromadb.py --jsonl path.jsonl  # use a custom JSONL file
"""

import argparse
import json
import os
import sys
from pathlib import Path

import chromadb


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JSONL = PROJECT_ROOT / "mlcc_catalog_rag_chunks_v2.jsonl"
DEFAULT_DB_DIR = PROJECT_ROOT / "chroma_db"
COLLECTION_NAME = "semco_mlcc_catalog_2025"


def load_chunks(jsonl_path: Path) -> list[dict]:
    """Load chunks from a JSONL file."""
    chunks = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                chunks.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"  ⚠️  Line {lineno}: JSON parse error — {e}")
    return chunks


def flatten_metadata(meta: dict) -> dict:
    """Flatten metadata for ChromaDB (no nested lists/dicts allowed)."""
    flat = {}
    for key, value in meta.items():
        if isinstance(value, list):
            flat[key] = ", ".join(str(v) for v in value)
        elif isinstance(value, dict):
            for sub_key, sub_val in value.items():
                flat[f"{key}_{sub_key}"] = str(sub_val)
        elif value is None:
            flat[key] = ""
        else:
            flat[key] = value
    return flat


def ingest(
    jsonl_path: Path = DEFAULT_JSONL,
    db_dir: Path = DEFAULT_DB_DIR,
    reset: bool = False,
) -> None:
    """Main ingestion logic."""
    # ── Load chunks ────────────────────────────────────────
    print(f"📂 Loading chunks from: {jsonl_path}")
    chunks = load_chunks(jsonl_path)
    print(f"   Loaded {len(chunks)} chunks")

    if not chunks:
        print("   Nothing to ingest. Exiting.")
        sys.exit(1)

    # ── Connect to ChromaDB ────────────────────────────────
    db_dir.mkdir(parents=True, exist_ok=True)
    print(f"💾 ChromaDB persistent dir: {db_dir}")
    client = chromadb.PersistentClient(path=str(db_dir))

    # ── Reset if requested ─────────────────────────────────
    if reset:
        existing = [c.name for c in client.list_collections()]
        if COLLECTION_NAME in existing:
            client.delete_collection(COLLECTION_NAME)
            print(f"   🗑️  Deleted existing collection '{COLLECTION_NAME}'")

    # ── Get or create collection ───────────────────────────
    # Use the default embedding function (all-MiniLM-L6-v2)
    # Override via EMBEDDING_MODEL env var if needed
    embedding_model = os.environ.get("EMBEDDING_MODEL")
    if embedding_model:
        print(f"   Using custom embedding model: {embedding_model}")
        from chromadb.utils import embedding_functions
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef,
        )
    else:
        collection = client.get_or_create_collection(name=COLLECTION_NAME)

    # ── Ingest ─────────────────────────────────────────────
    print(f"\n🚀 Ingesting into collection '{COLLECTION_NAME}'...")

    ids = []
    documents = []
    metadatas = []

    for chunk in chunks:
        chunk_id = chunk["id"]
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})

        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(flatten_metadata(meta))

    # ChromaDB upsert: if the id already exists, it updates; otherwise inserts
    batch_size = 50
    for start in range(0, len(ids), batch_size):
        end = min(start + batch_size, len(ids))
        collection.upsert(
            ids=ids[start:end],
            documents=documents[start:end],
            metadatas=metadatas[start:end],
        )
        print(f"   Upserted {end}/{len(ids)} chunks")

    # ── Summary ────────────────────────────────────────────
    final_count = collection.count()
    print(f"\n✅ Done! Collection '{COLLECTION_NAME}' now has {final_count} documents.")
    print(f"   DB location: {db_dir}")


def main():
    parser = argparse.ArgumentParser(
        description="Ingest MLCC catalog chunks into ChromaDB"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete and recreate the collection before ingesting",
    )
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=DEFAULT_JSONL,
        help=f"Path to JSONL file (default: {DEFAULT_JSONL.name})",
    )
    parser.add_argument(
        "--db-dir",
        type=Path,
        default=DEFAULT_DB_DIR,
        help=f"ChromaDB persistent directory (default: {DEFAULT_DB_DIR})",
    )
    args = parser.parse_args()

    ingest(jsonl_path=args.jsonl, db_dir=args.db_dir, reset=args.reset)


if __name__ == "__main__":
    main()
