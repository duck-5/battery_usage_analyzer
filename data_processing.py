from datetime import datetime, timedelta
import numpy as np

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
        
        duration_hours = (end_point[0] - start_point[0]).total_seconds() / 3600
        value_change = end_point[1] - start_point[1]
        avg_gradient = value_change / duration_hours if duration_hours != 0 else 0
        
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
        
        start_point_idx = min(range(len(data_points)), key=lambda i: abs(data_points[i][0] - start_time))
        end_point_idx = min(range(len(data_points)), key=lambda i: abs(data_points[i][0] - end_time))
        
        start_point = data_points[start_point_idx]
        end_point = data_points[end_point_idx]

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
    Calculates the average gradient of usage over the last 48 hours, excluding charging.
    """
    if not data_points or len(data_points) < 2:
        return 0

    end_time = data_points[-1][0]
    start_time_period = end_time - timedelta(days=2)
    
    usage_points = [p for p in data_points if p[0] >= start_time_period]
    
    usage_gradients = []
    for i in range(len(usage_points) - 1):
        time_diff_hours = (usage_points[i+1][0] - usage_points[i][0]).total_seconds() / 3600
        if time_diff_hours > 0:
            gradient = (usage_points[i+1][1] - usage_points[i][1]) / time_diff_hours
            if gradient <= 0:
                usage_gradients.append(gradient)

    return np.mean(usage_gradients) if usage_gradients else 0