# QGIS Global Forest Watch (GFW) Dynamic Tile Controller

A lightweight PyQGIS dock widget that enables real-time streaming and filtering of Global Forest Watch (GFW) Integrated Deforestation Alerts directly inside QGIS.

This tool dynamically updates tile requests to GFW's Tile Cache API, allowing users to filter deforestation alerts by date range, visualization style, and confidence level without downloading heavy GeoTIFF files or requiring AWS/API credentials.

---

## ⚠️ Provenance & Disclaimer

* **Provenance**: This tool was **vibe coded** (AI-assisted / rapidly prototyped) to address an immediate operational need for streaming dynamic GFW tiles directly into QGIS.
* **Maintenance & Responsibility**: This repository is provided "as-is" for community use and experimentation. Neither the authors nor associated organizations (including CMI) assume any inherent responsibility over its ongoing maintenance, updates, or how the tool or its output data are used.

---

## Features

* **Interactive Date Pickers**: Select custom `Start Date` and `End Date` using calendar widgets.
* **Visualization Toggle**: Switch between visual map overlays (`true_color`) and raw data tiles (`encoded`).
* **Confidence Filtering**: Filter alerts by detection confidence (`low`, `nominal`, `high`).
* **Dynamic Layer Refresh**: Automatically re-fetches and repaints map tiles without creating duplicate layers.
* **Zero Dependencies**: Runs out of the box using QGIS's built-in Python environment and Qt libraries.

---

## Quick Start / Installation

Until this tool gets accepted into the official QGIS Plugin Repository, you can run it directly:

### Run Directly from GitHub

No file downloads or installation required. Open the **QGIS Python Console** (`Cmd + Option + P` on macOS, `Ctrl + Alt + P` on Windows/Linux) and run the following script:

```python
import urllib.request
from qgis.utils import iface
from qgis.PyQt.QtCore import Qt

# Fetch and execute the controller script directly from GitHub
url = "https://raw.githubusercontent.com/nicopace/qgis-gfw-integratedalerts-layer/main/gfw_controller_plugin.py"
code = urllib.request.urlopen(url).read().decode('utf-8')
exec(code)

# Launch the dock panel
gfw_dock = GFWLayerControllerDock(iface)
iface.addDockWidget(Qt.RightDockWidgetArea, gfw_dock)
gfw_dock.show()

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
