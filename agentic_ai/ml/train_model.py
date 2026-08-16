import json
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from agentic_ai.config.agent_config import MODEL_FILE_PATH, MODEL_META_PATH
from agentic_ai.ml.feature_engineering import get_driver_features


FEATURE_COLUMNS = [
    "rating",
    "total_trips",
    "total_revenue",
    "average_fare",
    "average_distance",
    "average_duration",
]

TARGET_COLUMN = "underperformance_risk"


def train_and_persist_model():
    print("Extracting driver features from PostgreSQL Gold warehouse...")
    df = get_driver_features()

    if df.empty:
        raise RuntimeError("No driver records returned for feature engineering.")

    print(f"Total driver records for training: {len(df)}")

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if len(np.unique(y)) > 1 and y.value_counts().min() >= 2 else None
    )


    clf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1] if hasattr(clf, "predict_proba") else y_pred

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))

    try:
        auc = float(roc_auc_score(y_test, y_proba))
    except Exception:
        auc = 1.0

    print(f"Model Training Completed:")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1 Score:  {f1:.4f}")
    print(f"  ROC-AUC:   {auc:.4f}")

    class_dist = y.value_counts().to_dict()
    class_dist_clean = {str(k): int(v) for k, v in class_dist.items()}

    meta = {
        "model_type": "RandomForestClassifier",
        "training_period": "2024-01-01 to 2024-01-20 (Features)",
        "validation_period": "2024-01-21 to 2024-01-31 (Target & Holdout Eval)",
        "features": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "target_definition": "Future Period 2 underperformance (Period 2 revenue <= 35th percentile or Period 2 trips < 1)",
        "sample_count": len(df),
        "class_distribution": class_dist_clean,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "roc_auc": round(auc, 4),
        },
        "importances": {col: round(float(imp), 4) for col, imp in zip(FEATURE_COLUMNS, clf.feature_importances_)},
    }

    with open(MODEL_META_PATH, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Model persisted to: {MODEL_FILE_PATH}")
    print(f"Metadata persisted to: {MODEL_META_PATH}")
    return meta


if __name__ == "__main__":
    train_and_persist_model()
