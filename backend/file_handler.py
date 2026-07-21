import os
from typing import Optional
import pandas as pd

SUPPORTED_SURVEY_EXT = (".csv", ".xlsx", ".xls")


def load_file(uploaded_file):
    if hasattr(uploaded_file, "read") and hasattr(uploaded_file, "name"):
        file_name = uploaded_file.name
        if file_name.lower().endswith(".csv"):
            return pd.read_csv(uploaded_file)
        return pd.read_excel(uploaded_file)

    if isinstance(uploaded_file, (str, os.PathLike)):
        uploaded_file = str(uploaded_file)
        if uploaded_file.lower().endswith(".csv"):
            return pd.read_csv(uploaded_file)
        return pd.read_excel(uploaded_file)

    raise ValueError("Unsupported upload type for file loading.")


def find_survey_file(project_folder: str) -> Optional[str]:
    if not os.path.isdir(project_folder):
        return None

    for file_name in sorted(os.listdir(project_folder)):
        if "quota" in file_name.lower():
            continue
        if file_name.lower().endswith(SUPPORTED_SURVEY_EXT):
            return os.path.join(project_folder, file_name)

    return None


def find_quota_file(project_folder: str) -> Optional[str]:
    if not os.path.isdir(project_folder):
        return None

    for file_name in sorted(os.listdir(project_folder)):
        if "quota" in file_name.lower() and file_name.lower().endswith(SUPPORTED_SURVEY_EXT):
            return os.path.join(project_folder, file_name)

    return None


def load_project_survey(project_folder: str):
    path = find_survey_file(project_folder)
    if path is None:
        raise FileNotFoundError("No survey data file found in project folder.")
    return load_file(path)


def load_project_quota(project_folder: str):
    path = find_quota_file(project_folder)
    if path is None:
        return None
    return load_file(path)
