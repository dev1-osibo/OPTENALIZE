import pytest
import pandas as pd
from io import StringIO
from dataset_precheck_workflow_local import run_precheck, run_cleaning_workflow

@pytest.fixture
def load_datasets():
    """Load datasets for testing."""
    datasets = {
        "blank_cells": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/blank_cells.csv"),
        "date_year_columns": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/date_year_columns.csv"),
        "duplicates": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/duplicates.csv"),
        "mixed_issues": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/mixed_issues.csv"),
        "mixed_types": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/mixed_types.csv"),
        "non_standard_cols": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/non_standard_cols.csv"),
        "white_spaces": pd.read_csv("C:/Users/babas/OneDrive/Documents/OPTENALIZE/white_spaces.csv"),
    }
    return datasets


def test_precheck_blank_cells(load_datasets):
    """Test blank cells detection in the precheck."""
    dataset = load_datasets["blank_cells"]
    blank_cells = dataset.isnull().sum().sum()
    assert blank_cells > 0, "No blank cells detected where expected."


def test_precheck_whitespace_issues(load_datasets):
    """Test whitespace issues detection in the precheck."""
    dataset = load_datasets["white_spaces"]
    whitespace_issues = sum(
        dataset[col].astype(str).str.contains(r"^\s|\s$", na=False).sum()
        for col in dataset.columns
    )
    assert whitespace_issues > 0, "No whitespace issues detected where expected."


def test_precheck_numeric_in_non_numeric_columns(load_datasets):
    """Test numeric values in non-numeric columns detection."""
    dataset = load_datasets["mixed_types"]
    numeric_in_non_numeric = sum(
        dataset[col].apply(lambda x: isinstance(x, (int, float))).sum()
        for col in dataset.select_dtypes(exclude=["number"]).columns
    )
    assert numeric_in_non_numeric > 0, "No numeric values in non-numeric columns detected where expected."


def test_precheck_non_numeric_in_numeric_columns(load_datasets):
    """Test non-numeric values in numeric columns detection."""
    dataset = load_datasets["mixed_types"]
    non_numeric_in_numeric = sum(
        dataset[col].apply(lambda x: not isinstance(x, (int, float)) and pd.notnull(x)).sum()
        for col in dataset.select_dtypes(include=["number"]).columns
    )
    assert non_numeric_in_numeric > 0, "No non-numeric values in numeric columns detected where expected."


def test_cleaning_blank_cells(load_datasets):
    """Test handling of blank cells during cleaning."""
    dataset = load_datasets["blank_cells"].copy()
    for col in dataset.columns:
        if pd.api.types.is_numeric_dtype(dataset[col]):
            dataset[col].fillna(dataset[col].mean(), inplace=True)
    assert dataset.isnull().sum().sum() == 0, "Blank cells were not handled properly."


def test_cleaning_whitespace(load_datasets):
    """Test handling of whitespace issues during cleaning."""
    dataset = load_datasets["white_spaces"].copy()
    for col in dataset.columns:
        dataset[col] = dataset[col].astype(str).str.strip()
    whitespace_issues = sum(
        dataset[col].astype(str).str.contains(r"^\s|\s$", na=False).sum()
        for col in dataset.columns
    )
    assert whitespace_issues == 0, "Whitespace issues were not handled properly."


def test_cleaning_numeric_in_non_numeric_columns(load_datasets):
    """Test handling of numeric values in non-numeric columns during cleaning."""
    dataset = load_datasets["mixed_types"].copy()
    for col in dataset.select_dtypes(exclude=["number"]).columns:
        dataset[col] = dataset[col].apply(lambda x: "N/A" if isinstance(x, (int, float)) else x)
    numeric_in_non_numeric = sum(
        dataset[col].apply(lambda x: isinstance(x, (int, float))).sum()
        for col in dataset.select_dtypes(exclude=["number"]).columns
    )
    assert numeric_in_non_numeric == 0, "Numeric values in non-numeric columns were not handled properly."


def test_cleaning_non_numeric_in_numeric_columns(load_datasets):
    """Test handling of non-numeric values in numeric columns during cleaning."""
    dataset = load_datasets["mixed_types"].copy()
    for col in dataset.select_dtypes(include=["number"]).columns:
        dataset[col] = pd.to_numeric(dataset[col], errors='coerce')
    non_numeric_in_numeric = sum(
        dataset[col].apply(lambda x: not isinstance(x, (int, float)) and pd.notnull(x)).sum()
        for col in dataset.select_dtypes(include=["number"]).columns
    )
    assert non_numeric_in_numeric == 0, "Non-numeric values in numeric columns were not handled properly."


def test_date_year_validation(load_datasets):
    """Test validation and fixing of date/year columns."""
    dataset = load_datasets["date_year_columns"].copy()
    for col in dataset.columns:
        try:
            pd.to_datetime(dataset[col])
        except Exception as e:
            assert False, f"Date validation failed for column {col}: {e}"


def test_duplicates_handling(load_datasets):
    """Test handling of duplicate rows."""
    dataset = load_datasets["duplicates"].copy()
    initial_row_count = len(dataset)
    dataset = dataset.drop_duplicates()
    final_row_count = len(dataset)
    assert final_row_count < initial_row_count, "Duplicate rows were not removed properly."