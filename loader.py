import pandas as pd
from utils import Event

def load_data_from_excel(file_path: str):
    """
    Loads battery and event data from a two-sheet Excel file.

    Args:
        file_path (str): The path to the Excel file.

    Returns:
        dict: A dictionary containing 'battery_data' and 'events_data' as lists.
    """
    try:
        # Load Battery Data sheet
        df_data = pd.read_excel(file_path, sheet_name='Data')
        
        # Fill forward empty date values
        df_data['Date'] = df_data['Date'].ffill()
        
        # Combine Date and Time into a single datetime object
        df_data['datetime'] = pd.to_datetime(df_data['Date'].astype(str) + ' ' + df_data['Time'].astype(str), format='%Y-%m-%d %H:%M:%S')

        # Create list of tuples for battery data
        battery_data = list(zip(df_data['datetime'], df_data['Battery']))

        # Load Events sheet
        df_events = pd.read_excel(file_path, sheet_name='Events')

        df_events['datetime'] = pd.to_datetime(df_events['Start Date'].astype(str) + ' ' + df_events['Start Time'].astype(str), format='%Y-%m-%d %H:%M:%S')
        # Create list of Event objects
        events_data = []
        for index, row in df_events.iterrows():
            events_data.append(
                Event(
                    label=row['Label'],
                    color=row['Color'],
                    start_time=row['datetime'],
                    duration_minutes=row['Duration [min]']
                )
            )

        return {
            'battery_data': battery_data,
            'events_data': events_data
        }
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None