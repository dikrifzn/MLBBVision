from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CropObject:
    name: str
    x: int
    y: int
    width: int
    height: int
    visible: bool = True
    selected: bool = False

    def as_coordinates(self) -> list[int]:
        return [int(self.x), int(self.y), int(self.width), int(self.height)]

    def update_geometry(self, x: int, y: int, width: int, height: int) -> None:
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def copy(self, name: str, offset_x: int = 24, offset_y: int = 24) -> "CropObject":
        return CropObject(
            name=name,
            x=self.x + offset_x,
            y=self.y + offset_y,
            width=self.width,
            height=self.height,
            visible=self.visible,
            selected=False,
        )