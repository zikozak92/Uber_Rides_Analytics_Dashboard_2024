import streamlit as st
import pandas as pd
import os
from src.preprocess import add_derived_features
from src.metrics import calculate_ride_metrics, prepare_volume_data, vehicle_type_metrics_dataframe
from src.visualizations import (create_sparkline, plot_revenue_by_vehicle_type, plot_volume_chart,
                                plot_booking_status_pie, plot_revenue_distribution_box,
                                plot_cancellation_reason_counts)

# Custom CSS for enhanced styling
with open("static/style.css", "r") as f:
    (st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True))

# Streamlit app layout
st.set_page_config(page_title="Uber Rides Analytics Dashboard 2024", layout="wide")

# Title and header
st.title("Uber Rides Analytics Dashboard 2024")
st.markdown("Analyze ride-sharing patterns, cancellations, revenue, and ratings from 150K Uber bookings in 2024.")
# Load data


@st.cache_data
def load_data():
    file_path = os.path.join('data', 'ncr_ride_bookings.csv')
    df = pd.read_csv(file_path)
    df = add_derived_features(df)
    return df


df = load_data()

# Sidebar: Filters
st.sidebar.header("🔍 Filters")

# Vehicle Type Filter: Checkboxes in Expander
st.sidebar.subheader("Vehicle Type")
with st.sidebar.expander("Select Vehicle Types"):
    vehicle_options = df['Vehicle Type'].unique()
    selected_vehicles = []
    for v in vehicle_options:
        if st.checkbox(v, value=True, key=f"vehicle_{v}"):
            selected_vehicles.append(v)
    if not selected_vehicles:
        selected_vehicles = vehicle_options

# Date Range Filter
st.sidebar.subheader("Date & Time")
date_range = st.sidebar.date_input("Date Range", [df['Timestamp'].min().date(), df['Timestamp'].max().date()], key="date_range")
hours = st.sidebar.slider("Hour of Day", min_value=0, max_value=23, value=(0, 23), key="hours")

# Booking Status Filter: Checkboxes in Expander
st.sidebar.subheader("Booking Status")
with st.sidebar.expander("Select Booking Status"):
    status_options = df['Booking Status'].unique()
    selected_status = []
    for s in status_options:
        if st.checkbox(s, value=True, key=f"status_{s}"):
            selected_status.append(s)
    if not selected_status:
        selected_status = status_options

# Payment Method Filter: Checkboxes in Expander
st.sidebar.subheader("Payment Method")
with st.sidebar.expander("Select Payment Methods"):
    payment_options = df['Payment Method'].unique()
    selected_payments = []
    for p in payment_options:
        if st.checkbox(p, value=True, key=f"payment_{p}"):
            selected_payments.append(p)
    if not selected_payments:
        selected_payments = payment_options


# Filter DataFrame
filtered_df = df[
    (df['Vehicle Type'].isin(selected_vehicles)) &
    (df['Timestamp'].dt.date >= date_range[0]) & (df['Timestamp'].dt.date <= date_range[1]) &
    (df['Hour'].between(hours[0], hours[1])) &
    (df['Booking Status'].isin(selected_status)) &
    (df['Payment Method'].isin(selected_payments))
]

# Handle empty filtered DataFrame
if filtered_df.empty:
    st.warning("No data matches the selected filters. Showing all data instead.")
    filtered_df = df.copy()

# Download filtered data
st.sidebar.markdown("📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.sidebar.download_button("Download CSV", csv, "filtered_uber_data.csv", "text/csv")


# ############ Section 1: KPI Cards ############
st.header("📊 Key Metrics")

# Calculate metrics and prepare daily trend data
metrics = calculate_ride_metrics(filtered_df)

# Monthly trends for sparklines (grouped by month)
monthly_trends = filtered_df.groupby(filtered_df['Timestamp'].dt.to_period('M')).agg({
    'Booking ID': 'count',  # For Total Rides
    'Booking Status': [
        lambda x: (x == 'Completed').mean() * 100,  # Success Rate
        lambda x: (x == 'Cancelled by Customer').mean() * 100  # Customer Cancellation Rate
    ],
    'Revenue': 'mean',  # Avg Revenue
    'Driver Ratings': 'mean'  # Avg Driver Rating
}).reset_index()
monthly_trends.columns = ['Month', 'Total Rides', 'Success Rate', 'Customer Cancellation Rate', 'Avg Revenue', 'Avg Driver Rating']
monthly_trends['Month'] = monthly_trends['Month'].astype(str)  # Convert Period to string for plotting

# Display metrics with sparklines
col1, col2, col3, col4, col5 = st.columns(5, border=1)

with col1:
    with st.container():
        fig = create_sparkline(monthly_trends, 'Total Rides')
        st.metric("Total Rides 🚗", f"{metrics['total_rides']:,}")
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col2:
    with st.container():
        fig = create_sparkline(monthly_trends, 'Success Rate', color='#28a745')
        st.metric("Success Rate ✅", f"{metrics['success_rate']:.2f}%")
        st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col3:
    fig = create_sparkline(monthly_trends, 'Customer Cancellation Rate', color='#ff6f61')
    st.metric("Customer Cancellation 🚫", f"{metrics['customer_cancellation_rate']:.2f}%")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col4:
    fig = create_sparkline(monthly_trends, 'Avg Revenue', color='#0057b8')
    st.metric("Avg Revenue 💰", f"₹ {metrics['avg_revenue']:.2f}")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

with col5:
    fig = create_sparkline(monthly_trends, 'Avg Driver Rating', color='#f1c40f')
    st.metric("Avg Driver Rating ⭐", f"{metrics['avg_driver_rating']:.2f}")
    st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})

# ############ Section 2: Visualizations (Tabbed Interface) ############

st.header("📈 Visualizations")

# Create two columns for side-by-side charts
col1, col2 = st.columns([0.65, 0.35], gap='small', border=1)

with col1:
    st.subheader("Ride Volume by Time Period")
    time_granularity = st.selectbox("Select Time Period", ["Hour", "Day of Week", "Month"], key="volume_granularity")
    volume_data, x_col, x_title, x_tickvals, x_ticktext = prepare_volume_data(filtered_df, time_granularity)
    fig = plot_volume_chart(volume_data, x_col, x_title, x_tickvals, x_ticktext)
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("Booking Status Breakdown")
    fig2 = plot_booking_status_pie(filtered_df)
    st.plotly_chart(fig2, width='stretch')

# Create three columns for side-by-side charts
col1, col2, col3 = st.columns([0.42, 0.23, 0.35], gap='small', border=1)

with col1:
    st.subheader("Revenue by Vehicle Type")
    fig3 = plot_revenue_by_vehicle_type(filtered_df)
    st.plotly_chart(fig3, width='stretch')

with col2:
    st.subheader("Fare Distribution")
    fig4 = plot_revenue_distribution_box(filtered_df)
    st.plotly_chart(fig4, width='stretch')

with col3:
    st.subheader("Cancel Reasons (Customer)")
    fig5 = plot_cancellation_reason_counts(filtered_df, 'cust', 0)
    st.plotly_chart(fig5, width='stretch')

    st.subheader("Cancel Reasons (Driver)")
    fig6 = plot_cancellation_reason_counts(filtered_df, 'driver', 1)
    st.plotly_chart(fig6, width='stretch')

# Show table with Vehicles Type metrics

st.header("🚀 Vehicles Type Performance")
vh_metrics_df = vehicle_type_metrics_dataframe(filtered_df)
st.dataframe(vh_metrics_df, width='stretch', hide_index=True)


# Footer
st.markdown("---")
st.markdown("🚗 Built with Streamlit by Zakaria Elyazghi | Data Source: [Kaggle](https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard) | Last Updated: August 2025", unsafe_allow_html=True)
