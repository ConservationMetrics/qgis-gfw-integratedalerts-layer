import os
import urllib.parse
from qgis.PyQt.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QDateEdit, QComboBox, QPushButton, QAction
)
from qgis.PyQt.QtCore import QDate, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsRasterLayer, QgsProject

class GFWLayerControllerDock(QDockWidget):
    def __init__(self, iface):
        super().__init__("GFW Alerts Layer Controller")
        self.iface = iface
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
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
        
        raw_params = f"start_date={start_str}&end_date={end_str}&render_type={render_type}&alert_confidence={confidence}"
        encoded_params = urllib.parse.quote(raw_params, safe='')
        
        base_url = "https://tiles.globalforestwatch.org/gfw_integrated_alerts/latest/dynamic/%7Bz%7D/%7Bx%7D/%7By%7D.png"
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
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()
