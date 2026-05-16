"""
Flask API for the Mariah Carey Music Videos Database.
Provides endpoints for searching, filtering, and managing music videos.
"""

import os
import re
import sys
import logging
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure backend directory is in path for imports
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from google_sheets import get_all_videos, get_video_by_id, add_video, update_video, delete_video
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend"))
CORS(app)

# Thumbnail upload configuration
THUMBNAIL_FOLDER = os.path.join(os.path.dirname(__file__), "thumbnails")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
MAX_THUMBNAIL_SIZE = 5 * 1024 * 1024  # 5MB
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Fields that can be searched/filtered
SEARCH_FIELDS = ["Name", "Display Name", "Version Name", "Director", "Director of Photography",
                 "Producer", "Editor", "Video Type", "Video Category", "Record Location", "Note"]
FILTER_FIELDS = ["Video Type", "Video Category", "Director", "Director of Photography",
                 "Record Location", "Album"]
YEAR_FIELD = "Release Date (US)"

MONTH_MAP = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}


def parse_date(date_str):
    """
    Parse a date string like 'February 19, 2010' or 'April 15, 2005'
    into a sortable tuple (year, month, day).
    Returns (9999, 99, 99) for unparseable dates so they sort last.
    """
    if not date_str or not date_str.strip():
        return (9999, 99, 99)

    date_str = date_str.strip()

    # Try "Month Day, Year" format (e.g., "February 19, 2010")
    match = re.match(r"([a-zA-Z]+)\s+(\d{1,2}),?\s+(\d{4})", date_str)
    if match:
        month_name = match.group(1).lower()
        day = int(match.group(2))
        year = int(match.group(3))
        month = MONTH_MAP.get(month_name)
        if month:
            return (year, month, day)

    # Try "Month Year" format (e.g., "December 2001")
    match = re.match(r"([a-zA-Z]+)\s+(\d{4})", date_str)
    if match:
        month_name = match.group(1).lower()
        year = int(match.group(2))
        month = MONTH_MAP.get(month_name)
        if month:
            return (year, month, 1)

    # Try just "Year" format
    match = re.match(r"(\d{4})", date_str)
    if match:
        return (int(match.group(1)), 1, 1)

    return (9999, 99, 99)


@app.route("/api/videos", methods=["GET"])
def list_videos():
    """
    Get all music videos with optional search and filtering.
    
    Query parameters:
    - search: Search term across multiple text fields
    - video_type: Filter by Video Type
    - video_category: Filter by Video Category
    - director: Filter by Director
    - sort: Sort field name
    - order: Sort order (asc or desc)
    """
    try:
        videos = get_all_videos()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Apply text search
    search = request.args.get("search", "").lower().strip()
    if search:
        filtered = []
        for v in videos:
            searchable = " ".join(
                str(v.get(field, "")).lower() for field in SEARCH_FIELDS
            )
            if search in searchable:
                filtered.append(v)
        videos = filtered

    # Apply field filters
    for field in FILTER_FIELDS:
        param_key = field.lower().replace(" ", "_").replace("-", "_")
        value = request.args.get(param_key, "").strip().lower()
        if value:
            videos = [
                v for v in videos
                if value in str(v.get(field, "")).lower()
            ]

    # Year filter (extracted from Release Date (US) field)
    year = request.args.get("year", "").strip()
    if year:
        videos = [
            v for v in videos
            if str(v.get(YEAR_FIELD, "")).strip().endswith(year)
        ]

    # Sorting
    sort = request.args.get("sort", "").strip()
    order = request.args.get("order", "asc").strip().lower()

    if sort and videos:
        reverse = order == "desc"
        try:
            if sort == YEAR_FIELD:
                # Use proper date parsing for date sorting
                videos.sort(
                    key=lambda x: parse_date(x.get(sort, "")),
                    reverse=reverse,
                )
            else:
                videos.sort(
                    key=lambda x: (str(x.get(sort, "") or "").lower()),
                    reverse=reverse,
                )
        except Exception:
            pass  # If sorting fails, return unsorted

    return jsonify(videos)


@app.route("/api/videos/<video_id>", methods=["GET"])
def get_video(video_id):
    """Get a single music video by its row index."""
    try:
        video = get_video_by_id(video_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if video:
        return jsonify(video)
    return jsonify({"error": "Video not found"}), 404


@app.route("/api/videos", methods=["POST"])
def create_video():
    """Add a new music video."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    if "Name" not in data or not data.get("Name", "").strip():
        return jsonify({"error": "'Name' is required"}), 400

    try:
        result = add_video(data)
        return jsonify(result), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/videos/<video_id>", methods=["PUT"])
def edit_video(video_id):
    """Update an existing music video."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        result = update_video(video_id, data)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/videos/<video_id>", methods=["DELETE"])
def remove_video(video_id):
    """Delete a music video."""
    try:
        result = delete_video(video_id)
        if "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/filters", methods=["GET"])
def get_filter_options():
    """Get distinct filter options for dropdowns."""
    try:
        videos = get_all_videos()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    filter_data = {}
    for field in FILTER_FIELDS:
        values = sorted(set(
            str(v.get(field, "")).strip()
            for v in videos
            if v.get(field, "").strip()
        ))
        filter_data[field.lower().replace(" ", "_").replace("-", "_")] = values

    # Extract unique years from Release Date (US)
    years = sorted(set(
        str(v.get(YEAR_FIELD, "")).strip()[-4:]
        for v in videos
        if v.get(YEAR_FIELD, "").strip() and str(v.get(YEAR_FIELD, "")).strip()[-4:].isdigit()
    ), reverse=True)
    filter_data["years"] = years

    return jsonify(filter_data)


# Thumbnail upload endpoint
@app.route("/api/upload-thumbnail", methods=["POST"])
def upload_thumbnail():
    """Upload a thumbnail image for a music video."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    if not allowed_file(file.filename):
        return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    # Read file content to check size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > MAX_THUMBNAIL_SIZE:
        return jsonify({"error": f"File too large. Max size: {MAX_THUMBNAIL_SIZE // (1024*1024)}MB"}), 400
    
    filename = secure_filename(file.filename)
    # Add timestamp to avoid name conflicts
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{name}_{timestamp}{ext}"
    filepath = os.path.join(THUMBNAIL_FOLDER, filename)
    file.save(filepath)
    logger.info(f"Thumbnail saved: {filename}")
    return jsonify({"filename": filename, "url": f"/api/thumbnails/{filename}"})


# Serve thumbnail images
@app.route("/api/thumbnails/<filename>")
def serve_thumbnail(filename):
    """Serve a thumbnail image."""
    return send_from_directory(THUMBNAIL_FOLDER, filename)


@app.route("/")
def serve_frontend():
    """Serve the frontend index.html."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/style/<path:filename>")
def serve_style(filename):
    """Serve files from the style directory (fonts, etc.)."""
    style_dir = os.path.join(os.path.dirname(__file__), "..", "style")
    return send_from_directory(style_dir, filename)

@app.route("/<path:path>")
def serve_static(path):
    """Serve static frontend files. Only match non-API paths."""
    if path.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(app.static_folder, path)


# Health check endpoint for Render
@app.route("/health")
def health_check():
    """Health check endpoint to verify the app is running."""
    return jsonify({"status": "ok"})

# Test Google Sheets connection at startup
with app.app_context():
    try:
        logger.info("Testing Google Sheets connection at startup...")
        test_videos = get_all_videos()
        logger.info(f"Successfully connected to Google Sheets. Found {len(test_videos)} videos.")
    except Exception as e:
        logger.error(f"Failed to connect to Google Sheets at startup: {e}")
        logger.error("The app will start but API endpoints may fail until credentials are configured.")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
