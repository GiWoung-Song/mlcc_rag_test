"""Mock search_rag tool for testing.

In production, this tool queries the SEMCO MLCC vector DB
(collection: semco_mlcc_catalog_2025) built from
mlcc_catalog_rag_chunks_v2_partnumber_focused.jsonl.

This mock implementation performs simple keyword matching against the
local JSONL file so the agent workflow can be tested end-to-end
without a real vector DB.
"""

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CHUNKS_PATH = _PROJECT_ROOT / "mlcc_catalog_rag_chunks_v2_partnumber_focused.jsonl"

_chunks: list[dict] | None = None


def _load_chunks() -> list[dict]:
    global _chunks
    if _chunks is not None:
        return _chunks

    _chunks = []
    if _CHUNKS_PATH.is_file():
        with open(_CHUNKS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        _chunks.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return _chunks


def _matches_filter(metadata: dict, search_group: str | None,
                    position: int | None, chunk_type: str | None) -> bool:
    """Check if a chunk's metadata matches the provided filters."""
    if search_group is not None and metadata.get("search_group") != search_group:
        return False
    if position is not None and metadata.get("position") != position:
        return False
    if chunk_type is not None and metadata.get("chunk_type") != chunk_type:
        return False
    return True


def search_rag(
    query: str,
    top_k: int = 5,
    search_group: str | None = None,
    position: int | None = None,
    chunk_type: str | None = None,
) -> dict:
    """Search the SEMCO MLCC catalog vector DB.

    Retrieves chunks from the MLCC catalog that are relevant to the query.
    The catalog covers part numbering codes, product families, reliability
    levels, new-product examples, and caution characteristics.

    Use metadata filters to narrow results and avoid noisy broad searches.
    For code mapping lookups (positions 1-7), prefer reading
    catalog-codebook.md directly instead of calling this tool.

    In the test environment this performs keyword matching against the
    local chunk file. In production it queries the actual vector DB.

    Args:
        query: Natural-language or code-based search query.
               Examples: "high level II outdoor 85 85 1000h",
               "0201 0603 4.7uF X5R 4V", "DC bias characteristics"
        top_k: Maximum number of chunks to return (default 5).
        search_group: Filter by search_group metadata. Common values:
                      "mapping_core" (part number code tables),
                      "family_reference" (product family descriptions),
                      "caution_reference" (DC bias, AC voltage cautions),
                      "dimension_reference" (size/thickness details),
                      "overview" (product overview).
        position: Filter by part number position (1-11).
                  e.g. 2 for size_code, 3 for temperature_code,
                  6 for rated_voltage_code.
        chunk_type: Filter by chunk type. Common values:
                    "mapping_row", "mapping_table", "mapping_rule",
                    "family_reference", "dimension_row".

    Returns:
        A dict with 'status', 'query', 'result_count', and 'results'.
        Each result contains 'chunk_id', 'score', 'text', and 'metadata'.
    """
    chunks = _load_chunks()
    if not chunks:
        return {
            "status": "error",
            "error": (
                f"Chunk file not found or empty at {_CHUNKS_PATH}. "
                "Make sure mlcc_catalog_rag_chunks_v2_partnumber_focused.jsonl "
                "exists in the project root."
            ),
        }

    keywords = query.lower().split()
    scored: list[tuple[float, dict]] = []

    for chunk in chunks:
        metadata = chunk.get("metadata", {})

        # Apply metadata filters before scoring
        if not _matches_filter(metadata, search_group, position, chunk_type):
            continue

        text = chunk.get("text", "").lower()
        aliases = " ".join(metadata.get("aliases", [])).lower()
        searchable = text + " " + aliases

        hits = sum(1 for kw in keywords if kw in searchable)
        if hits > 0:
            score = hits / len(keywords)
            scored.append((score, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    results = []
    for score, chunk in top:
        results.append({
            "chunk_id": chunk.get("id", "unknown"),
            "score": round(score, 3),
            "text": chunk.get("text", "")[:2000],
            "metadata": chunk.get("metadata", {}),
        })

    return {
        "status": "success",
        "query": query,
        "filters": {
            k: v for k, v in [
                ("search_group", search_group),
                ("position", position),
                ("chunk_type", chunk_type),
            ] if v is not None
        },
        "result_count": len(results),
        "results": results,
    }
