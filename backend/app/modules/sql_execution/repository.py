import json
from pathlib import Path
from threading import RLock
from typing import Any


class SQLExecutionRepository:
    _lock = RLock()

    def __init__(self, data_dir: Path) -> None:
        self.path = data_dir / "history" / "sql_executions.json"
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
        items = self._read()
        items.append(item)
        self._write(items[-1000:])
        return item

    def get(self, execution_id: str) -> dict[str, Any] | None:
        return next((item for item in self._read() if item["id"] == execution_id), None)

    def list(self, limit: int = 100) -> list[dict[str, Any]]:
        return list(reversed(self._read()))[:limit]
