import time
import duckdb
from pathlib import Path
import sys
from typing import Dict, Any

class SchemaFormatter:
    """
    Formats a DuckDB schema string into a readable, indented structure.
    """
    @staticmethod
    def format_and_print(schema: Dict[str, Any]):
        """Pretty-prints the entire schema dictionary."""
        print("--- Schema for galaxy.json ---")
        for name, dtype in schema.items():
            SchemaFormatter._print_field(name, dtype, "  ")
        print("------------------------------\n")

    @staticmethod
    def _print_field(name: str, dtype: str, indent: str):
        """Prints a single field, deciding whether to print on one line or multiple."""
        dtype = dtype.strip()
        is_complex = dtype.startswith("STRUCT(") or dtype.endswith("[]") or dtype.startswith("MAP(")

        if is_complex:
            print(f"{indent}{name}:")
            SchemaFormatter._print_type_details(dtype, indent + "  ")
        else:
            print(f"{indent}{name}: {dtype}")

    @staticmethod
    def _print_type_details(dtype: str, indent: str):
        """Prints the indented details for complex types (STRUCT, LIST, MAP)."""
        dtype = dtype.strip()
        if dtype.startswith("STRUCT("):
            print(f"{indent}STRUCT")
            content = dtype[len("STRUCT("):-1]
            SchemaFormatter._print_struct_fields(content, indent + "  ")
        elif dtype.endswith("[]"):
            print(f"{indent}LIST OF")
            SchemaFormatter._print_type_details(dtype[:-2], indent + "  ")
        elif dtype.startswith("MAP("):
            print(f"{indent}{dtype}")

    @staticmethod
    def _print_struct_fields(content: str, indent: str):
        """Parses and prints the fields within a STRUCT content string."""
        fields = []
        balance = 0
        last_split = 0
        for i, char in enumerate(content):
            if char == '(':
                balance += 1
            elif char == ')':
                balance -= 1
            elif char == ',' and balance == 0:
                fields.append(content[last_split:i])
                last_split = i + 1
        fields.append(content[last_split:])

        for field in fields:
            field = field.strip()
            if ' ' in field:
                name, dtype = field.split(' ', 1)
                SchemaFormatter._print_field(name, dtype, indent)

class DuckDBProcessor:
    """
    Uses DuckDB to efficiently process large JSON files.
    """
    @staticmethod
    def process_galaxy_data(input_file: Path, output_file: Path, output_format: str = 'json') -> None:
        """
        Queries a large JSON file to extract core system data.

        Args:
            input_file: Path to the large JSON file (e.g., galaxy.json).
            output_file: Path to save the output file.
            output_format: The desired output format ('json' or 'parquet').

        Raises:
            FileNotFoundError: If the input file does not exist.
            FileExistsError: If the output file already exists.
            ValueError: If the output format is not supported.
            RuntimeError: If an error occurs during DuckDB processing.
        """
        if output_format.lower() not in ['json', 'parquet']:
            raise ValueError(f"Unsupported output format: '{output_format}'. Must be 'json' or 'parquet'.")

        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if output_file.exists():
            raise FileExistsError(f"Output file already exists at {output_file}")

        output_file.parent.mkdir(parents=True, exist_ok=True)

        print(f"Starting processing of {input_file} with DuckDB...")
        try:
            con = duckdb.connect(database=':memory:', read_only=False)
            
            # Enable DuckDB's progress bar, which will print to stderr
            con.execute("PRAGMA enable_progress_bar=true;")

            query = f"""
            COPY (
                SELECT
                    id64,
                    name,
                    coords,
                    population
                FROM read_json_auto('{input_file}')
            ) TO '{output_file}' (FORMAT {output_format.upper()});
            """

            print(f"Executing DuckDB query to create {output_format.upper()} file...")
            con.execute(query)
            print(f"\nSuccessfully created galaxy data file at: {output_file}")

        except Exception as e:
            raise RuntimeError(f"An error occurred during DuckDB processing: {e}")
        finally:
            if 'con' in locals() and con:
                con.close()


    @staticmethod
    def get_json_schema(input_file: Path) -> Dict[str, Any]:
        """
        Infers and returns the schema of a JSON file using DuckDB.
        """
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        print(f"Inferring schema for {input_file}...")
        try:
            con = duckdb.connect(database=':memory:', read_only=False)
            # The DESCRIBE statement is perfect for quickly getting the schema
            query = f"DESCRIBE SELECT * FROM read_json_auto('{input_file}');"
            result = con.execute(query).fetchall()

            # The result is a list of tuples, convert it to a more friendly dictionary
            schema = {row[0]: str(row[1]) for row in result}
            return schema

        except Exception as e:
            raise RuntimeError(f"An error occurred while inferring schema: {e}")
        finally:
            if 'con' in locals() and con:
                con.close()


def print_schema(input_path: Path = Path("data/galaxy.json")):
    global e
    try:
        schema = DuckDBProcessor.get_json_schema(input_path)
        SchemaFormatter.format_and_print(schema)
    except (FileNotFoundError, RuntimeError) as e:
        print(f"ERROR getting schema: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    input_galaxy_path = Path("data/galaxy.json")
    input_galaxy_populated_path = Path("data/galaxy_populated.json")

    output_galaxy_path = Path("data/processed_galaxy.json")
    output_galaxy_populated_path = Path("data/processed_galaxy_populated.json")
    file_format = 'json'

    print_schema()

    files_to_process = [
        (input_galaxy_populated_path, output_galaxy_populated_path),
        (input_galaxy_path, output_galaxy_path)
    ]

    for input_path, output_path in files_to_process:
        try:
            print(f"--- Processing {input_path} ---")
            start_time = time.time()
            DuckDBProcessor.process_galaxy_data(input_path, output_path, output_format=file_format)
            end_time = time.time()
            elapsed_seconds = end_time - start_time
            minutes, seconds = divmod(elapsed_seconds, 60)
            print(f"Processing took {int(minutes)} minutes and {int(seconds)} seconds.\n")
        except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as e:
            print(f"ERROR processing {input_path}: {e}\n", file=sys.stderr)

    sys.exit(0)
