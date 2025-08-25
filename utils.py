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
        self.start_time = datetime.strptime(start_time, "%d.%m.%Y %H%M")
        self.duration = timedelta(minutes=duration_minutes)
        self.end_time = self.start_time + self.duration