import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO
import random
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import missingno as msno

# Initialize session state management
if "action_log" not in st.session_state:
    st.session_state["action_log"] = []
if "original_dataset" not in st.session_state:
    st.session_state["original_dataset"] = None
if "current_step" not in st.session_state:
    st.session_state["current_step"] = 1
if "data_quality_score" not in st.session_state:
    st.session_state["data_quality_score"] = 0
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = []

# Function to calculate data quality score
def calculate_quality_score(dataset):
    """Calculate a data quality score from 0-100"""
    metrics = {
        "missing_data": 1 - dataset.isnull().mean().mean(),
        "duplicate_rows": 1 - (dataset.duplicated().sum() / len(dataset) if len(dataset) > 0 else 0),
        "type_consistency": sum(len(dataset[col].apply(type).unique()) == 1 for col in dataset.columns) / len(dataset.columns) if len(dataset.columns) > 0 else 0
    }
    # Weighted average of metrics
    weights = {"missing_data": 0.4, "duplicate_rows": 0.3, "type_consistency": 0.3}
    score = sum(metrics[m] * weights[m] for m in metrics) * 100
    return round(score, 1)
    
# Utility: Detect likely year column 
def is_likely_year_column(col_name, series):
    """
    Heuristically determine if a column likely represents years (e.g., 1990, 2022).
    - Matches keywords in column name.
    - Checks for consistent 4-digit numeric values (with/without commas).
    """
    name_match = any(keyword in col_name.lower() for keyword in ["year", "date", "birth", "decade"])
    # Remove commas and check if most non-null entries are 4-digit numbers
    cleaned_series = series.dropna().astype(str).str.replace(",", "")
    numeric_format_match = cleaned_series.str.match(r"^\d{4}$").mean() > 0.6
    return name_match and numeric_format_match

# AI-powered issue detection and recommendations
def generate_ai_recommendations(dataset):
    """Generate intelligent recommendations based on dataset analysis"""
    recommendations = []
    
    # Check for missing values
    missing_cols = dataset.columns[dataset.isnull().any()].tolist()
    if missing_cols:
        missing_pct = dataset[missing_cols].isnull().mean()
        for col, pct in missing_pct.items():
            severity = "High" if pct > 0.3 else "Medium" if pct > 0.1 else "Low"
            
            # Recommend strategy based on data type
            if pd.api.types.is_numeric_dtype(dataset[col]) and not is_likely_year_column(col, dataset[col]):
                strategy = "mean"
                description = f"Fill missing values in '{col}' with column mean/median"
            else:
                strategy = "mode"
                description = f"Fill missing values in '{col}' with most common value"
                
            recommendations.append({
                "issue": "Missing Values",
                "column": col,
                "severity": severity,
                "description": description,
                "action": "fill_missing",
                "params": {"column": col, "strategy": strategy},
                "auto_fix": severity != "High"  # Auto-fix for low/medium severity
            })
    
    # Check for duplicate rows
    dup_count = dataset.duplicated().sum()
    if dup_count > 0:
        recommendations.append({
            "issue": "Duplicate Rows",
            "column": "multiple",
            "severity": "Medium" if dup_count / len(dataset) < 0.1 else "High",
            "description": f"Remove {dup_count} duplicate rows",
            "action": "remove_duplicates",
            "params": {},
            "auto_fix": True
        })
    
    # Check for inconsistent data types
    for col in dataset.columns:
        if len(dataset[col].apply(type).unique()) > 1:
            recommendations.append({
                "issue": "Type Inconsistency",
                "column": col,
                "severity": "Medium",
                "description": f"Standardize data types in '{col}'",
                "action": "fix_types",
                "params": {"column": col},
                "auto_fix": True
            })
    
    # Detect and standardize year-like columns
    if is_likely_year_column(col, dataset[col]):
        recommendations.append({
            "issue": "Year Format",
            "column": col,
            "severity": "Medium",
            "description": f"Standardize year format in '{col}'",
            "action": "standardize_year_format",
            "params": {"column": col},
            "auto_fix": True
        })
    
    # Check for date columns that need standardization
    date_cols = [col for col in dataset.columns if "date" in col.lower() or "time" in col.lower()]
    for col in date_cols:
        if dataset[col].dtype != 'datetime64[ns]':
            recommendations.append({
                "issue": "Date Format",
                "column": col,
                "severity": "Medium",
                "description": f"Standardize date format in '{col}'",
                "action": "standardize_dates",
                "params": {"column": col},
                "auto_fix": True
            })
    
    # Check for columns with high missing values
    high_missing_cols = [col for col in dataset.columns if dataset[col].isnull().mean() > 0.7]
    if high_missing_cols:
        recommendations.append({
            "issue": "High Missing Columns",
            "column": ", ".join(high_missing_cols),
            "severity": "High",
            "description": f"Remove columns with >70% missing values: {', '.join(high_missing_cols)}",
            "action": "remove_high_missing",
            "params": {"columns": high_missing_cols},
            "auto_fix": False  # Don't auto-fix as this removes data
        })
    
    # Check for whitespace issues
    whitespace_issues = False
    for col in dataset.select_dtypes(include=['object']).columns:
        if (dataset[col].astype(str).str.contains(r'^\s|\s$', regex=True).any()):
            whitespace_issues = True
            recommendations.append({
                "issue": "Whitespace",
                "column": col,
                "severity": "Low",
                "description": f"Clean leading/trailing whitespace in '{col}'",
                "action": "clean_whitespace",
                "params": {"column": col},
                "auto_fix": True
            })
    
    return recommendations

# Apply fixes based on recommendations
def apply_fixes(dataset, selected_recommendations):
    """Apply selected fixes to the dataset"""
    if not selected_recommendations:
        return dataset
    
    # Create a copy to avoid modifying the original
    df = dataset.copy()
    
    for rec in selected_recommendations:
        action = rec["action"]
        params = rec["params"]
        
        if action == "fill_missing":
            col = params["column"]
            strategy = params["strategy"]
            
            if strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].median(), inplace=True)
            elif strategy == "mode":
                mode_value = df[col].mode()[0] if not df[col].mode().empty else "Missing"
                df[col].fillna(mode_value, inplace=True)
            
            log_action(f"Filled missing values in '{col}' using {strategy}")
            
        elif action == "remove_duplicates":
            before_count = len(df)
            df.drop_duplicates(inplace=True)
            after_count = len(df)
            log_action(f"Removed {before_count - after_count} duplicate rows")
            
        elif action == "fix_types":
            col = params["column"]
            # Try to convert to numeric if possible
            try:
                if df[col].dtype == 'object':
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    log_action(f"Converted '{col}' to numeric type")
            except:
                pass
                
        elif action == "standardize_dates":
            col = params["column"]
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                df[col] = df[col].dt.strftime("%Y-%m-%d")
                log_action(f"Standardized dates in '{col}'")
            except:
                pass
        
        elif action == "standardize_year_format":
            col = params["column"]
            df[col] = pd.to_datetime(df[col].astype(str).str.replace(",", ""), errors='coerce').dt.year
            log_action(f"Standardized year format in '{col}'")

                
        elif action == "remove_high_missing":
            columns = params["columns"]
            df.drop(columns=columns, inplace=True)
            log_action(f"Removed columns with high missing values: {', '.join(columns)}")
            
        elif action == "clean_whitespace":
            col = params["column"]
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                log_action(f"Cleaned whitespace in '{col}'")
    
    # Update quality score
    st.session_state["data_quality_score"] = calculate_quality_score(df)
    
    return df

# Log actions for audit trail
def log_action(message):
    """Audit logging with timestamps"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["action_log"].append((timestamp, message))

# Display data quality dashboard
def display_quality_dashboard(dataset, recommendations):
    """Display visual data quality metrics"""
    st.subheader("Data Quality Dashboard")
    
    # Calculate quality score if not already done
    if st.session_state["data_quality_score"] == 0:
        st.session_state["data_quality_score"] = calculate_quality_score(dataset)
    
    score = st.session_state["data_quality_score"]
    
    if score is None:
        score = calculate_quality_score(dataset)
        st.session_state["data_quality_score"] = score
      
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    # Display quality score gauge
    with col1:
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Quality Score"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': get_score_color(score)},
                'steps': [
                    {'range': [0, 50], 'color': "lightcoral"},
                    {'range': [50, 80], 'color': "lightyellow"},
                    {'range': [80, 100], 'color': "lightgreen"}
                ]
            }
        ))
        fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)
    
    # Display issue counts by severity
    with col2:
        severity_counts = {"High": 0, "Medium": 0, "Low": 0}
        for rec in recommendations:
            severity_counts[rec["severity"]] += 1
        
        st.metric("High Severity Issues", severity_counts["High"], 
                 delta=None, delta_color="inverse")
        st.metric("Medium Severity Issues", severity_counts["Medium"], 
                 delta=None, delta_color="inverse")
        st.metric("Low Severity Issues", severity_counts["Low"], 
                 delta=None, delta_color="inverse")
    
    # Display dataset stats
    with col3:
        st.metric("Rows", dataset.shape[0])
        st.metric("Columns", dataset.shape[1])
        st.metric("Missing Cells", dataset.isnull().sum().sum())

# Get color based on score
def get_score_color(score):
    if score is None:
        return "gray"
    elif score >= 80:
        return "green"
    elif score >= 50:
        return "orange"
    else:
        return "red"

# Generate comprehensive data visualizations
def generate_data_visualizations(dataset, key_suffix="default"):
    """Generate comprehensive data visualizations for analysis"""
    st.subheader("Data Visualizations")
    
    # Create tabs for different visualization types
    viz_tabs = st.tabs(["Distributions", "Correlations", "Missing Values", "Outliers"])
    
    # Tab 1: Distributions
    with viz_tabs[0]:
        st.write("### Column Distributions")
        
        # Select columns for visualization
        numeric_cols = dataset.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = dataset.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if numeric_cols:
            # Let user select a numeric column
            selected_num_col = st.selectbox("Select numeric column:", numeric_cols, key=f"selectbox_numeric_{key_suffix}")
            
            # Create distribution plot with Plotly
            fig = make_subplots(rows=2, cols=1, 
                               subplot_titles=("Distribution", "Box Plot"),
                               vertical_spacing=0.2)
            
            # Histogram
            fig.add_trace(
                go.Histogram(x=dataset[selected_num_col].dropna(), 
                            name="Distribution",
                            marker_color='rgba(56, 108, 176, 0.7)'),
                row=1, col=1
            )
            
            # Box plot
            fig.add_trace(
                go.Box(x=dataset[selected_num_col].dropna(), 
                      name="Box Plot",
                      marker_color='rgba(56, 108, 176, 0.7)'),
                row=2, col=1
            )
            
            fig.update_layout(height=500, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            stats = dataset[selected_num_col].describe()
            st.write("Statistics:")
            st.write(stats)
        
        if categorical_cols:
            # Let user select a categorical column
            selected_cat_col = st.selectbox("Select categorical column:", categorical_cols, key=f"selectbox_categorical_{key_suffix}")
            
            # Create bar chart for categorical data
            value_counts = dataset[selected_cat_col].value_counts().reset_index()
            value_counts.columns = [selected_cat_col, 'Count']
            
            # Limit to top 20 categories if there are too many
            if len(value_counts) > 20:
                value_counts = value_counts.head(20)
                title = f"Top 20 values in {selected_cat_col}"
            else:
                title = f"Values in {selected_cat_col}"
            
            fig = px.bar(value_counts, x=selected_cat_col, y='Count', 
                        title=title,
                        color_discrete_sequence=['rgba(56, 108, 176, 0.7)'])
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Correlations
    with viz_tabs[1]:
        st.write("### Correlation Analysis")
        
        if len(numeric_cols) > 1:
            # Create correlation matrix
            corr_matrix = dataset[numeric_cols].corr()
            
            # Create heatmap
            fig = px.imshow(corr_matrix, 
                           text_auto=True, 
                           color_continuous_scale='RdBu_r',
                           title="Correlation Matrix")
            
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
            
            # Show strongest correlations
            st.write("### Strongest Correlations")
            
            # Get upper triangle of correlation matrix
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            
            # Find strongest correlations
            strongest_corr = upper.unstack().sort_values(ascending=False).dropna()
            strongest_corr = strongest_corr[strongest_corr != 1.0]  # Remove self-correlations
            
            if not strongest_corr.empty:
                strongest_df = pd.DataFrame(strongest_corr).reset_index()
                strongest_df.columns = ['Feature 1', 'Feature 2', 'Correlation']
                st.write(strongest_df.head(10))
                
                # Scatter plot of top correlation
                if len(strongest_df) > 0:
                    col1, col2 = strongest_df.iloc[0, 0], strongest_df.iloc[0, 1]
                    fig = px.scatter(dataset, x=col1, y=col2, 
                                    title=f"Scatter Plot: {col1} vs {col2}",
                                    opacity=0.6)
                    
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No correlations found in the dataset.")
        else:
            st.info("Need at least two numeric columns to calculate correlations.")
    
    # Tab 3: Missing Values
    with viz_tabs[2]:
        st.write("### Missing Value Analysis")
        
        # Calculate missing values percentage
        missing_percent = (dataset.isnull().sum() / len(dataset)) * 100
        missing_percent = missing_percent[missing_percent > 0].sort_values(ascending=False)
        
        if not missing_percent.empty:
            # Create bar chart of missing values
            missing_df = pd.DataFrame({'Column': missing_percent.index, 
                                      'Missing %': missing_percent.values})
            
            fig = px.bar(missing_df, x='Column', y='Missing %',
                        title="Missing Values by Column",
                        color='Missing %',
                        color_continuous_scale='Reds')
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Missing value patterns
            st.write("### Missing Value Patterns")
            
            # Use matplotlib for missing value patterns
            plt.figure(figsize=(10, 6))
            msno_matrix = msno.matrix(dataset.sample(min(1000, len(dataset))))
            
            # Save the figure to a BytesIO object
            buf = BytesIO()
            plt.savefig(buf, format="png")
            buf.seek(0)
            
            # Display the image
            st.image(buf)
        else:
            st.success("No missing values in the dataset!")
    
    # Tab 4: Outliers
    with viz_tabs[3]:
        st.write("### Outlier Detection")
        
        if numeric_cols:
            # Let user select a column
            selected_col = st.selectbox(
                "Select column for outlier detection:",
                numeric_cols,
                key=f"outlier_col_{key_suffix}"
            )           
# Calculate IQR
            Q1 = dataset[selected_col].quantile(0.25)
            Q3 = dataset[selected_col].quantile(0.75)
            IQR = Q3 - Q1
            
            # Define outliers
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = dataset[(dataset[selected_col] < lower_bound) | 
                              (dataset[selected_col] > upper_bound)][selected_col]
            
            # Create box plot with outliers highlighted
            fig = go.Figure()
            
            # Add box plot
            fig.add_trace(go.Box(
                y=dataset[selected_col],
                name=selected_col,
                boxpoints='outliers',
                marker_color='rgba(56, 108, 176, 0.7)',
                line_color='rgba(56, 108, 176, 0.7)'
            ))
            
            fig.update_layout(
                title=f"Box Plot with Outliers: {selected_col}",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display outlier statistics
            st.write(f"### Outlier Statistics for {selected_col}")
            
            outlier_stats = {
                "Total Values": len(dataset[selected_col]),
                "Number of Outliers": len(outliers),
                "Percentage of Outliers": f"{(len(outliers) / len(dataset[selected_col]) * 100):.2f}%",
                "Lower Bound": lower_bound,
                "Upper Bound": upper_bound,
                "Min Value": dataset[selected_col].min(),
                "Max Value": dataset[selected_col].max()
            }
            
            # Display as two columns
            col1, col2 = st.columns(2)
            for i, (key, value) in enumerate(outlier_stats.items()):
                if i < len(outlier_stats) // 2 + len(outlier_stats) % 2:
                    col1.metric(key, value)
                else:
                    col2.metric(key, value)
            
            # Show outlier values
            if len(outliers) > 0:
                if st.checkbox("Show Outlier Values", key=f"show_outliers_{key_suffix}"):
                    st.write(outliers)
        else:
            st.info("No numeric columns available for outlier detection.")

# Main application with wizard interface
def main():
    st.set_page_config(page_title="Smart Data Health Center", layout="wide")
    
    # Application header
    st.title("🧹 Smart Data Health Center")
    st.markdown("*AI-powered data cleaning made simple*")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Navigation")
        steps = [
            "1. Upload Data",
            "2. AI Analysis",
            "3. Clean Data",
            "4. Review & Export"
        ]
        
        # Display steps with highlighting for current step
        for i, step in enumerate(steps, 1):
            if i == st.session_state["current_step"]:
                st.markdown(f"**→ {step}**")
            else:
                st.markdown(f"  {step}")
        
        # Help section
        with st.expander("ℹ️ Help & Tips"):
            st.markdown("""
            **Quick Tips:**
            - Upload CSV, Excel, or Parquet files
            - Let AI analyze your data quality
            - Apply recommended fixes with one click
            - Review changes before exporting
            
            **Need more help?** Check the documentation link below.
            """)
            st.link_button("Documentation", "https://example.com/docs")
    
    # Main content area - Step 1: Upload Data
    if st.session_state["current_step"] == 1:
        st.header("Step 1: Upload Your Dataset")
        
        # File upload with format detection
        uploaded_file = st.file_uploader("Upload Dataset", type=["csv", "xlsx", "parquet"])
        
        if uploaded_file:
            try:
                # Load the dataset based on file type
                file_type = uploaded_file.name.split('.')[-1].lower()
                
                with st.spinner("Loading dataset..."):
                    if file_type == "csv":
                        dataset = pd.read_csv(uploaded_file, low_memory=False)
                    elif file_type == "xlsx":
                        dataset = pd.read_excel(uploaded_file)
                    elif file_type == "parquet":
                        dataset = pd.read_parquet(uploaded_file)
                
                # Store the original dataset
                st.session_state["original_dataset"] = dataset.copy()
                
                # Display dataset preview
                st.subheader("Dataset Preview")
                st.dataframe(dataset.head(5))
                
                # Display basic stats
                st.subheader("Dataset Summary")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Rows", dataset.shape[0])
                    st.metric("Columns", dataset.shape[1])
                with col2:
                    st.metric("Missing Values", dataset.isnull().sum().sum())
                    st.metric("Duplicate Rows", dataset.duplicated().sum())
                
                # Continue button
                if st.button("Continue to Analysis →"):
                    st.session_state["current_step"] = 2
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    # Step 2: AI Analysis
    elif st.session_state["current_step"] == 2:
        st.header("Step 2: AI Data Analysis")
        
        if st.session_state["original_dataset"] is not None:
            dataset = st.session_state["original_dataset"].copy()
            
            # Generate AI recommendations
            with st.spinner("AI is analyzing your dataset..."):
                recommendations = generate_ai_recommendations(dataset)
                st.session_state["recommendations"] = recommendations
                st.session_state["data_quality_score"] = calculate_quality_score(dataset)
            
            # Display quality dashboard
            display_quality_dashboard(dataset, recommendations)
            
            # Display recommendations
            st.subheader("AI-Recommended Cleaning Actions")
            
            if not recommendations:
                st.success("Great news! Your dataset looks clean. No issues detected.")
            else:
                for i, rec in enumerate(recommendations):
                    severity_color = {
                        "High": "🔴", 
                        "Medium": "🟠",
                        "Low": "🟡"
                    }
                    
                    st.markdown(f"{severity_color[rec['severity']]} **{rec['issue']}**: {rec['description']}")
            
            # Add data visualizations
                generate_data_visualizations(dataset)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Upload"):
                    st.session_state["current_step"] = 1
                    st.rerun()
            with col2:
                if st.button("Continue to Cleaning →"):
                    st.session_state["current_step"] = 3
                    st.rerun()
        else:
            st.warning("Please upload a dataset first.")
            if st.button("Go to Upload"):
                st.session_state["current_step"] = 1
                st.rerun()
    
    # Step 3: Clean Data
    elif st.session_state["current_step"] == 3:
        st.header("Step 3: Clean Your Data")
        
        if st.session_state["original_dataset"] is not None:
            dataset = st.session_state["original_dataset"].copy()
            recommendations = st.session_state["recommendations"]
            
            if not recommendations:
                st.success("Your dataset is already clean! No cleaning actions needed.")
            else:
                # Display cleaning options
                st.subheader("Select Cleaning Actions")
                
                # Group recommendations by issue type
                issue_types = {}
                for rec in recommendations:
                    if rec["issue"] not in issue_types:
                        issue_types[rec["issue"]] = []
                    issue_types[rec["issue"]].append(rec)
                
                # Create tabs for different issue types
                tabs = st.tabs(list(issue_types.keys()))
                
                # Track selected recommendations
                selected_recs = []
                
                for i, (issue, recs) in enumerate(issue_types.items()):
                    with tabs[i]:
                        for rec in recs:
                            selected = st.checkbox(
                                f"{rec['description']} ({rec['severity']})", 
                                value=rec["auto_fix"]
                            )
                            if selected:
                                selected_recs.append(rec)
                
                # One-click cleaning options
                st.subheader("Cleaning Options")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Smart Clean (Apply Selected)"):
                        with st.spinner("Applying intelligent fixes..."):
                            cleaned_dataset = apply_fixes(dataset, selected_recs)
                            st.session_state["cleaned_dataset"] = cleaned_dataset
                            st.success("Cleaning completed successfully!")
                            
                            # Show before/after comparison
                            st.subheader("Before vs After")
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("Original Dataset (First 3 rows)")
                                st.dataframe(dataset.head(3))
                            with col2:
                                st.write("Cleaned Dataset (First 3 rows)")
                                st.dataframe(cleaned_dataset.head(3))
                
                with col2:
                    if st.button("Select All Recommended"):
                        # This would need to be implemented with session state in a real app
                        st.info("In a real app, this would select all recommended fixes")
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Analysis"):
                    st.session_state["current_step"] = 2
                    st.rerun()
            with col2:
                if st.button("Continue to Export →"):
                    st.session_state["current_step"] = 4
                    st.rerun()
        else:
            st.warning("Please upload a dataset first.")
            if st.button("Go to Upload"):
                st.session_state["current_step"] = 1
                st.rerun()
    
    # Step 4: Review & Export
    elif st.session_state["current_step"] == 4:
        st.header("Step 4: Review & Export")
        
        if "cleaned_dataset" in st.session_state:
            cleaned_dataset = st.session_state["cleaned_dataset"]
            original_dataset = st.session_state["original_dataset"]
            
            # Display quality improvement
            original_score = calculate_quality_score(original_dataset)
            new_score = calculate_quality_score(cleaned_dataset)
            
            st.subheader("Data Quality Improvement")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Original Quality Score", f"{original_score}%")
            
            with col2:
                st.metric("New Quality Score", f"{new_score}%", 
                         delta=f"{new_score - original_score:.1f}%")
            
            with col3:
                st.metric("Improvement", f"{(new_score - original_score):.1f}%")
            
            # Display dataset stats comparison
            st.subheader("Dataset Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Original Dataset")
                st.metric("Rows", original_dataset.shape[0])
                st.metric("Columns", original_dataset.shape[1])
                st.metric("Missing Values", original_dataset.isnull().sum().sum())
                st.metric("Duplicate Rows", original_dataset.duplicated().sum())
            
            with col2:
                st.write("Cleaned Dataset")
                st.metric("Rows", cleaned_dataset.shape[0])
                st.metric("Columns", cleaned_dataset.shape[1])
                st.metric("Missing Values", cleaned_dataset.isnull().sum().sum())
                st.metric("Duplicate Rows", cleaned_dataset.duplicated().sum())
            
            # Audit log
            with st.expander("View Audit Log"):
                if st.session_state["action_log"]:
                    log_df = pd.DataFrame(st.session_state["action_log"], 
                                         columns=["Timestamp", "Action"])
                    st.dataframe(log_df)
                else:
                    st.info("No actions have been logged yet.")
            
            # Data visualizations
            with st.expander("Data Visualizations"):
                st.write("### Before Cleaning")
                generate_data_visualizations(st.session_state["original_dataset"], key_suffix="original")
                
                st.write("### After Cleaning")
                generate_data_visualizations(st.session_state["cleaned_dataset"], key_suffix="cleaned")
            
            # Export options
            st.subheader("Export Options")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export to CSV
                csv_buffer = BytesIO()
                cleaned_dataset.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name="cleaned_data.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export to Excel
                excel_buffer = BytesIO()
                cleaned_dataset.to_excel(excel_buffer, index=False)
                excel_data = excel_buffer.getvalue()
                
                st.download_button(
                    label="Download as Excel",
                    data=excel_data,
                    file_name="cleaned_data.xlsx",
                    mime="application/vnd.ms-excel"
                )
            
            with col3:
                # Export cleaning report
                st.button("Generate Cleaning Report", disabled=True)
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back to Cleaning"):
                    st.session_state["current_step"] = 3
                    st.rerun()
            with col2:
                if st.button("Start New Project"):
                    # Reset session state
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.session_state["action_log"] = []
                    st.session_state["current_step"] = 1
                    st.rerun()
        else:
            if "original_dataset" in st.session_state:
                st.warning("Please complete the cleaning step first.")
                if st.button("Go to Cleaning"):
                    st.session_state["current_step"] = 3
                    st.rerun()
            else:
                st.warning("Please upload a dataset first.")
                if st.button("Go to Upload"):
                    st.session_state["current_step"] = 1
                    st.rerun()

if __name__ == "__main__":
    main()

# Print a message to show the code is ready to run
print("Smart Data Health Center code is ready to run with Streamlit!")
print("Run this with: streamlit run smart_data_health_center.py")