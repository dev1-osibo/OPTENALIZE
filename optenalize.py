import streamlit as st
import pandas as pd

st.title("Optenalize")
st.write("Welcome to the Optenalize App!")

# Initialize session state
if "dataset" not in st.session_state:
    st.session_state["dataset"] = None

# File Upload Section
st.subheader("Upload Your Dataset")
uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or JSON):", type=["csv", "xlsx", "json"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        st.session_state["dataset"] = pd.read_csv(uploaded_file)
    elif file_type in ["xls", "xlsx"]:
        st.session_state["dataset"] = pd.read_excel(uploaded_file)
    elif file_type == "json":
        st.session_state["dataset"] = pd.read_json(uploaded_file)
    st.success("Dataset successfully uploaded!")

# Ensure feedback if no dataset is uploaded
if st.session_state["dataset"] is None:
    st.info("Please upload a dataset to start.")
else:
    # Call data cleaning workflow
    def data_cleaning_workflow():
        st.header("Data Cleaning")
        dataset = st.session_state["dataset"]

        # Missing Value Summary
        st.subheader("Missing Values Summary")
        with st.expander("Show Missing Values Summary"):
            missing_summary = dataset.isnull().sum().sort_values(ascending=False)
            missing_percentage = (missing_summary / len(dataset)) * 100
            st.write(pd.DataFrame({"Missing Values": missing_summary, "Percentage": missing_percentage}))

        # Handle Missing Values
        essential_columns = st.multiselect(
            "Select essential columns:",
            options=dataset.columns,
            default=[],
            help="Choose columns that are critical for your analysis."
        )

        # Handle Rows with Missing Values
        if essential_columns:
            missing_value_action = st.radio(
                "How to handle missing values in essential columns?",
                ["Impute with column mean", "Impute with random values", "Delete rows"]
            )
            if st.button("Apply Action"):
                if missing_value_action == "Impute with column mean":
                    dataset[essential_columns] = dataset[essential_columns].fillna(dataset[essential_columns].mean())
                    st.success("Missing values in essential columns were imputed with column means.")
                elif missing_value_action == "Impute with random values":
                    for col in essential_columns:
                        col_min, col_max = dataset[col].min(), dataset[col].max()
                        dataset[col] = dataset[col].apply(
                            lambda x: pd.Series([col_min, col_max]).sample(1).values[0] if pd.isnull(x) else x
                        )
                    st.success("Missing values in essential columns were imputed with random values.")
                elif missing_value_action == "Delete rows":
                    dataset = dataset.dropna(subset=essential_columns)
                    st.success("Rows with missing values in essential columns were deleted.")
                st.session_state["dataset"] = dataset

        # Standardize Column Names
        st.subheader("Standardize Column Names")
        if st.button("Standardize Columns"):
            dataset.columns = dataset.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("[^a-zA-Z0-9_]", "")
            st.session_state["dataset"] = dataset
            st.success("Column names standardized.")

        # Preview Cleaned Dataset
        st.subheader("Preview Cleaned Dataset")
        if st.checkbox("Show Cleaned Dataset"):
            st.dataframe(dataset.head())

        # Download Cleaned Dataset
        st.subheader("Download Cleaned Dataset")
        cleaned_data_csv = dataset.to_csv(index=False)
        st.download_button(
            label="Download Cleaned Dataset",
            data=cleaned_data_csv,
            file_name="cleaned_dataset.csv",
            mime="text/csv",
        )

    data_cleaning_workflow()