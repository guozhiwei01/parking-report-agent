from typing import Any, Dict, List

import pandas as pd


REQUIRED_COLUMNS = [
    "应收金额",
    "实收金额(元)",
    "实际抵扣额(元)",
    "支付方式",
    "支付渠道",
    "收费时间",
    "进车时间",
]


def analyze_transactions(csv_path: str) -> Dict[str, Any]:
    df = read_transactions(csv_path)
    metrics = compute_hard_metrics(df)
    profile = profile_transactions(df)
    return {"metrics": metrics, "profile": profile}


def read_transactions(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError("CSV missing required columns: " + ", ".join(missing))
    return df


def compute_hard_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    payment_counts = df["支付方式"].fillna("未知").astype(str).value_counts()
    top_method = payment_counts.index[0] if not payment_counts.empty else "未知"
    top_method_count = int(payment_counts.iloc[0]) if not payment_counts.empty else 0

    receivable = round(float(df["应收金额"].sum()), 2)
    collected = round(float(df["实收金额(元)"].sum()), 2)
    actual_deduct = round(float(df["实际抵扣额(元)"].sum()), 2)
    collection_rate = round(collected / receivable * 100, 1) if receivable else 0.0

    return {
        "total_transactions": int(len(df)),
        "receivable_amount": receivable,
        "collected_amount": collected,
        "actual_deduct_amount": actual_deduct,
        "collection_rate": collection_rate,
        "top_payment_method": top_method,
        "top_payment_method_count": top_method_count,
    }


def profile_transactions(df: pd.DataFrame) -> Dict[str, Any]:
    profiled = df.copy()
    profiled["收费时间"] = pd.to_datetime(profiled["收费时间"], errors="coerce")
    profiled["进车时间"] = pd.to_datetime(profiled["进车时间"], errors="coerce")
    duration_hours = (profiled["收费时间"] - profiled["进车时间"]).dt.total_seconds() / 3600
    profiled["停车时长(小时)"] = duration_hours

    return {
        "period": _period(profiled),
        "payment_method_counts": _value_counts(profiled, "支付方式"),
        "payment_channel_counts": _value_counts(profiled, "支付渠道"),
        "duration": {
            "average_hours": round(float(duration_hours.mean()), 2),
            "max_hours": round(float(duration_hours.max()), 2),
            "bins": _duration_bins(duration_hours),
        },
        "entry_hour_counts": _hour_counts(profiled["进车时间"]),
        "charge_hour_counts": _hour_counts(profiled["收费时间"]),
        "anomaly_candidates": _anomaly_candidates(profiled),
    }


def _period(df: pd.DataFrame) -> Dict[str, str]:
    charged = df["收费时间"].dropna()
    if charged.empty:
        return {"start": "", "end": ""}
    return {
        "start": charged.min().strftime("%Y-%m-%d"),
        "end": charged.max().strftime("%Y-%m-%d"),
    }


def _hour_counts(timestamps: pd.Series) -> List[Dict[str, Any]]:
    # 模板要求：早上 6 点到晚上 8 点，1 小时单位
    hours = range(6, 20)
    counts = timestamps.dropna().dt.hour.value_counts()
    return [{"hour": hour, "count": int(counts.get(hour, 0))} for hour in hours]


def _value_counts(df: pd.DataFrame, column: str) -> List[Dict[str, Any]]:
    counts = df[column].fillna("未知").astype(str).value_counts()
    return [{"name": str(name), "count": int(count)} for name, count in counts.items()]


def _duration_bins(duration_hours: pd.Series) -> List[Dict[str, Any]]:
    bins = [0, 2, 4, 6, 8, 10, 12, float("inf")]
    labels = ["0-2", "2-4", "4-6", "6-8", "8-10", "10-12", "12+"]
    categorized = pd.cut(duration_hours, bins=bins, labels=labels, right=False)
    counts = categorized.value_counts().reindex(labels, fill_value=0)
    return [{"range": label, "count": int(counts[label])} for label in labels]


def _anomaly_candidates(df: pd.DataFrame) -> List[Dict[str, Any]]:
    long_stay = df[df["停车时长(小时)"] >= 12].copy()
    zero_receivable_collected = df[(df["应收金额"] == 0) & (df["实收金额(元)"] > 0)].copy()
    full_deduct = df[(df["应收金额"] > 0) & (df["实际抵扣额(元)"] >= df["应收金额"])].copy()

    return [
        {"type": "long_stay_over_12h", "count": int(len(long_stay))},
        {"type": "zero_receivable_with_collection", "count": int(len(zero_receivable_collected))},
        {"type": "full_deduct", "count": int(len(full_deduct))},
    ]
