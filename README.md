# Battery Usage Analysis & Prediction

This project is a Python-based tool for analyzing and visualizing battery usage data. By processing time-series data from a simple Excel spreadsheet, it automatically identifies key trends, correlates battery drain with specific events, and generates predictive plots to estimate future battery life.

-----

## Features

  * **Automatic Data Segmentation**: The tool automatically identifies distinct usage and charging segments based on changes in the battery trend.
  * **Trend Analysis**: It calculates the average gradient (rate of change) and variability for each segment, providing clear insights into battery performance.
  * **Event Correlation**: You can log specific events in the spreadsheet to see how they impact battery drain.
  * **Battery Life Prediction**: Two distinct predictive models estimate when the battery will drain to 0%, based on both the most recent trend and the average usage over the last two days.
  * **Excel-based Input**: All data is loaded directly from a simple, two-sheet Excel file, making it easy to update and use.

-----

## Processing Methods

The core of this tool lies in its ability to segment time-series data and analyze the rate of battery change.

  * **Segmentation**: The code identifies "segments" by looking for points where the direction of the battery level changes (e.g., from draining to charging, or a sudden change in drain speed).

  * **Gradient Calculation**: The average gradient for each segment is calculated using the formula:

    $\\text{Average Gradient} = \\frac{\\Delta B}{\\Delta t}$
    
    where $\\Delta B$ is the change in battery percentage and $\\Delta t$ is the duration of the segment in hours.

  * **Predictions**:

    1.  The **"Current Trend"** prediction uses the average gradient of the most recent segment to project when the battery will hit 0%.
    2.  The **"Last 2-Day Usage"** prediction calculates an average gradient from all draining segments within the last 48 hours to provide a more holistic estimate.

-----

## Required Excel Format

The tool expects an Excel file with two sheets, named exactly as specified:

### `Data` Sheet

This sheet contains your raw battery log.

| Column Header | Description                                                                                                                              |
| :------------ | :--------------------------------------------------------------------------------------------------------------------------------------- |
| `Date`        | The date of the entry in `DD.MM.YYYY` format. This column only needs to be filled when the date changes. The code will automatically fill in the missing values. |
| `Time`        | The time of the entry in `HHMM` format.                                                                                                  |
| `Battery`     | The battery percentage at that time.                                                                                                     |

### `Events` Sheet

This sheet is for logging events you want to correlate with battery usage.

| Column Header | Description                                                         |
| :------------ | :------------------------------------------------------------------ |
| `Label`       | A name for the event (e.g., "Gaming," "Charging," "Video Call"). |
| `Start Date`  | The date the event started in `DD.MM.YYYY` format.                      |
| `Start Time`  | The time the event started in `HHMM` format.                            |
| `Duration`    | The duration of the event in minutes.                               |
| `Color`       | A color for the event's visual overlay (e.g., `#ADD8E6`).         |

-----

## Example Visualizations

### Battery Usage with Segments

This plot shows the raw data with overlaid trend lines and a staircase graph representing the expected battery level based on the average segment gradient.

\!

### Battery Usage with Event Gradients

This plot shows the battery data with specific event periods highlighted, and a trend line representing the average gradient during each event.

\!

### Battery Drain Predictions

This plot extends the battery usage graph to show two future predictions: one based on the current usage trend, and one based on the average usage of the last two days. The staircase graphs visualize these predictions step-by-step.

\!
