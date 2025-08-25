import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import timedelta
from analyzer.utils import PLOTLY_TEMPLATE, BATTERY_LINE_COLOR, TREND_LINE_COLOR, PREDICTION_LINE_COLOR_1, PREDICTION_LINE_COLOR_2, EVENT_OPACITY, create_staircase_values

def create_segment_plot(data_points, segments, events):
    """Generates the plot for battery usage with segments and a table of gradients."""
    fig = go.Figure()
    
    # --- Main Plot Trace ---
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Actual Battery Level',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ))

    # --- Trend Lines on Plot ---
    for i, segment in enumerate(segments):
        hovertemplate = (f"<b>Trend:</b> {segment['avg_gradient']:.2f}%/hr<br>"
                         f"<b>Variability (std):</b> {segment['variability']:.2f}<extra></extra>")
        fig.add_trace(go.Scatter(
            x=[segment['start'][0], segment['end'][0]],
            y=[segment['start'][1], segment['end'][1]],
            mode='lines',
            line=dict(color=TREND_LINE_COLOR, dash='dot', width=2),
            name=f'Segment {i+1} Trend: {segment["avg_gradient"]:.2f}%/hr',
            showlegend=True,
            hoveron="points",
            hovertemplate=hovertemplate
        ))

        staircase_x, staircase_y = create_staircase_values(segment["start"],segment["end"],  segment["avg_gradient"]) 
            
        fig.add_trace(go.Scatter(
            x=staircase_x,
            y=staircase_y,
            mode='lines',
            line=dict(shape='hv', color=TREND_LINE_COLOR, width=2),
            name='Expected Value (Staircase)',
            hovertemplate="<b>Expected Level:</b> %{y}%<extra></extra>",
            showlegend=False
        ))
        

    # --- Event Rectangles ---
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

    # --- Layout Updates ---
    fig.update_layout(
        title='Battery Usage with Segments',
        template=PLOTLY_TEMPLATE,
        xaxis_title="Time",
        yaxis_title="Battery Percentage (%)",
        hovermode="x unified",
        height=700
    )
    
    return fig

def create_event_gradient_plot(data_points, event_gradients, events):
    """Generates the plot for battery usage with event gradients."""
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

        # --- Staircase Graph for Events ---
        staircase_x_events, staircase_y_events = create_staircase_values(eg["start_point"],eg["end_point"],  eg["gradient"]) 
            
        fig.add_trace(go.Scatter(
            x=staircase_x_events,
            y=staircase_y_events,
            mode='lines',
            line=dict(shape='hv', color=eg["color"], width=2),
            name='Expected Value (Staircase)',
            hovertemplate="<b>Expected Level:</b> %{y}%<extra></extra>",
            showlegend=False
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

        fig.add_trace(go.Scatter(
            x=[last_time, drain_time_1],
            y=[last_value, 0],
            mode='lines',
            line=dict(color=PREDICTION_LINE_COLOR_1, dash='dash', width=2),
            name=f'Current Trend Prediction ({pred_gradient_1:.2f}%/hr)',
            hovertemplate=(f"<b>Current Trend Prediction</b><br>"
                           f"Predicted drain time: {drain_time_1.strftime('%d.%m.%Y %H:%M')}<extra></extra>")
        ))
        
        staircase_x_pred1, staircase_y_pred1 = create_staircase_values(last_point, (drain_time_1, 0), pred_gradient_1) 
           
        fig.add_trace(go.Scatter(
            x=staircase_x_pred1,
            y=staircase_y_pred1,
            mode='lines',
            line=dict(shape='hv', color='blue', width=2),
            name='Current Trend Steps',
            hovertemplate="<b>Predicted Level:</b> %{y}%<extra></extra>"
        ))

    # Prediction 2: Last 2-Day Usage
    if pred_gradient_2 < 0:
        time_to_drain_2_hours = -last_value / pred_gradient_2
        drain_time_2 = last_time + timedelta(hours=time_to_drain_2_hours)

        fig.add_trace(go.Scatter(
            x=[last_time, drain_time_2],
            y=[last_value, 0],
            mode='lines',
            line=dict(color=PREDICTION_LINE_COLOR_2, dash='dash', width=2),
            name=f'Last 2-Day Usage Prediction ({pred_gradient_2:.2f}%/hr)',
            hovertemplate=(f"<b>Last 2-Day Usage Prediction</b><br>"
                           f"Predicted drain time: {drain_time_2.strftime('%d.%m.%Y %H:%M')}<extra></extra>")
        ))

        staircase_x_pred2, staircase_y_pred2 = create_staircase_values(last_point, (drain_time_2, 0), pred_gradient_2) 
        fig.add_trace(go.Scatter(
            x=staircase_x_pred2,
            y=staircase_y_pred2,
            mode='lines',
            line=dict(shape='hv', color='green', width=2),
            name='Last 2-Day Steps',
            hovertemplate="<b>Predicted Level:</b> %{y}%<extra></extra>"
        ))
    
    fig.update_layout(
        title='Battery Drain Predictions',
        template=PLOTLY_TEMPLATE,
        xaxis_title="Time",
        yaxis_title="Battery Percentage (%)",
        hovermode="x unified"
    )
    return fig