import math


def values_match(submitted: str | None, truth: str | None) -> bool:
    """Compare two values with null handling, numeric coercion, and case-insensitive fallback."""
    if submitted is None and truth is None:
        return True
    if submitted is None or truth is None:
        return False

    # Numeric coercion
    try:
        s_num = float(submitted)
        t_num = float(truth)
        return math.isclose(s_num, t_num, rel_tol=1e-9, abs_tol=1e-9)
    except (ValueError, TypeError):
        pass

    # Case-insensitive string comparison
    return submitted.strip().lower() == truth.strip().lower()


def compute_metrics(
    extracted_values: dict[str, str | None],
    ground_truth: dict[str, str | None],
) -> dict[str, float | None]:
    """Compute accuracy, precision, recall, F1 for extracted values against ground truth.

    Returns dict with keys: accuracy, precision, recall, f1.
    Returns all None if ground truth is empty.
    """
    if not ground_truth:
        return {"accuracy": None, "precision": None, "recall": None, "f1": None}

    tp = 0
    fp = 0
    fn = 0

    # Check each ground truth document
    for doc_id, gt_value in ground_truth.items():
        if doc_id in extracted_values:
            if values_match(extracted_values[doc_id], gt_value):
                tp += 1
            else:
                fp += 1
        else:
            fn += 1

    # Documents in extracted but not in ground truth are ignored (no penalty)

    total = tp + fp + fn
    accuracy = tp / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "accuracy": round(accuracy, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
    }
