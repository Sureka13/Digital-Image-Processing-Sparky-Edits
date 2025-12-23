"""
Sparky Edits - Digital Image Processing Application
Author: Surekadevi A/P Shanmuganathan
Tech Stack: Python, PyQt5, OpenCV
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt


class SparkyEdits(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sparky Edits - Image Processing Application")
        self.setGeometry(200, 200, 1000, 700)

        label = QLabel("Sparky Edits\nDigital Image Processing Application", self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px;")
        self.setCentralWidget(label)


def main():
    app = QApplication(sys.argv)
    window = SparkyEdits()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

