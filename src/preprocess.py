import pandas as pd


def add_derived_features(df):
    """
    Add derived features to the Uber dataset for enhanced analytics.

    Parameters:
    df (pandas.DataFrame): Input DataFrame with raw Uber data.

    Returns:
    pandas.DataFrame: DataFrame with new columns (e.g., Hour, Day of Week, Revenue).
    """
    # Create a copy to avoid modifying the original DataFrame
    df = df.copy()

    # Replace null values in Payment Method with 'No Payment'
    df['Payment Method'] = df['Payment Method'].fillna('No Payment')

    # Convert Date and Time to datetime (assuming separate Date and Time columns)
    df['Timestamp'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%Y-%m-%d %H:%M:%S', errors='coerce')

    # Extract temporal features
    df['Hour'] = df['Timestamp'].dt.hour
    df['Day_of_Week'] = df['Timestamp'].dt.day_name()
    df['Month'] = df['Timestamp'].dt.month_name()

    # Calculate revenue (Booking Value for Completed rides only)
    df['Revenue'] = df.apply(lambda x: x['Booking Value'] if x['Booking Status'] == 'Completed' else 0, axis=1)

    # Flag high-value trips (above 75th percentile of Booking Value)
    booking_value_threshold = df[df['Booking Status'] == 'Completed']['Booking Value'].quantile(0.75)
    df['High_Value_Trip'] = df['Booking Value'].apply(lambda x: 1 if x >= booking_value_threshold else 0)

    # Categorize trip duration (Short, Medium, Long based on Avg CTAT)
    df['Trip_Duration_Category'] = pd.cut(
        df['Avg CTAT'],
        bins=[0, 10, 30, float('inf')],
        labels=['Short', 'Medium', 'Long'],
        include_lowest=True
    )

    # Flag peak hours (e.g., 7-9 AM, 5-7 PM)
    df['Is_Peak_Hour'] = df['Hour'].apply(lambda x: 1 if x in [7, 8, 9, 17, 18, 19] else 0)

    return df
