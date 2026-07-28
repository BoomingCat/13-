import json
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any


class AnalysisHistoryRepository:
    _lock = RLock()

    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / "history" / "analysis_tasks.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        with self._lock:
            return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, items: list[dict[str, Any]]) -> None:
        with self._lock:
            temporary = self.path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(self.path)

    def save(self, item: dict[str, Any]) -> dict[str, Any]:
        record = {**item, "created_at": datetime.now(UTC).isoformat()}
        items = self._read()
        items.append(record)
        self._write(items[-1000:])
        return record

    def list(self, limit: int) -> list[dict[str, Any]]:
        return list(reversed(self._read()))[:limit]

    def get(self, task_id: str) -> dict[str, Any] | None:
        return next((item for item in self._read() if item["task_id"] == task_id), None)

    def delete(self, task_id: str) -> bool:
        items = self._read()
        filtered = [item for item in items if item["task_id"] != task_id]
        if len(filtered) == len(items):
            return False
        self._write(filtered)
        return True
