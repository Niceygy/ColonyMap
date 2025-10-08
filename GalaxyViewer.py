import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from PySide6.QtGui import QAction, QPalette, QColor
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from ProcessGalaxyPopulated import GalaxyPopulatedProcessor


class GalaxyViewer(QMainWindow):
    """
    An interactive GUI for viewing galaxy data with level-of-detail rendering, built with PySide6.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galaxy Map Viewer")
        self.setGeometry(100, 100, 1280, 800)

        self.data = None
        self.scatter_plot = None

        self._create_menu()
        self._create_plot_widget()

        # Connect the zoom/pan event to the update function
        self.ax.callbacks.connect('xlim_changed', self.on_zoom_pan)
        self.ax.callbacks.connect('ylim_changed', self.on_zoom_pan)

    def _create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open", self)
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("&Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_plot_widget(self):
        # Central widget to hold everything
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Matplotlib plot setup
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Style the plot for a dark theme
        plot_bg_color = '#1E1E1E'
        self.ax.set_facecolor('#000000')
        self.fig.set_facecolor(plot_bg_color)
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        # Set background color for the main window to match the plot figure
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(plot_bg_color))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select a processed galaxy data file",
            "./data",
            "JSON files (*.json);;All files (*.*)",
        )
        if file_path:
            self.load_data(Path(file_path))

    def load_data(self, file_path: Path):
        if not file_path.exists():
            QMessageBox.critical(self, "Error", f"File not found: {file_path}")
            return
        try:
            print("Loading data...")
            # Using pandas for efficient data handling
            df = pd.read_json(file_path)
            # Extract coordinates into separate columns for performance
            df['x'] = df['coords'].apply(lambda c: c['x'])
            df['y'] = df['coords'].apply(lambda c: c['y'])
            self.data = df
            print(f"Successfully loaded {len(self.data)} systems.")
            self.update_plot(initial_load=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load or process data: {e}")
            self.data = None

    def on_zoom_pan(self, ax):
        """Callback for when the user zooms or pans."""
        self.update_plot()

    def update_plot(self, initial_load=False):
        """
        Updates the plot based on the current zoom level (LOD).
        """
        if self.data is None:
            self.ax.clear()
            # Re-apply dark theme settings after clearing
            self.ax.set_facecolor('#000000')
            self.ax.tick_params(axis='x', colors='white')
            self.ax.tick_params(axis='y', colors='white')
            self.ax.spines['left'].set_color('white')
            self.ax.spines['right'].set_color('white')
            self.ax.spines['top'].set_color('white')
            self.ax.spines['bottom'].set_color('white')
            self.ax.xaxis.label.set_color('white')
            self.ax.yaxis.label.set_color('white')
            self.ax.set_title("No data loaded")
            self.canvas.draw_idle()
            self.scatter_plot = None # Ensure scatter_plot is reset
            return

        # Clear the axes before drawing new data
        self.ax.clear()
        # Re-apply dark theme settings after clearing
        self.ax.set_facecolor('#000000')
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.spines['left'].set_color('white')
        self.ax.spines['right'].set_color('white')
        self.ax.spines['top'].set_color('white')
        self.ax.spines['bottom'].set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')

        if initial_load:
            xlim = (self.data['x'].min(), self.data['x'].max())
            ylim = (self.data['y'].min(), self.data['y'].max())
            self.ax.set_xlim(xlim)
            self.ax.set_ylim(ylim)
        else:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()

        # Determine the number of points to display based on zoom level
        x_range = abs(xlim[1] - xlim[0])

        # Define LOD thresholds
        if x_range > 40000:  # Zoomed way out
            num_points = 2000
        elif x_range > 10000:  # Zoomed out
            num_points = 5000
        elif x_range > 1000:  # Medium zoom
            num_points = 10000
        else:  # Zoomed in
            num_points = len(self.data)  # Show all points when zoomed in enough

        # Filter data to the current view
        view_data = self.data[
            (self.data['x'] >= xlim[0]) & (self.data['x'] <= xlim[1]) &
            (self.data['y'] >= ylim[0]) & (self.data['y'] <= ylim[1])
            ]

        # Sample the data if necessary
        if len(view_data) > num_points:
            display_data = view_data.sample(n=num_points)
        else:
            display_data = view_data

        # Create new scatter plot (since axes were cleared)
        self.scatter_plot = self.ax.scatter(display_data['x'], display_data['y'], s=1, c='white', alpha=0.2)

        # Restore limits, as scatter can change them
        self.ax.set_xlim(xlim)
        self.ax.set_ylim(ylim)

        self.ax.set_title(f"Galaxy Map ({len(display_data)} of {len(view_data)} systems shown)")
        self.canvas.draw_idle()


if __name__ == "__main__":
    # Important: You may need to install pandas and PySide6:
    # pip install pandas PySide6

    app = QApplication(sys.argv)

    galaxy_populated_json = Path("data/galaxy_populated.json")
    processed_galaxy_populated_json = Path("data/processed_galaxy_populated.json")

    if not processed_galaxy_populated_json.exists():
        msg_box = QMessageBox()
        reply = msg_box.question(
            None,  # No parent widget
            "Processed Data Not Found",
            f"The processed data file was not found at:\n{processed_galaxy_populated_json}\n\n"
            f"Do you want to process the raw data file now?\n"
            f"(This may take a while)\n\n"
            f"Source: {galaxy_populated_json}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                print("Processing raw data... This may take a while.")
                GalaxyPopulatedProcessor.process_and_save(galaxy_populated_json, processed_galaxy_populated_json)
                QMessageBox.information(None, "Success", f"Successfully created processed data file at:\n{processed_galaxy_populated_json}")
            except (FileNotFoundError, FileExistsError, IOError, RuntimeError) as e:
                QMessageBox.critical(None, "Processing Error", f"An error occurred during processing:\n\n{e}")

    main_window = GalaxyViewer()
    main_window.show()

    if processed_galaxy_populated_json.exists():
        main_window.load_data(processed_galaxy_populated_json)
    else:
        if main_window.isVisible():
            QMessageBox.information(main_window, "Information", "No data loaded. Use File > Open to load a processed galaxy data file.")

    sys.exit(app.exec())
