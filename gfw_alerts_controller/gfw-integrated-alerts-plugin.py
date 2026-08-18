import urllib.parse
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QDateEdit, QComboBox, QPushButton
)
from qgis.PyQt.QtCore import QDate, Qt
from qgis.core import QgsRasterLayer, QgsProject
from qgis.utils import iface

class GFWLayerControllerDock(QDockWidget):
    def __init__(self):
        super().__init__("GFW Alerts Layer Controller")
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 1. Start Date Picker
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start Date:"))
        self.start_picker = QDateEdit()
        self.start_picker.setDisplayFormat("yyyy-MM-dd")
        self.start_picker.setDate(QDate(2024, 1, 1))
        self.start_picker.setCalendarPopup(True)
        start_layout.addWidget(self.start_picker)
        
        # 2. End Date Picker
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End Date:"))
        self.end_picker = QDateEdit()
        self.end_picker.setDisplayFormat("yyyy-MM-dd")
        self.end_picker.setDate(QDate.currentDate())
        self.end_picker.setCalendarPopup(True)
        end_layout.addWidget(self.end_picker)

        # 3. Render Type Dropdown
        render_layout = QHBoxLayout()
        render_layout.addWidget(QLabel("Render Type:"))
        self.render_combo = QComboBox()
        self.render_combo.addItems(["true_color", "encoded"])
        render_layout.addWidget(self.render_combo)

        # 4. Confidence Dropdown
        conf_layout = QHBoxLayout()
        conf_layout.addWidget(QLabel("Confidence:"))
        self.conf_combo = QComboBox()
        self.conf_combo.addItems(["low", "nominal", "high"])
        conf_layout.addWidget(self.conf_combo)
        
        # 5. Apply Button
        self.btn_update = QPushButton("Apply Settings")
        self.btn_update.clicked.connect(self.update_layer)
        
        # Connect change signals to update map dynamically
        self.start_picker.dateChanged.connect(self.update_layer)
        self.end_picker.dateChanged.connect(self.update_layer)
        self.render_combo.currentIndexChanged.connect(self.update_layer)
        self.conf_combo.currentIndexChanged.connect(self.update_layer)
        
        # Build UI layout
        layout.addLayout(start_layout)
        layout.addLayout(end_layout)
        layout.addLayout(render_layout)
        layout.addLayout(conf_layout)
        layout.addWidget(self.btn_update)
        
        widget.setLayout(layout)
        self.setWidget(widget)
        
    def update_layer(self):
        start_str = self.start_picker.date().toString("yyyy-MM-dd")
        end_str = self.end_picker.date().toString("yyyy-MM-dd")
        render_type = self.render_combo.currentText()
        confidence = self.conf_combo.currentText()
        
        # Format raw inner query parameters
        raw_params = f"start_date={start_str}&end_date={end_str}&render_type={render_type}&alert_confidence={confidence}"
        
        # Percent-encode query parameters for QGIS tile engine
        encoded_params = urllib.parse.quote(raw_params, safe='')
        
        # Construct dynamic URI
        base_url = "https://tiles.globalforestwatch.org/gfw_integrated_alerts/v20260814/dynamic/%7Bz%7D/%7Bx%7D/%7By%7D.png"
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
            
        iface.mapCanvas().refresh()

# Add dock widget to QGIS
gfw_dock = GFWLayerControllerDock()
iface.addDockWidget(Qt.RightDockWidgetArea, gfw_dock)