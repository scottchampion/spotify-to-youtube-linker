import csv
import os
import sys
import time
import subprocess
from datetime import datetime


# Global configuration for CSV column mapping
SEARCH_COLUMN_TRACK = 'Track Name'
SEARCH_COLUMN_ARTIST = 'Artist Name(s)'
TARGET_COLUMN = 'Youtube URL'


def get_youtube_url(track, artist):
    """
    Search YouTube for a track and artist using yt-dlp.
    Returns the first verified video URL or a status message.
    """
    # Remove quotes from search to prevent shell argument issues
    search_query = f"{track} {artist}".replace('"', '')
    
    # ytsearch5 allows the filter to look through the first 5 results
    # to find a verified channel before giving up.
    cmd = [
        'yt-dlp', 
        f"ytsearch5:{search_query}",
        '--match-filter', 'channel_is_verified',
        '--playlist-items', '1',
        '--print', '%(webpage_url)s',
        '--quiet', 
        '--no-warnings'
    ]
    
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        url = result.stdout.strip()
        return url if url else "NOT_FOUND"
    except Exception:
        # Catching timeouts or subprocess execution errors
        return "ERROR"


def main():
    """
    Handles file I/O, CLI arguments, and the main processing loop.
    """
    # Ensure user provided an input file
    if len(sys.argv) < 2:
        print("Usage: python3 script_name.py <input_file.csv>")
        return

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Create a unique filename to prevent overwriting previous runs
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name, extension = os.path.splitext(input_file)
    output_file = f"{base_name}_urls_{timestamp}{extension}"

    # Pre-scan file to provide a progress counter [1/Total]
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        total_records = sum(1 for line in f) - 1

    print("--- Starting Search ---")
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}\n")

    # Use 'utf-8-sig' to handle files exported with a Byte Order Mark (BOM)
    with open(input_file, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile, quotechar='"')
        
        # Prepare headers for the output file
        original_fields = [f.strip() for f in reader.fieldnames]
        if TARGET_COLUMN in original_fields:
            fieldnames = original_fields
        else:
            fieldnames = original_fields + [TARGET_COLUMN]

        with open(
            output_file, mode='w', encoding='utf-8', newline='', buffering=1
        ) as outfile:
            writer = csv.DictWriter(
                outfile, 
                fieldnames=fieldnames, 
                quotechar='"', 
                quoting=csv.QUOTE_ALL
            )
            writer.writeheader()
            
            count = 0
            for row in reader:
                count += 1
                # Standardize whitespace in keys/values
                clean_row = {k.strip(): v for k, v in row.items()}
                
                track = clean_row.get(SEARCH_COLUMN_TRACK, '')
                artist = clean_row.get(SEARCH_COLUMN_ARTIST, '')
                
                print(
                    f"[{count}/{total_records}] {track} - {artist}...", 
                    end=" ", 
                    flush=True
                )
                
                url = get_youtube_url(track, artist)
                print(f"{url}")
                
                clean_row[TARGET_COLUMN] = url
                writer.writerow(clean_row)
                
                # Prevent rate-limiting from YouTube search
                time.sleep(1.2)

    print(f"\nDone! Processed {count} songs.")
    print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    main()