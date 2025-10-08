import json
import numpy
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # Add this import

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
        
    def create_plot(array):
        """Loads the array and creates a 3D scatter plot

        Args:
            array: from process_to_array
        """
        print("\nCreating plot...")
        x = array[:, 0]
        y = array[:, 1]
        z = array[:, 2]
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, s=1)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("System 3D scatter plot")
        plt.show()
            
            
if __name__ == "__main__":
    array = ScatterPlotCreator.process_to_array("data/processed_galaxy_populated.json")
    ScatterPlotCreator.create_plot(array)
