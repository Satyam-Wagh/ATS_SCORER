import streamlit as st
import pandas as pd
import numpy as np

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="Streamlit Interactive Dashboard",
    page_icon="📊",
    layout="wide"
)

# 2. Application Title & Description
st.title("📊 Interactive Business Analytics Dashboard")
st.markdown("This dashboard demonstrates core **Streamlit** widgets, layout options, and charting libraries.")

# 3. Sidebar for Inputs/Filters
st.sidebar.header("🎯 Filter Controls")

# Input widgets in the sidebar
data_points = st.sidebar.slider("Number of Data Points", min_value=50, max_value=500, value=200, step=50)
selected_category = st.sidebar.selectbox("Select Target Region", ["Global", "North America", "Europe", "Asia-Pacific"])
show_raw_data = st.sidebar.checkbox("Show Raw Data Table", value=False)

# 4. Data Generation (Using standard Python/Pandas logic)
@st.cache_data # Caches the function data to prevent re-running on every widget click
def generate_mock_data(rows):
    dates = pd.date_range(start="2026-01-01", periods=rows)
    revenue = np.random.normal(loc=5000, scale=1500, size=rows).cumsum()
    expenses = revenue * np.random.uniform(0.6, 0.8, size=rows)
    
    df = pd.DataFrame({
        "Date": dates,
        "Revenue ($)": revenue.round(2),
        "Expenses ($)": expenses.round(2)
    })
    df["Profit ($)"] = (df["Revenue ($)"] - df["Expenses ($)"]).round(2)
    return df

df = generate_mock_data(data_points)

# 5. Core Metric KPI Cards (Layout Columns)
col1, col2, col3 = st.columns(3)

latest_revenue = df["Revenue ($)"].iloc[-1]
latest_expenses = df["Expenses ($)"].iloc[-1]
latest_profit = df["Profit ($)"].iloc[-1]

with col1:
    st.metric(label="Total Revenue", value=f"${latest_revenue:,.2f}", delta="+8.2%")
with col2:
    st.metric(label="Operational Expenses", value=f"${latest_expenses:,.2f}", delta="-2.1%", delta_color="inverse")
with col3:
    st.metric(label="Net Profit margin", value=f"${latest_profit:,.2f}", delta="+12.4%")

st.divider()

# 6. Interactive Charts
st.subheader(f"📈 Financial Trajectory Performance — {selected_category}")

# Setting up layout for charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Revenue vs. Expenses Trend**")
    # Streamlit native line chart (requires index to be the x-axis or explicit columns)
    st.line_chart(df, x="Date", y=["Revenue ($)", "Expenses ($)"])

with chart_col2:
    st.markdown("**Cumulative Net Profit**")
    # Streamlit native area chart
    st.area_chart(df, x="Date", y="Profit ($)", color="#29b5e8")

# 7. Conditional Display (Handling Checkboxes)
if show_raw_data:
    st.divider()
    st.subheader("📋 Raw Underlying Dataset")
    # Display an interactive data table with dataframe styling
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True
    )
    
    # Download Button for exporting data
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name='dashboard_export.csv',
        mime='text/csv',
    )
