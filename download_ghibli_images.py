import requests
import os
import re
import sys

# The correct unofficial Ghibli API endpoint for films
API_URL = "https://ghibliapi.vercel.app/films"

# Directory where images will be saved
DOWNLOAD_DIR = "ghibli_movie_images"

def sanitize_filename(filename):
    """Removes characters that are invalid for filenames."""
    # Remove invalid characters like / \ : * ? " < > |
    sanitized = re.sub(r'[\\/*?:"<>|]', "", filename)
    # Replace spaces with underscores for better compatibility
    sanitized = sanitized.replace(" ", "_")
    # Reduce multiple underscores to a single one
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized

def download_image(url, filepath):
    """Downloads an image from a URL and saves it to a filepath."""
    try:
        response = requests.get(url, stream=True, timeout=15) # Added timeout
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Write the content to the file
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Successfully downloaded: {os.path.basename(filepath)}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}", file=sys.stderr)
        return False
    except IOError as e:
        print(f"Error writing file {filepath}: {e}", file=sys.stderr)
        return False

def fetch_and_download_ghibli_images():
    """Fetches film data from the Ghibli API and downloads images."""
    print(f"Fetching film data from {API_URL}...")

    try:
        response = requests.get(API_URL, timeout=10) # Added timeout
        response.raise_for_status() # Check if the request was successful
        films = response.json() # Parse JSON response into a Python list
        print(f"Found {len(films)} films.")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}", file=sys.stderr)
        sys.exit(1) # Exit if we can't get the film list
    except ValueError as e: # Catches JSON decoding errors
        print(f"Error parsing JSON response: {e}", file=sys.stderr)
        sys.exit(1)

    # Create the download directory if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"Images will be saved in directory: '{DOWNLOAD_DIR}'")

    download_count = 0
    error_count = 0

    # Iterate through each film in the list
    for film in films:
        title = film.get("title", "unknown_title")
        image_url = film.get("image") # This seems to be the poster image URL

        if not image_url:
            print(f"Warning: No image URL found for film: {title}", file=sys.stderr)
            continue # Skip to the next film if no image URL

        # Sanitize the film title to create a safe filename
        base_filename = sanitize_filename(title)
        # Try to get the file extension from the URL, default to .jpg
        file_extension = os.path.splitext(image_url)[1]
        if not file_extension:
            file_extension = ".jpg" # Default extension if none found

        # Construct the full path to save the image
        filepath = os.path.join(DOWNLOAD_DIR, f"{base_filename}{file_extension}")

        print(f"\nAttempting to download image for: {title}")
        print(f"Image URL: {image_url}")
        print(f"Saving to: {filepath}")

        # Download the image
        if download_image(image_url, filepath):
            download_count += 1
        else:
            error_count += 1

    print(f"\n--- Download Complete ---")
    print(f"Successfully downloaded {download_count} images.")
    if error_count > 0:
        print(f"Failed to download {error_count} images.")

# --- Main execution ---
if __name__ == "__main__":
    fetch_and_download_ghibli_images()