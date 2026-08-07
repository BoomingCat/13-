from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metadata_catalog_and_search() -> None:
    tables = client.get("/api/v1/metadata/tables")
    assert tables.status_code == 200
    assert len(tables.json()) >= 6
    search = client.get("/api/v1/metadata/search", params={"q": "不良率"})
    assert search.status_code == 200
    assert any(item["table_name"] == "fact_quality_inspection" for item in search.json()["tables"])
    relations = client.get("/api/v1/metadata/relations")
    assert relations.status_code == 200
    assert relations.json()


def test_sql_execution_and_audit() -> None:
    valid = client.post(
        "/api/v1/sql/validate",
        json={"sql": "SELECT * FROM manufacturing.fact_inventory"},
    )
    assert valid.status_code == 200
    assert valid.json()["valid"] is True

    rejected = client.post(
        "/api/v1/sql/execute",
        json={"sql": "DELETE FROM manufacturing.fact_inventory"},
    )
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    executions = client.get("/api/v1/sql/executions")
    assert executions.status_code == 200
    assert executions.json()[0]["id"] == rejected.json()["id"]


def test_analytics_and_visualization() -> None:
    data = {
        "columns": ["line", "defect_rate"],
        "rows": [["产线A", 2.1], ["产线B", 4.8], ["产线C", 3.2]],
    }
    summary = client.post(
        "/api/v1/analytics/summary",
        json={**data, "numeric_columns": ["defect_rate"]},
    )
    assert summary.status_code == 200
    assert summary.json()["summaries"][0]["maximum"] == 4.8

    ranking = client.post(
        "/api/v1/analytics/ranking",
        json={**data, "category_column": "line", "value_column": "defect_rate"},
    )
    assert ranking.status_code == 200
    assert ranking.json()["rows"][0][0] == "产线B"

    chart = client.post(
        "/api/v1/visualization/build",
        json={**data, "title": "各产线不良率", "chart_type": "bar"},
    )
    assert chart.status_code == 200
    assert chart.json()["chart_type"] == "bar"


def test_analysis_history_and_report() -> None:
    analysis = client.post(
        "/api/v1/analysis/query",
        json={"question": "分析最近30天各产线的不良率"},
    )
    assert analysis.status_code == 200
    result = analysis.json()
    assert result["plan"]["metric_codes"] == ["defect_rate"]
    assert result["rows"]
    assert result["columns"] == ["category", "value"]
    assert all(isinstance(row[1], (int, float)) for row in result["rows"])

    history = client.get(f"/api/v1/history/tasks/{result['task_id']}")
    assert history.status_code == 200
    assert history.json()["question"] == result["question"]

    report = client.post(
        "/api/v1/reports",
        json={
            "question": result["question"],
            "sql": result["sql"],
            "columns": result["columns"],
            "rows": result["rows"],
            "conclusion": result["conclusion"],
        },
    )
    assert report.status_code == 200
    assert "# 企业数据分析报告" in report.json()["content"]


def test_modeling_uses_test_split_and_importance() -> None:
    response = client.post(
        "/api/v1/modeling/run",
        json={
            "algorithm": "linear_regression",
            "features": [[1], [2], [3], [4], [5], [6], [7], [8], [9], [10]],
            "target": [2, 4, 6, 8, 10, 12, 14, 16, 18, 20],
            "feature_names": ["input"],
            "test_size": 0.2,
        },
    )
    assert response.status_code == 200
    assert response.json()["test_count"] == 2
    assert "input" in response.json()["feature_importance"]
