from pathlib import Path


REQUIRED_MARKERS = (
    "<!-- telegram-brief:start -->",
    "<!-- telegram-brief:end -->",
)
REQUIRED_FIELDS = (
    "Pick:",
    "Why/impact:",
    "Learning:",
    "Plan:",
    "Alternatives:",
    "Contribution:",
    "Repository/issue:",
    "Branch/commit:",
    "Validation:",
    "Draft PR/fallback:",
    "Action needed:",
)


def _dated_reports() -> list[Path]:
    return sorted(Path("reports").glob("????-??-??.md"))


def test_dated_reports_have_single_telegram_brief() -> None:
    reports = _dated_reports()
    assert reports, "expected at least one dated contribution report"

    for report in reports:
        text = report.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS:
            assert text.count(marker) == 1, f"{report}: expected exactly one {marker}"

        start = text.index(REQUIRED_MARKERS[0])
        end = text.index(REQUIRED_MARKERS[1], start)
        brief = text[start:end]
        for field in REQUIRED_FIELDS:
            assert brief.count(field) == 1, f"{report}: expected exactly one {field} in brief"


def test_telegram_brief_fields_are_single_lines() -> None:
    for report in _dated_reports():
        text = report.read_text(encoding="utf-8")
        start = text.index(REQUIRED_MARKERS[0])
        end = text.index(REQUIRED_MARKERS[1], start)
        brief_lines = text[start:end].splitlines()

        for field in REQUIRED_FIELDS:
            matches = [line for line in brief_lines if line.startswith(field)]
            assert len(matches) == 1, f"{report}: expected one line starting with {field}"
            assert matches[0][len(field) :].strip(), f"{report}: {field} must have a concise value"


def test_telegram_brief_precedes_full_report() -> None:
    for report in _dated_reports():
        text = report.read_text(encoding="utf-8")
        assert text.lstrip().startswith(REQUIRED_MARKERS[0]), (
            f"{report}: telegram brief must be the first report block"
        )
