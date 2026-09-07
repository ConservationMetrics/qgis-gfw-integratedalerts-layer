import json
import os
import urllib.parse
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDateEdit, QComboBox, QPushButton, QAction
)
from qgis.PyQt.QtCore import QDate, Qt, QTimer, QUrl
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsRasterLayer, QgsProject, QgsNetworkAccessManager

DATASET_API_URL = "https://data-api.globalforestwatch.org/dataset/gfw_integrated_alerts"
FALLBACK_VERSION = "v20260814"
REQUEST_TIMEOUT_MS = 10000

class VersionResolver:
    """Resolves the current GFW tile version dynamically via the Data API.

    Uses QgsNetworkAccessManager (respects QGIS proxy/SSL settings) with an
    async, non-blocking fetch. The resolved version is cached for the session;
    failures fall back to a pinned known-good version without caching, so the
    next request retries.
    """
    def __init__(self):
        self._version = None
        self._pending = []
        self._reply = None
        self._timer = None

    def resolve(self, callback):
        if self._version:
            callback(self._version, True)
            return
        self._pending.append(callback)
        if self._reply is None:
            self._start_fetch()

    def _start_fetch(self):
        request = QNetworkRequest(QUrl(DATASET_API_URL))
        request.setRawHeader(b"Accept", b"application/json")
        self._reply = QgsNetworkAccessManager.instance().get(request)
        self._reply.finished.connect(self._on_finished)
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._reply.abort)
        self._timer.start(REQUEST_TIMEOUT_MS)

    def _on_finished(self):
        if self._timer:
            self._timer.stop()
        reply, self._reply = self._reply, None
        version = None
        if reply.error() == QNetworkReply.NetworkError.NoError:
            try:
                payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
            except (ValueError, UnicodeDecodeError):
                payload = None
            if isinstance(payload, dict) and payload.get("status") == "success":
                versions = (payload.get("data") or {}).get("versions") or []
                if versions:
                    version = versions[-1]
        reply.deleteLater()
        live = version is not None
        if live:
            self._version = version
        else:
            version = FALLBACK_VERSION
        callbacks, self._pending = self._pending, []
        for callback in callbacks:
            callback(version, live)

version_resolver = VersionResolver()

class GFWLayerControllerDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("GFW Alerts Layer Controller")
        self.iface = iface
        self.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)

        widget = QWidget()
        layout = QVBoxLayout()

        # Start Date
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Date:"))
        self.start_picker = QDateEdit()
        self.start_picker.setDisplayFormat("yyyy-MM-dd")
        self.start_picker.setDate(QDate(2024, 1, 1))
        self.start_picker.setCalendarPopup(True)
        start_layout.addWidget(self.start_picker)

        # End Date
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Date:"))
        self.end_picker = QDateEdit()
        self.end_picker.setDisplayFormat("yyyy-MM-dd")
        self.end_picker.setDate(QDate.currentDate())
        self.end_picker.setCalendarPopup(True)
        end_layout.addWidget(self.end_picker)

        # Render Type
        render_layout = QHBoxLayout()
        render_layout.addWidget(QLabel("Render Type:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["true_color", "encoded"])
        render_layout.addWidget(self.render_combo)

        # Confidence
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence:"))
        self.conf_combo = QComboBox()
        self.conf_combo.addItems(["low", "nominal", "high"])
        conf_layout.addWidget(self.conf_combo)

        # Apply Button
        self.btn_update = QPushButton("Apply Settings")
        self.btn_update.clicked.connect(self.update_layer)

        self.start_picker.dateChanged.connect(self.update_layer)
        self.end_picker.dateChanged.connect(self.update_layer)
        self.render_combo.currentIndexChanged.connect(self.update_layer)
        self.conf_combo.currentIndexChanged.connect(self.update_layer)

        # Version status label
        self.version_label = QLabel("Version: resolving…")

        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addLayout(render_layout)
        layout.addLayout(conf_layout)
        layout.addWidget(self.btn_update)
        layout.addWidget(self.version_label)

        widget.setLayout(layout)
        self.setWidget(widget)

        # Prefetch so the first Apply is instant
        version_resolver.resolve(self._update_version_label)

    def update_layer(self):
        version_resolver.resolve(self._apply_layer)

    def _update_version_label(self, version, live):
        suffix = "live" if live else "fallback — API unreachable"
        self.version_label.setText(f"Version: {version} ({suffix})")

    def _apply_layer(self, version, live):
        self._update_version_label(version, live)

        start_str = self.start_picker.date().toString("yyyy-MM-dd")
        end_str = self.end_picker.date().toString("yyyy-MM-dd")
        render_type = self.render_combo.currentText()
        confidence = self.conf_combo.currentText()

        raw_params = f"start_date={start_str}&end_date={end_str}&render_type={render_type}&alert_confidence={confidence}"
        encoded_params = urllib.parse.quote(raw_params, safe='')

        base_url = f"https://tiles.globalforestwatch.org/gfw_integrated_alerts/{version}/dynamic/%7Bz%7D/%7Bx%7D/%7By%7D.png"
        uri = f"http-header:referer=&type=xyz&url={base_url}?{encoded_params}&zmax=18&zmin=1"

        layer_name = "GFW Integrated Alerts (Dynamic)"
        layers = QgsProject.instance().mapLayersByName(layer_name)

        if not layers:
            layer = QgsRasterLayer(uri, layer_name, "wms")
            QgsProject.instance().addMapLayer(layer)
        else:
            layer = layers[0]
            layer.dataProvider().setDataSourceUri(uri)
            layer.dataProvider().reloadData()
            layer.triggerRepaint()

        self.iface.mapCanvas().refresh()

class GFWControllerPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.dock = None
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(QIcon(icon_path), "GFW Alerts Controller", self.iface.mainWindow())
        self.action.triggered.connect(self.run)

        # CORRECT API METHOD: addPluginToMenu or addPluginToRasterMenu
        self.iface.addPluginToMenu("&GFW Alerts Controller", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        # CORRECT API METHOD: removePluginMenu
        self.iface.removePluginMenu("&GFW Alerts Controller", self.action)
        self.iface.removeToolBarIcon(self.action)
        if self.dock:
            self.iface.removeDockWidget(self.dock)

    def run(self):
        if not self.dock:
            self.dock = GFWLayerControllerDock(self.iface)
            self.iface.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)
        self.dock.show()
