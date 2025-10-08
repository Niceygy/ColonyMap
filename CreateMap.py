import json
import numpy
import math
import matplotlib.pyplot as plt

class ScatterPlotCreator:
    def process_to_array(file_name: str):
        result = []
        
        with open(file_name, "r") as f:
            data = json.load(f)
            
            length = len(data)
            current_item = 1
            
            for item in data:
                result.append([
                    item['coords']['x'],
                    item['coords']['y'],
                    item['population']
                ])
                
                percent = round((current_item / length) * 100)
                print(
                    f"\rProcessing to numpy array... ({current_item} / {length}, {percent}%)",
                    end='', flush=True
                    )
                current_item += 1            
            
            f.close()            
            result = numpy.array(result)
            return result
        
    def create_plot(array):
        print("Creating plot...")
        x = array[:, 0]
        y = array[:, 1]
        plt.scatter(x, y, s=1)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("System scatter plot")
        plt.savefig('plot_image.png', dpi=300)
        print("Plot saved as plot_image.png")
            
            
if __name__ == "__main__":
    array = ScatterPlotCreator.process_to_array("data/processed_galaxy_populated.json")
    ScatterPlotCreator.create_plot(array)
