import pandas as pd
import streamlit as st
from io import BytesIO
import random
from datetime import datetime

# Initialize session state management
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []
if "original_dataset" not in st.session_state:
    st.session_state["original_dataset"] = None

# Enhanced precheck function with data profiling
def run_precheck(dataset):
    """Comprehensive data quality assessment with statistical profiling"""
    st.subheader("Comprehensive Data Quality Assessment")
    
    # Initialize analysis containers
    analysis_results = {
        "Basic Statistics": pd.DataFrame(),
        "Quality Metrics": {},
        "Type Analysis": {}
    }

    # Calculate quality metrics
    quality_metrics = {
        "Blank Cells": dataset.isnull().sum().sum(),
        "Whitespace Issues": sum(
            dataset[col].astype(str).str.contains(r"^\s|\s$", na=False).sum()
            for col in dataset.columns
        ),
        "Type Inconsistencies": sum(
            len(dataset[col].apply(type).unique()) > 1
            for col in dataset.columns
        )
    }

    # Generate type analysis
    for col in dataset.columns:
        analysis_results["Type Analysis"][col] = {
            "DataType": str(dataset[col].dtype),
            "Unique Types": dataset[col].apply(type).unique(),
            "Null Percentage": f"{dataset[col].isnull().mean() * 100:.2f}%"
        }

    # Display results
    with st.expander("Basic Dataset Statistics"):
        st.write(dataset.describe(include='all'))

    
    with st.expander("Data Quality Report"):
        for metric, value in quality_metrics.items():
            st.metric(label=metric, value=value)
    
    with st.expander("Advanced Type Analysis"):
        st.json(analysis_results["Type Analysis"])

# Enhanced cleaning workflow with version control
def run_cleaning_workflow(dataset):
    """Interactive cleaning pipeline with audit tracking"""
    st.subheader("Smart Cleaning Workflow")
    
    # Cleaning action registry
    cleaning_actions = {
        "Handle Missing Values": False,
        "Clean Whitespace": False,
        "Fix Data Types": False,
        "Standardize Dates": False,
        "Remove Duplicates": False
    }

    # Dynamic UI layout
    cols = st.columns(len(cleaning_actions))
    for i, action in enumerate(cleaning_actions):
        cleaning_actions[action] = cols[i].checkbox(action)

    # Missing value handling
    if cleaning_actions["Handle Missing Values"]:
        handle_missing_values(dataset)

    # Whitespace cleaning
    if cleaning_actions["Clean Whitespace"]:
        clean_whitespace(dataset)

    # Data type standardization
    if cleaning_actions["Fix Data Types"]:
        standardize_data_types(dataset)

    # Date standardization
    if cleaning_actions["Standardize Dates"]:
        standardize_dates(dataset)

    # Deduplication
    if cleaning_actions["Remove Duplicates"]:
        remove_duplicates(dataset)

    # Version comparison tool
    with st.expander("Version Comparison"):
        if st.session_state["original_dataset"] is not None:
            col1, col2 = st.columns(2)
            with col1:
                st.write("Original Dataset Sample:")
                st.dataframe(st.session_state["original_dataset"].head(3))
            with col2:
                st.write("Current Dataset Sample:")
                st.dataframe(dataset.head(3))

    # Audit log display
    st.subheader("Audit Trail")
    st.table(pd.DataFrame(st.session_state["action_log"], columns=["Timestamp", "Action"]))

# Advanced missing value handler
def handle_missing_values(dataset):
    """Sophisticated null value treatment with multiple strategies"""
    st.subheader("Missing Value Imputation")
    
    strategy = st.radio("Select Imputation Method:", [
        "Advanced Random Imputation", 
        "ML-Based Imputation",
        "Forward/Backward Fill",
        "Custom Value"
    ])

    if strategy == "Advanced Random Imputation":
        for col in dataset.columns:
            if pd.api.types.is_numeric_dtype(dataset[col]):
                non_null = dataset[col].dropna()
                if len(non_null) > 0:
                    dataset[col] = dataset[col].apply(
                        lambda x: random.choice(non_null) if pd.isnull(x) else x
                    )
        log_action("Advanced random imputation applied")

    elif strategy == "ML-Based Imputation":
        try:
            from sklearn.experimental import enable_iterative_imputer
            from sklearn.impute import IterativeImputer
            imputer = IterativeImputer()
            numeric_cols = dataset.select_dtypes(include=np.number).columns
            dataset[numeric_cols] = imputer.fit_transform(dataset[numeric_cols])
            log_action("ML-based imputation performed")
        except ImportError:
            st.error("ML imputation requires scikit-learn")

    elif strategy == "Forward/Backward Fill":
        dataset.ffill(inplace=True)
        dataset.bfill(inplace=True)
        log_action("Forward/backward fill applied")

    elif strategy == "Custom Value":
        custom_values = {}
        for col in dataset.columns:
            custom = st.text_input(f"Custom value for {col}:")
            if custom:
                try:
                    dataset[col].fillna(type(dataset[col].iloc[0])(custom), inplace=True)
                except ValueError:
                    dataset[col].fillna(custom, inplace=True)
        log_action("Custom value imputation applied")

# Enhanced date standardization
def standardize_dates(dataset):
    """Flexible date parser with automatic format detection"""
    st.subheader("Date Standardization Engine")
    
    date_cols = [col for col in dataset.columns if "date" in col.lower()]
    if not date_cols:
        st.info("No date-related columns detected")
        return

    for col in date_cols:
        with st.expander(f"Processing: {col}"):
            original_sample = dataset[col].head(5).tolist()
            
            # Try multiple parsing strategies
            parsed = pd.to_datetime(dataset[col], errors='coerce', infer_datetime_format=True)
            if parsed.isna().any():
                parsed = pd.to_datetime(dataset[col], errors='coerce', dayfirst=True)
            
            success_rate = 1 - parsed.isna().mean()
            if success_rate > 0.9:
                dataset[col] = parsed
                log_action(f"Standardized {col} with {success_rate*100:.1f}% success")
            else:
                st.warning(f"Low parsing success ({success_rate*100:.1f}%) for {col}")
                custom_format = st.text_input(f"Enter custom format for {col}:")
                if custom_format:
                    try:
                        dataset[col] = pd.to_datetime(dataset[col], format=custom_format, errors='coerce')
                        log_action(f"Custom format {custom_format} applied to {col}")
                    except ValueError:
                        st.error("Invalid date format specification")

# Main application workflow
def main():
    st.title("Enterprise Data Health Center")
    
    # File upload with format detection
    uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "xlsx", "parquet"])
    if uploaded_file:
        file_type = uploaded_file.name.split('.')[-1].lower()
        try:
            if file_type == "csv":
                dataset = pd.read_csv(uploaded_file, low_memory=False)
            elif file_type == "xlsx":
                dataset = pd.read_excel(uploaded_file)
            elif file_type == "parquet":
                dataset = pd.read_parquet(uploaded_file)
            
            # Preserve original data
            if st.session_state["original_dataset"] is None:
                st.session_state["original_dataset"] = dataset.copy()
            
            # Interactive workflow
            run_precheck(dataset)
            run_cleaning_workflow(dataset)
            
            # Export functionality
            st.subheader("Data Export")
            export_format = st.selectbox("Export Format:", ["CSV", "Parquet", "Excel"])
            buffer = BytesIO()
            if export_format == "CSV":
                dataset.to_csv(buffer, index=False)
                st.download_button("Download CSV", buffer.getvalue(), "cleaned_data.csv")
            elif export_format == "Parquet":
                dataset.to_parquet(buffer)
                st.download_button("Download Parquet", buffer.getvalue(), "cleaned_data.parquet")
            elif export_format == "Excel":
                with pd.ExcelWriter(buffer) as writer:
                    dataset.to_excel(writer, index=False)
                st.download_button("Download Excel", buffer.getvalue(), "cleaned_data.xlsx")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

def log_action(message):
    """Audit logging with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["action_log"].append((timestamp, message))

if __name__ == "__main__":
    main()
