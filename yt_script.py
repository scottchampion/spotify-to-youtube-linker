import csv
import os
import sys
import time
from datetime import datetime
import yt_dlp

# Global configuration - Constants in SCREAMING_SNAKE_CASE
SEARCH_COL_TRACK = 'Track Name'
SEARCH_COL_ARTIST = 'Artist Name(s)'
TARGET_COL = 'Youtube URL'


def get_youtube_url(ydl, track, artist):
    """
    Search YouTube using the native yt_dlp instance.
    Returns the first result URL or a status message.
    """
    query = f"ytsearch5:{track} {artist}"

    try:
        # download=False only fetches metadata, making it very fast
        info = ydl.extract_info(query, download=False)

        if 'entries' in info and len(info['entries']) > 0:
            return info['entries'][0].get('url') or "NOT_FOUND"
        return "NOT_FOUND"
    except Exception as e:
        return f"ERROR: {str(e)}"


def main():
    """Main execution logic for Spotify to YouTube URL conversion."""
    if len(sys.argv) < 2:
        print("Usage: python3 script_name.py <input_file.csv>")
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Setup output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, _ = os.path.splitext(input_file)
    output_file = f"{base}_urls_{timestamp}.csv"

    # Engine Configuration
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'match_filter': yt_dlp.utils.match_filter_func('channel_is_verified'),
    }

    print(f"--- Starting Search (Branch: native-api) ---")
    print("Press Ctrl+C to stop at any time.\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            with open(input_file, mode='r', encoding='utf-8-sig') as infile:
                # Count records and rewind
                total_records = sum(1 for _ in infile) - 1
                infile.seek(0)
                
                reader = csv.DictReader(infile)
                fields = list(reader.fieldnames)
                if TARGET_COL not in fields:
                    fields.append(TARGET_COL)

                with open(output_file, 'w', encoding='utf-8', 
                          newline='', buffering=1) as out:
                    writer = csv.DictWriter(out, fieldnames=fields, 
                                            quoting=csv.QUOTE_ALL)
                    writer.writeheader()

                    for count, row in enumerate(reader, 1):
                        track = row.get(SEARCH_COL_TRACK, '').strip()
                        artist = row.get(SEARCH_COL_ARTIST, '').strip()

                        print(f"[{count}/{total_records}] {track}...", 
                              end=" ", flush=True)

                        url = get_youtube_url(ydl, track, artist)
                        print(f"{url}")

                        row[TARGET_COL] = url
                        writer.writerow(row)
                        time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[!] Search stopped by user. Progress saved to CSV.")
        sys.exit(0)

    print(f"\nSearch complete. Results saved to: {output_file}")


if __name__ == "__main__":
    main()