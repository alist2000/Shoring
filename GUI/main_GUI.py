import json
import sys
from functools import partial
from PySide6.QtCore import Qt, QPointF
from PySide6.QtCore import Signal, QObject
from PySide6.QtGui import QPainter
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QLineEdit, QLabel, QPushButton, QComboBox, QFormLayout,
                               QGroupBox, QListWidget, QMessageBox, QDialog, QDialogButtonBox, QDoubleSpinBox)
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from Soil import SoilProfile, SoilLayerWidget, SoilVisualization
from input import *


class ShoringPreview(QGraphicsView):
    def __init__(self, soil_profile, parent=None):
        super().__init__(parent)
        self.soil_profile = soil_profile
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)

    def update_preview(self):
        self.scene.clear()

        # Define some constants
        scale = 10  # pixels per foot
        width = 300
        retaining_height = sum(layer.height for layer in self.soil_profile.layers)
        embedment_depth = self.calculate_embedment_depth()  # You need to implement this method
        total_height = (retaining_height + embedment_depth) * scale

        # Draw pile
        pile = self.scene.addRect(width / 2 - 5, 0, 10, total_height, QPen(Qt.black), QBrush(Qt.gray))

        # Draw soil layers
        y = 0
        for layer in self.soil_profile.layers:
            height = layer.height * scale
            # Behind pile (active pressure)
            self.scene.addRect(0, y, width / 2 - 5, height, QPen(Qt.black), QBrush(QColor(255, 200, 200)))
            # In front of pile (passive pressure)
            self.scene.addRect(width / 2 + 5, y, width / 2 - 5, height, QPen(Qt.black), QBrush(QColor(200, 255, 200)))
            y += height

        # Draw embedment depth
        embedment_rect = self.scene.addRect(0, y, width, embedment_depth * scale, QPen(Qt.black),
                                            QBrush(QColor(200, 200, 255)))

        # Draw pressure diagrams (simplified)
        active_pressure = self.scene.addPolygon(QPolygonF([
            QPointF(width / 2 - 5, 0),
            QPointF(width / 4, total_height),
            QPointF(width / 2 - 5, total_height)
        ]), QPen(Qt.red))

        passive_pressure = self.scene.addPolygon(QPolygonF([
            QPointF(width / 2 + 5, retaining_height * scale),
            QPointF(3 * width / 4, total_height),
            QPointF(width / 2 + 5, total_height)
        ]), QPen(Qt.blue))

        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def calculate_embedment_depth(self):
        # This is a placeholder. You need to implement the actual calculation
        # based on your soil mechanics principles and design requirements
        return 5  # Example: 5 feet embedment depth

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)


class GeometricalSoilPropertiesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.soil_profile = SoilProfile()

        layout = QHBoxLayout(self)

        # Left side - Shoring properties and Soil Layers
        left_layout = QVBoxLayout()
        layout.addLayout(left_layout, 2)

        # Shoring Type selection
        self.shoring_type_combo = QComboBox()
        self.shoring_type_combo.addItems(["Cantilever", "Raker", "Anchor"])
        self.shoring_type_combo.currentIndexChanged.connect(self.update_form)
        left_layout.addWidget(QLabel("Shoring Type:"))
        left_layout.addWidget(self.shoring_type_combo)

        # Theory selection
        theory_combo = QComboBox()
        theory_combo.addItems(["User Defined", "Rankine", "Coulomb"])
        theory_combo.currentTextChanged.connect(self.soil_profile.set_theory)
        left_layout.addWidget(QLabel("Theory:"))
        left_layout.addWidget(theory_combo)

        # Dynamic form for shoring properties
        self.shoring_form = QFormLayout()
        left_layout.addLayout(self.shoring_form)

        # Initialize with Cantilever form
        self.update_form(0)

        # Soil Layers
        soil_group = QGroupBox("Soil Layers")
        soil_layout = QVBoxLayout()
        self.layer_widget = SoilLayerWidget(self.soil_profile)
        soil_layout.addWidget(self.layer_widget)
        soil_group.setLayout(soil_layout)
        left_layout.addWidget(soil_group)

        # Right side - Visualization
        right_layout = QVBoxLayout()
        layout.addLayout(right_layout, 3)

        self.visualization = SoilVisualization(self.soil_profile)
        right_layout.addWidget(self.visualization)

    def update_form(self, index):
        # Clear existing form
        for i in reversed(range(self.shoring_form.rowCount())):
            self.shoring_form.removeRow(i)

        if index in [1, 2]:  # Raker or Anchor
            support_type = "Raker" if index == 1 else "Anchor"
            self.add_support_form(support_type)

    def add_support_form(self, support_type):
        self.supports = []

        self.angle_input = QDoubleSpinBox()
        self.angle_input.setRange(0, 90)
        self.angle_input.setValue(45)
        self.shoring_form.addRow(f"{support_type} Angle (degrees):", self.angle_input)

        # Connect this method to the angle input's valueChanged signal
        self.angle_input.valueChanged.connect(self.update_angle)

        add_button = QPushButton(f"Add {support_type}")
        add_button.clicked.connect(lambda: self.add_support(support_type))
        self.shoring_form.addRow(add_button)

    def add_support(self, support_type):
        support_index = len(self.supports) + 1  # Updated to reflect 1-based indexing
        group_box = QGroupBox(f"{support_type} {support_index}")
        form_layout = QFormLayout(group_box)

        distance_input = QDoubleSpinBox()
        distance_input.setRange(0, 100)
        distance_input.setSingleStep(0.1)
        distance_input.valueChanged.connect(self.on_support_distance_changed)

        form_layout.addRow(f"{support_type} Distance from Top (m):", distance_input)

        remove_button = QPushButton(f"Remove {support_type}")
        # Connect using a reference to the group_box
        remove_button.clicked.connect(partial(self.remove_support_by_group, group_box))
        form_layout.addRow(remove_button)

        self.supports.append((group_box, distance_input))
        self.shoring_form.addRow(group_box)

        # Update SoilProfile
        self.soil_profile.set_shoring_type(support_type)
        self.soil_profile.set_angle(self.angle_input.value())
        self.soil_profile.set_supports([
            {"distance_from_top": input.value()} for _, input in self.supports
        ])

        # Emit a custom signal or directly update the preview if available
        self.emit_soil_profile_changed()

    def remove_support_by_group(self, group_box):
        for index, (gb, _) in enumerate(self.supports):
            if gb == group_box:
                self.remove_support(index)
                break

    def on_support_distance_changed(self):
        # Update the SoilProfile's supports whenever a distance is changed
        self.soil_profile.set_supports([
            {"distance_from_top": input.value()} for _, input in self.supports
        ])
        self.emit_soil_profile_changed()

    def emit_soil_profile_changed(self):
        # Emit a signal or call a method to update the preview
        # Assuming SoilProfile has a signal named 'changed'
        self.soil_profile.layer_changed.emit()  # Replace with the appropriate signal

    def remove_support(self, index):
        if 0 <= index < len(self.supports):
            group_box, _ = self.supports.pop(index)
            self.shoring_form.removeRow(group_box)

            # Update the remaining support labels
            for i, (remaining_group, _) in enumerate(self.supports[index:], start=index + 1):
                remaining_group.setTitle(f"{remaining_group.title().split()[0]} {i}")

            # Update SoilProfile
            self.soil_profile.set_supports([
                {"distance_from_top": input.value()} for _, input in self.supports
            ])

            # Emit a custom signal or directly update the preview if available
            self.emit_soil_profile_changed()

    def update_angle(self):
        self.soil_profile.set_angle(self.angle_input.value())

    def to_dict(self):
        data = {
            "shoring_type": self.shoring_type_combo.currentText(),
            "soil_profile": self.soil_profile.to_dict(),
        }

        if self.shoring_type_combo.currentIndex() in [1, 2]:  # Raker or Anchor
            data["angle"] = self.angle_input.value()
            data["supports"] = []  # Initialize the supports list
            for group_box, distance_input in self.supports:
                support_data = {
                    "type": self.shoring_type_combo.currentText(),
                    "distance_from_top": distance_input.value()
                }
                data["supports"].append(support_data)

        return data

        # if self.shoring_type_combo.currentIndex() in [1, 2]:
        #     data["angle"] = self.angle_input.value()
        #     for _, distance_input in self.supports:
        #         support_data = {
        #             "type": self.shoring_type_combo.currentText(),
        #             "distance_from_top": distance_input.value()
        #         }
        #         data["supports"].append(support_data)

        return data

    def populate_from_dict(self, data):
        self.shoring_type_combo.setCurrentText(data["shoring_type"])
        self.update_form(self.shoring_type_combo.currentIndex())

        if "angle" in data["soil_profile"]:
            self.angle_input.setValue(data["soil_profile"]["angle"])

        # Remove existing supports before adding new ones
        for _ in range(len(self.supports)):
            self.remove_support(0)

        for support in data.get("supports", []):
            self.add_support(support["type"])
            # After adding, set the distance
            group_box, distance_input = self.supports[-1]
            distance_input.setValue(support["distance_from_top"])

        self.soil_profile.set_theory(data["soil_profile"]["theory"]["name"])
        for layer in data["soil_profile"]["layers"]:
            self.soil_profile.add_layer(layer["height"], layer["properties"])

        self.layer_widget.update_view()
        self.visualization.update_view()


class SurchargeLoad:
    def __init__(self, load_type, properties):
        self.load_type = load_type
        self.properties = properties


class SurchargeProfile(QObject):
    load_changed = Signal()

    def __init__(self):
        super().__init__()
        self.loads = []
        self.ka_surcharge = 1.0

    def add_load(self, load_type, properties):
        self.loads.append(SurchargeLoad(load_type, properties))
        self.load_changed.emit()

    def remove_load(self, index):
        if 0 <= index < len(self.loads):
            del self.loads[index]
            self.load_changed.emit()

    def remove_loads(self):
        self.loads = []
        self.load_changed.emit()

    def update_load(self, index, load_type, properties):
        if 0 <= index < len(self.loads):
            self.loads[index] = SurchargeLoad(load_type, properties)
            self.load_changed.emit()

    def set_ka_surcharge(self, value):
        self.ka_surcharge = value
        self.load_changed.emit()

    def to_dict(self):
        return {
            "ka_surcharge": self.ka_surcharge,
            "loads": [
                {
                    "load_type": load.load_type,
                    "properties": load.properties
                } for load in self.loads
            ]
        }


class SurchargeLoadDialog(QDialog):
    def __init__(self, load=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Surcharge Load")
        self.layout = QVBoxLayout(self)

        self.form = QFormLayout()
        self.load_type_combo = QComboBox()
        self.load_type_combo.addItems(["Uniform", "Point Load", "Line Load", "Strip Load"])
        self.load_type_combo.currentTextChanged.connect(self.update_form)
        self.form.addRow("Load Type:", self.load_type_combo)

        self.property_inputs = {}
        self.layout.addLayout(self.form)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        if load:
            self.load_type_combo.setCurrentText(load.load_type)
            self.update_form(load.load_type)
            for key, value in load.properties.items():
                if key in self.property_inputs:
                    self.property_inputs[key].setText(str(value))
        else:
            self.update_form("Uniform")

    def update_form(self, load_type):
        for i in reversed(range(1, self.form.rowCount())):
            self.form.removeRow(i)

        self.property_inputs.clear()
        common_fields = ["q", "Surcharge Effect Depth"]

        if load_type == "Uniform":
            fields = common_fields
        elif load_type in ["Point Load", "Line Load"]:
            fields = common_fields + ["l"]
        elif load_type == "Strip Load":
            fields = common_fields + ["l1", "l2"]

        for field in fields:
            self.property_inputs[field] = QLineEdit()
            self.form.addRow(f"{field}:", self.property_inputs[field])

    def get_values(self):
        load_type = self.load_type_combo.currentText()
        properties = {field: float(input.text()) for field, input in self.property_inputs.items()}
        return load_type, properties


class SurchargeWidget(QGroupBox):
    def __init__(self, surcharge_profile):
        super().__init__("Surcharge Loads")
        self.surcharge_profile = surcharge_profile
        self.surcharge_profile.load_changed.connect(self.update_view)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.ka_surcharge_input = QLineEdit(str(self.surcharge_profile.ka_surcharge))
        self.ka_surcharge_input.textChanged.connect(self.update_ka_surcharge)
        layout.addWidget(QLabel("Ka Surcharge:"))
        layout.addWidget(self.ka_surcharge_input)

        self.load_list = QListWidget()
        self.load_list.itemDoubleClicked.connect(self.edit_load)
        layout.addWidget(self.load_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Load")
        self.remove_button = QPushButton("Remove Load")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_load)
        self.remove_button.clicked.connect(self.remove_load)

        self.update_view()

    def update_view(self):
        self.load_list.clear()
        for i, load in enumerate(self.surcharge_profile.loads):
            self.load_list.addItem(f"Load {i + 1}: {load.load_type}")

    def add_load(self):
        dialog = SurchargeLoadDialog(parent=self)
        if dialog.exec():
            load_type, properties = dialog.get_values()
            self.surcharge_profile.add_load(load_type, properties)

    def remove_load(self):
        current_row = self.load_list.currentRow()
        if current_row >= 0:
            self.surcharge_profile.remove_load(current_row)

    def edit_load(self, item):
        index = self.load_list.row(item)
        load = self.surcharge_profile.loads[index]
        dialog = SurchargeLoadDialog(load, parent=self)
        if dialog.exec():
            load_type, properties = dialog.get_values()
            self.surcharge_profile.update_load(index, load_type, properties)

    def update_ka_surcharge(self, value):
        try:
            self.surcharge_profile.set_ka_surcharge(float(value))
        except ValueError:
            pass


class LaggingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QFormLayout(self)

        self.ph_max_input = QLineEdit()
        layout.addRow("Ph max:", self.ph_max_input)

        self.fb_input = QLineEdit()
        layout.addRow("Fb:", self.fb_input)

        self.timber_size_combo = QComboBox()
        self.timber_size_combo.addItems(["2 x 12", "3 x 12", "4 x 12"])  # Add more sizes as needed
        layout.addRow("Timber Size:", self.timber_size_combo)

    def to_dict(self):
        return {
            "ph_max": self.ph_max_input.text(),
            "fb": self.fb_input.text(),
            "timber_size": self.timber_size_combo.currentText()
        }


from PySide6.QtWidgets import QFileDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shoring System Design")
        self.setGeometry(100, 100, 1000, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # Create tabs
        self.general_info_tab = self.create_general_info_tab()
        self.general_properties_tab = self.create_general_properties_tab()
        self.geo_soil_tab = GeometricalSoilPropertiesTab()
        # main_layout.addWidget(self.geo_soil_tab)  # Ensure it's added

        # Instantiate ShoringPreview
        # self.shoring_preview = ShoringPreview(self.geo_soil_tab.soil_profile)
        # main_layout.addWidget(self.shoring_preview)

        # Connect the layer_changed signal to update the preview
        # self.geo_soil_tab.soil_profile.layer_changed.connect(self.shoring_preview.update_preview)

        self.surcharge_tab = self.create_surcharge_tab()
        self.lagging_tab = LaggingTab()

        self.tab_widget.addTab(self.geo_soil_tab, "Geometrical and Soil Properties")
        self.tab_widget.addTab(self.surcharge_tab, "Surcharge")
        self.tab_widget.addTab(self.lagging_tab, "Lagging")

        button_layout = QHBoxLayout()
        calculate_button = QPushButton("Calculate")
        calculate_button.clicked.connect(self.calculate)
        button_layout.addWidget(calculate_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_data)
        button_layout.addWidget(save_button)

        load_button = QPushButton("Load")
        load_button.clicked.connect(self.load_data)
        button_layout.addWidget(load_button)

        main_layout.addLayout(button_layout)

    def create_general_info_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        fields = ["Title", "Job No", "Designer", "Checker", "Company", "Client", "Unit", "Date", "Comment"]
        self.general_info_inputs = {}
        for field in fields:
            self.general_info_inputs[field] = QLineEdit()
            layout.addRow(field, self.general_info_inputs[field])

        self.tab_widget.addTab(tab, "General Information")
        return tab

    def create_general_properties_tab(self):
        tab = QWidget()
        layout = QFormLayout()
        tab.setLayout(layout)

        fields = ["FS", "E", "Pile Spacing", "Fy", "Allowable Deflection"]
        self.general_properties_inputs = {}
        for field in fields:
            self.general_properties_inputs[field] = QLineEdit()
            layout.addRow(field, self.general_properties_inputs[field])

        self.sections_combo = QComboBox()
        layout.addRow("Sections", self.sections_combo)

        self.tab_widget.addTab(tab, "General Properties")
        return tab

    def create_surcharge_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        self.surcharge_profile = SurchargeProfile()
        self.surcharge_widget = SurchargeWidget(self.surcharge_profile)
        layout.addWidget(self.surcharge_widget)

        return tab

    def calculate(self):
        data = self.get_all_data()
        json_data = json.dumps(data, indent=2)
        print(json_data)
        # Step A: Imagine we have read everything from GUI into these DTOs:
        gen_info = GeneralInfoData(
            title=data["general_info"]["Title"],
            job_no=data["general_info"]["Job No"],
            designer=data["general_info"]["Designer"],
            checker=data["general_info"]["Checker"],
            company=data["general_info"]["Company"],
            client=data["general_info"]["Client"],
            unit=data["general_info"]["Unit"],
            date=data["general_info"]["Date"],
            comment=data["general_info"]["Comment"]
        )

        gen_props = GeneralPropertiesData(
            fs=float(data["general_properties"]["FS"]),
            E=float(data["general_properties"]["E"]),
            pile_spacing=float(data["general_properties"]["Pile Spacing"]),
            fy=float(data["general_properties"]["Fy"]),
            allowable_deflection=float(data["general_properties"]["Allowable Deflection"]),
            section_name=data["sections"]
        )

        # 1 Soil layer with height=10 ft:
        layers = []
        theory_name = data["geometrical_soil_properties"]["soil_profile"]["theory"]["name"]
        for layer in data["geometrical_soil_properties"]["soil_profile"]["layers"]:
            layer_ = SoilLayerData(height=layer["height"], properties=layer["properties"])
            layers.append(layer_)
        soil_profile = SoilProfileData(
            theory_name=theory_name,
            layers=layers,
            has_water=data["geometrical_soil_properties"]["soil_profile"]["water_level"]["has_water"],
            water_depth=data["geometrical_soil_properties"]["soil_profile"]["water_level"]["depth"]
        )

        # No supports for Cantilever
        geo_soil = GeometricalSoilData(
            shoring_type=data["geometrical_soil_properties"]["shoring_type"],
            angle=data["geometrical_soil_properties"]["soil_profile"]["angle"],
            supports=data["geometrical_soil_properties"]["soil_profile"]["supports"],
            soil_profile=soil_profile
        )

        # Example Surcharge: 1 uniform load
        from math import inf
        surch_loads = []
        for surcharge in data["surcharge"]["loads"]:
            surch_load = SurchargeLoadData(surcharge["load_type"], surcharge["properties"])
            surch_loads.append(surch_load)

        surcharge_data = SurchargeData(
            ka_surcharge=data["surcharge"]["ka_surcharge"],
            loads=surch_loads
        )

        lagging = LaggingData(ph_max=float(data["lagging"]["ph_max"]), fb=float(data["lagging"]["fb"]),
                              timber_size=data["lagging"]["timber_size"])

        # Consolidate
        gui_data = GUIData(
            general_info=gen_info,
            general_props=gen_props,
            geo_soil=geo_soil,
            surcharge=surcharge_data,
            lagging=lagging
        )

    def get_all_data(self):
        return {
            "general_info": {field: input.text() for field, input in self.general_info_inputs.items()},
            "general_properties": {field: input.text() for field, input in self.general_properties_inputs.items()},
            "sections": self.sections_combo.currentText(),
            "geometrical_soil_properties": self.geo_soil_tab.to_dict(),
            "surcharge": self.surcharge_profile.to_dict(),
            "lagging": self.lagging_tab.to_dict()
        }

    def save_data(self):
        data = self.get_all_data()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Data", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(data, f, indent=2)

    def load_data(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Data", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, 'r') as f:
                data = json.load(f)
            self.populate_ui_with_data(data)

    def populate_ui_with_data(self, data):
        # Populate General Info
        for field, value in data['general_info'].items():
            if field in self.general_info_inputs:
                self.general_info_inputs[field].setText(value)

        # Populate General Properties
        for field, value in data['general_properties'].items():
            if field in self.general_properties_inputs:
                self.general_properties_inputs[field].setText(value)

        # Populate Geometrical and Soil Properties
        self.geo_soil_tab.populate_from_dict(data['geometrical_soil_properties'])

        # Set Sections
        index = self.sections_combo.findText(data['sections'])
        if index >= 0:
            self.sections_combo.setCurrentIndex(index)

        # Populate Soil Profile
        theory_name = data["geometrical_soil_properties"]['soil_profile']['theory']["name"]
        try:
            self.geo_soil_tab.soil_profile.set_theory(theory_name)
        except ValueError:
            QMessageBox.warning(self, "Warning",
                                f"Unknown soil theory: {theory_name}. Using User Defined theory instead.")
            self.geo_soil_tab.soil_profile.set_theory("User Defined")

        for layer in data["geometrical_soil_properties"]['soil_profile']['layers']:
            self.geo_soil_tab.soil_profile.add_layer(layer['height'], layer['properties'])

        # Populate Surcharge
        self.surcharge_profile.set_ka_surcharge(data['surcharge']['ka_surcharge'])
        self.surcharge_profile.remove_loads()
        for load in data['surcharge']['loads']:
            self.surcharge_profile.add_load(load['load_type'], load['properties'])

        # Populate Lagging
        self.lagging_tab.ph_max_input.setText(data['lagging']['ph_max'])
        self.lagging_tab.fb_input.setText(data['lagging']['fb'])
        index = self.lagging_tab.timber_size_combo.findText(data['lagging']['timber_size'])
        if index >= 0:
            self.lagging_tab.timber_size_combo.setCurrentIndex(index)

        # Update views
        self.geo_soil_tab.layer_widget.update_view()
        self.geo_soil_tab.visualization.update_view()
        self.surcharge_widget.update_view()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
DATA = {
    "general_info": {
        "Title": "Ventura",
        "Job No": "",
        "Designer": "AMIA",
        "Checker": "",
        "Company": "AMIA ",
        "Client": "",
        "Unit": "",
        "Date": "",
        "Comment": ""
    },
    "general_properties": {
        "FS": "1.3",
        "E": "29000",
        "Pile Spacing": "8",
        "Fy": "50",
        "Allowable Deflection": "5"
    },
    "sections": "",
    "geometrical_soil_properties": {
        "shoring_type": "Cantilever",
        "soil_profile": {
            "theory": {
                "name": "UserDefinedTheory",
                "type": "Triangle",
                "h1": 0,
                "h2": 0,
                "sigma_a": 0
            },
            "layers": [
                {
                    "height": 15.0,
                    "properties": {
                        "EFP Active": 31.0,
                        "EFP Passive": 600.0,
                        "Distribution Type": "Triangle"
                    }
                }
            ],
            "water_level": {
                "has_water": False,
                "depth": 0
            },
            "shoring_type": "Cantilever",
            "angle": 45,
            "supports": []
        },
        "supports": []
    },
    "surcharge": {
        "ka_surcharge": 1.0,
        "loads": [
            {
                "load_type": "Uniform",
                "properties": {
                    "q": 300.0,
                    "Surcharge Effect Depth": 10.0
                }
            }
        ]
    },
    "lagging": {
        "ph_max": "400",
        "fb": "0.9",
        "timber_size": "2 x 12"
    }
}
