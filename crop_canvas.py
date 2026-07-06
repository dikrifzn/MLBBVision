from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView

from crop_object import CropObject
from crop_rect_item import CropRectItem


DEFAULT_RECT_SIZE = 72
DEFAULT_DUPLICATE_OFFSET = 24
MIN_ZOOM_FACTOR = 0.35
MAX_ZOOM_FACTOR = 4.0
EMPTY_SCENE_WIDTH = 640
EMPTY_SCENE_HEIGHT = 360


class CropCanvas(QGraphicsView):

    objectSelected = Signal(str)
    geometryChanged = Signal(str, int, int, int, int)
    objectsChanged = Signal()
    imageChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self._image_pixmap = QPixmap()
        self._image_item: QGraphicsPixmapItem | None = None
        self._objects: dict[str, CropObject] = {}
        self._items: dict[str, CropRectItem] = {}
        self._selected_name: str | None = None

        self._panning = False
        self._pan_start_position = QPointF()
        self._horizontal_scroll_start = 0
        self._vertical_scroll_start = 0
        self._zoom_factor = 1.0

        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(self.DragMode.NoDrag)
        self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(self.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QColor(28, 28, 28))
        self.setMouseTracking(True)

        self._scene.selectionChanged.connect(self._on_scene_selection_changed)

    def load_image(self, file_path: str) -> bool:
        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            return False

        self._image_pixmap = pixmap
        self._rebuild_scene(reset_zoom=True)
        self.imageChanged.emit()
        return True

    def image_pixmap(self) -> QPixmap:
        return QPixmap(self._image_pixmap)

    def image_size(self) -> tuple[int, int]:
        return self._image_pixmap.width(), self._image_pixmap.height()

    def set_objects(self, objects: dict[str, CropObject]) -> None:
        self._objects = objects
        self._rebuild_scene(reset_zoom=False)
        self.objectsChanged.emit()

    def objects(self) -> dict[str, CropObject]:
        return self._objects

    def selected_object(self) -> CropObject | None:
        if self._selected_name is None:
            return None
        return self._objects.get(self._selected_name)

    def selected_name(self) -> str | None:
        return self._selected_name

    def export_coordinates(self) -> dict[str, list[int]]:
        return {name: crop_object.as_coordinates() for name, crop_object in self._objects.items()}

    def make_unique_name(self, desired_name: str) -> str:
        base_name = desired_name.strip() or "variable"
        if base_name not in self._objects:
            return base_name

        index = 2
        while True:
            candidate_name = f"{base_name}_{index}"
            if candidate_name not in self._objects:
                return candidate_name
            index += 1

    def default_spawn_geometry(self) -> tuple[int, int, int, int]:
        width = DEFAULT_RECT_SIZE
        height = DEFAULT_RECT_SIZE

        if self._selected_name and self._selected_name in self._objects:
            selected_object = self._objects[self._selected_name]
            return (
                selected_object.x + DEFAULT_DUPLICATE_OFFSET,
                selected_object.y + DEFAULT_DUPLICATE_OFFSET,
                width,
                height,
            )

        scene_center = self.mapToScene(self.viewport().rect().center())
        x = int(round(scene_center.x() - width / 2))
        y = int(round(scene_center.y() - height / 2))
        return x, y, width, height

    def add_object(self, crop_object: CropObject) -> CropObject:
        unique_name = self.make_unique_name(crop_object.name)
        crop_object.name = unique_name
        self._objects[unique_name] = crop_object

        item = self._create_item(crop_object)
        self._items[unique_name] = item
        self._scene.addItem(item)

        self._update_scene_rect()
        self.select_object(unique_name)
        self.objectsChanged.emit()
        return crop_object

    def remove_object(self, name: str) -> None:
        item = self._items.pop(name, None)
        if item is not None:
            self._scene.removeItem(item)

        self._objects.pop(name, None)

        if self._selected_name == name:
            self._selected_name = None
            self.objectSelected.emit("")

        self._update_scene_rect()
        self.objectsChanged.emit()

    def rename_object(self, old_name: str, desired_name: str) -> str:
        if old_name not in self._objects:
            return old_name

        unique_name = self.make_unique_name(desired_name)
        if unique_name == old_name:
            return old_name

        crop_object = self._objects.pop(old_name)
        item = self._items.pop(old_name)

        crop_object.name = unique_name
        self._objects[unique_name] = crop_object
        self._items[unique_name] = item

        if self._selected_name == old_name:
            self._selected_name = unique_name

        item.crop_object = crop_object
        item.sync_from_object(notify=False)

        item.crop_object = crop_object
        item.update()
        self.objectsChanged.emit()
        return unique_name

    def set_visibility(self, name: str, visible: bool) -> None:
        crop_object = self._objects.get(name)
        item = self._items.get(name)
        if crop_object is None or item is None:
            return

        crop_object.visible = visible
        item.setVisible(visible)
        self.objectsChanged.emit()

    def update_object_geometry(self, name: str, x: int, y: int, width: int, height: int) -> None:
        item = self._items.get(name)
        crop_object = self._objects.get(name)
        if item is None or crop_object is None:
            return

        item.apply_geometry(x, y, width, height, notify=False)
        self.geometryChanged.emit(name, crop_object.x, crop_object.y, crop_object.width, crop_object.height)
        self.objectsChanged.emit()
        self._update_scene_rect()

    def select_object(self, name: str) -> None:
        if name not in self._items:
            self.clear_selection()
            return

        self._scene.blockSignals(True)
        self._scene.clearSelection()
        self._scene.blockSignals(False)

        item = self._items[name]
        item.setSelected(True)
        self._selected_name = name

        for crop_name, crop_object in self._objects.items():
            crop_object.selected = crop_name == name

        self.objectSelected.emit(name)

    def clear_selection(self) -> None:
        self._scene.clearSelection()
        self._selected_name = None
        for crop_object in self._objects.values():
            crop_object.selected = False
        self.objectSelected.emit("")

    def duplicate_selected(self) -> CropObject | None:
        selected_object = self.selected_object()
        if selected_object is None:
            return None

        duplicate_name = self.make_unique_name(f"{selected_object.name}_copy")
        duplicate_object = selected_object.copy(duplicate_name)
        return self.add_object(duplicate_object)

    def _create_item(self, crop_object: CropObject) -> CropRectItem:
        item = CropRectItem(
            crop_object=crop_object,
            bounds_provider=self._scene_bounds,
            geometry_changed_callback=self._on_item_geometry_changed,
        )
        item.setZValue(1.0)
        return item

    def _rebuild_scene(self, reset_zoom: bool) -> None:
        selected_name = self._selected_name

        self._scene.blockSignals(True)
        self._scene.clear()
        self._items.clear()

        if not self._image_pixmap.isNull():
            self._image_item = self._scene.addPixmap(self._image_pixmap)
            self._image_item.setZValue(0.0)
        else:
            self._image_item = None

        for name, crop_object in self._objects.items():
            item = self._create_item(crop_object)
            self._items[name] = item
            self._scene.addItem(item)

        self._scene.blockSignals(False)

        self._update_scene_rect()

        if selected_name and selected_name in self._items:
            self._items[selected_name].setSelected(True)
            self._selected_name = selected_name
        else:
            self._selected_name = None

        if reset_zoom:
            self.resetTransform()
            if not self._scene.sceneRect().isNull():
                self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def _scene_bounds(self) -> QRectF:
        if not self._image_pixmap.isNull():
            return QRectF(0.0, 0.0, float(self._image_pixmap.width()), float(self._image_pixmap.height()))

        scene_rect = self._scene.sceneRect()
        if scene_rect.isValid() and scene_rect.width() > 0 and scene_rect.height() > 0:
            return scene_rect

        return QRectF(0.0, 0.0, float(EMPTY_SCENE_WIDTH), float(EMPTY_SCENE_HEIGHT))

    def _update_scene_rect(self) -> None:
        self._scene.setSceneRect(self._scene_bounds())

    def _on_item_geometry_changed(self, crop_object: CropObject) -> None:
        self._objects[crop_object.name] = crop_object
        self.geometryChanged.emit(crop_object.name, crop_object.x, crop_object.y, crop_object.width, crop_object.height)
        self.objectsChanged.emit()
        self._update_scene_rect()

    def _on_scene_selection_changed(self) -> None:
        selected_items = [item for item in self._scene.selectedItems() if isinstance(item, CropRectItem)]
        selected_name = selected_items[0].crop_object.name if selected_items else None

        self._selected_name = selected_name
        for crop_object in self._objects.values():
            crop_object.selected = crop_object.name == selected_name

        self.objectSelected.emit(selected_name or "")

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start_position = event.position()
            self._horizontal_scroll_start = self.horizontalScrollBar().value()
            self._vertical_scroll_start = self.verticalScrollBar().value()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._panning:
            delta = event.position() - self._pan_start_position
            self.horizontalScrollBar().setValue(int(self._horizontal_scroll_start - delta.x()))
            self.verticalScrollBar().setValue(int(self._vertical_scroll_start - delta.y()))
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.unsetCursor()
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def wheelEvent(self, event) -> None:  # type: ignore[override]
        if not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
            super().wheelEvent(event)
            return

        zoom_in = event.angleDelta().y() > 0
        zoom_multiplier = 1.15 if zoom_in else 0.87
        next_zoom = self._zoom_factor * zoom_multiplier

        if next_zoom < MIN_ZOOM_FACTOR or next_zoom > MAX_ZOOM_FACTOR:
            return

        self._zoom_factor = next_zoom
        self.scale(zoom_multiplier, zoom_multiplier)
        event.accept()