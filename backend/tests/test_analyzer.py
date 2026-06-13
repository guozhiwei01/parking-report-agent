from app.reporting.analyzer import analyze_transactions


def test_sample_csv_hard_metrics() -> None:
    result = analyze_transactions("Interview_materials/data.csv")
    metrics = result["metrics"]

    assert metrics["total_transactions"] == 3674
    assert metrics["receivable_amount"] == 105795.0
    assert metrics["collected_amount"] == 57397.5
    assert metrics["actual_deduct_amount"] == 48285.0
    assert metrics["collection_rate"] == 54.3
    assert metrics["top_payment_method"] == "微信"
    assert metrics["top_payment_method_count"] == 1435


def test_sample_csv_profile() -> None:
    profile = analyze_transactions("Interview_materials/data.csv")["profile"]

    assert profile["payment_channel_counts"][0] == {"name": "线上支付", "count": 3122}
    assert profile["duration"]["bins"][-1] == {"range": "12+", "count": 78}


def test_sample_csv_period() -> None:
    profile = analyze_transactions("Interview_materials/data.csv")["profile"]

    assert profile["period"] == {"start": "2026-04-01", "end": "2026-04-30"}


def test_sample_csv_hourly_distribution() -> None:
    profile = analyze_transactions("Interview_materials/data.csv")["profile"]

    entry = profile["entry_hour_counts"]
    charge = profile["charge_hour_counts"]
    # 模板要求：早上 6 点到晚上 8 点，1 小时单位（14 个区间）
    assert [item["hour"] for item in entry] == list(range(6, 20))
    assert [item["hour"] for item in charge] == list(range(6, 20))
    assert all(item["count"] >= 0 for item in entry)
    assert all(item["count"] >= 0 for item in charge)
