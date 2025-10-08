import gzip
import os
import shutil
from pathlib import Path
from typing import List, Tuple, Optional

import requests
from requests.adapters import HTTPAdapter

# List of URLs to download and extract
# bless https://spansh.co.uk/dumps
TARGET_URLS: List[Tuple[str, str]] = [
    #TODO COMMENTED BECAUSE THEY ARE BIG AND LET'S BE RESPECTFUL :)
    #("https://downloads.spansh.co.uk/galaxy.json.gz", "galaxy.json"),
    #("https://downloads.spansh.co.uk/galaxy_populated.json.gz", "galaxy_populated.json"),
    #("https://downloads.spansh.co.uk/galaxy_1day.json.gz", "galaxy_1day.json") #TODO Only here because it's smaller probably not neeted
]


def _download_file(session: requests.Session, url: str, temp_gz_path: Path, total_size: Optional[int]) -> bool:
    """
    Downloads a file from a given URL to a temporary path with progress reporting.

    Args:
        session: The requests.Session object to use for the download.
        url: The URL of the file to download.
        temp_gz_path: The path to save the downloaded file to.
        total_size: The total size of the file in bytes, if known. Used for progress calculation.

    Returns:
        True if the download was successful, False otherwise.
    """
    print(f"Downloading to {temp_gz_path}...")
    try:
        # Use GET request with stream=True for efficiency on large files
        download_response = session.get(url, stream=True, timeout=300)
        download_response.raise_for_status()

        downloaded_bytes = 0
        chunk_size = 8192

        with open(temp_gz_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                downloaded_bytes += len(chunk)

                # Progress reporting logic using \r to overwrite the current line
                if total_size:
                    percent = (downloaded_bytes / total_size) * 100
                    # Update progress roughly every 1MB or on the final chunk
                    if downloaded_bytes % (1024 * 1024) < chunk_size or downloaded_bytes == total_size:
                        progress_msg = (
                            f"\rProgress: {downloaded_bytes / (1024 * 1024):.2f} MB / "
                            f"{total_size / (1024 * 1024):.2f} MB ({percent:.1f}%)"
                        )
                        print(progress_msg, end='', flush=True)
                else:
                    # Update progress every 10MB if total size is unknown
                    if downloaded_bytes % (10 * 1024 * 1024) < chunk_size:
                        print(f"\rDownloaded: {downloaded_bytes / (1024 * 1024):.2f} MB", end='', flush=True)

        # Ensure final progress print is complete and on a fresh line
        if total_size:
            final_msg = (
                f"\rProgress: {downloaded_bytes / (1024 * 1024):.2f} MB / "
                f"{total_size / (1024 * 1024):.2f} MB (100.0%)"
            )
            print(final_msg)
        else:
            print(f"\rDownloaded: {downloaded_bytes / (1024 * 1024):.2f} MB")

        print("Download successful.")
        return True

    except requests.exceptions.RequestException as e:
        print(f"\nERROR: Download failed for {url}: {e}")
        # Clean up potentially incomplete file
        if os.path.exists(temp_gz_path):
            os.remove(temp_gz_path)
        return False


def _extract_gzipped_file(temp_gz_path: Path, final_json_path: Path) -> None:
    """
    Extracts a gzipped file to a destination path.

    Args:
        temp_gz_path: The path to the gzipped file.
        final_json_path: The path to save the extracted file to.
    """
    print(f"Extracting to {final_json_path}...")
    try:
        with gzip.open(temp_gz_path, 'rb') as f_in, open(final_json_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        print(f"Extraction successful! Final file: {final_json_path.name}")
        os.remove(temp_gz_path)
        print(f"Cleaned up {temp_gz_path.name}")

    except OSError as e:
        print(f"ERROR: Extraction failed for {temp_gz_path.name}: {e}")


def download_and_extract_files(urls: List[Tuple[str, str]], output_dir: str = "data") -> None:
    """
    Checks if files at the given URLs exist, downloads them (streaming) with
    progress reporting, and extracts the gzipped JSON content to the specified
    output directory.

    Args:
        urls: A list of tuples, where each tuple contains a URL to a .json.gz file
              and the desired final .json filename.
        output_dir: The directory where the final .json files will be saved.
    """

    # Create the output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Output directory ensured: {output_path.resolve()}")

    # Set up retry mechanism for robustness
    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=3))
    session.mount('https://', HTTPAdapter(max_retries=3))

    for url, file_name_json in urls:
        file_name_gz = url.split("/")[-1]
        temp_gz_path = output_path / file_name_gz
        final_json_path = output_path / file_name_json

        if final_json_path.exists():
            print(f"File {final_json_path.name} already exists. Skipping download and extraction.")
            continue

        print("-" * 40)
        print(f"Processing URL: {url}")

        total_size = None

        # 1. Check Existence (using HEAD request) and get size
        try:
            response = session.head(url, timeout=10)
            response.raise_for_status()

            content_length = response.headers.get('Content-Length')
            if content_length:
                total_size = int(content_length)
                print(f"File confirmed existing. Size: {total_size / (1024 * 1024):.2f} MB (gzipped)")
            else:
                print("File confirmed existing (Content-Length header missing, progress will only show MB downloaded).")

        except requests.exceptions.HTTPError as e:
            print(f"ERROR: File not found or inaccessible (HTTP {e.response.status_code}) at {url}")
            continue
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Connection failed for {url}: {e}")
            continue

        # 2. Download the gzipped file
        if not _download_file(session, url, temp_gz_path, total_size):
            continue  # Skip to next file if download failed

        # 3. Extract the JSON content
        _extract_gzipped_file(temp_gz_path, final_json_path)

    print("-" * 40)
    print("All files processed.")


if __name__ == "__main__":
    # Run the main function
    download_and_extract_files(TARGET_URLS)
