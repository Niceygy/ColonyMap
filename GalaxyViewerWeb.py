import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt, mpld3
from mpl_toolkits.mplot3d import Axes3D  # Add at the top with other imports

class GalaxyWebViewer():
    def __init__(self):
        self.data = None   
        self.load_data(Path("data/processed_galaxy_populated.json"))
        self.display_data()     
        
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
        except Exception as e:
            print(f"Error: Failed to load or process data: {e}")
            self.data = None
            
    def display_data(self):
        X = self.data['x']
        Y = self.data['y']
        Z = self.data['z']
        
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(X, Y, Z, s=1, c=Z, cmap='rainbow', alpha=0.5)
        mpld3.show()
        
if __name__ == "__main__":
        GalaxyWebViewer()
        # GalaxyWebViewer.display_data()