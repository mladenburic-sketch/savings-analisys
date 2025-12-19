"""
Streamlit application for disputes and savings analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.data_loader import load_disputes_data, clean_disputes_data
from src.calculations import (
    calculate_summary_metrics,
    calculate_by_category,
    calculate_by_date,
    calculate_top_disputes
)
from src.visualizations import (
    plot_discrepancy_timeline,
    plot_discrepancy_by_category,
    plot_discrepancy_distribution,
    plot_discrepancy_pie,
    plot_daily_summary
)

# Page configuration
st.set_page_config(
    page_title="Savings Analysis - Disputes Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("💰 Savings Analysis Dashboard")
st.markdown("Analyze savings (positive values) vs underbilled amounts (negative values)")

# Data loading
@st.cache_data
def load_data():
    """Loads and cleans data with caching"""
    try:
        df = load_disputes_data()
        df_clean = clean_disputes_data(df)
        return df_clean
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.warning("No data available for display.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Filters")
    
    # Filter by dispute status
    if 'discrepancy_status' in df.columns:
        status_options = ['All'] + list(df['discrepancy_status'].unique())
        selected_status = st.selectbox("Dispute Status", status_options)
        if selected_status != 'All':
            df = df[df['discrepancy_status'] == selected_status]
    
    # Filter by discrepancy type
    if 'discrepancy_type' in df.columns:
        type_options = ['All'] + list(df['discrepancy_type'].unique())
        selected_type = st.selectbox("Discrepancy Type", type_options)
        if selected_type != 'All':
            df = df[df['discrepancy_type'] == selected_type]
    
    # Filter by customer
    if 'customerName' in df.columns:
        customer_options = ['All'] + sorted(list(df['customerName'].unique()))
        selected_customer = st.selectbox("Customer", customer_options)
        if selected_customer != 'All':
            df = df[df['customerName'] == selected_customer]
    
    # Filter by date
    if 'disputedAt' in df.columns:
        min_date = df['disputedAt'].min().date() if pd.notna(df['disputedAt'].min()) else datetime.now().date() - timedelta(days=30)
        max_date = df['disputedAt'].max().date() if pd.notna(df['disputedAt'].max()) else datetime.now().date()
        
        date_range = st.date_input(
            "Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df = df[
                (df['disputedAt'].dt.date >= date_range[0]) & 
                (df['disputedAt'].dt.date <= date_range[1])
            ]
    
    st.divider()
    st.markdown(f"**Total disputes:** {len(df)}")
    
    total_savings = df[df['discrepancy_value'] > 0]['discrepancy_value'].sum()
    total_underbilled = abs(df[df['discrepancy_value'] < 0]['discrepancy_value'].sum())
    
    st.markdown(f"**💰 Total Savings:** ${total_savings:,.2f}")
    st.markdown(f"**⚠️ Total Underbilled:** ${total_underbilled:,.2f}")
    st.markdown(f"**📊 Net Impact:** ${df['discrepancy_value'].sum():,.2f}")

# --- MAIN CONTENT ---

# Metrics
st.header("📊 Key Metrics")
metrics = calculate_summary_metrics(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Disputes",
        f"{metrics['total_disputes']:,}",
        delta=f"{metrics['disputes_with_positive_value']} savings"
    )

with col2:
    st.metric(
        "Total Savings",
        f"${metrics['total_positive_discrepancy']:,.2f}",
        delta_color="normal"
    )

with col3:
    st.metric(
        "Total Underbilled",
        f"${metrics['total_negative_discrepancy']:,.2f}",
        delta_color="inverse"
    )

with col4:
    st.metric(
        "Net Impact",
        f"${metrics['total_discrepancy_value']:,.2f}",
        delta=f"{metrics['disputes_with_negative_value']} underbilled"
    )

st.divider()

# Tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Time Analysis",
    "🏢 Category Analysis",
    "📋 Top Disputes",
    "📊 Detailed Overview"
])

with tab1:
    st.subheader("Savings vs Underbilled - Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            plot_daily_summary(df),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            plot_discrepancy_timeline(df),
            use_container_width=True
        )
    
    # Monthly aggregation
    if 'disputedAt' in df.columns:
        monthly = calculate_by_date(df, freq='M')
        if not monthly.empty:
            st.subheader("Monthly Aggregation")
            # Add savings and underbilled columns
            monthly['savings'] = monthly['total_discrepancy'].apply(lambda x: x if x > 0 else 0)
            monthly['underbilled'] = monthly['total_discrepancy'].apply(lambda x: abs(x) if x < 0 else 0)
            st.dataframe(monthly, use_container_width=True)

with tab2:
    st.subheader("Savings vs Underbilled by Category")
    
    category_type = st.selectbox(
        "Select category for analysis:",
        ['discrepancy_type', 'customerName', 'item', 'siteName'],
        key='category_selector'
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            plot_discrepancy_by_category(df, category_type, top_n=15),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            plot_discrepancy_pie(df, category_type),
            use_container_width=True
        )
    
    # Table with aggregated data
    category_summary = calculate_by_category(df, category_type)
    if not category_summary.empty:
        st.subheader(f"Details by {category_type}")
        st.dataframe(category_summary, use_container_width=True)

with tab3:
    st.subheader("Top Savings and Underbilled Disputes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        n_top_savings = st.slider("Number of top savings to display:", 5, 30, 10, key='top_savings')
        top_savings = df[df['discrepancy_value'] > 0].nlargest(n_top_savings, 'discrepancy_value')[
            ['po_number', 'customerName', 'siteName', 'item', 
             'discrepancy_value', 'gallons', 'disputedAt', 'discrepancy_type']
        ]
        st.markdown("**💰 Top Savings:**")
        st.dataframe(top_savings, use_container_width=True, hide_index=True)
    
    with col2:
        n_top_underbilled = st.slider("Number of top underbilled to display:", 5, 30, 10, key='top_underbilled')
        top_underbilled = df[df['discrepancy_value'] < 0].nsmallest(n_top_underbilled, 'discrepancy_value')[
            ['po_number', 'customerName', 'siteName', 'item', 
             'discrepancy_value', 'gallons', 'disputedAt', 'discrepancy_type']
        ]
        st.markdown("**⚠️ Top Underbilled:**")
        st.dataframe(top_underbilled, use_container_width=True, hide_index=True)
    
    # Value distribution
    st.subheader("Distribution of Savings vs Underbilled")
    st.plotly_chart(
        plot_discrepancy_distribution(df),
        use_container_width=True
    )

with tab4:
    st.subheader("Detailed Overview of All Disputes")
    
    # Display options
    show_cols = st.multiselect(
        "Select columns to display:",
        options=df.columns.tolist(),
        default=['po_number', 'disputedAt', 'customerName', 'siteName', 
                'discrepancy_type', 'item', 'discrepancy_value', 'gallons']
    )
    
    if show_cols:
        st.dataframe(
            df[show_cols],
            use_container_width=True,
            height=600
        )
    
    # Download option
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download filtered data (CSV)",
        data=csv,
        file_name=f"disputes_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

# Footer
st.divider()
st.caption("💡 Tip: Use filters in the sidebar to focus analysis on specific categories or periods.")

