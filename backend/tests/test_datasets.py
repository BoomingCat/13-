from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

DATA_DIRECTORY = Path(r"D:\竞赛\服务外包\13届省赛\data")


def test_dataset_catalog_reads_manufacturing_csv_files() -> None:
    original = settings.external_data_dir
    settings.external_data_dir = DATA_DIRECTORY
    try:
        response = TestClient(app).get("/api/v1/datasets")
        assert response.status_code == 200
        datasets = {item["name"]: item for item in response.json()}
        assert len(datasets) == 10
        assert datasets["dim_product"]["row_count"] == 30
        assert "product_id" in datasets["dim_product"]["columns"]
    finally:
        settings.external_data_dir = original


def test_dataset_preview_has_typed_values() -> None:
    original = settings.external_data_dir
    settings.external_data_dir = DATA_DIRECTORY
    try:
        response = TestClient(app).get(
            "/api/v1/datasets/mes_process_output/rows",
            params={"offset": 0, "limit": 2},
        )
        assert response.status_code == 200
        result = response.json()
        assert result["total"] == 2752
        assert result["returned"] == 2
        assert isinstance(result["rows"][0]["input_qty"], int)
    finally:
        settings.external_data_dir = original


def test_unknown_dataset_returns_404() -> None:
    original = settings.external_data_dir
    settings.external_data_dir = DATA_DIRECTORY
    try:
        response = TestClient(app).get("/api/v1/datasets/not_exists")
        assert response.status_code == 404
    finally:
        settings.external_data_dir = original
