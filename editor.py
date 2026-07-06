from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QSignalBlocker
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from crop_canvas import CropCanvas
from crop_object import CropObject
from json_manager import JsonManager


MAX_COORDINATE_VALUE = 99999
PREVIEW_MIN_HEIGHT = 280


class Editor(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.manager = JsonManager()
        self._updating_controls = False
        self._updating_list = False
        self._suppress_autosave = False
        self._image_width = 0
        self._image_height = 0
        self._image_path = ""

        self.setWindowTitle("MLBBVision Crop Editor")
        self.resize(1500, 900)

        self.btnOpen = QPushButton("Open Image")
        self.searchVariable = QLineEdit()
        self.searchVariable.setPlaceholderText("Search variable")

        self.listVariable = QListWidget()
        self.listVariable.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        self.canvas = CropCanvas()

        self.spinX = QSpinBox()
        self.spinY = QSpinBox()
        self.spinW = QSpinBox()
        self.spinH = QSpinBox()

        for spin_box in (self.spinX, self.spinY, self.spinW, self.spinH):
            spin_box.setRange(0, MAX_COORDINATE_VALUE)

        self.preview = QLabel("Preview")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        self.preview.setMinimumHeight(PREVIEW_MIN_HEIGHT)
        self.preview.setMinimumWidth(240)
        self.preview.setStyleSheet(
            """
            QLabel {
                background: #1e1e1e;
                color: #bcbcbc;
                border: 1px solid #444;
            }
            """
        )

        self._build_layout()
        self._connect_signals()

        self._load_coordinates_from_disk()
        self._refresh_variable_list()
        self._restore_selection()

    def _build_layout(self) -> None:
        top_bar = QHBoxLayout()
        top_bar.addWidget(self.btnOpen)
        top_bar.addWidget(self.searchVariable, 1)

        left_panel = QVBoxLayout()
        left_panel.addWidget(self.listVariable)

        right_panel = QVBoxLayout()
        coordinate_form = QFormLayout()
        coordinate_form.addRow("X", self.spinX)
        coordinate_form.addRow("Y", self.spinY)
        coordinate_form.addRow("Width", self.spinW)
        coordinate_form.addRow("Height", self.spinH)
        right_panel.addLayout(coordinate_form)
        right_panel.addWidget(self.preview, 1)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.canvas, 4)
        main_layout.addLayout(right_panel, 1)

        root_layout = QVBoxLayout(self)
        root_layout.addLayout(top_bar)
        root_layout.addLayout(main_layout, 1)

    def _connect_signals(self) -> None:
        self.btnOpen.clicked.connect(self.open_image)

        self.searchVariable.textChanged.connect(self._refresh_variable_list)
        self.listVariable.currentItemChanged.connect(self._on_current_variable_changed)

        self.spinX.valueChanged.connect(self._on_geometry_editor_changed)
        self.spinY.valueChanged.connect(self._on_geometry_editor_changed)
        self.spinW.valueChanged.connect(self._on_geometry_editor_changed)
        self.spinH.valueChanged.connect(self._on_geometry_editor_changed)

        self.canvas.objectSelected.connect(self._on_canvas_object_selected)
        self.canvas.geometryChanged.connect(self._on_canvas_geometry_changed)
        self.canvas.objectsChanged.connect(self._autosave_coordinates)
        self.canvas.imageChanged.connect(self._update_preview)

    def _load_coordinates_from_disk(self) -> None:
        self._suppress_autosave = True
        try:
            state = self.manager.load_state()
            image_state = state.get("image", {})
            if isinstance(image_state, dict):
                self._image_width = int(image_state.get("width", 0) or 0)
                self._image_height = int(image_state.get("height", 0) or 0)
                self._image_path = str(image_state.get("path", "") or "")
            else:
                self._image_width = 0
                self._image_height = 0
                self._image_path = ""

            raw_variables = state.get("variables", {})
            objects: dict[str, CropObject] = {}
            if isinstance(raw_variables, dict):
                for name, value in raw_variables.items():
                    if not isinstance(name, str) or not isinstance(value, dict):
                        continue
                    try:
                        objects[name] = CropObject(
                            name=name,
                            x=int(value.get("x", 0)),
                            y=int(value.get("y", 0)),
                            width=int(value.get("w", 0)),
                            height=int(value.get("h", 0)),
                        )
                    except (TypeError, ValueError):
                        continue

            self.canvas.set_objects(objects)

            if self._image_path:
                image_file = Path(self._image_path)
                if image_file.exists():
                    self.canvas.load_image(self._image_path)
        finally:
            self._suppress_autosave = False

        self._refresh_displayed_coordinates()

    def _restore_selection(self) -> None:
        selected_name = self.canvas.selected_name()
        if selected_name is not None:
            self._select_list_item(selected_name)
        elif self.listVariable.count() > 0:
            self.listVariable.setCurrentRow(0)

    def _refresh_displayed_coordinates(self) -> None:
        self._update_controls(self.canvas.selected_object())
        self._update_preview()

    def _refresh_variable_list(self) -> None:
        search_text = self.searchVariable.text().strip().lower()
        selected_name = self.canvas.selected_name()

        with QSignalBlocker(self.listVariable):
            self._updating_list = True
            self.listVariable.clear()

            for name, crop_object in self._sorted_objects():
                if search_text and search_text not in name.lower():
                    continue

                item = QListWidgetItem(name)
                self.listVariable.addItem(item)

                if name == selected_name:
                    self.listVariable.setCurrentItem(item)

            self._updating_list = False

    def _sorted_objects(self) -> list[tuple[str, CropObject]]:
        return list(self.canvas.objects().items())

    def _select_list_item(self, name: str | None) -> None:
        if not name:
            self.listVariable.setCurrentItem(None)
            return

        for index in range(self.listVariable.count()):
            item = self.listVariable.item(index)
            if item is not None and item.text() == name:
                self.listVariable.setCurrentItem(item)
                return

    def _update_controls(self, crop_object: CropObject | None) -> None:
        self._updating_controls = True
        try:
            with QSignalBlocker(self.spinX), QSignalBlocker(self.spinY), QSignalBlocker(self.spinW), QSignalBlocker(self.spinH):
                if crop_object is None:
                    self.spinX.setValue(0)
                    self.spinY.setValue(0)
                    self.spinW.setValue(0)
                    self.spinH.setValue(0)
                else:
                    self.spinX.setValue(crop_object.x)
                    self.spinY.setValue(crop_object.y)
                    self.spinW.setValue(crop_object.width)
                    self.spinH.setValue(crop_object.height)
        finally:
            self._updating_controls = False

    def _update_preview(self) -> None:
        crop_object = self.canvas.selected_object()
        if crop_object is None:
            self.preview.setPixmap(QPixmap())
            self.preview.setText("Preview")
            return

        image_pixmap = self.canvas.image_pixmap()
        if image_pixmap.isNull():
            self.preview.setPixmap(QPixmap())
            self.preview.setText("Preview")
            return

        crop_pixmap = image_pixmap.copy(crop_object.x, crop_object.y, crop_object.width, crop_object.height)
        if crop_pixmap.isNull():
            self.preview.setPixmap(QPixmap())
            self.preview.setText("Preview")
            return

        scaled = crop_pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.preview.setText("")
        self.preview.setPixmap(scaled)

    def _autosave_coordinates(self, *args) -> None:
        if self._suppress_autosave:
            return

        self._save_state()

    def _save_state(self) -> None:
        image_width, image_height = self.canvas.image_size()
        if image_width <= 0 or image_height <= 0:
            image_width = self._image_width
            image_height = self._image_height

        self.manager.save_state_with_image_path(
            image_width,
            image_height,
            self._image_path,
            self.canvas.export_coordinates(),
        )

    def _on_canvas_object_selected(self, name: str) -> None:
        self._select_list_item(name or None)
        self._update_controls(self.canvas.selected_object())
        self._update_preview()

    def _on_canvas_geometry_changed(self, name: str, x: int, y: int, width: int, height: int) -> None:
        if self.canvas.selected_name() != name:
            return

        self._update_controls(CropObject(name=name, x=x, y=y, width=width, height=height))
        self._update_preview()
        self._refresh_variable_list()

    def _on_current_variable_changed(self, current_item: QListWidgetItem | None, previous_item: QListWidgetItem | None) -> None:
        if self._updating_list:
            return

        if current_item is None:
            self.canvas.clear_selection()
            self._update_controls(None)
            self._update_preview()
            return

        self.canvas.select_object(current_item.text())

    def _on_geometry_editor_changed(self) -> None:
        if self._updating_controls:
            return

        selected_name = self.canvas.selected_name()
        if selected_name is None or self.canvas.objects().get(selected_name) is None:
            return

        self.canvas.update_object_geometry(
            selected_name,
            self.spinX.value(),
            self.spinY.value(),
            self.spinW.value(),
            self.spinH.value(),
        )

    def open_image(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            str(Path.cwd()),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )

        if not file_path:
            return

        if self._image_path:
            self._save_state()

        self._suppress_autosave = True
        try:
            snapshot = self.manager.load_state_for_image(file_path)
            if snapshot is not None:
                raw_variables = snapshot.get("variables", {})
                objects: dict[str, CropObject] = {}
                if isinstance(raw_variables, dict):
                    for name, value in raw_variables.items():
                        if not isinstance(name, str) or not isinstance(value, dict):
                            continue
                        try:
                            objects[name] = CropObject(
                                name=name,
                                x=int(value.get("x", 0)),
                                y=int(value.get("y", 0)),
                                width=int(value.get("w", 0)),
                                height=int(value.get("h", 0)),
                            )
                        except (TypeError, ValueError):
                            continue
                self.canvas.set_objects(objects)

            if not self.canvas.load_image(file_path):
                return

            self._image_path = file_path
            image_width, image_height = self.canvas.image_size()
            self._image_width = image_width
            self._image_height = image_height
        finally:
            self._suppress_autosave = False

        self._save_state()
        self._refresh_displayed_coordinates()
        self._update_preview()