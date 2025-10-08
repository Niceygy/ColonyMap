import json
import sys

import numpy
from PyQt5.QtWidgets import QFileDialog, QApplication, QWidget, QVBoxLayout, QAction, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ScatterPlotCreator:
    def process_to_array(file_name: str):
        """
        Processes the JSON to a numpy 
        array that matplotlib can understand

        Args:
            file_name (str): JSON File name 

        Returns:
            array
        """
        result = []
        
        with open(file_name, "r") as f:
            data = json.load(f)
            
            length = len(data)
            current_item = 1
            
            for item in data:
                result.append([
                    item['coords']['x'],
                    item['coords']['y'],
                    item['coords']['z'],
                    item['population']
                ])
                
                percent = round((current_item / length) * 100)
                print(
                    f"\rProcessing to array... ({current_item} / {length}, {percent}%)",
                    end='', flush=True
                    )
                current_item += 1            
            
            f.close()            
            result = numpy.array(result)
            return result
        
    # def create_plot(array):
    #     """Loads the array and creates a 3D scatter plot
    #
    #     Args:
    #         array: from process_to_array
    #     """
    #     print("\nCreating plot...")
    #     x = array[:, 0]
    #     y = array[:, 1]
    #     z = array[:, 2]
    #     fig = plt.figure(figsize=(19.2, 10.8))
    #     ax = fig.add_subplot(111, projection='3d')
    #     ax.scatter(x, y, z, s=1)
    #     ax.set_xlabel("X")
    #     ax.set_ylabel("Y")
    #     ax.set_zlabel("Z")
    #     ax.set_title("System 3D scatter plot")
    #     # plt.show()
    #     plt.savefig("System 3D scatter plot.png", dpi=100)
    #     plt.close()

class PlotWindow(QMainWindow):
    def __init__(self, array):
        super().__init__()
        self.setWindowTitle("System 3D scatter plot")
        self.setGeometry(100, 100, 1200, 800)
        self._createMenuBar()
        self._createMainWidget(array)

    def _createMenuBar(self):
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("File")
        saveAction = QAction("Save Plot", self)
        saveAction.triggered.connect(self.save_plot)
        fileMenu.addAction(saveAction)
        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

    def _createMainWidget(self, array):
        widget = QWidget()
        layout = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(8, 6)))
        layout.addWidget(self.canvas)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.plot_3d(array)

    def plot_3d(self, array):
        ax = self.canvas.figure.add_subplot(111, projection='3d')
        x = array[:, 0]
        y = array[:, 1]
        z = array[:, 2]
        ax.scatter(x, y, z, s=1)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("System 3D scatter plot")
        self.canvas.draw()

    def save_plot(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Plot", "", "PNG Files (*.png);;All Files (*)", options=options)
        if filePath:
            self.canvas.figure.savefig(filePath, dpi=100)


if __name__ == "__main__":
    array = ScatterPlotCreator.process_to_array("data/processed_galaxy_populated.json")
    app = QApplication(sys.argv)
    window = PlotWindow(array)
    window.show()
    sys.exit(app.exec_())

