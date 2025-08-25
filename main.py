from analyzer.data_processing import (
    calculate_segments,
    calculate_segment_metrics,
    calculate_event_gradients,
    calculate_last_2day_usage_gradient
)
from analyzer.plotting import (
    create_segment_plot,
    create_event_gradient_plot,
    create_prediction_plot
)
from analyzer.loader import load_data_from_excel
import plotly.io as pio

def main():
    """Main function to process data and generate the combined plot."""
    
    # Load data from Excel file
    excel_data = load_data_from_excel(r'battery_usage.xlsx') # CHANGE THIS TO YOUR FILE PATH
    if not excel_data:
        return # Exit if data loading failed

    battery_data = excel_data['battery_data']
    events = excel_data['events_data']
    
    if not battery_data:
        print("No battery data found to process.")
        return
        
    # Process data
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