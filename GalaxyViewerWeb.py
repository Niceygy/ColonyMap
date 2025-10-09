import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt, mpld3

class GalaxyWebViewer():
    def __init__(self):
        self.data = None
        
        
    def load_data(self, file_path: Path):
        if not file_path.exists():
            print(f"ERROR: Path does not exist: {file_path}")
            return
        try:
            print("Loading data...")
            # Using pandas for efficient data handling
            df = pd.read_json(file_path)
            # Extract coordinates into separate columns for performance
            df['x'] = df['coords'].apply(lambda c: c['x'])
            df['y'] = df['coords'].apply(lambda c: c['y'])
            df['z'] = df['coords'].apply(lambda c: c['z'])
            df['population'] = df['population']
            
            # Filter to systems within 10,000 LY of Sol
            df = df[(df['x'] < 10*1000) & (df['y'] < 10*1000) & (df['z'] < 10*1000)]
            
            self.data = df
            print(f"Successfully loaded {len(self.data)} systems.")
            self.update_plot(initial_load=True)
        except Exception as e:
            print(f"Error: Failed to load or process data: {e}")
            self.data = None
            
    def display_data(self):
        X = self.data['x']
        Y =
        Z = 
        
        plt.plot()
        mpld3.show()