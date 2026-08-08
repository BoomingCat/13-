from collections.abc import Iterator
from pathlib import Path
from shutil import copytree

import pytest

from app.core.config import settings


@pytest.fixture(autouse=True)
def isolated_json_storage(tmp_path: Path) -> Iterator[None]:
    """Keep API tests from modifying the project's tracked JSON fixtures."""
    original_data_dir = settings.data_dir
    original_llm_enabled = settings.llm_enabled
    isolated_data_dir = tmp_path / "data"
    copytree(settings.resolved_data_dir, isolated_data_dir)
    settings.data_dir = isolated_data_dir
    settings.llm_enabled = False
    try:
        yield
    finally:
        settings.data_dir = original_data_dir
        settings.llm_enabled = original_llm_enabled
