from __future__ import annotations

from collections.abc import Callable
from enum import Enum, auto

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QBrush, QCursor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsRectItem

from crop_object import CropObject


MIN_RECT_SIZE = 12
HANDLE_MARGIN = 6
HANDLE_SIZE = 7


def color_for_variable_name(name: str) -> QColor:
    lowered_name = name.lower()

    if "hero" in lowered_name:
        return QColor(46, 204, 113)
    if "item" in lowered_name:
        return QColor(52, 152, 219)
    if "gold" in lowered_name:
        return QColor(241, 196, 15)
    if "kda" in lowered_name:
        return QColor(231, 76, 60)
    if "name" in lowered_name:
        return QColor(26, 188, 156)

    return QColor(230, 126, 34)


class InteractionMode(Enum):
    NONE = auto()
    MOVE = auto()
    RESIZE_LEFT = auto()
    RESIZE_RIGHT = auto()
    RESIZE_TOP = auto()
    RESIZE_BOTTOM = auto()
    RESIZE_TOP_LEFT = auto()
    RESIZE_TOP_RIGHT = auto()
    RESIZE_BOTTOM_LEFT = auto()
    RESIZE_BOTTOM_RIGHT = auto()


class CropRectItem(QGraphicsRectItem):

    def __init__(
        self,
        crop_object: CropObject,
        bounds_provider: Callable[[], QRectF],
        geometry_changed_callback: Callable[[CropObject], None],
    ) -> None:
        super().__init__()

        self.crop_object = crop_object
        self._bounds_provider = bounds_provider
        self._geometry_changed_callback = geometry_changed_callback

        self._interaction_mode = InteractionMode.NONE
        self._press_scene_pos = QPointF()
        self._start_position = QPointF()
        self._start_rect = QRectF()

        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)
        self.setPen(self._make_pen())
        self.setBrush(self._make_brush())
        self.sync_from_object(notify=False)

    def sync_from_object(self, notify: bool = False) -> None:
        self.setVisible(self.crop_object.visible)
        self.setPos(float(self.crop_object.x), float(self.crop_object.y))
        self.setRect(0.0, 0.0, float(self.crop_object.width), float(self.crop_object.height))
        self.setPen(self._make_pen())
        self.setBrush(self._make_brush())
        self.update()

        if notify:
            self._geometry_changed_callback(self.crop_object)

    def apply_geometry(self, x: float, y: float, width: float, height: float, notify: bool = True) -> None:
        x, y, width, height = self._clamp_geometry(x, y, width, height)

        self.setPos(x, y)
        self.setRect(0.0, 0.0, width, height)

        self.crop_object.update_geometry(int(round(x)), int(round(y)), int(round(width)), int(round(height)))
        self.setPen(self._make_pen())
        self.setBrush(self._make_brush())
        self.update()

        if notify:
            self._geometry_changed_callback(self.crop_object)

    def _make_pen(self) -> QPen:
        pen_color = color_for_variable_name(self.crop_object.name)
        if self.isSelected():
            pen_color = pen_color.lighter(130)

        pen = QPen(pen_color)
        pen.setWidth(2)
        return pen

    def _make_brush(self) -> QBrush:
        base_color = color_for_variable_name(self.crop_object.name)
        return QBrush(QColor(base_color.red(), base_color.green(), base_color.blue(), 45))

    def _clamp_geometry(self, x: float, y: float, width: float, height: float) -> tuple[float, float, float, float]:
        width = max(float(MIN_RECT_SIZE), float(width))
        height = max(float(MIN_RECT_SIZE), float(height))

        bounds = self._bounds_provider()
        if not bounds.isValid() or bounds.width() <= 0 or bounds.height() <= 0:
            return x, y, width, height

        max_width = max(float(MIN_RECT_SIZE), bounds.width())
        max_height = max(float(MIN_RECT_SIZE), bounds.height())

        width = min(width, max_width)
        height = min(height, max_height)

        left = bounds.left()
        top = bounds.top()
        right = bounds.right() - width
        bottom = bounds.bottom() - height

        if right < left:
            x = left
            width = bounds.width()
        else:
            x = min(max(x, left), right)

        if bottom < top:
            y = top
            height = bounds.height()
        else:
            y = min(max(y, top), bottom)

        return x, y, width, height

    def _interaction_mode_for_point(self, point: QPointF) -> InteractionMode:
        rect = self.rect()
        near_left = point.x() <= HANDLE_MARGIN
        near_right = point.x() >= rect.width() - HANDLE_MARGIN
        near_top = point.y() <= HANDLE_MARGIN
        near_bottom = point.y() >= rect.height() - HANDLE_MARGIN

        if near_left and near_top:
            return InteractionMode.RESIZE_TOP_LEFT
        if near_right and near_top:
            return InteractionMode.RESIZE_TOP_RIGHT
        if near_left and near_bottom:
            return InteractionMode.RESIZE_BOTTOM_LEFT
        if near_right and near_bottom:
            return InteractionMode.RESIZE_BOTTOM_RIGHT
        if near_left:
            return InteractionMode.RESIZE_LEFT
        if near_right:
            return InteractionMode.RESIZE_RIGHT
        if near_top:
            return InteractionMode.RESIZE_TOP
        if near_bottom:
            return InteractionMode.RESIZE_BOTTOM

        return InteractionMode.MOVE

    def _cursor_for_mode(self, mode: InteractionMode) -> Qt.CursorShape:
        if mode in {InteractionMode.RESIZE_TOP_LEFT, InteractionMode.RESIZE_BOTTOM_RIGHT}:
            return Qt.CursorShape.SizeFDiagCursor
        if mode in {InteractionMode.RESIZE_TOP_RIGHT, InteractionMode.RESIZE_BOTTOM_LEFT}:
            return Qt.CursorShape.SizeBDiagCursor
        if mode in {InteractionMode.RESIZE_LEFT, InteractionMode.RESIZE_RIGHT}:
            return Qt.CursorShape.SizeHorCursor
        if mode in {InteractionMode.RESIZE_TOP, InteractionMode.RESIZE_BOTTOM}:
            return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.SizeAllCursor

    def hoverMoveEvent(self, event) -> None:  # type: ignore[override]
        self.setCursor(QCursor(self._cursor_for_mode(self._interaction_mode_for_point(event.pos()))))
        super().hoverMoveEvent(event)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self._interaction_mode = self._interaction_mode_for_point(event.pos())
            self._press_scene_pos = event.scenePos()
            self._start_position = QPointF(self.pos())
            self._start_rect = QRectF(self.rect())
            self.setCursor(QCursor(self._cursor_for_mode(self._interaction_mode)))

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._interaction_mode == InteractionMode.NONE or not (event.buttons() & Qt.MouseButton.LeftButton):
            super().mouseMoveEvent(event)
            return

        delta = event.scenePos() - self._press_scene_pos
        start_x = self._start_position.x()
        start_y = self._start_position.y()
        start_width = self._start_rect.width()
        start_height = self._start_rect.height()

        new_x = start_x
        new_y = start_y
        new_width = start_width
        new_height = start_height

        if self._interaction_mode == InteractionMode.MOVE:
            new_x = start_x + delta.x()
            new_y = start_y + delta.y()
        elif self._interaction_mode == InteractionMode.RESIZE_LEFT:
            new_x = start_x + delta.x()
            new_width = start_width - delta.x()
        elif self._interaction_mode == InteractionMode.RESIZE_RIGHT:
            new_width = start_width + delta.x()
        elif self._interaction_mode == InteractionMode.RESIZE_TOP:
            new_y = start_y + delta.y()
            new_height = start_height - delta.y()
        elif self._interaction_mode == InteractionMode.RESIZE_BOTTOM:
            new_height = start_height + delta.y()
        elif self._interaction_mode == InteractionMode.RESIZE_TOP_LEFT:
            new_x = start_x + delta.x()
            new_width = start_width - delta.x()
            new_y = start_y + delta.y()
            new_height = start_height - delta.y()
        elif self._interaction_mode == InteractionMode.RESIZE_TOP_RIGHT:
            new_width = start_width + delta.x()
            new_y = start_y + delta.y()
            new_height = start_height - delta.y()
        elif self._interaction_mode == InteractionMode.RESIZE_BOTTOM_LEFT:
            new_x = start_x + delta.x()
            new_width = start_width - delta.x()
            new_height = start_height + delta.y()
        elif self._interaction_mode == InteractionMode.RESIZE_BOTTOM_RIGHT:
            new_width = start_width + delta.x()
            new_height = start_height + delta.y()

        self.apply_geometry(new_x, new_y, new_width, new_height, notify=True)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        self._interaction_mode = InteractionMode.NONE
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        super().mouseReleaseEvent(event)

    def paint(self, painter: QPainter, option, widget=None) -> None:  # type: ignore[override]
        super().paint(painter, option, widget)

        if not self.isSelected():
            return

        painter.save()
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255)))

        for handle_rect in self._handle_rects():
            painter.drawRect(handle_rect)

        painter.restore()

    def _handle_rects(self) -> list[QRectF]:
        rect = self.rect()
        handle_half = HANDLE_SIZE / 2

        def handle_center(x: float, y: float) -> QRectF:
            return QRectF(x - handle_half, y - handle_half, HANDLE_SIZE, HANDLE_SIZE)

        return [
            handle_center(rect.left(), rect.top()),
            handle_center(rect.center().x(), rect.top()),
            handle_center(rect.right(), rect.top()),
            handle_center(rect.left(), rect.center().y()),
            handle_center(rect.right(), rect.center().y()),
            handle_center(rect.left(), rect.bottom()),
            handle_center(rect.center().x(), rect.bottom()),
            handle_center(rect.right(), rect.bottom()),
        ]