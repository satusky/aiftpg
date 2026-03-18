import io

import pytest


async def _setup_data(client):
    """Upload ground truth and submit from multiple teams."""
    csv_content = "document_id,value\ndoc1,hello\ndoc2,world\ndoc3,foo\n"
    await client.post(
        "/api/ground-truth/upload",
        files={"file": ("gt.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        data={"variable_id": "var1"},
    )

    # Team A: perfect score
    await client.post(
        "/api/submissions",
        json={
            "team_name": "team_a",
            "variable_id": "var1",
            "extracted_values": {"doc1": "hello", "doc2": "world", "doc3": "foo"},
        },
    )
    # Team B: partial score
    await client.post(
        "/api/submissions",
        json={
            "team_name": "team_b",
            "variable_id": "var1",
            "extracted_values": {"doc1": "hello", "doc2": "WRONG"},
        },
    )


@pytest.mark.asyncio
async def test_leaderboard(client):
    await _setup_data(client)
    response = await client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Team A should be rank 1
    assert data[0]["team_name"] == "team_a"
    assert data[0]["rank"] == 1
    assert data[0]["best_f1"] == 1.0


@pytest.mark.asyncio
async def test_overall_leaderboard(client):
    await _setup_data(client)
    response = await client.get("/api/leaderboard/overall")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["team_name"] == "team_a"


@pytest.mark.asyncio
async def test_list_teams(client):
    await _setup_data(client)
    response = await client.get("/api/teams")
    assert response.status_code == 200
    names = [t["team_name"] for t in response.json()]
    assert "team_a" in names
    assert "team_b" in names


@pytest.mark.asyncio
async def test_team_detail(client):
    await _setup_data(client)
    response = await client.get("/api/teams/team_a")
    assert response.status_code == 200
    data = response.json()
    assert data["team_name"] == "team_a"
    assert len(data["variables"]) == 1
    assert data["variables"][0]["variable_id"] == "var1"


@pytest.mark.asyncio
async def test_team_not_found(client):
    response = await client.get("/api/teams/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_dashboard_html(client):
    await _setup_data(client)
    response = await client.get("/dashboard/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "team_a" in response.text


@pytest.mark.asyncio
async def test_dashboard_team_detail_html(client):
    await _setup_data(client)
    response = await client.get("/dashboard/teams/team_a")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "team_a" in response.text


@pytest.mark.asyncio
async def test_rescore(client):
    """Rescore should update scores after ground truth changes."""
    # Submit without ground truth
    await client.post(
        "/api/submissions",
        json={
            "team_name": "team_a",
            "variable_id": "var1",
            "extracted_values": {"doc1": "hello"},
        },
    )

    # Verify NULL scores
    subs = (await client.get("/api/submissions")).json()
    assert subs[0]["f1"] is None

    # Upload ground truth
    csv_content = "document_id,value\ndoc1,hello\n"
    await client.post(
        "/api/ground-truth/upload",
        files={"file": ("gt.csv", io.BytesIO(csv_content.encode()), "text/csv")},
        data={"variable_id": "var1"},
    )

    # Rescore
    response = await client.post("/api/ground-truth/rescore")
    assert response.status_code == 200
    assert response.json()["rescored"] == 1

    # Verify scores updated
    subs = (await client.get("/api/submissions")).json()
    assert subs[0]["f1"] == 1.0
