from app.infrastructure.sql.guard import SQLGuard
from app.modules.analysis.templates import EQUIPMENT, INVENTORY, PRODUCTION, QUALITY, select_template
from app.modules.reporting.service import ReportService


def test_template_selection() -> None:
    assert select_template("统计产量趋势") is PRODUCTION
    assert select_template("分析工序良率") is QUALITY
    assert select_template("统计设备停机") is EQUIPMENT
    assert select_template("检查安全库存") is INVENTORY


def test_sql_guard() -> None:
    guard = SQLGuard()
    valid = guard.validate("SELECT * FROM manufacturing.fact_inventory")
    assert valid.valid
    assert "LIMIT 1000" in (valid.normalized_sql or "")
    assert not guard.validate("DELETE FROM manufacturing.fact_inventory").valid
    assert not guard.validate("SELECT * FROM secret.users").valid


def test_markdown_report() -> None:
    report = ReportService().build_markdown(question="测试", sql="SELECT 1", columns=["value"], rows=[[1]], conclusion="正常")
    assert "# 企业数据分析报告" in report
    assert "SELECT 1" in report
