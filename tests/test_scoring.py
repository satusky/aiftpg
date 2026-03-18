from app.scoring import compute_metrics, values_match


class TestValuesMatch:
    def test_both_none(self):
        assert values_match(None, None) is True

    def test_one_none(self):
        assert values_match("hello", None) is False
        assert values_match(None, "hello") is False

    def test_exact_match(self):
        assert values_match("hello", "hello") is True

    def test_case_insensitive(self):
        assert values_match("Hello", "hello") is True
        assert values_match("WORLD", "world") is True

    def test_whitespace_stripped(self):
        assert values_match("  hello  ", "hello") is True

    def test_numeric_match(self):
        assert values_match("42", "42.0") is True
        assert values_match("100.50", "100.5") is True

    def test_numeric_mismatch(self):
        assert values_match("42", "43") is False

    def test_string_mismatch(self):
        assert values_match("hello", "world") is False


class TestComputeMetrics:
    def test_empty_ground_truth(self):
        result = compute_metrics({"doc1": "val"}, {})
        assert result["f1"] is None

    def test_empty_submission(self):
        result = compute_metrics({}, {"doc1": "val"})
        assert result["f1"] == 0.0
        assert result["recall"] == 0.0

    def test_perfect_score(self):
        gt = {"doc1": "a", "doc2": "b", "doc3": "c"}
        extracted = {"doc1": "a", "doc2": "b", "doc3": "c"}
        result = compute_metrics(extracted, gt)
        assert result["f1"] == 1.0
        assert result["accuracy"] == 1.0
        assert result["precision"] == 1.0
        assert result["recall"] == 1.0

    def test_partial_match(self):
        gt = {"doc1": "a", "doc2": "b", "doc3": "c"}
        extracted = {"doc1": "a", "doc2": "WRONG"}
        # TP=1, FP=1, FN=1
        result = compute_metrics(extracted, gt)
        assert result["precision"] == 0.5
        assert result["recall"] == 0.5

    def test_extra_docs_ignored(self):
        gt = {"doc1": "a"}
        extracted = {"doc1": "a", "doc99": "extra"}
        result = compute_metrics(extracted, gt)
        assert result["f1"] == 1.0

    def test_all_wrong(self):
        gt = {"doc1": "a", "doc2": "b"}
        extracted = {"doc1": "WRONG", "doc2": "WRONG"}
        result = compute_metrics(extracted, gt)
        assert result["precision"] == 0.0
        assert result["recall"] == 0.0
        assert result["f1"] == 0.0
