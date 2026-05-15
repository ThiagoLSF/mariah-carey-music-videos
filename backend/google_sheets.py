"""
Google Sheets integration for the Mariah Carey Music Videos Database.
Handles reading from and writing to the Google Sheet.
"""

import os
import sys
import json
import logging
import gspread
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

# Ensure backend directory is in path for imports
_backend_dir = os.path.dirname(os.path.abspath(__file__))
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from config import SPREADSHEET_ID, SHEET_NAME, SCOPES, COLUMNS, API_KEY_FILE


def get_google_credentials():
    """Get Google Sheets API credentials from service account file."""
    logger.info("Looking for Google credentials...")
    logger.info(f"API_KEY_FILE path: {API_KEY_FILE}")
    logger.info(f"File exists: {os.path.exists(API_KEY_FILE)}")
    
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, "r") as f:
                content = f.read().strip()
            if content.startswith("{"):
                logger.info("Using service_account.json for credentials")
                return Credentials.from_service_account_file(API_KEY_FILE, scopes=SCOPES)
            else:
                logger.warning("service_account.json exists but does not start with '{'")
        except Exception as e:
            logger.warning(f"Failed to load service_account.json: {e}")

    # Try environment variable
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    logger.info(f"GOOGLE_CREDENTIALS env var present: {creds_json is not None}")
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            logger.info("Using GOOGLE_CREDENTIALS environment variable")
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except json.JSONDecodeError as e:
            logger.error(f"GOOGLE_CREDENTIALS is not valid JSON: {e}")
        except ValueError as e:
            logger.error(f"GOOGLE_CREDENTIALS contains invalid credentials: {e}")

    raise Exception(
        "Google credentials not found. Place service_account.json in the backend/ folder "
        "or set the GOOGLE_CREDENTIALS environment variable."
    )


def get_sheet():
    """Get the Google Sheet worksheet."""
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    logger.info(f"Opening spreadsheet with ID: {SPREADSHEET_ID}")
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    logger.info(f"Accessing sheet: {SHEET_NAME}")
    return spreadsheet.sheet1


def _row_to_dict(headers, row):
    """Convert a row of values to a dictionary using column names."""
    record = {}
    for i, header in enumerate(headers):
        if i < len(row):
            record[header] = row[i]
        else:
            record[header] = ""
    return record


def get_all_videos():
    """Fetch all music videos from the Google Sheet."""
    sheet = get_sheet()
    all_values = sheet.get_all_values()

    if not all_values:
        return []

    headers = all_values[0]
    records = []
    for i, row in enumerate(all_values[1:]):
        if any(cell.strip() for cell in row):  # Skip empty rows
            record = _row_to_dict(headers, row)
            record["_row"] = i + 1  # 1-based row index (excluding header)
            records.append(record)

    return records


def get_video_by_id(video_id):
    """Fetch a single music video by its row index (1-based, excluding header)."""
    records = get_all_videos()
    idx = int(video_id) - 1 if video_id.isdigit() else -1
    if 0 <= idx < len(records):
        return records[idx]
    return None


def add_video(video_data):
    """Add a new music video to the Google Sheet."""
    sheet = get_sheet()
    all_values = sheet.get_all_values()
    headers = all_values[0] if all_values else COLUMNS

    # Build the row in column order
    row = []
    for col in COLUMNS:
        if col in video_data:
            row.append(str(video_data[col]))
        else:
            row.append("")

    sheet.append_row(row)

    # Return the new row index as ID
    new_id = len(all_values)  # header + existing data rows
    return {"message": "Video added successfully", "id": new_id}


def update_video(video_id, video_data):
    """Update an existing music video in the Google Sheet by row index."""
    sheet = get_sheet()
    all_values = sheet.get_all_values()
    headers = all_values[0] if all_values else COLUMNS

    row_idx = int(video_id)
    if row_idx < 1 or row_idx >= len(all_values):
        return {"error": f"Video with ID {video_id} not found"}, 404

    # Get the current row values
    current_row = all_values[row_idx]

    # Build updated row by applying changes on top of current values
    updated_row = list(current_row)
    for col_name, value in video_data.items():
        if col_name in headers:
            col_idx = headers.index(col_name)
            # Extend row if needed
            while len(updated_row) <= col_idx:
                updated_row.append("")
            updated_row[col_idx] = str(value)

    # Batch update the entire row at once
    # Use gspread's 1-based (row, col) range format
    end_col = len(updated_row)
    # gspread's update accepts a list of lists with a cell_list or range
    cell_list = sheet.range(row_idx + 1, 1, row_idx + 1, end_col)
    for i, cell in enumerate(cell_list):
        cell.value = updated_row[i] if i < len(updated_row) else ""
    sheet.update_cells(cell_list)

    return {"message": f"Video {video_id} updated successfully"}


def delete_video(video_id):
    """Delete a music video from the Google Sheet by row index."""
    sheet = get_sheet()
    all_values = sheet.get_all_values()

    row_idx = int(video_id)
    if row_idx < 1 or row_idx >= len(all_values):
        return {"error": f"Video with ID {video_id} not found"}, 404

    sheet.delete_rows(row_idx + 1)
    return {"message": f"Video {video_id} deleted successfully"}
