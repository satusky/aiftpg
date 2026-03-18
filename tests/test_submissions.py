import io

import pytest


@pytest.mark.asyncio
async def test_submit_without_ground_truth(client):
    """Submission without ground truth should store but have NULL scores."""
    response = await client.post(
        "/api/submissions",
        json={
            "team_name": "team_alpha",
            "variable_id": "var1",
            "extracted_values": {"doc1": "hello"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["team_name"] == "team_alpha"
    assert data["variable_id"] == "var1"
    assert data["f1"] is None


@pytest.mark.asyncio
async def test_submit_with_ground_truth(client):
    """Submission with ground truth should compute scores."""
    # Upload ground truth
    csv_content = "document_id,value\ndoc1,hello\ndoc2,world\ndoc3,foo\n"
    await client.post(
        "/api/ground-truth/upload",
        files={"file": ("gt.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        data={"variable_id": "var1"},
    )

    # Submit with 2/3 correct, missing doc3
    response = await client.post(
        "/api/submissions",
        json={
            "team_name": "team_alpha",
            "variable_id": "var1",
            "extracted_values": {"doc1": "hello", "doc2": "world"},
        },
    )
    assert response.status_code == 200
    data = response.json()
    # TP=2, FP=0, FN=1 -> precision=1.0, recall=2/3
    assert data["precision"] == 1.0
    assert abs(data["recall"] - 2 / 3) < 0.001


@pytest.mark.asyncio
async def test_submit_extra_fields(client):
    """Extra fields should be stored."""
    response = await client.post(
        "/api/submissions",
        json={
            "team_name": "team_beta",
            "variable_id": "var1",
            "extracted_values": {"doc1": "val"},
            "model_name": "gpt-4",
            "confidence": 0.95,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["extra_fields"]["model_name"] == "gpt-4"
    assert data["extra_fields"]["confidence"] == 0.95


@pytest.mark.asyncio
async def test_list_submissions(client):
    await client.post(
        "/api/submissions",
        json={"team_name": "team_a", "variable_id": "v1", "extracted_values": {"d1": "x"}},
    )
    await client.post(
        "/api/submissions",
        json={"team_name": "team_b", "variable_id": "v1", "extracted_values": {"d1": "y"}},
    )

    # List all
    response = await client.get("/api/submissions")
    assert response.status_code == 200
    assert len(response.json()) == 2

    # Filter by team
    response = await client.get("/api/submissions?team_name=team_a")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["team_name"] == "team_a"


@pytest.mark.asyncio
async def test_get_submission(client):
    resp = await client.post(
        "/api/submissions",
        json={"team_name": "team_a", "variable_id": "v1", "extracted_values": {"d1": "x"}},
    )
    sub_id = resp.json()["id"]
    response = await client.get(f"/api/submissions/{sub_id}")
    assert response.status_code == 200
    assert response.json()["id"] == sub_id


@pytest.mark.asyncio
async def test_get_submission_not_found(client):
    response = await client.get("/api/submissions/99999")
    assert response.status_code == 404
