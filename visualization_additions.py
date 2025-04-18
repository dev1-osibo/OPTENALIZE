# Add these imports to the top of your file
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import missingno as msno
from io import BytesIO

# Add this function to your code
def generate_data_visualizations(dataset):
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
            selected_num_col = st.selectbox("Select numeric column:", numeric_cols)
            
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
            selected_cat_col = st.selectbox("Select categorical column:", categorical_cols)
            
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
            selected_col = st.selectbox("Select column for outlier detection:", numeric_cols, key="outlier_col")
            
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
                with st.expander("View Outlier Values"):
                    st.write(outliers)
        else:
            st.info("No numeric columns available for outlier detection.")

# Add this to your Step 2: AI Analysis section
if st.session_state["current_step"] == 2:
    # After displaying quality dashboard and recommendations
    with st.expander("Explore Data Visualizations", expanded=True):
        generate_data_visualizations(dataset)

# Also add this to your Step 4: Review & Export section
elif st.session_state["current_step"] == 4:
    # After displaying quality improvement
    with st.expander("Data Visualizations"):
        st.write("### Before Cleaning")
        generate_data_visualizations(st.session_state["original_dataset"])
        
        st.write("### After Cleaning")
        generate_data_visualizations(st.session_state["cleaned_dataset"])