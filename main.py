from data_processing import (
    parse_battery_data,
    calculate_segments,
    calculate_segment_metrics,
    calculate_event_gradients,
    calculate_last_2day_usage_gradient
)
from plotting import (
    create_segment_plot,
    create_event_gradient_plot,
    create_prediction_plot
)
from utils import Event
import plotly.io as pio

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

    # Process data
    battery_data = parse_battery_data(raw_data)
    raw_segments = calculate_segments(battery_data)
    processed_segments = calculate_segment_metrics(raw_segments)
    event_gradients = calculate_event_gradients(battery_data, events)
    pred_gradient_1 = processed_segments[-1]['avg_gradient'] if processed_segments else 0
    pred_gradient_2 = calculate_last_2day_usage_gradient(battery_data)
    
    # Generate and display individual figures
    fig_segments = create_segment_plot(battery_data, processed_segments, events)
    fig_events = create_event_gradient_plot(battery_data, event_gradients, events)
    fig_predictions = create_prediction_plot(battery_data, pred_gradient_1, pred_gradient_2)

    pio.renderers.default = "browser"
    fig_segments.show()
    fig_events.show()
    fig_predictions.show()

if __name__ == "__main__":
    main()