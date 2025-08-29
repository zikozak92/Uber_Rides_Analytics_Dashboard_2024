import plotly.express as px
import plotly.graph_objects as go


# Function to create sparkline
def create_sparkline(data, y_col, color='#003087'):
    fig = go.Figure(
        go.Scatter(
            x=data['Month'], y=data[y_col], mode='lines+markers',
            line=dict(color=color, width=2.5, shape='spline'),
            marker=dict(size=3),hoverinfo='none'  # Disable hover
        )
    )
    fig.update_layout(
        showlegend=False, margin=dict(l=0, r=0, t=0, b=0), height=50,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig


def plot_volume_chart(volume_data, x_col, x_title, x_tickvals=None, x_ticktext=None):
    """
    Create a Plotly chart for ride volume with smoothed lines.

    Args:
        volume_data (pd.DataFrame): DataFrame with time period and 'Ride Volume' columns.
        x_col (str): Column name for x-axis.
        x_title (str): X-axis title.
        x_tickvals (list or None): X-axis tick values (e.g., for Hour).
        x_ticktext (list or None): X-axis tick labels (e.g., for Hour).

    Returns:
        go.Figure: Plotly figure with smoothed line chart.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=volume_data[x_col],
        y=volume_data['Ride Volume'],
        mode='lines+markers',
        line=dict(color='#003087', width=3, shape='spline'),  # Smooth lines
        marker=dict(size=6),
        hovertemplate='%{x}: %{y:,} rides<extra></extra>'
    ))

    fig.update_layout(
        # title=None,
        xaxis_title=None,
        yaxis_title="Number of Rides",
        xaxis=dict(tickvals=x_tickvals, ticktext=x_ticktext),
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        showlegend=False
    )

    return fig


def plot_booking_status_pie(df):
    """
    Create a Plotly pie chart for Booking Status distribution with enhanced styling.

    Args:
        df (pd.DataFrame): Filtered DataFrame with 'Booking Status' column.

    Returns:
        go.Figure: Plotly pie chart with bigger value labels, bottom legend, and legend title.
    """
    status_counts = df['Booking Status'].value_counts().reset_index(name='Count')
    fig = px.pie(
        status_counts,
        names='Booking Status',
        values='Count',
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_traces(
        textfont=dict(size=16),  # Bigger value labels
        textinfo='percent',
        hovertemplate='%{label}: %{value:,} rides (%{percent})<extra></extra>'
    )
    fig.update_layout(
        height=400,  # Bigger pie chart
        margin=dict(l=20, r=20, t=20, b=70),  # Reduced side/top margins, more bottom space for legend
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333'),
        showlegend=True,
        legend=dict(
            title="Booking Status",
            title_font_size=17,  # Bigger legend title
            font=dict(size=15),  # Bigger legend text
            orientation="h",
            yanchor="bottom",
            y=-0.7,  # Legend further at the bottom
            xanchor="center",
            x=0.5
        )
    )
    return fig


def plot_revenue_by_vehicle_type(df):
    """
    Create a fancy Plotly bar chart for total revenue by Vehicle Type with emojis as x-axis labels.

    Args:
        df (pd.DataFrame): Filtered DataFrame with 'Vehicle Type' and 'Revenue' columns.

    Returns:
        go.Figure: Plotly bar chart with gradient bars, no text labels, emoji x-axis labels, and custom hover.
    """
    # Aggregate revenue by Vehicle Type
    revenue_data = df.groupby('Vehicle Type')['Revenue'].sum().reset_index()

    # Map Vehicle Types to Uber-like emojis
    vehicle_emoji_map = {
        'eBike': '🚴',  # Electric bike
        'Go Sedan': '🚗',  # Standard sedan
        'Auto': '🛺',  # Auto-rickshaw
        'Premier Sedan': '🚘',  # Premium sedan
        'Bike': '🏍️',  # Motorcycle
        'Go Mini': '🚐',  # Small van
        'Uber XL': '🚙'  # Larger SUV
    }
    # Apply emojis, default to vehicle type name if no emoji
    revenue_data['Emoji'] = revenue_data['Vehicle Type'].map(vehicle_emoji_map).fillna(revenue_data['Vehicle Type'])

    # Create bar chart with gradient colors
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=revenue_data['Vehicle Type'],
        y=revenue_data['Revenue'],
        marker=dict(
            color=revenue_data['Revenue'],
            colorscale=[[0, '#0057b8'], [1, '#003087']],  # Uber-inspired blue gradient
            line=dict(color='#ffffff', width=1),  # White bar borders
            showscale=False
        ),
        hovertemplate='Vehicle: %{customdata}<br>Revenue: ₹%{y:,.2f}<extra></extra>',
        customdata=revenue_data['Vehicle Type'],  # Use vehicle type name for hover
        text=None,  # No text labels on bars
        textposition=None
    ))

    fig.update_layout(
        xaxis_title="Vehicle Type",
        yaxis_title="Total Revenue (₹)",
        height=470,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333', size=12),
        showlegend=False,
        xaxis=dict(
            ticktext=revenue_data['Emoji'],  # Use emojis as labels
            tickvals=revenue_data['Vehicle Type'],  # Map to original vehicle types
            tickangle=0,
            title_font=dict(size=14),
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(200,200,200,0.2)'
        ),
        bargap=0.2
    )

    return fig


def plot_revenue_distribution_box(df):
    """
    Create a fancy Plotly box plot for revenue distribution across all rides.

    Args:
        df (pd.DataFrame): Filtered DataFrame with 'Revenue' column.

    Returns:
        go.Figure: Plotly box plot with Uber-inspired styling and custom hover.
    """
    fig = go.Figure()
    fig.add_trace(go.Box(
        y=df['Revenue'],
        name='Revenue',
        marker=dict(
            color='#003087',  # Uber blue for outliers
            outliercolor='#ff6f61',  # Red for outliers
            line=dict(color='#0057b8', width=1.5)  # Darker blue outline
        ),
        fillcolor='rgba(0, 80, 135, 0.2)',  # Light blue fill with transparency
        line=dict(width=3),
        boxpoints=False
    ))

    fig.update_layout(
        yaxis_title="Revenue (₹)",
        xaxis_title=None,
        height=450,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333', size=12),
        showlegend=False,
        yaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(200,200,200,0.2)',
            zeroline=False
        ),
        xaxis=dict(
            showticklabels=False,  # No x-axis labels for single box
            showgrid=False
        )
    )

    return fig


def plot_cancellation_reason_counts(df, source, x_title):
    """
    Create a fancy Plotly horizontal bar plot for count of customer cancellation reasons.

    Args:
        df (pd.DataFrame): Filtered DataFrame with 'Booking Status' and 'Cancellation Reason (Customer)' columns.
        source: either customer or driver
        x_title: show x title or not
    Returns:
        go.Figure: Plotly horizontal bar plot with gradient bars and custom hover.
    """

    if source == 'cust':
        cancel_book_st = 'Cancelled by Customer'
        cancel_reason_col = 'Reason for cancelling by Customer'
    else:
        cancel_book_st = 'Cancelled by Driver'
        cancel_reason_col = 'Driver Cancellation Reason'

    # Filter for cancelled rides
    cancelled_df = df[df['Booking Status'] == cancel_book_st]

    # Aggregate counts by cancellation reason
    reason_counts = cancelled_df[cancel_reason_col].value_counts().reset_index()
    reason_counts.columns = ['Reason', 'Count']

    # Sort by count (descending) for better visualization
    reason_counts = reason_counts.sort_values('Count', ascending=True)

    # Create horizontal bar chart with gradient colors
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=reason_counts['Reason'],  # Horizontal bars
        x=reason_counts['Count'],
        orientation='h',
        marker=dict(
            color=reason_counts['Count'],
            colorscale=[[0, '#0057b8'], [1, '#003087']],  # Uber-inspired blue gradient
            line=dict(color='#ffffff', width=1),  # White bar borders
            showscale=False
        ),
        hovertemplate='Reason: %{y}<br>Count: %{x:,}<extra></extra>',
        text=reason_counts['Reason'],  # Place reasons inside bars
        textposition='inside',  # Position text inside bars
        insidetextanchor='start',
        textfont=dict(color='#ffffff', size=16)  # White text, readable size
    ))

    fig.update_layout(
        xaxis_title="Number of Cancellations" if x_title == 1 else None,
        height=200,
        margin=dict(l=20, r=20, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#333333', size=12),
        showlegend=False,
        xaxis=dict(
            title_font=dict(size=14),
            tickfont=dict(size=12),
            gridcolor='rgba(200,200,200,0.2)'
        ),
        yaxis=dict(
            showticklabels=False,  # No y-axis labels
            showgrid=False,
            autorange='reversed'  # Highest count at top
        ),
        bargap=0.3
    )

    return fig

