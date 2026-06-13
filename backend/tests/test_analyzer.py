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
