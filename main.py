from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from editor import Editor


def main() -> int:
	app = QApplication(sys.argv)
	window = Editor()
	window.show()
	return app.exec()


if __name__ == "__main__":
	raise SystemExit(main())