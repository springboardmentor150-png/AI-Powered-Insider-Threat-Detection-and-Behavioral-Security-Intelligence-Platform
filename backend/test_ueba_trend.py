
from unittest.mock import patch

from app.ueba import get_trend_direction


def make_trend(first: int, second: int) -> list[dict]:
    """Build 14 days of mock anomaly counts."""
    counts = [first] * 7 + [second] * 7
    return [
        {"date": str(i), "anomaly_count": count}
        for i, count in enumerate(counts)
    ]


def test_trend_directions() -> None:
    cases = [
        ("stable", 10, 11, "stable"),
        ("increasing", 10, 14, "increasing"),
        ("decreasing", 10, 6, "decreasing"),
        ("zero to positive", 0, 2, "increasing"),
    ]

    for name, first, second, expected in cases:
        with patch(
            "app.ueba.get_risk_trend",
            return_value=make_trend(first, second),
        ):
            result = get_trend_direction("EMP_TEST")

        actual = result["direction"]

        assert actual == expected, (
            f"{name}: expected {expected!r}, got {actual!r}"
        )

        print(
            f"PASS: {name} -> {actual} "
            f"(first average: {result['first_week_average']}, "
            f"second average: {result['second_week_average']})"
        )


if __name__ == "__main__":
    test_trend_directions()
