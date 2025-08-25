from datetime import datetime, timedelta

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
        self.start_time = start_time
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration

def calculate_percent_duration_of_segment(gradient_percent_by_hours):
    delta = timedelta(hours=(1/abs(gradient_percent_by_hours)))
    return delta

    
def create_staircase_values(first_point, last_point, gradient):
    y_delta = -1 if gradient < 0 else 1
    x_delta = calculate_percent_duration_of_segment(gradient)
    staircase_y = [value for value in range(first_point[1], last_point[1], y_delta)]
    staircase_x = [first_point[0]+ i* x_delta for i in range(len(staircase_y)) ]
    return staircase_x, staircase_y