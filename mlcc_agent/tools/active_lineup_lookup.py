"""Mock active_lineup_lookup tool for testing.

In production, this tool queries the mdh_continous_view_3 view
to find currently flowing chip_prod_id rows.

This mock returns sample data so the agent dialogue flow can be
tested without a real DB connection.
"""

# Sample active lineup data for testing
_SAMPLE_LINEUP = [
    "CL32A106KOY8NNE",
    "CL32A106MOY8NNC",
    "CL32B106KOY8NNE",
    "CL32B106MOY8NNC",
    "CL32A475KOY8NNE",
    "CL32A475MOY8NNC",
    "CL03A475MR3CNNC",
    "CL03A475MR3CNNE",
    "CL03X475MS3CNWC",
    "CL10A106MQ8NNNC",
    "CL10A106MQ8NNNE",
    "CL10B225KP8NNNC",
    "CL21A106KPFNNNE",
    "CL21B106KOQNNNE",
]


def active_lineup_lookup(chip_prod_id: str) -> dict:
    """Look up currently flowing products by chip_prod_id pattern.

    Searches the mdh_continous_view_3 view for chip_prod_id rows
    matching the given pattern. Use '_' for unknown single-character
    positions and '%' for variable-length wildcards if needed.

    Args:
        chip_prod_id: Full or partial chip_prod_id pattern.
                      Examples: "CL32_106_O____", "CL03A515MR3____",
                      "%CL32_106_O____%"

    Returns:
        A dict with 'status', 'pattern', 'hit_count', and 'hits'.
    """
    pattern = chip_prod_id.strip()

    # Remove surrounding % for matching, but keep _ as single-char wildcard
    clean = pattern.strip("%")

    hits = []
    for prod_id in _SAMPLE_LINEUP:
        if _matches(prod_id, clean):
            hits.append(prod_id)

    return {
        "status": "success",
        "pattern": pattern,
        "hit_count": len(hits),
        "hits": hits,
    }


def _matches(prod_id: str, pattern: str) -> bool:
    """Simple pattern match: '_' matches any single char."""
    if len(pattern) != len(prod_id):
        # If lengths differ, try substring match
        return pattern.replace("_", "") != "" and all(
            pc == "_" or pc == c
            for pc, c in zip(pattern, prod_id[: len(pattern)])
        )
    return all(pc == "_" or pc == c for pc, c in zip(pattern, prod_id))
