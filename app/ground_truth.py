import csv
import io
import json


def parse_csv(content: str | bytes) -> dict[str, str]:
    """Parse CSV with header (document_id,value) into {doc_id: value} dict."""
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    reader = csv.DictReader(io.StringIO(content))
    result = {}
    for row in reader:
        doc_id = row.get("document_id", "").strip()
        value = row.get("value", "").strip()
        if doc_id:
            result[doc_id] = value if value else None
    return result


def parse_json(content: str | bytes) -> dict[str, str]:
    """Parse JSON {doc_id: value, ...} into {doc_id: value} dict."""
    if isinstance(content, bytes):
        content = content.decode("utf-8")

    data = json.loads(content)
    if not isinstance(data, dict):
        raise ValueError("JSON ground truth must be an object mapping document_id to value")
    return {str(k): str(v) if v is not None else None for k, v in data.items()}


def parse_ground_truth(content: str | bytes, filename: str) -> dict[str, str]:
    """Parse ground truth file based on extension."""
    lower = filename.lower()
    if lower.endswith(".json"):
        return parse_json(content)
    elif lower.endswith(".csv"):
        return parse_csv(content)
    else:
        # Try CSV first, then JSON
        try:
            return parse_csv(content)
        except Exception:
            return parse_json(content)
