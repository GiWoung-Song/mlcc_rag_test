"""Mock check_optimal_design tool for testing.

In production, this tool verifies whether a given lot_id has
sufficient reference data to run DOE simulation.

This mock returns sample responses for known test lot IDs.
"""

# Sample reference data for testing
_VALID_LOTS = {
    "L240301-A": {
        "충족인자": [
            "Sheet 두께",
            "전극 폭",
            "전극 수",
            "Margin L",
            "Margin W",
            "유전체 두께",
            "Cover 두께",
            "유전상수",
        ],
        "부족인자": [],
    },
    "L240215-B": {
        "충족인자": [
            "Sheet 두께",
            "전극 폭",
            "전극 수",
            "Margin L",
        ],
        "부족인자": [
            "유전체 두께",
            "Cover 두께",
            "유전상수",
        ],
    },
}


def check_optimal_design(lot_id: str) -> dict:
    """Check whether a reference LOT is valid for DOE simulation.

    Verifies that the given lot_id has all required reference factors
    to run the optimal_design simulation. If any factors are missing,
    the lot cannot be used and a different lot_id should be provided.

    Args:
        lot_id: The reference LOT identifier to validate.
                Example: "L240301-A"

    Returns:
        A dict with 'status', 'lot_id', '충족인자' (satisfied factors),
        and '부족인자' (missing factors).
    """
    lot_id = lot_id.strip()

    if lot_id in _VALID_LOTS:
        data = _VALID_LOTS[lot_id]
        return {
            "status": "success",
            "lot_id": lot_id,
            "충족인자": data["충족인자"],
            "부족인자": data["부족인자"],
        }

    # Unknown lot_id -> treat as having missing factors for safety
    return {
        "status": "success",
        "lot_id": lot_id,
        "충족인자": ["Sheet 두께", "전극 폭"],
        "부족인자": ["전극 수", "유전체 두께", "Cover 두께", "유전상수", "Margin"],
    }
