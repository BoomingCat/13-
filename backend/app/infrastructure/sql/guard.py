from dataclasses import dataclass, field

import sqlglot
from sqlglot import expressions as exp


@dataclass(frozen=True)
class SQLValidationResult:
    valid: bool
    normalized_sql: str | None = None
    errors: list[str] = field(default_factory=list)


class SQLGuard:
    def __init__(self, allowed_schemas: set[str] | None = None, max_rows: int = 1000) -> None:
        self.allowed_schemas = allowed_schemas or {"manufacturing"}
        self.max_rows = max_rows

    def validate(self, sql: str) -> SQLValidationResult:
        errors: list[str] = []
        try:
            statements = sqlglot.parse(sql, read="postgres")
        except sqlglot.errors.ParseError as error:
            return SQLValidationResult(False, errors=[f"SQL 语法错误: {error}"])
        if len(statements) != 1:
            return SQLValidationResult(False, errors=["仅允许执行单条 SQL"])
        statement = statements[0]
        if not isinstance(statement, (exp.Select, exp.Union)):
            errors.append("仅允许 SELECT 查询")
        forbidden = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter, exp.Create, exp.Command)
        if any(statement.find(node) for node in forbidden):
            errors.append("检测到写入或管理语句")
        for table in statement.find_all(exp.Table):
            if table.db and table.db not in self.allowed_schemas:
                errors.append(f"禁止访问 Schema: {table.db}")
        if errors:
            return SQLValidationResult(False, errors=errors)
        if not statement.args.get("limit"):
            statement = statement.limit(self.max_rows)
        return SQLValidationResult(True, normalized_sql=statement.sql(dialect="postgres"))
