import pandas as pd


def calculate_ride_metrics(df):
    """
    Calculate KPIs for Uber rides dataset.

    Parameters:
    df (pandas.DataFrame): Input DataFrame with Uber data (after preprocessing).

    Returns:
    dict: Dictionary with KPIs (total rides, success rate, cancellation rates, etc.).
    """
    metrics = {
        'total_rides': len(df),
        'success_rate': (len(df[df['Booking Status'] == 'Completed']) / len(df) * 100) if len(df) > 0 else 0,
        'customer_cancellation_rate': (len(df[df['Booking Status'] == 'Cancelled by Customer']) / len(df) * 100) if len(
            df) > 0 else 0,
        'driver_cancellation_rate': (len(df[df['Booking Status'] == 'Cancelled by Driver']) / len(df) * 100) if len(
            df) > 0 else 0,
        'avg_revenue': df['Revenue'].mean() if len(df) > 0 else 0,
        'avg_driver_rating': df['Driver Ratings'].mean() if len(df) > 0 else 0
    }
    return metrics


def prepare_volume_data(df, granularity):
    """
    Prepare ride volume data for the volume rides chart based on user-selected granularity.

    Args:
        df (pd.DataFrame): Filtered DataFrame with 'Timestamp' and 'Booking ID' columns.
        granularity (str): Selected time period ('Hour', 'Day of Week', 'Month').

    Returns:
        tuple: (volume_data, x_col, x_title, chart_type, x_tickvals, x_ticktext)
            - volume_data (pd.DataFrame): Aggregated data with time period and ride volume.
            - x_col (str): Column name for x-axis.
            - x_title (str): X-axis title.
            - chart_type (str): Plotly chart type ('bar' or 'scatter').
            - x_tickvals (list or None): X-axis tick values (for Hour).
            - x_ticktext (list or None): X-axis tick labels (for Hour).
    """
    if granularity == "Hour":
        volume_data = df.groupby(df['Timestamp'].dt.hour).agg({
            'Booking ID': 'count'
        }).reset_index()
        volume_data.columns = ['Hour', 'Ride Volume']
        x_col = 'Hour'
        x_title = 'Hour of Day'
        x_tickvals = list(range(24))
        x_ticktext = [f"{h:02d}:00" for h in range(24)]
    elif granularity == "Day of Week":
        volume_data = df.groupby(df['Timestamp'].dt.day_name()).agg({
            'Booking ID': 'count'
        }).reset_index()
        volume_data.columns = ['Day of Week', 'Ride Volume']
        # Sort by day order (Monday to Sunday)
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        volume_data['Day of Week'] = pd.Categorical(volume_data['Day of Week'], categories=day_order, ordered=True)
        volume_data = volume_data.sort_values('Day of Week')
        x_col = 'Day of Week'
        x_title = 'Day of Week'
        x_tickvals = None
        x_ticktext = None
    else:  # Month
        volume_data = df.groupby(df['Timestamp'].dt.to_period('M')).agg({
            'Booking ID': 'count'
        }).reset_index()
        volume_data.columns = ['Month', 'Ride Volume']
        volume_data['Month'] = volume_data['Month'].astype(str)
        x_col = 'Month'
        x_title = 'Month'
        x_tickvals = None
        x_ticktext = None

    return volume_data, x_col, x_title, x_tickvals, x_ticktext


def vehicle_type_metrics_dataframe(df):
    """
    Create a Pandas DataFrame grouped by Vehicle Type with key metrics for display as a table.

    Args:
        df (pd.DataFrame): Filtered DataFrame with 'Vehicle Type', 'Booking Status',
                          'Booking Value', 'Ride Distance', and 'Driver Ratings' columns.

    Returns:
        pd.DataFrame: DataFrame with metrics for each vehicle type.
    """
    # Group by Vehicle Type and calculate metrics
    metrics = df.groupby('Vehicle Type').agg({
        'Booking Status': [
            'count',  # Total Bookings
            lambda x: (x == 'Completed').mean() * 100,  # Success Rate
            lambda x: (x == 'Incomplete').mean() * 100,  # Incomplete Rate
            lambda x: ((x == 'Cancelled by Customer') | (x == 'Cancelled by Driver')).mean() * 100  # Cancellation Rate
        ],
        'Booking Value': 'mean',  # Average Revenue
        'Ride Distance': 'mean',  # Average Distance
        'Driver Ratings': 'mean'  # Average Driver Rating
    }).reset_index()

    # Flatten column names
    metrics.columns = [
        'Vehicle Type', 'Total Bookings', 'Success Rate (%)',
        'Incomplete Rate (%)', 'Cancellation Rate (%)',
        'Average Revenue (₹)', 'Average Distance (km)', 'Average Driver Rating'
    ]

    # Round numeric columns for display
    metrics = metrics.round({
        'Success Rate (%)': 1, 'Incomplete Rate (%)': 1,
        'Cancellation Rate (%)': 1, 'Average Revenue (₹)': 2,
        'Average Distance (km)': 2, 'Average Driver Rating': 2
    })

    return metrics
