from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analysis_query() -> None:
    response = TestClient(app).post(
        "/api/v1/analysis/query",
        json={"question": "统计每条产线最近7天的产量趋势"},
    )
    assert response.status_code == 200
    assert response.json()["sql"].startswith("SELECT")
    assert response.json()["rows"]


def test_knowledge_json_crud() -> None:
    client = TestClient(app)
    metric_code = "test_energy_usage"
    payload = {
        "metric_code": metric_code,
        "metric_name": "测试能耗",
        "category": "能源",
        "description": "自动化测试临时指标",
        "formula_expression": "SUM(energy_kwh)",
        "unit": "kWh",
        "source_tables": ["manufacturing.fact_energy"],
    }
    created = client.post("/api/v1/knowledge/metrics", json=payload)
    assert created.status_code == 201
    assert created.json()["version"] == 1

    updated = client.put(
        f"/api/v1/knowledge/metrics/{metric_code}",
        json={"metric_name": "测试总能耗"},
    )
    assert updated.status_code == 200
    assert updated.json()["version"] == 2

    searched = client.get("/api/v1/knowledge/search", params={"q": "总能耗"})
    assert searched.status_code == 200
    assert searched.json()["metrics"][0]["metric_code"] == metric_code

    deleted = client.delete(f"/api/v1/knowledge/metrics/{metric_code}")
    assert deleted.status_code == 204


def test_catalog_uses_json_storage() -> None:
    response = TestClient(app).get("/api/v1/catalog/metrics")
    assert response.status_code == 200
    assert any(item["code"] == "defect_rate" for item in response.json()["items"])


def test_runtime_reports_offline_mode() -> None:
    response = TestClient(app).get("/api/v1/catalog/runtime")
    assert response.status_code == 200
    assert response.json()["storage_backend"] == "json"
    assert response.json()["query_executor"] == "mock"
    assert response.json()["llm_enabled"] is False
