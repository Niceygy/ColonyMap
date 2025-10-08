# 3dPlotTest.py
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QFileDialog, QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Scatter Plot Viewer")
        self.setGeometry(100, 100, 1200, 800)
        self._createMenuBar()
        self._createMainWidget()

    def _createMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        saveAction = QAction("Save Plot", self)
        saveAction.triggered.connect(self.save_plot)
        fileMenu.addAction(saveAction)
        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def _createMainWidget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(8, 6)))
        layout.addWidget(self.canvas)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.plot_3d()

    def plot_3d(self):
        ax = self.canvas.figure.add_subplot(111, projection='3d')
        np.random.seed(42)
        X = np.random.rand(100)
        Y = np.random.rand(100)
        Z = np.random.rand(100)
        ax.scatter(X, Y, Z, c='r', marker='o')
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        ax.set_title('Basic 3D Scatter Plot')
        self.canvas.draw()

    def save_plot(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png);;All Files (*)", options=options)
        if filePath:
            self.canvas.figure.savefig(filePath)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PlotWindow()
    window.show()
    sys.exit(app.exec_())