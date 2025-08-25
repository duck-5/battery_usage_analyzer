import plotly.graph_objects as go
from datetime import timedelta
from utils import PLOTLY_TEMPLATE, BATTERY_LINE_COLOR, TREND_LINE_COLOR, PREDICTION_LINE_COLOR_1, PREDICTION_LINE_COLOR_2, EVENT_OPACITY

def create_segment_plot(data_points, segments, events):
    """Generates the plot for battery usage with segments."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Battery Level',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ))

    for segment_index, segment in enumerate(segments):
        hovertemplate = (f"<b>Trend:</b> {segment['avg_gradient']:.2f}%/hr<br>"
                         f"<b>Variability (std):</b> {segment['variability']:.2f}<extra></extra>")
        fig.add_trace(go.Scatter(
            x=[segment['start'][0], segment['end'][0]],
            y=[segment['start'][1], segment['end'][1]],
            name=f'Segment {segment_index} Trend: {segment["avg_gradient"]:.2f}%/hr',
            mode='lines',
            line=dict(color=TREND_LINE_COLOR, dash='dot', width=2),
            showlegend=True,
            hoveron="points",
            hovertemplate=hovertemplate
        ))

    for event in events:
        fig.add_vrect(
            x0=event.start_time,
            x1=event.end_time,
            fillcolor=event.color,
            opacity=EVENT_OPACITY,
            layer="below",
            line_width=0,
            annotation_text=f"<b>{event.label}</b>",
            annotation_position="top left",
            annotation_font_size=12,
        )
    
    fig.update_layout(
        title='Battery Usage with Segments',
        template=PLOTLY_TEMPLATE,
        xaxis_title="Time",
        yaxis_title="Battery Percentage (%)",
        hovermode="x unified"
    )
    return fig

def create_event_gradient_plot(data_points, event_gradients, events):
    """Generates the plot for battery usage with event gradients."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Battery Level',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ))

    for eg in event_gradients:
        fig.add_trace(go.Scatter(
            x=[eg['start_point'][0], eg['end_point'][0]],
            y=[eg['start_point'][1], eg['end_point'][1]],
            mode='lines',
            line=dict(color=eg['color'], dash='dash', width=3),
            name=f"Trend for {eg['label']}",
            hoveron="points",
            hovertemplate=f"<b>Event:</b> {eg['label']}<br><b>Avg Gradient:</b> {eg['gradient']:.2f}%/hr<extra></extra>"
        ))
        
    for event in events:
        fig.add_vrect(
            x0=event.start_time,
            x1=event.end_time,
            fillcolor=event.color,
            opacity=EVENT_OPACITY,
            layer="below",
            line_width=0,
            annotation_text=f"<b>{event.label}</b>",
            annotation_position="top left",
            annotation_font_size=12,
        )
    
    fig.update_layout(
        title='Battery Usage with Event Gradients',
        template=PLOTLY_TEMPLATE,
        xaxis_title="Time",
        yaxis_title="Battery Percentage (%)",
        hovermode="x unified"
    )
    return fig

def create_prediction_plot(data_points, pred_gradient_1, pred_gradient_2):
    """Generates the prediction plot."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Actual Battery Level',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ))

    last_point = data_points[-1]
    last_time = last_point[0]
    last_value = last_point[1]
    
    if pred_gradient_1 < 0:
        time_to_drain_1_hours = -last_value / pred_gradient_1
        drain_time_1 = last_time + timedelta(hours=time_to_drain_1_hours)
        time_left_1 = timedelta(hours=time_to_drain_1_hours)
        
        days_1 = time_left_1.days
        hours_1 = time_left_1.seconds // 3600
        minutes_1 = (time_left_1.seconds % 3600) // 60

        fig.add_trace(go.Scatter(
            x=[last_time, drain_time_1],
            y=[last_value, 0],
            mode='lines',
            line=dict(color=PREDICTION_LINE_COLOR_1, dash='dash', width=2),
            name=f'Current Trend Prediction ({pred_gradient_1:.2f}%/hr)',
            hovertemplate=(f"<b>Current Trend Prediction</b><br>"
                           f"Time to drain: {days_1}d {hours_1}h {minutes_1}m<br>"
                           f"Predicted drain time: {drain_time_1.strftime('%d.%m.%Y %H:%M')}<extra></extra>")
        ))

    if pred_gradient_2 < 0:
        time_to_drain_2_hours = -last_value / pred_gradient_2
        drain_time_2 = last_time + timedelta(hours=time_to_drain_2_hours)
        time_left_2 = timedelta(hours=time_to_drain_2_hours)
        
        days_2 = time_left_2.days
        hours_2 = time_left_2.seconds // 3600
        minutes_2 = (time_left_2.seconds % 3600) // 60

        fig.add_trace(go.Scatter(
            x=[last_time, drain_time_2],
            y=[last_value, 0],
            mode='lines',
            line=dict(color=PREDICTION_LINE_COLOR_2, dash='dash', width=2),
            name=f'Last 2-Day Usage Prediction ({pred_gradient_2:.2f}%/hr)',
            hovertemplate=(f"<b>Last 2-Day Usage Prediction</b><br>"
                           f"Time to drain: {days_2}d {hours_2}h {minutes_2}m<br>"
                           f"Predicted drain time: {drain_time_2.strftime('%d.%m.%Y %H:%M')}<extra></extra>")
        ))
    
    fig.update_layout(
        title='Battery Drain Predictions',
        template=PLOTLY_TEMPLATE,
        xaxis_title="Time",
        yaxis_title="Battery Percentage (%)",
        hovermode="x unified"
    )
    return fig