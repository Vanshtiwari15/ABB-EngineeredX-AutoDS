"""
Data Upload and Analysis page
"""

import streamlit as st
import pandas as pd
import io
import requests
import json
from typing import Optional


def show_data_upload():
    """Display data upload and analysis page"""
    
    st.header("📊 Data Upload & Analysis")
    
    st.markdown("""
    Upload your dataset to get started. Supported formats: **CSV**, **Excel (XLSX)**, **Parquet**
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Dataset")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["csv", "xlsx", "parquet"],
            help="Select your dataset file"
        )
        
        target_column = st.text_input(
            "Target Column Name (optional)",
            help="Name of the column to predict (for supervised learning)"
        )
        
        if uploaded_file is not None:
            st.success(f"✓ File uploaded: {uploaded_file.name}")
            
            # Try to read and display data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.parquet'):
                    df = pd.read_parquet(uploaded_file)
                
                st.markdown(f"**File Preview** (First 5 rows)")
                st.dataframe(df.head(), use_container_width=True)
                
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
    
    with col2:
        st.subheader("Dataset Information")
        
        if uploaded_file is not None:
            try:
                # Read file
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.parquet'):
                    df = pd.read_parquet(uploaded_file)
                
                # Display statistics
                col1_stat, col2_stat = st.columns(2)
                with col1_stat:
                    st.metric("Samples", len(df))
                    st.metric("Memory (MB)", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f}")
                
                with col2_stat:
                    st.metric("Features", len(df.columns))
                    numeric_cols = len(df.select_dtypes(include=['number']).columns)
                    st.metric("Numeric Features", numeric_cols)
                
                # Data types
                st.markdown("**Data Types**")
                dtype_counts = df.dtypes.value_counts()
                for dtype, count in dtype_counts.items():
                    st.write(f"- {str(dtype)}: {count} columns")
                
                # Missing values
                missing = df.isnull().sum().sum()
                if missing > 0:
                    st.warning(f"⚠️ Missing values detected: {missing} cells ({missing / (len(df) * len(df.columns)) * 100:.1f}%)")
                else:
                    st.success("✓ No missing values")
                
                # Column names
                st.markdown("**Columns**")
                st.write(", ".join(df.columns.tolist()))
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Analysis section
    if uploaded_file is not None:
        st.markdown("---")
        st.subheader("📈 Detailed Analysis")
        
        try:
            df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else \
                 pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else \
                 pd.read_parquet(uploaded_file)
            
            tab1, tab2, tab3 = st.tabs(["Statistics", "Data Types", "Correlations"])
            
            with tab1:
                st.markdown("**Descriptive Statistics**")
                st.dataframe(df.describe().T, use_container_width=True)
            
            with tab2:
                st.markdown("**Data Type Overview**")
                dtype_df = pd.DataFrame({
                    'Column': df.columns,
                    'Data Type': df.dtypes,
                    'Non-Null Count': df.count(),
                    'Null Count': df.isnull().sum(),
                })
                st.dataframe(dtype_df, use_container_width=True)
            
            with tab3:
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    st.markdown("**Feature Correlation Matrix**")
                    corr = df[numeric_cols].corr()
                    st.dataframe(corr, use_container_width=True)
                else:
                    st.info("No numeric columns for correlation analysis")
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
        
        # Recommendations preview
        st.markdown("---")
        st.subheader("🔍 Quick Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Check for imbalance
            if target_column and target_column in df.columns:
                try:
                    target = df[target_column]
                    if target.dtype == 'object' or target.nunique() < 50:
                        value_counts = target.value_counts()
                        ratio = value_counts.min() / value_counts.max()
                        if ratio < 0.5:
                            st.warning("⚠️ Class imbalance detected")
                        else:
                            st.success("✓ Balanced classes")
                except:
                    pass
        
        with col2:
            # Dataset size assessment
            if len(df) < 1000:
                st.warning("⚠️ Small dataset (< 1000 samples)")
            elif len(df) > 100000:
                st.success("✓ Large dataset")
            else:
                st.info("ℹ️ Medium dataset")
        
        with col3:
            # Feature complexity
            if len(df.columns) > 50:
                st.warning("⚠️ High dimensionality")
            elif len(df.columns) < 5:
                st.info("ℹ️ Low dimensionality")
            else:
                st.success("✓ Manageable dimensionality")
