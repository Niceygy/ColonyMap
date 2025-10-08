import json
from decimal import Decimal
from pathlib import Path
import ijson
import os




class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle Decimal objects.
    """
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


class GalaxyPopulatedProcessor:
    """
    Extracts only the data that we need from galaxy_populated.json giving us a MUCH
    smaller dataset (17gig down to 16 meg) to work with
    """
    @staticmethod
    def process_and_save(input_file: Path, output_file: Path) -> None:
        """
        Reads data from the input file in a stream, extracts the required fields,
        and saves them to the output file with progress reporting.
        """
        if not input_file.exists():
            print(f"ERROR: Input file not found at {input_file}")
            return

        if output_file.exists():
            print(f"ERROR: Output file already exists at {output_file}")
            return

        if not os.access(output_file.parent, os.W_OK):
            print(f"ERROR: Cannot write to directory {output_file.parent}")
            return

        try:
            total_size = input_file.stat().st_size
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(input_file, 'rb') as f_in, open(output_file, 'w') as f_out:
                f_out.write('[\n')

                processed_count = 0
                is_first_item = True
                items = ijson.items(f_in, 'item')

                for item in items:
                    if all(key in item for key in ['id64', 'name', 'coords', 'population']):
                        processed_item = {
                            'id64': item['id64'],
                            'name': item['name'],
                            'coords': item['coords'],
                            'population': item['population']
                        }

                        if not is_first_item:
                            f_out.write(',\n')

                        json.dump(processed_item, f_out, indent=4, cls=CustomJSONEncoder)
                        is_first_item = False
                        processed_count += 1

                        # Update progress every 10,000 items
                        if processed_count % 10000 == 0:
                            bytes_read = f_in.tell()
                            percent = (bytes_read / total_size) * 100
                            print(
                                f"\rProcessing: {bytes_read / (1024 * 1024):.2f}MB / {total_size / (1024 * 1024):.2f}MB ({percent:.1f}%) - {processed_count} items",
                                end='', flush=True)

                # Final progress update to show 100%
                final_progress = f"\rProcessing: {total_size / (1024 * 1024):.2f}MB / {total_size / (1024 * 1024):.2f}MB (100.0%) - {processed_count} items"
                print(final_progress)

                f_out.write('\n]')
                print(f"Successfully saved to {output_file}")

        except ijson.JSONError as e:
            print(f"\nERROR: Could not decode JSON from {input_file}: {e}")
        except OSError as e:
            print(f"\nERROR: Could not read from {input_file} or write to {output_file}: {e}")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    input_path = Path("data/galaxy_populated.json")
    output_path = Path("data/processed_galaxy_populated.json")
    GalaxyPopulatedProcessor.process_and_save(input_path, output_path)
