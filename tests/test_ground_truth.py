import pytest

from app.ground_truth import parse_csv, parse_json, parse_ground_truth


class TestParseCSV:
    def test_basic(self):
        csv_content = "document_id,value\ndoc1,hello\ndoc2,world\n"
        result = parse_csv(csv_content)
        assert result == {"doc1": "hello", "doc2": "world"}

    def test_bytes(self):
        result = parse_csv(b"document_id,value\ndoc1,val1\n")
        assert result == {"doc1": "val1"}

    def test_empty_value(self):
        result = parse_csv("document_id,value\ndoc1,\n")
        assert result == {"doc1": None}

    def test_strips_whitespace(self):
        result = parse_csv("document_id,value\n  doc1  ,  val1  \n")
        assert result == {"doc1": "val1"}


class TestParseJSON:
    def test_basic(self):
        result = parse_json('{"doc1": "hello", "doc2": "world"}')
        assert result == {"doc1": "hello", "doc2": "world"}

    def test_null_value(self):
        result = parse_json('{"doc1": null}')
        assert result == {"doc1": None}

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_json('[1, 2, 3]')


class TestParseGroundTruth:
    def test_csv_by_extension(self):
        result = parse_ground_truth("document_id,value\ndoc1,val\n", "data.csv")
        assert result == {"doc1": "val"}

    def test_json_by_extension(self):
        result = parse_ground_truth('{"doc1": "val"}', "data.json")
        assert result == {"doc1": "val"}


@pytest.mark.asyncio
async def test_upload_ground_truth(client):
    import io
    csv_content = "document_id,value\ndoc1,hello\ndoc2,world\n"
    response = await client.post(
        "/api/ground-truth/upload",
        files={"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        data={"variable_id": "var1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["documents_loaded"] == 2
    assert data["variable_id"] == "var1"


@pytest.mark.asyncio
async def test_list_ground_truth(client):
    import io
    csv_content = "document_id,value\ndoc1,hello\n"
    await client.post(
        "/api/ground-truth/upload",
        files={"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        data={"variable_id": "var1"},
    )
    response = await client.get("/api/ground-truth")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["variable_id"] == "var1"
    assert data[0]["document_count"] == 1


@pytest.mark.asyncio
async def test_delete_ground_truth(client):
    import io
    csv_content = "document_id,value\ndoc1,hello\n"
    await client.post(
        "/api/ground-truth/upload",
        files={"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        data={"variable_id": "var1"},
    )
    response = await client.delete("/api/ground-truth/var1")
    assert response.status_code == 200
    assert response.json()["deleted"] == 1
