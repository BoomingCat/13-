import csv
from collections.abc import Iterator
from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.modules.datasets.schemas import (
    DatasetColumn,
    DatasetDetail,
    DatasetRows,
    DatasetStatus,
    DatasetSummary,
)


class DatasetConfigurationError(RuntimeError):
    pass


class DatasetNotFoundError(FileNotFoundError):
    pass


def _convert(value: str) -> Any:
    stripped = value.strip()
    if stripped == "":
        return None
    lowered = stripped.casefold()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        return int(stripped)
    except ValueError:
        pass
    try:
        return float(stripped)
    except ValueError:
        pass
    for parser in (date.fromisoformat, datetime.fromisoformat):
        try:
            return parser(stripped).isoformat()
        except ValueError:
            pass
    return stripped


def _data_type(values: list[Any]) -> str:
    present = [value for value in values if value is not None]
    if not present:
        return "string"
    if all(isinstance(value, bool) for value in present):
        return "boolean"
    if all(isinstance(value, int) and not isinstance(value, bool) for value in present):
        return "integer"
    if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in present):
        return "number"
    return "string"


class CsvDatasetRepository:
    def __init__(self, directory: Path | None) -> None:
        self.directory = directory

    def status(self) -> DatasetStatus:
        available = bool(self.directory and self.directory.is_dir())
        return DatasetStatus(
            configured=self.directory is not None,
            available=available,
            directory=str(self.directory or ""),
            csv_count=len(self._files()) if available else 0,
        )

    def _require_directory(self) -> Path:
        if self.directory is None:
            raise DatasetConfigurationError("未配置 EXTERNAL_DATA_DIR")
        if not self.directory.is_dir():
            raise DatasetConfigurationError(f"数据目录不存在: {self.directory}")
        return self.directory

    def _files(self) -> list[Path]:
        directory = self._require_directory()
        return sorted(directory.glob("*.csv"), key=lambda path: path.name.casefold())

    def _path(self, name: str) -> Path:
        safe_name = Path(name).stem
        path = self._require_directory() / f"{safe_name}.csv"
        if not path.is_file():
            raise DatasetNotFoundError(f"数据集 {safe_name} 不存在")
        return path

    @staticmethod
    def _reader(path: Path) -> Iterator[dict[str, str]]:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            yield from csv.DictReader(stream)

    @staticmethod
    def _header(path: Path) -> list[str]:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            return next(csv.reader(stream), [])

    def list(self) -> list[DatasetSummary]:
        result = []
        for path in self._files():
            columns = self._header(path)
            row_count = sum(1 for _ in self._reader(path))
            result.append(DatasetSummary(
                name=path.stem,
                filename=path.name,
                row_count=row_count,
                column_count=len(columns),
                columns=columns,
            ))
        return result

    def detail(self, name: str, sample_size: int = 20) -> DatasetDetail:
        path = self._path(name)
        columns = self._header(path)
        samples: dict[str, list[Any]] = {column: [] for column in columns}
        nullable = {column: False for column in columns}
        row_count = 0
        for raw_row in self._reader(path):
            row_count += 1
            for column in columns:
                value = _convert(raw_row.get(column, ""))
                nullable[column] = nullable[column] or value is None
                if row_count <= sample_size and value not in samples[column]:
                    samples[column].append(value)
        schema = [
            DatasetColumn(
                name=column,
                data_type=_data_type(samples[column]),
                nullable=nullable[column],
                sample_values=samples[column][:5],
            )
            for column in columns
        ]
        return DatasetDetail(
            name=path.stem,
            filename=path.name,
            path=str(path),
            row_count=row_count,
            column_count=len(columns),
            columns=columns,
            column_schema=schema,
        )

    def rows(self, name: str, offset: int, limit: int) -> DatasetRows:
        path = self._path(name)
        columns = self._header(path)
        selected: list[dict[str, Any]] = []
        total = 0
        for total, raw_row in enumerate(self._reader(path), start=1):
            index = total - 1
            if offset <= index < offset + limit:
                selected.append({column: _convert(raw_row.get(column, "")) for column in columns})
        return DatasetRows(
            dataset=path.stem,
            columns=columns,
            rows=selected,
            offset=offset,
            limit=limit,
            returned=len(selected),
            total=total,
        )
