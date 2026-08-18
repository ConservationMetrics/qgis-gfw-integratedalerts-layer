# QGIS Global Forest Watch (GFW) Dynamic Tile Controller

A lightweight PyQGIS dock widget that enables real-time streaming and filtering of Global Forest Watch (GFW) Integrated Deforestation Alerts directly inside QGIS.

This tool dynamically updates tile requests to GFW's Tile Cache API, allowing users to filter deforestation alerts by date range, visualization style, and confidence level without downloading heavy GeoTIFF files or requiring AWS/API credentials.

---

## Features

* **Interactive Date Pickers**: Select custom `Start Date` and `End Date` using calendar widgets.
* **Visualization Toggle**: Switch between visual map overlays (`true_color`) and raw data tiles (`encoded`).
* **Confidence Filtering**: Filter alerts by detection confidence (`low`, `nominal`, `high`).
* **Dynamic Layer Refresh**: Automatically re-fetches and repaints map tiles without creating duplicate layers.
* **Zero Dependencies**: Runs out of the box using QGIS's built-in Python environment and Qt libraries.

---

## Quick Start / Installation

Till this tool gets accepted in the plugin store, here are some ways you can install them in your system:

### Option 1: Run via Script Editor (Recommended)

1. Launch **QGIS**.
2. Open the **Python Console**:
* **macOS**: `Cmd + Option + P`
* **Windows/Linux**: `Ctrl + Alt + P`


3. Click the **Show Editor** icon (notepad icon in the console toolbar) to open the script editor panel.
4. Open `gfw_alerts_controller.py` (or paste the code into a new editor tab).
5. Click the green **Run Script** play button.
6. A new dock panel titled **GFW Alerts Layer Controller** will appear on the right side of your QGIS window.

### Option 2: Execute in Python Console

Copy and execute `gfw_alerts_controller.py` inside the QGIS Python Console using `exec()`:

```python
with open('/path/to/gfw_alerts_controller.py') as f:
    exec(f.read())

```

---

## Parameters Overview

| Control | Options | Description |
| --- | --- | --- |
| **Start Date** | `YYYY-MM-DD` | Initial date threshold for alert detection. |
| **End Date** | `YYYY-MM-DD` | Final date threshold for alert detection (defaults to today's date). |
| **Render Type** | `true_color` | Renders the visual map overlay (teal/pink deforestation pixels). |
|  | `encoded` | Renders raw RGB-encoded tiles representing loss date and confidence. |
| **Confidence** | `low` | Displays all detected alerts (highest coverage). |
|  | `nominal` | Displays alerts confirmed by at least two observations. |
|  | `high` | Displays alerts confirmed across multiple satellite platforms. |

---

## Technical Details & How It Works

**Dataset Endpoint**: Queries `gfw_integrated_alerts` (combining GLAD-L, GLAD-S2, RADD, and DIST-ALERT systems).

---

## Data Attribution & Citation

Data provided by **Global Forest Watch / World Resources Institute (WRI)**.

* **Dataset**: GFW Integrated Deforestation Alerts
* **Resolution**: Resampled to 10 m
* **Source**: [GFW Tile Cache API](https://tiles.globalforestwatch.org/)
