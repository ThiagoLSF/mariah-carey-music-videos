"""
Google Sheets integration for the Mariah Carey Music Videos Database.
Handles reading from and writing to the Google Sheet.
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, SHEET_NAME, SCOPES, COLUMNS, API_KEY_FILE


def get_google_credentials():
    """Get Google Sheets API credentials from service account file."""
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, "r") as f:
                content = f.read().strip()
            if content.startswith("{"):
                return Credentials.from_service_account_file(API_KEY_FILE, scopes=SCOPES)
        except Exception:
            pass

    # Try environment variable
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if creds_json:
        try:
            creds_dict = json.loads(creds_json)
            return Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except (json.JSONDecodeError, ValueError):
            pass

    raise Exception(
        "Google credentials not found. Place service_account.json in the backend/ folder."
    )


def get_sheet():
    """Get the Google Sheet worksheet."""
    creds = get_google_credentials()
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
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
    for row in all_values[1:]:
        if any(cell.strip() for cell in row):  # Skip empty rows
            records.append(_row_to_dict(headers, row))

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

    # Update each provided field
    for col_name, value in video_data.items():
        if col_name in headers:
            col_idx = headers.index(col_name)
            sheet.update_cell(row_idx + 1, col_idx + 1, str(value))

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
