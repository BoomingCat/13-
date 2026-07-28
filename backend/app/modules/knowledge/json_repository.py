import json
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any


class JsonKnowledgeRepository:
    """适合本地开发的 JSON Repository，接口与数据库 Repository 保持一致。"""

    _lock = RLock()

    def __init__(self, file_path: Path, code_field: str, name_field: str, *, versioned: bool = False) -> None:
        self.file_path = file_path
        self.code_field = code_field
        self.name_field = name_field
        self.versioned = versioned
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.file_path.exists():
            self._write([])

    def _read(self) -> list[dict[str, Any]]:
        with self._lock:
            return json.loads(self.file_path.read_text(encoding="utf-8"))

    def _write(self, items: list[dict[str, Any]]) -> None:
        with self._lock:
            temporary = self.file_path.with_suffix(".json.tmp")
            temporary.write_text(
                json.dumps(items, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            temporary.replace(self.file_path)

    async def list(
        self,
        keyword: str | None = None,
        category: str | None = None,
        status: str | None = "active",
    ) -> list[dict[str, Any]]:
        items = self._read()
        if keyword:
            normalized = keyword.casefold()
            items = [
                item for item in items
                if normalized in " ".join(
                    str(item.get(field, ""))
                    for field in (self.code_field, self.name_field, "description")
                ).casefold()
            ]
        if category:
            items = [item for item in items if item.get("category") == category]
        if status:
            items = [item for item in items if item.get("status") == status]
        return sorted((deepcopy(item) for item in items), key=lambda item: item[self.name_field])

    async def get_by_code(self, code: str) -> dict[str, Any] | None:
        return next(
            (deepcopy(item) for item in self._read() if item[self.code_field] == code),
            None,
        )

    async def create(self, values: dict[str, Any]) -> dict[str, Any]:
        items = self._read()
        now = datetime.now(UTC).isoformat()
        entity = deepcopy(values)
        entity.update({
            "id": max((int(item["id"]) for item in items), default=0) + 1,
            "created_at": now,
            "updated_at": now,
        })
        if self.versioned:
            entity["version"] = 1
        items.append(entity)
        self._write(items)
        return deepcopy(entity)

    async def update(self, entity: dict[str, Any], values: dict[str, Any]) -> dict[str, Any]:
        items = self._read()
        for index, item in enumerate(items):
            if item[self.code_field] != entity[self.code_field]:
                continue
            updated = {**item, **deepcopy(values), "updated_at": datetime.now(UTC).isoformat()}
            if self.versioned:
                updated["version"] = int(item.get("version", 1)) + 1
            items[index] = updated
            self._write(items)
            return deepcopy(updated)
        raise KeyError(entity[self.code_field])

    async def delete(self, entity: dict[str, Any]) -> None:
        items = [
            item for item in self._read()
            if item[self.code_field] != entity[self.code_field]
        ]
        self._write(items)


def build_json_repositories(data_dir: Path) -> tuple[JsonKnowledgeRepository, ...]:
    knowledge_dir = data_dir / "knowledge"
    return (
        JsonKnowledgeRepository(knowledge_dir / "objects.json", "object_code", "object_name"),
        JsonKnowledgeRepository(knowledge_dir / "metrics.json", "metric_code", "metric_name", versioned=True),
        JsonKnowledgeRepository(knowledge_dir / "rules.json", "rule_code", "rule_name"),
        JsonKnowledgeRepository(knowledge_dir / "topics.json", "topic_code", "topic_name"),
    )
