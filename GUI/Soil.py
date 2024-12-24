from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QLineEdit, QPushButton, QComboBox, QFormLayout,
                               QGroupBox, QListWidget, QMessageBox, QDialog, QDialogButtonBox, QGraphicsView,
                               QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsLineItem, \
                               QGraphicsTextItem, QCheckBox, QLabel, QDoubleSpinBox, QGraphicsEllipseItem)
from PySide6.QtCore import Signal, QObject, Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF
import math

from Theory import SoilTheoryFactory, UserDefinedTheory


# Model
class SoilLayer:
    def __init__(self, height, properties):
        self.height = height
        self.properties = properties


class SoilProfile(QObject):
    layer_changed = Signal()
    theory_changed = Signal()
    water_level_changed = Signal()

    def __init__(self):
        super().__init__()
        self.layers = []
        self.theory = UserDefinedTheory()
        self.has_water = False
        self.water_depth = 0
        self.shoring_type = "Cantilever"
        self.angle = 45
        self.supports = []

    def set_shoring_type(self, shoring_type):
        self.shoring_type = shoring_type
        self.layer_changed.emit()

    def set_angle(self, angle):
        self.angle = angle
        self.layer_changed.emit()

    def set_supports(self, supports):
        self.supports = supports
        self.layer_changed.emit()

    def set_theory(self, theory_name):
        self.theory = SoilTheoryFactory.create_theory(theory_name)
        self.layers.clear()
        self.layer_changed.emit()

    def add_layer(self, height, properties):
        if isinstance(self.theory, UserDefinedTheory) and len(self.layers) >= 1:
            raise ValueError("User Defined theory allows only one layer")

        if isinstance(self.theory, UserDefinedTheory):
            distribution_type = properties.get('Distribution Type', 'Triangle')
            h1 = properties.get('H1', 0)
            h2 = properties.get('H2', 0)
            sigma_a = properties.get('Sigma a', 0)
            self.theory.set_distribution(distribution_type, h1, h2, sigma_a)

        self.layers.append(SoilLayer(height, properties))
        self.layer_changed.emit()

    def remove_layer(self, index):
        if 0 <= index < len(self.layers):
            del self.layers[index]
            self.layer_changed.emit()

    def set_water_level(self, has_water, depth=0):
        self.has_water = has_water
        self.water_depth = depth if has_water else 0
        self.water_level_changed.emit()

    def update_layer(self, index, height, properties):
        if 0 <= index < len(self.layers):
            self.layers[index] = SoilLayer(height, properties)
            if isinstance(self.theory, UserDefinedTheory):
                distribution_type = properties.get('Distribution Type', 'Triangle')
                h1 = properties.get('H1', 0)
                h2 = properties.get('H2', 0)
                sigma_a = properties.get('Sigma a', 0)
                self.theory.set_distribution(distribution_type, h1, h2, sigma_a)
                self.theory_changed.emit()
            self.layer_changed.emit()

    def to_dict(self):
        data = {
            "theory": {
                "name": self.theory.__class__.__name__,
            },
            "layers": [
                {
                    "height": layer.height,
                    "properties": layer.properties
                } for layer in self.layers
            ],
            "water_level": {
                "has_water": self.has_water,
                "depth": self.water_depth
            },
            "shoring_type": self.shoring_type,
            "angle": self.angle,
            "supports": self.supports
        }
        if isinstance(self.theory, UserDefinedTheory):
            data["theory"].update(self.theory.get_distribution_params())
        return data


class WaterLevelDialog(QDialog):
    def __init__(self, has_water, water_depth, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Water Level")
        layout = QVBoxLayout(self)

        self.has_water_checkbox = QCheckBox("Water Present")
        self.has_water_checkbox.setChecked(has_water)
        layout.addWidget(self.has_water_checkbox)

        depth_layout = QHBoxLayout()
        depth_layout.addWidget(QLabel("Water Depth from Top (m):"))
        self.depth_input = QDoubleSpinBox()
        self.depth_input.setRange(0, 1000)  # Adjust range as needed
        self.depth_input.setValue(water_depth)
        self.depth_input.setDecimals(2)
        self.depth_input.setSingleStep(0.1)
        depth_layout.addWidget(self.depth_input)
        layout.addLayout(depth_layout)

        self.has_water_checkbox.stateChanged.connect(self.toggle_depth_input)
        self.toggle_depth_input(Qt.Checked if has_water else Qt.Unchecked)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def toggle_depth_input(self, state):
        if self.has_water_checkbox.isChecked():
            self.depth_input.setEnabled(state == Qt.Checked)
            self.depth_input.setEnabled(True)
        else:
            self.depth_input.setEnabled(False)

    def get_values(self):
        return self.has_water_checkbox.isChecked(), self.depth_input.value() if self.depth_input.isEnabled() else 0


# View
class LayerPropertyDialog(QDialog):
    def __init__(self, layer, theory, parent=None):
        super().__init__(parent)
        self.layer = layer
        self.theory = theory
        self.setWindowTitle("Layer Properties")
        self.layout = QVBoxLayout(self)

        self.form = QFormLayout()
        self.height_input = QLineEdit(str(self.layer.height))
        self.form.addRow("Height (m):", self.height_input)

        self.property_inputs = {}
        for param in self.theory.get_parameters():
            if param == 'Distribution Type':
                self.distribution_combo = QComboBox()
                self.distribution_combo.addItems(["Triangle", "Trapezoidal"])
                self.distribution_combo.currentTextChanged.connect(self.update_distribution_inputs)
                self.form.addRow(f"{param}:", self.distribution_combo)
            else:
                self.property_inputs[param] = QLineEdit(str(self.layer.properties.get(param, '')))
                self.form.addRow(f"{param}:", self.property_inputs[param])

        self.distribution_inputs = {}
        self.distribution_form = QFormLayout()
        self.layout.addLayout(self.form)
        self.layout.addLayout(self.distribution_form)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)
        if isinstance(theory, UserDefinedTheory):
            distribution_type = layer.properties.get('Distribution Type', 'Triangle')
            self.distribution_combo.setCurrentText(distribution_type)
            self.update_distribution_inputs(distribution_type)

            if distribution_type == "Trapezoidal":
                for param in ["H1", "H2", "Sigma a"]:
                    self.distribution_inputs[param].setText(str(layer.properties.get(param, '')))

    def update_distribution_inputs(self, distribution_type):
        for i in reversed(range(self.distribution_form.rowCount())):
            self.distribution_form.removeRow(i)

        self.distribution_inputs.clear()

        if distribution_type == "Trapezoidal":
            for param in ["H1", "H2", "Sigma a"]:
                self.distribution_inputs[param] = QLineEdit()
                self.distribution_form.addRow(f"{param}:", self.distribution_inputs[param])

    def get_values(self):
        height = float(self.height_input.text())
        properties = {param: float(input.text()) for param, input in self.property_inputs.items()}

        if isinstance(self.theory, UserDefinedTheory):
            distribution_type = self.distribution_combo.currentText()
            properties['Distribution Type'] = distribution_type
            if distribution_type == "Trapezoidal":
                for param, input in self.distribution_inputs.items():
                    properties[param] = float(input.text())

        return height, properties


class SoilLayerWidget(QGroupBox):
    def __init__(self, soil_profile):
        super().__init__("Soil Layers")
        self.soil_profile = soil_profile
        self.soil_profile.layer_changed.connect(self.update_view)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.layer_list = QListWidget()
        self.layer_list.itemDoubleClicked.connect(self.edit_layer)
        layout.addWidget(self.layer_list)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Layer")
        self.remove_button = QPushButton("Remove Layer")
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        layout.addLayout(button_layout)

        self.add_button.clicked.connect(self.add_layer)
        self.remove_button.clicked.connect(self.remove_layer)

        self.water_level_button = QPushButton("Set Water Level")
        self.water_level_button.clicked.connect(self.set_water_level)
        button_layout.addWidget(self.water_level_button)

        self.update_view()

    def set_water_level(self):
        dialog = WaterLevelDialog(self.soil_profile.has_water, self.soil_profile.water_depth, self)
        if dialog.exec():
            has_water, depth = dialog.get_values()
            self.soil_profile.set_water_level(has_water, depth)

    def update_view(self):
        self.layer_list.clear()
        for i, layer in enumerate(self.soil_profile.layers):
            properties_str = ", ".join(f"{k}: {v}" for k, v in layer.properties.items())
            if isinstance(self.soil_profile.theory, UserDefinedTheory):
                distribution_params = self.soil_profile.theory.get_distribution_params()
                properties_str += f", Distribution: {distribution_params['type']}"
                if distribution_params['type'] == 'Trapezoidal':
                    properties_str += f", H1: {distribution_params['h1']}, H2: {distribution_params['h2']}, Sigma a: {distribution_params['sigma_a']}"
            self.layer_list.addItem(f"Layer {i + 1}: {layer.height} m - {properties_str}")

    def add_layer(self):
        dialog = LayerPropertyDialog(SoilLayer(0, {}), self.soil_profile.theory, self)
        if dialog.exec():
            try:
                height, properties = dialog.get_values()
                self.soil_profile.add_layer(height, properties)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))

    def remove_layer(self):
        current_row = self.layer_list.currentRow()
        if current_row >= 0:
            self.soil_profile.remove_layer(current_row)

    def edit_layer(self, item):
        index = self.layer_list.currentRow()
        layer = self.soil_profile.layers[index]
        dialog = LayerPropertyDialog(layer, self.soil_profile.theory, self)
        if dialog.exec():
            try:
                height, properties = dialog.get_values()
                self.soil_profile.update_layer(index, height, properties)
            except ValueError as e:
                QMessageBox.warning(self, "Invalid Input", str(e))


class SoilVisualization(QGraphicsView):
    def __init__(self, soil_profile):
        super().__init__()
        self.soil_profile = soil_profile
        self.soil_profile.layer_changed.connect(self.update_view)
        self.soil_profile.theory_changed.connect(self.update_view)
        self.soil_profile.water_level_changed.connect(self.update_view)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setMinimumSize(400, 300)

    def update_view(self):
        self.scene.clear()

        if not self.soil_profile.layers:
            return

        scale = 20  # pixels per meter
        width = 600
        margin = 50
        retaining_height = sum(layer.height for layer in self.soil_profile.layers)
        embedment_depth = self.calculate_embedment_depth()
        total_height = (retaining_height + embedment_depth) * scale

        # Draw pile
        pile = QGraphicsRectItem(width / 2 - 5, margin, 10, total_height)
        pile.setBrush(QBrush(Qt.gray))
        self.scene.addItem(pile)

        # Draw soil layers
        y = margin
        for i, layer in enumerate(self.soil_profile.layers):
            height = layer.height * scale

            # Behind pile (active pressure)
            active_rect = QGraphicsRectItem(margin, y, width / 2 - margin - 5, height)
            active_rect.setBrush(QBrush(QColor(255, 200, 200)))
            self.scene.addItem(active_rect)

            # Layer text
            text = QGraphicsTextItem(f"Layer {i + 1}\nHeight: {layer.height} m")
            text.setPos(margin + 5, y + 5)
            self.scene.addItem(text)

            y += height

        # Draw embedment depth
        embedment_rect = QGraphicsRectItem(margin, y, width - 2 * margin, embedment_depth * scale)
        embedment_rect.setBrush(QBrush(QColor(200, 255, 255)))
        self.scene.addItem(embedment_rect)

        # Draw pressure distribution
        if isinstance(self.soil_profile.theory, UserDefinedTheory):
            self.draw_user_defined_pressure(width, margin, scale, retaining_height, embedment_depth)
        else:
            self.draw_triangular_pressure(width, margin, scale, retaining_height, embedment_depth)

        # Draw ground level line
        ground_line = QGraphicsLineItem(margin, margin, width - margin, margin)
        ground_line.setPen(QPen(Qt.black, 2))
        self.scene.addItem(ground_line)

        # Add labels
        self.add_label("Ground Level", width - margin + 5, margin)
        self.add_label(f"Retaining Height: {retaining_height} m", width - margin + 25,
                       margin + retaining_height * scale / 2)
        self.add_label(f"Embedment Depth: {embedment_depth} m", width - margin + 25,
                       margin + retaining_height * scale + embedment_depth * scale / 2)

        # Draw water level if present
        if self.soil_profile.has_water:
            water_y = margin + self.soil_profile.water_depth * scale
            water_line = self.scene.addLine(margin, water_y, width - margin, water_y, QPen(Qt.blue, 2, Qt.DashLine))
            water_label = self.scene.addText(f"Water Level: {self.soil_profile.water_depth} m")
            water_label.setPos(width - margin + 5, water_y)
            water_label.setDefaultTextColor(Qt.blue)

        # Draw supports (rakers or anchors)
        self.draw_supports(width, margin, scale, retaining_height)

        # Set the scene rect to fit all items
        self.scene.setSceneRect(self.scene.itemsBoundingRect().adjusted(-margin, -margin, margin, margin))

        # Fit the view to the scene
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def draw_supports(self, width, margin, scale, retaining_height):
        if not hasattr(self.soil_profile, 'supports') or not self.soil_profile.supports:
            return

        support_type = self.soil_profile.shoring_type
        if support_type not in ['Raker', 'Anchor']:
            return

        angle = self.soil_profile.angle
        for support in self.soil_profile.supports:
            distance_from_top = support['distance_from_top']
            y = margin + distance_from_top * scale

            if support_type == 'Anchor':
                start_x = width / 2 - 5
                end_x = start_x - math.cos(math.radians(angle)) * (retaining_height * scale / 2)  # Arbitrary length
                end_y = y + math.sin(math.radians(angle)) * (retaining_height * scale / 2)
            else:  # Raker
                start_x = width / 2 + 5
                end_x = start_x + (retaining_height * scale + margin - y) / math.tan(
                    math.radians(angle))  # Mirrored arbitrary length
                end_y = retaining_height * scale + margin  # Keep the same vertical direction

            support_line = QGraphicsLineItem(start_x, y, end_x, end_y)
            support_line.setPen(QPen(Qt.black, 2))
            self.scene.addItem(support_line)

            # Add a circle at the connection point
            connection_point = QGraphicsEllipseItem(start_x - 3, y - 3, 6, 6)
            connection_point.setBrush(QBrush(Qt.black))
            self.scene.addItem(connection_point)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            # Zoom
            factor = 1.2
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            self.scale(factor, factor)
        else:
            # Normal scroll
            super().wheelEvent(event)

    def draw_user_defined_pressure(self, width, margin, scale, retaining_height, embedment_depth):
        theory = self.soil_profile.theory
        h = retaining_height * scale
        total_height = (retaining_height + embedment_depth) * scale

        # Draw active pressure
        if theory.distribution_type == "Triangle":
            # Draw active pressure
            efp_active = 0
            if self.soil_profile.layers:
                efp_active = self.soil_profile.layers[0].properties.get('EFP Active', 0)
            active_pressure = QGraphicsPolygonItem(QPolygonF([
                QPointF(width / 2 - 5, margin),
                QPointF((width / 2 - 5 - (efp_active * h / (scale * 10))), margin + h),
                QPointF(width / 2 - 5, margin + h)
            ]))

        else:  # Trapezoidal
            h1 = theory.h1 * scale
            h2 = theory.h2 * scale
            sigma_a = theory.sigma_a * scale

            active_pressure = QGraphicsPolygonItem(QPolygonF([
                QPointF(width / 2 - 5, margin),
                QPointF((width / 2 - 5 - (sigma_a / (scale * 10))), margin + h1),
                QPointF((width / 2 - 5 - (sigma_a / (scale * 10))), margin + h - h2),
                QPointF(width / 2 - 5, margin + h),
                QPointF(width / 2 - 5, margin)
            ]))

        active_pressure.setBrush(QBrush(QColor(255, 0, 0, 128)))
        active_pressure.setPen(QPen(Qt.red))
        self.scene.addItem(active_pressure)

        # Draw passive pressure
        efp_passive = 0
        # Draw active pressure
        efp_active = 0
        if self.soil_profile.layers:
            efp_passive = self.soil_profile.layers[0].properties.get('EFP Passive', 0)
            # efp_passive = self.soil_profile.layers[0].properties.get('EFP Passive', 0) * scale / 10
            efp_active = self.soil_profile.layers[0].properties.get('EFP Active', 0)
            # efp_active = self.soil_profile.layers[0].properties.get('EFP Active', 0) * scale / 10
        active_pressure_embedment = QGraphicsPolygonItem(QPolygonF([
            QPointF(width / 2 - 5, margin + h),
            QPointF((width / 2 - 5 - (efp_active * h / (scale * 10))), margin + h),
            QPointF((width / 2 - 5 - (efp_active * total_height / (scale * 10))), margin + total_height),
            QPointF(width / 2 - 5, margin + total_height),
            QPointF(width / 2 - 5, margin + h)
        ]))

        passive_pressure = QGraphicsPolygonItem(QPolygonF([
            QPointF(width / 2 + 5, margin + h),
            QPointF(width / 2 + 5 + (efp_passive * (total_height - h) / (scale * 10)), margin + total_height),
            QPointF(width / 2 + 5, margin + total_height)
        ]))
        passive_pressure.setBrush(QBrush(QColor(0, 0, 255, 128)))
        passive_pressure.setPen(QPen(Qt.blue))
        self.scene.addItem(passive_pressure)
        active_pressure_embedment.setBrush(QBrush(QColor(255, 0, 0, 128)))
        active_pressure_embedment.setPen(QPen(Qt.red))
        self.scene.addItem(active_pressure_embedment)

    def draw_triangular_pressure(self, width, margin, scale, retaining_height, embedment_depth):
        total_height = (retaining_height + embedment_depth) * scale

        # Active pressure (triangular)
        active_pressure = QGraphicsPolygonItem(QPolygonF([
            QPointF(width / 2 - 5, margin),
            QPointF(width / 4, margin + total_height),
            QPointF(width / 2 - 5, margin + total_height)
        ]))
        active_pressure.setBrush(QBrush(QColor(255, 200, 200, 128)))
        active_pressure.setPen(QPen(Qt.red))
        self.scene.addItem(active_pressure)

        # Passive pressure (triangular)
        passive_pressure = QGraphicsPolygonItem(QPolygonF([
            QPointF(width / 2 + 5, margin + retaining_height * scale),
            QPointF(3 * width / 4, margin + total_height),
            QPointF(width / 2 + 5, margin + total_height)
        ]))
        passive_pressure.setBrush(QBrush(QColor(200, 255, 200, 128)))
        passive_pressure.setPen(QPen(Qt.blue))
        self.scene.addItem(passive_pressure)

    def draw_load_diagram_axis(self, width, margin, scale, total_height):
        # Vertical axis
        v_axis = QGraphicsLineItem(margin - 30, margin, margin - 30, margin + total_height)
        v_axis.setPen(QPen(Qt.black, 2))
        self.scene.addItem(v_axis)

        # Horizontal axis
        h_axis = QGraphicsLineItem(margin - 80, margin, margin - 30, margin)
        h_axis.setPen(QPen(Qt.black, 2))
        self.scene.addItem(h_axis)

        # Axis labels
        self.add_label("Load Diagram", margin - 90, margin - 20)
        self.add_label("q (lb/ft)", margin - 25, margin - 40)
        self.add_label("z (ft)", margin - 60, margin + total_height + 10)

        # Tick marks and values
        for i in range(0, int(total_height / scale) + 1, 5):
            y = margin + i * scale
            tick = QGraphicsLineItem(margin - 35, y, margin - 30, y)
            self.scene.addItem(tick)
            value = QGraphicsTextItem(str(i))
            value.setPos(margin - 55, y - 10)
            self.scene.addItem(value)

        for i in range(-2000, 1000, 1000):
            x = margin - 30 + i * scale / 1000
            tick = QGraphicsLineItem(x, margin, x, margin + 5)
            self.scene.addItem(tick)
            value = QGraphicsTextItem(str(i))
            value.setPos(x - 20, margin + 10)
            self.scene.addItem(value)

    def get_soil_color(self, index):
        colors = [QColor(255, 200, 200), QColor(200, 255, 200), QColor(200, 200, 255),
                  QColor(255, 255, 200), QColor(255, 200, 255), QColor(200, 255, 255)]
        return colors[index % len(colors)]

    def add_label(self, text, x, y):
        label = QGraphicsTextItem(text)
        label.setPos(x, y)
        self.scene.addItem(label)

    def calculate_embedment_depth(self):
        # Placeholder: implement actual calculation
        return 5  # Example: 5 meters embedment depth

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.scene is not None:  # Check if scene exists
            self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
