"""Optional ML extension for geothermal classification.

Trains a lightweight RandomForestClassifier on pre-computed geothermal
features and returns feature importance. Physics-based calculations remain
primary; this is enhancement only.

Usage:
    python -m app.services.geothermal.ml_classifier
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def fetch_training_data() -> tuple[list[dict[str, Any]], list[str]]:
    """Load features and target from Supabase for all municipalities."""
    client = get_supabase_client()

    suit_resp = client.table("geothermal_suitability").select("*").limit(10000).execute()
    climate_resp = client.table("municipality_climate_monthly").select(
        "municipality_id,t2m"
    ).limit(10000).execute()
    hydro_resp = client.table("hydropower_suitability").select(
        "municipality_id,mean_elevation_m,mean_slope_deg"
    ).limit(10000).execute()

    suit_rows = {r["municipality_id"]: r for r in (suit_resp.data or [])}
    climate_rows = {r["municipality_id"]: r for r in (climate_resp.data or [])}
    hydro_rows = {r["municipality_id"]: r for r in (hydro_resp.data or [])}

    features: list[dict[str, float]] = []
    targets: list[str] = []

    for mid, row in suit_rows.items():
        cls = row.get("classification")
        if not cls:
            continue

        feat: dict[str, float] = {
            "heat_flow_score": float(row.get("heat_flow_score") or 0),
            "fault_distance_km": float(row.get("fault_distance_km") or 0),
            "fault_density": float(row.get("fault_density") or 0),
            "volcano_distance_km": float(row.get("volcano_distance_km") or 0),
            "aquifer_score": float(row.get("aquifer_score") or 0),
            "temperature_score": float(row.get("temperature_score") or 0),
            "geothermal_score": float(row.get("geothermal_score") or 0),
        }

        c = climate_rows.get(mid, {})
        feat["temperature"] = float(c.get("t2m") or 0)

        h = hydro_rows.get(mid, {})
        feat["elevation"] = float(h.get("mean_elevation_m") or 0)
        feat["slope"] = float(h.get("mean_slope_deg") or 0)

        features.append(feat)
        targets.append(cls)

    return features, targets


def train_model(features: list[dict[str, float]], targets: list[str]) -> dict[str, Any]:
    """Train a RandomForestClassifier and return feature importance."""
    try:
        from sklearn.ensemble import RandomForestClassifier
    except ImportError:
        logger.error("scikit-learn is not installed. Install it to use the ML extension.")
        return {"error": "scikit-learn not installed"}

    if not features or not targets:
        return {"error": "Insufficient training data"}

    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report

    X = pd.DataFrame(features)
    y = pd.Series(targets)

    # Fill missing values with column median
    X = X.fillna(X.median())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    importance = dict(zip(X.columns, clf.feature_importances_.tolist()))
    importance = {k: round(v, 4) for k, v in sorted(importance.items(), key=lambda x: x[1], reverse=True)}

    return {
        "accuracy": round(acc, 4),
        "feature_importance": importance,
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "classes": list(clf.classes_),
    }


def main() -> None:
    logger.info("Fetching training data...")
    features, targets = fetch_training_data()
    logger.info("Loaded %d samples.", len(features))

    result = train_model(features, targets)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
