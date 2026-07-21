import os
from typing import Dict, Optional

import pandas as pd

from backend.file_handler import find_quota_file, find_survey_file, load_file


def load_project_survey(project_folder: str) -> pd.DataFrame:
    path = find_survey_file(project_folder)
    if path is None:
        raise FileNotFoundError("No survey file found in project folder.")
    return load_file(path)


def load_project_quota(project_folder: str) -> Optional[pd.DataFrame]:
    path = find_quota_file(project_folder)
    if path is None:
        return None
    return load_file(path)


def run_duplicate_id_check(df: pd.DataFrame, id_col: str) -> pd.DataFrame:
    if id_col not in df.columns:
        raise KeyError(f"Respondent ID column '{id_col}' was not found in the dataset.")
    return df[df.duplicated(subset=[id_col], keep=False)].copy()


def run_missing_values_check(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum().sort_values(ascending=False)


def run_speed_check(df: pd.DataFrame, duration_col: str, threshold_pct: float = 0.4) -> Dict[str, Optional[pd.DataFrame]]:
    if duration_col not in df.columns:
        raise KeyError(f"Duration column '{duration_col}' was not found in the dataset.")
    if not pd.api.types.is_numeric_dtype(df[duration_col]):
        raise TypeError(f"Duration column '{duration_col}' must be numeric.")

    median_duration = float(df[duration_col].median())
    threshold = median_duration * threshold_pct
    speeders = df[df[duration_col] < threshold].copy()

    return {
        "median_duration": median_duration,
        "threshold": threshold,
        "speeders": speeders,
    }


def run_quota_compliance(df: pd.DataFrame, quota: Optional[pd.DataFrame]) -> Dict[str, Optional[pd.DataFrame]]:
    if quota is None or quota.empty:
        return {"compliance_table": None, "message": "No quota file available for this project."}

    headers = [c.lower() for c in quota.columns]
    if len(headers) < 2:
        return {"compliance_table": quota, "message": "Quota template did not contain enough columns to evaluate compliance."}

    if quota.columns[0] in df.columns:
        group_col = quota.columns[0]
        target_col = quota.columns[1]
        if not pd.api.types.is_numeric_dtype(quota[target_col]):
            return {"compliance_table": quota, "message": "Quota target column must be numeric to compare against actual counts."}

        actual = df.groupby(group_col).size().rename("Actual").reset_index()
        expected = quota[[group_col, target_col]].rename(columns={target_col: "Target"})
        merged = expected.merge(actual, on=group_col, how="left")
        merged["Actual"] = merged["Actual"].fillna(0).astype(int)
        merged["Shortfall"] = merged["Target"] - merged["Actual"]
        merged["Status"] = merged.apply(
            lambda row: "OK" if row["Actual"] >= row["Target"] else "Under target",
            axis=1,
        )
        return {"compliance_table": merged, "message": "Quota compliance computed against project data."}

    return {
        "compliance_table": quota,
        "message": "Quota file loaded, but its first category column could not be matched against survey data columns.",
    }


def summarize_field(df: pd.DataFrame, column: str) -> Dict[str, Optional[pd.DataFrame]]:
    if column not in df.columns:
        raise KeyError(f"'{column}' is not a valid column in the dataset.")

    if pd.api.types.is_numeric_dtype(df[column]) and df[column].nunique() > 20:
        summary = df[column].describe().to_frame(name="Value")
        return {"summary": summary}

    values = df[column].value_counts(dropna=False).rename_axis(column).reset_index(name="Count")
    values["Percent"] = (values["Count"] / len(df) * 100).round(1).astype(str) + "%"
    return {"summary": values}


def build_project_overview(df: pd.DataFrame) -> Dict[str, Any]:
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": df.select_dtypes(include=["number"]).columns.tolist(),
        "text_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
    }
