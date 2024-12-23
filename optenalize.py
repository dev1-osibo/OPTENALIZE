import streamlit as st
import pandas as pd

# Define data cleaning workflow
def data_cleaning_workflow():
    """Implements the data cleaning workflow."""
    st.header("Data Cleaning")

    # Load dataset from session state
    if "dataset" not in st.session_state or st.session_state["dataset"] is None:
        st.warning("Please upload a dataset to start cleaning.")
        return
    
    dataset = st.session_state["dataset"]

    # Missing Value Summary
    st.subheader("Missing Values Summary")
    with st.expander("Show Missing Values Summary"):
        missing_summary = dataset.isnull().sum().sort_values(ascending=False)
        missing_percentage = (missing_summary / len(dataset)) * 100
        st.write(pd.DataFrame({"Missing Values": missing_summary, "Percentage": missing_percentage}))

    # Handle Missing Values
    st.subheader("Advanced Missing Value Handling")

    # Select Essential Columns
    essential_columns = st.multiselect(
        "Select essential columns:",
        options=dataset.columns,
        default=[],
        help="Choose columns that are critical for your analysis."
    )

    if essential_columns:
        st.write("How would you like to handle rows with missing values in these columns?")
        missing_value_action = st.radio(
            "Choose an action:",
            options=["Impute with column mean", "Impute with random values", "Delete rows"],
        )

        if st.button("Apply Action"):
            if missing_value_action == "Impute with column mean":
                dataset[essential_columns] = dataset[essential_columns].fillna(dataset[essential_columns].mean())
                st.success("Missing values in essential columns were imputed with column means.")
            elif missing_value_action == "Impute with random values":
                for col in essential_columns:
                    dataset[col] = dataset[col].apply(
                        lambda x: pd.Series([x]).dropna().sample(1).values[0] if pd.isnull(x) else x
                    )
                st.success("Missing values in essential columns were imputed with random values.")
            elif missing_value_action == "Delete rows":
                dataset = dataset.dropna(subset=essential_columns)
                st.success("Rows with missing values in essential columns were deleted.")

            st.session_state["dataset"] = dataset  # Update in session state

    # Drop Columns with High Missing Values
    st.subheader("Drop Columns with High Missing Values")
    missing_threshold = st.radio(
        "Select a threshold for dropping columns:",
        options=[10, 25, 50, 75, 100],
        index=2,
        format_func=lambda x: f"More than {x}% missing values",
    )

    if st.button("Apply Missing Value Threshold"):
        cols_to_drop = missing_percentage[missing_percentage > missing_threshold].index
        cols_to_warn = [col for col in essential_columns if col in cols_to_drop]

        if cols_to_warn:
            st.warning(f"The following essential columns exceed the threshold and will NOT be dropped: {cols_to_warn}")
            cols_to_drop = [col for col in cols_to_drop if col not in essential_columns]

        dataset = dataset.drop(columns=cols_to_drop)
        st.session_state["dataset"] = dataset  # Update in session state

        # Feedback
        if len(cols_to_drop) > 0:
            st.success(f"{len(cols_to_drop)} columns were dropped based on the threshold.")
            if st.checkbox("Show list of dropped columns"):
                st.write(list(cols_to_drop))
        else:
            st.info("No columns were dropped based on the threshold.")

# Drop Columns with High Missing Values
st.subheader("Drop Columns with High Missing Values")
missing_threshold = st.number_input(
    "Set a percentage threshold for dropping columns with missing values:",
    min_value=0,
    max_value=100,
    value=50,
    step=5,
    help="Columns with missing values above this percentage will be dropped."
)

if st.button("Apply Missing Value Threshold"):
    cols_to_drop = missing_percentage[missing_percentage > missing_threshold].index
    cols_to_warn = [col for col in essential_columns if col in cols_to_drop]

    if cols_to_warn:
        st.warning(f"The following essential columns exceed the threshold and will NOT be dropped: {cols_to_warn}")
        cols_to_drop = [col for col in cols_to_drop if col not in essential_columns]

    dataset = dataset.drop(columns=cols_to_drop)
    st.session_state["dataset"] = dataset  # Update in session state

    # Feedback
    if len(cols_to_drop) > 0:
        st.success(f"{len(cols_to_drop)} columns were dropped based on the threshold.")
        with st.expander("View list of dropped columns"):
            st.write(list(cols_to_drop))
    else:
        st.info("No columns were dropped based on the threshold.")

    # Impute Remaining Missing Values
    numeric_cols_with_na = dataset.select_dtypes(include=["number"]).isnull().sum()
    numeric_cols_to_impute = numeric_cols_with_na[numeric_cols_with_na > 0].index

    if len(numeric_cols_to_impute) > 0:
        dataset[numeric_cols_to_impute] = dataset[numeric_cols_to_impute].fillna(dataset[numeric_cols_to_impute].mean())
        st.session_state["dataset"] = dataset  # Update in session state
        st.success(f"Imputed missing values in {len(numeric_cols_to_impute)} numeric columns with column means.")
    else:
        st.info("No numeric columns required imputation.")


# Impute Remaining Missing Values
st.subheader("Impute Missing Values in Numeric Columns")
imputation_strategy = st.radio(
    "Choose an imputation strategy:",
    options=["Column mean", "Random values within column range"],
    help="Select how missing values should be handled for numeric columns."
)

if st.button("Apply Imputation Strategy"):
    numeric_cols_with_na = dataset.select_dtypes(include=["number"]).isnull().sum()
    numeric_cols_to_impute = numeric_cols_with_na[numeric_cols_with_na > 0].index

    if len(numeric_cols_to_impute) > 0:
        if imputation_strategy == "Column mean":
            dataset[numeric_cols_to_impute] = dataset[numeric_cols_to_impute].fillna(dataset[numeric_cols_to_impute].mean())
            st.success(f"Imputed missing values in {len(numeric_cols_to_impute)} numeric columns with column means.")
        elif imputation_strategy == "Random values within column range":
            for col in numeric_cols_to_impute:
                col_min, col_max = dataset[col].min(), dataset[col].max()
                dataset[col] = dataset[col].apply(
                    lambda x: pd.Series([x]).dropna().sample(1).values[0]
                    if pd.isnull(x) else x
                )
            st.success(f"Imputed missing values in {len(numeric_cols_to_impute)} numeric columns with random values.")
        
        st.session_state["dataset"] = dataset  # Update in session state
    else:
        st.info("No numeric columns required imputation.")

    
    # Handle Duplicates
    st.subheader("Handle Duplicates")
    if st.button("Remove Duplicates"):
        before = len(dataset)
        dataset = dataset.drop_duplicates()
        st.session_state["dataset"] = dataset
        after = len(dataset)
        st.success(f"Removed {before - after} duplicate rows.")

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

    # Download the Cleaned Dataset
    st.subheader("Download Cleaned Dataset")
    cleaned_data_csv = dataset.to_csv(index=False)
    st.download_button(
        label="Download Cleaned Dataset",
        data=cleaned_data_csv,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
    )


# Centralized App Heading
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 20px;">
        <h1>Welcome to Optenalize</h1>
        <h3>Your One-Stop Tool for Data Cleaning, Forecasting, and Machine Learning Insights</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "selected_goal" not in st.session_state:
    st.session_state["selected_goal"] = None

# Goal Selection
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
st.session_state["selected_goal"] = selected_goal

# File Upload Section
st.subheader("Step 1: Upload Your Dataset")
uploaded_file = st.file_uploader("Upload your file (CSV, Excel, or JSON):", type=["csv", "xlsx", "json"])

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "csv":
        st.session_state["dataset"] = pd.read_csv(uploaded_file)
    elif file_type in ["xls", "xlsx"]:
        st.session_state["dataset"] = pd.read_excel(uploaded_file)
    elif file_type == "json":
        st.session_state["dataset"] = pd.read_json(uploaded_file)

    if st.checkbox("Preview the dataset"):
        st.dataframe(st.session_state["dataset"].head())

# Branch into workflows
if st.session_state["selected_goal"] == "Clean the dataset":
    data_cleaning_workflow()
elif st.session_state["selected_goal"] == "Perform exploratory data analysis (EDA)":
    st.info("EDA workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Train a predictive model":
    st.info("Predictive modeling workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Perform general ML tasks":
    st.info("General ML workflow will be implemented next.")
elif st.session_state["selected_goal"] == "Other (specify custom goal)":
    st.info("Custom workflow will be implemented next.")