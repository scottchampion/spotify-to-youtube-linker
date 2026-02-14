import csv
import subprocess
import time
import os

INPUT_FILE = 'liked_songs_short.csv'
OUTPUT_FILE = 'liked_songs_short_with_urls.csv'
SEARCH_COLUMN_TRACK = 'Track Name'
SEARCH_COLUMN_ARTIST = 'Artist Name(s)'
TARGET_COLUMN = 'Youtube URL'

def get_youtube_url(track, artist):
    search_query = f"{track} {artist}".replace('"', '')
    cmd = [
        'yt-dlp', f"ytsearch5:{search_query}",
        '--match-filter', 'channel_is_verified',
        '--playlist-items', '1',
        '--print', '%(webpage_url)s',
        '--quiet', '--no-warnings'
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        url = result.stdout.strip()
        return url if url else "NOT_FOUND"
    except Exception:
        return "ERROR"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # --- NEW: Get total record count first ---
    with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
        # Subtract 1 for the header
        total_records = sum(1 for line in f) - 1

    with open(INPUT_FILE, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile, quotechar='"')
        
        original_fields = [f.strip() for f in reader.fieldnames]
        fieldnames = original_fields if TARGET_COLUMN in original_fields else original_fields + [TARGET_COLUMN]

        with open(OUTPUT_FILE, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writeheader()
            
            count = 0
            for row in reader:
                count += 1
                clean_row = {k.strip(): v for k, v in row.items()}
                
                track = clean_row.get(SEARCH_COLUMN_TRACK, '')
                artist = clean_row.get(SEARCH_COLUMN_ARTIST, '')
                
                # Dynamic progress output
                print(f"[{count}/{total_records}] Searching: {track} - {artist}")
                
                url = get_youtube_url(track, artist)
                clean_row[TARGET_COLUMN] = url
                writer.writerow(clean_row)
                
                time.sleep(1.5)

    print(f"\nFinished! Processed {count} records.")

if __name__ == "__main__":
    main()
