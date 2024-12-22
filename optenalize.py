import streamlit as st
import pandas as pd

# Initialize session state for goal selection
if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

# Goal Selection
st.title("Welcome to Optenalize")
st.subheader("What would you like to do today?")
selected_goal = st.selectbox(
    "Select your goal:",
    [
        "Clean the dataset",
        "Perform exploratory data analysis (EDA)",
        "Train a predictive model",
        "Perform general ML tasks",
        "Other (specify custom goal)"
    ]
)

# Store the selected goal in session state
st.session_state["selected_goal"] = selected_goal

# Display the selected goal
st.write(f"You selected: {st.session_state['selected_goal']}")

st.title("Optenalize: Data Cleaning and Forecasting")
st.write("Welcome to the Optenalize platform! Upload your dataset to get started.")

# File upload widget
uploaded_file = st.file_uploader("Upload your dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Show file name
    st.write(f"Uploaded file: {uploaded_file.name}")

    try:
        # Handle CSV and Excel files
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)

        # Display the data
        st.write("Here's a preview of your data:")
        st.dataframe(data.head())

    except Exception as e:
        st.error(f"Error loading file: {e}")

# Advanced Missing Value Handling
if uploaded_file:
    st.write("Data Cleaning Options:")

    # Select Essential Columns
    essential_columns = st.multiselect(
        "Select essential columns (rows with missing values here will be deleted):", 
        options=data.columns, 
        default=[],
        help="Choose columns that are critical for your analysis."
    )

    # Display missing value statistics
    st.write("Missing Values Summary:")
    missing_summary = data.isnull().sum() / len(data) * 100
    st.dataframe(missing_summary.rename("Missing (%)"))

    # Automatically handle missing values
    st.write("Automatically handling missing values:")
    missing_threshold = st.slider(
        "Drop columns with more than this % missing values", 0, 100, 50, 
        help="Columns exceeding this threshold will be dropped unless they are essential."
    )

    # Identify columns to drop
    cols_to_drop = missing_summary[missing_summary > missing_threshold].index
    cols_to_warn = [col for col in essential_columns if col in cols_to_drop]

    # Warn if essential columns exceed threshold
    if cols_to_warn:
        st.warning(f"The following essential columns exceed the threshold and will NOT be dropped: {cols_to_warn}")
        cols_to_drop = [col for col in cols_to_drop if col not in essential_columns]

    # Drop non-essential columns exceeding threshold
    data = data.drop(columns=cols_to_drop)
    st.success(f"Dropped columns: {list(cols_to_drop)}")

    # Handle rows with missing values in selected columns
    if essential_columns:
        data = data.dropna(subset=essential_columns)
        st.success("Dropped rows with missing values in essential columns.")

    # Impute remaining missing values
    data = data.fillna(data.mean(numeric_only=True))
    st.success("Imputed numeric missing values with column means.")

    # Display cleaned data
    st.write("Cleaned Data Preview:")
    st.dataframe(data.head())