import json
import sys
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
        Raises:
            FileNotFoundError: If the input file does not exist.
            FileExistsError: If the output file already exists.
            IOError: If there are permissions errors.
            ijson.JSONError: If the input file is not valid JSON.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found at {input_file}")

        if output_file.exists():
            raise FileExistsError(f"Output file already exists at {output_file}")

        try:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            # Test write permissions before starting the main processing
            with open(output_file, 'w') as f:
                pass
            os.remove(output_file)

        except OSError as e:
            raise IOError(f"Cannot write to directory {output_file.parent}: {e}")

        # Main processing block
        try:
            total_size = input_file.stat().st_size
            with open(input_file, 'rb') as f_in, open(output_file, 'w') as f_out:
                f_out.write('[' + '\n')

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
                            f_out.write(',' + '\n')

                        json.dump(processed_item, f_out, indent=4, cls=CustomJSONEncoder)
                        is_first_item = False
                        processed_count += 1

                        if processed_count % 10000 == 0:
                            bytes_read = f_in.tell()
                            percent = (bytes_read / total_size) * 100
                            print(
                                f"\rProcessing: {bytes_read / (1024 * 1024):.2f}MB / {total_size / (1024 * 1024):.2f}MB ({percent:.1f}%) - {processed_count} items",
                                end='', flush=True)

                final_progress = f"\rProcessing: {total_size / (1024 * 1024):.2f}MB / {total_size / (1024 * 1024):.2f}MB (100.0%) - {processed_count} items"
                print(final_progress)

                f_out.write('\n' + ']')
                print(f"Successfully saved to {output_file}")

        except (ijson.JSONError, OSError) as e:
            # Re-raise exceptions to be caught by the GUI
            raise e
        except Exception as e:
            # Wrap unexpected exceptions
            raise RuntimeError(f"An unexpected error occurred during processing: {e}")


if __name__ == "__main__":
    input_path = Path("data/galaxy_populated.json")
    output_path = Path("data/processed_galaxy_populated.json")
    try:
        GalaxyPopulatedProcessor.process_and_save(input_path, output_path)
    except (FileNotFoundError, FileExistsError, IOError, RuntimeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
