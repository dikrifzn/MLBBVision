# MLBBVision

MLBBVision is a lightweight desktop crop editor for Mobile Legends post-game screenshots.

## Stack

- Python 3.10+
- PySide6 Widgets
- OpenCV
- Pillow
- NumPy
- JSON

## Run

```bash
python main.py
```

## Notes

- Coordinates are stored in `coordinates.json`.
- Each variable maps to exactly one rectangle.
- Autosave is immediate after geometry or metadata changes.
