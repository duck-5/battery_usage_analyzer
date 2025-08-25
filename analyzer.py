from datetime import datetime, timedelta
import plotly.io as pio
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# --- Constants for Configuration ---
PLOTLY_TEMPLATE = "plotly_white"
BATTERY_LINE_COLOR = "#4682B4"  # SteelBlue
TREND_LINE_COLOR = "#FFD700"  # Gold
PREDICTION_LINE_COLOR_1 = "#FF4500"  # OrangeRed
PREDICTION_LINE_COLOR_2 = "#32CD32"  # LimeGreen
EVENT_OPACITY = 0.25

# --- Data Structures ---
class Event:
    """Represents a single event with a label, time, and duration."""
    def __init__(self, label: str, color: str, start_time: str, duration_minutes: int):
        self.label = label
        self.color = color
        self.start_time = datetime.strptime(start_time, "%d.%m.%Y %H%M")
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration

# --- Data Processing Functions ---
def parse_battery_data(raw_data: str) -> list[tuple[datetime, int]]:
    """
    Parses raw battery data string into a list of (datetime, battery_value) tuples.
    """
    if not raw_data.strip():
        return []
    
    data_points = []
    for line in raw_data.strip().split("\n"):
        try:
            date_str, time_str, value_str = line.split()
            dt = datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H%M")
            value = int(value_str)
            data_points.append((dt, value))
        except (ValueError, IndexError) as e:
            print(f"Skipping malformed line: '{line}' - Error: {e}")
            continue
    return data_points

def calculate_segments(data_points: list[tuple[datetime, int]]):
    """
    Identifies segments based on changes in gradient sign and returns the points for each segment.
    """
    segments = []
    if not data_points or len(data_points) < 2:
        return segments

    current_segment_points = [data_points[0]]
    for i in range(1, len(data_points) - 1):
        prev_value = data_points[i-1][1]
        current_value = data_points[i][1]
        next_value = data_points[i+1][1]
        
        # Change in trend is indicated by the product of consecutive value changes being negative
        if (current_value - prev_value) * (next_value - current_value) < 0:
            current_segment_points.append(data_points[i])
            segments.append(current_segment_points)
            current_segment_points = [data_points[i]]
        else:
            current_segment_points.append(data_points[i])
            
    current_segment_points.append(data_points[-1])
    segments.append(current_segment_points)
    
    return segments

def calculate_segment_metrics(segments: list):
    """
    Calculates average gradient and sub-gradient variability for each segment.
    """
    processed_segments = []
    for segment in segments:
        start_point = segment[0]
        end_point = segment[-1]
        
        # Calculate average gradient for the entire segment
        duration_hours = (end_point[0] - start_point[0]).total_seconds() / 3600
        value_change = end_point[1] - start_point[1]
        avg_gradient = value_change / duration_hours if duration_hours != 0 else 0
        
        # Calculate variability of sub-gradients
        sub_gradients = []
        for i in range(len(segment) - 1):
            sub_duration_hours = (segment[i+1][0] - segment[i][0]).total_seconds() / 3600
            if sub_duration_hours > 0:
                sub_gradient = (segment[i+1][1] - segment[i][1]) / sub_duration_hours
                sub_gradients.append(sub_gradient)
        
        variability = np.std(sub_gradients) if sub_gradients else 0
        
        processed_segments.append({
            'start': start_point,
            'end': end_point,
            'avg_gradient': avg_gradient,
            'variability': variability
        })
    
    return processed_segments

def calculate_event_gradients(data_points: list, events: list):
    """
    Calculates the average battery gradient for each event using the closest data points.
    """
    event_gradients = []
    if not data_points:
        return event_gradients

    for event in events:
        start_time = event.start_time
        end_time = event.end_time
        
        # Find the closest data points to the event's start and end times
        start_point_idx = min(range(len(data_points)), key=lambda i: abs(data_points[i][0] - start_time))
        end_point_idx = min(range(len(data_points)), key=lambda i: abs(data_points[i][0] - end_time))
        
        start_point = data_points[start_point_idx]
        end_point = data_points[end_point_idx]

        # Calculate the average gradient for the event
        duration_hours = (end_point[0] - start_point[0]).total_seconds() / 3600
        value_change = end_point[1] - start_point[1]
        avg_gradient = value_change / duration_hours if duration_hours > 0 else 0
        
        event_gradients.append({
            'label': event.label,
            'gradient': avg_gradient,
            'color': event.color,
            'start_point': start_point,
            'end_point': end_point
        })
    return event_gradients

def calculate_last_2day_usage_gradient(data_points: list):
    """
    Calculates the average gradient of usage (negative or zero gradients) over the last 48 hours.
    """
    if not data_points or len(data_points) < 2:
        return 0

    end_time = data_points[-1][0]
    start_time_period = end_time - timedelta(days=2)
    
    # Filter data points for the last 48 hours and for discharging periods
    usage_points = [p for p in data_points if p[0] >= start_time_period]
    
    usage_gradients = []
    for i in range(len(usage_points) - 1):
        time_diff_hours = (usage_points[i+1][0] - usage_points[i][0]).total_seconds() / 3600
        if time_diff_hours > 0:
            gradient = (usage_points[i+1][1] - usage_points[i][1]) / time_diff_hours
            if gradient <= 0:  # Only consider negative or zero gradients (usage)
                usage_gradients.append(gradient)

    return np.mean(usage_gradients) if usage_gradients else 0

# --- Combined Plotting Function ---
def create_combined_plot(data_points: list, events: list, segments: list, event_gradients: list, pred_gradient_1: float, pred_gradient_2: float):
    """
    Generates a single figure with three subplots.
    """
    fig = make_subplots(
        rows=3, cols=1,
        row_heights=[0.35, 0.35, 0.3],
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=("Battery Usage with Segments", "Battery Usage with Event Gradients", "Battery Drain Predictions")
    )

    # --- TOP SUBPLOT: Battery Usage Summary (Segments) ---
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Battery Level',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ), row=1, col=1)

    for segment in segments:
        hovertemplate = (f"<b>Trend:</b> {segment['avg_gradient']:.2f}%/hr<br>"
                         f"<b>Variability (std):</b> {segment['variability']:.2f}<extra></extra>")
        fig.add_trace(go.Scatter(
            x=[segment['start'][0], segment['end'][0]],
            y=[segment['start'][1], segment['end'][1]],
            mode='lines',
            line=dict(color=TREND_LINE_COLOR, dash='dot', width=2),
            showlegend=False,
            hoveron="points",
            hovertemplate=hovertemplate
        ), row=1, col=1)

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
            row=1, col=1
        )

    # --- MIDDLE SUBPLOT: Battery Usage (Events) ---
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Battery Level (Events)',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ), row=2, col=1)

    for eg in event_gradients:
        fig.add_trace(go.Scatter(
            x=[eg['start_point'][0], eg['end_point'][0]],
            y=[eg['start_point'][1], eg['end_point'][1]],
            mode='lines',
            line=dict(color=eg['color'], dash='dash', width=3),
            name=f"Trend for {eg['label']}",
            hoveron="points",
            hovertemplate=f"<b>Event:</b> {eg['label']}<br><b>Avg Gradient:</b> {eg['gradient']:.2f}%/hr<extra></extra>"
        ), row=2, col=1)
        
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
            row=2, col=1
        )

    # --- BOTTOM SUBPLOT: Predictions ---
    fig.add_trace(go.Scatter(
        x=[dt for dt, value in data_points],
        y=[value for dt, value in data_points],
        mode='lines+markers',
        name='Actual Battery Level',
        line=dict(color=BATTERY_LINE_COLOR, width=2),
        marker=dict(size=6, color=BATTERY_LINE_COLOR),
        hovertemplate="<b>Time:</b> %{x|%d.%m.%Y %H:%M}<br><b>Level:</b> %{y}%<extra></extra>"
    ), row=3, col=1)

    last_point = data_points[-1]
    last_time = last_point[0]
    last_value = last_point[1]
    
    # Prediction 1: Current Trend
    if pred_gradient_1 < 0:
        time_to_drain_1_hours = -last_value / pred_gradient_1
        drain_time_1 = last_time + timedelta(hours=time_to_drain_1_hours)
        time_left_1 = timedelta(hours=time_to_drain_1_hours)
        
        fig.add_trace(go.Scatter(
            x=[last_time, drain_time_1],
            y=[last_value, 0],
            mode='lines',
            line=dict(color=PREDICTION_LINE_COLOR_1, dash='dash', width=2),
            name=f'Current Trend Prediction ({pred_gradient_1:.2f}%/hr)',
            hovertemplate=(f"<b>Current Trend Prediction</b><br>Time to drain: {time_left_1.seconds // 3600}h {time_left_1.seconds % 3600 // 60}m<br>Predicted drain time: {drain_time_1.strftime('%d.%m.%Y %H:%M')}<extra></extra>")
        ), row=3, col=1)

    # Prediction 2: Last 2-Day Usage
    if pred_gradient_2 < 0:
        time_to_drain_2_hours = -last_value / pred_gradient_2
        drain_time_2 = last_time + timedelta(hours=time_to_drain_2_hours)
        time_left_2 = timedelta(hours=time_to_drain_2_hours)

        fig.add_trace(go.Scatter(
            x=[last_time, drain_time_2],
            y=[last_value, 0],
            mode='lines',
            line=dict(color=PREDICTION_LINE_COLOR_2, dash='dash', width=2),
            name=f'Last 2-Day Usage Prediction ({pred_gradient_2:.2f}%/hr)',
            hovertemplate=(f"<b>Last 2-Day Usage Prediction</b><br>Time to drain: {time_left_2.seconds // 3600}h {time_left_2.seconds % 3600 // 60}m<br>Predicted drain time: {drain_time_2.strftime('%d.%m.%Y %H:%M')}<extra></extra>")
        ), row=3, col=1)

    # --- Final Layout Updates ---
    fig.update_layout(
        title={
            'text': "Comprehensive Battery Usage Report",
            'x': 0.5,
            'xanchor': 'center',
            'font': dict(size=20)
        },
        template=PLOTLY_TEMPLATE,
        hovermode="x unified",
        xaxis_title="Time",
        yaxis_title="Battery Percentage (%)",
        yaxis2_title="Battery Percentage (%)",
        yaxis3_title="Battery Percentage (%)",
        showlegend=True
    )
    fig.update_xaxes(title_text="Time", row=3, col=1)

    pio.renderers.default = "browser"
    fig.show()

# --- Main Execution ---
def main():
    """Main function to process data and generate the combined plot."""
    raw_data = """
    24.8.2025 1007 47
    24.8.2025 1211 43
    24.8.2025 1424 40
    24.8.2025 1510 39
    24.8.2025 1558 36
    24.8.2025 1613 35
    24.8.2025 1746 33
    24.8.2025 1803 32
    24.8.2025 1829 31
    24.8.2025 1841 30
    24.8.2025 1906 29
    24.8.2025 1910 28
    24.8.2025 1930 27
    24.8.2025 2326 19
    25.8.2025 0109 54
    25.8.2025 0945 43
    25.8.2025 1014 42
    25.8.2025 1053 41
    25.8.2025 1145 40
    25.8.2025 1213 38
    25.8.2025 1333 37
    25.8.2025 1344 37
    25.8.2025 1353 36
    25.8.2025 1442 35
    25.8.2025 1504 35
    """
    
    events = [
        Event(label="Workout", color="blue", start_time="24.8.2025 1746", duration_minutes=17),
        Event(label="Charge", color="green", start_time="25.8.2025 0010", duration_minutes=40),
        Event(label="Sleep", color="purple", start_time="25.8.2025 0150", duration_minutes=8*60+19),
    ]

    battery_data = parse_battery_data(raw_data)
    
    raw_segments = calculate_segments(battery_data)
    processed_segments = calculate_segment_metrics(raw_segments)
    event_gradients = calculate_event_gradients(battery_data, events)
    
    # Calculate gradients for predictions
    pred_gradient_1 = processed_segments[-1]['avg_gradient'] if processed_segments else 0
    pred_gradient_2 = calculate_last_2day_usage_gradient(battery_data)
    
    create_combined_plot(battery_data, events, processed_segments, event_gradients, pred_gradient_1, pred_gradient_2)

if __name__ == "__main__":
    main()