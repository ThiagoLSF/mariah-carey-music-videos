"""
Configuration for the Mariah Carey Music Videos Database.
Uses Google Sheets as the data source.
"""

import os

# Google Sheets configuration
SPREADSHEET_ID = "1QeGCrebbt7UBHTnlLC--8mYptjXCYRi5LNvx21GUI0c"
SHEET_NAME = "Videos"

# Google Sheets API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Full column mapping (based on the actual spreadsheet structure)
# Index positions match the sheet columns (0-based)
COLUMNS = [
    "Name",                            # 0
    "Has Slate",                       # 1
    "Thumbnail",                       # 2
    "Key Artist",                      # 3
    "Main Video",                      # 4
    "Key Video",                       # 5
    "Unreleased",                      # 6
    "Version Name",                    # 7
    "Introduction Name",               # 8
    "Key Artist",                      # 9  (duplicate in spreadsheet)
    "Aliases",                         # 10
    "Video Type",                      # 11
    "Video Category",                  # 12
    "Director",                        # 13
    "Director of Photography",         # 14
    "Producer",                        # 15
    "Editor",                          # 16
    "Post Production (VFX, Color Grading etc)",  # 17
    "Release Date (US)",               # 18
    "Release Date Accuracy",           # 19
    "Release Date Estimated",          # 20
    "Record Date",                     # 21
    "Record Date Accuracy",            # 22
    "Record Date Estimated",           # 23
    "Record Location",                 # 24
    "Duration (Seconds)",              # 25
    "ISRC",                            # 26
    "IMDB",                            # 27
    "Note",                            # 28
    "Album",                           # 29
]

# Columns to display in the frontend table
DISPLAY_COLUMNS = [
    "Name",
    "Version Name",
    "Album",
    "Video Type",
    "Video Category",
    "Director",
    "Director of Photography",
    "Producer",
    "Release Date (US)",
    "Duration (Seconds)",
    "Record Location",
    "IMDB",
    "Note",
    "Has Slate",
]

# Service account file path
API_KEY_FILE = os.path.join(os.path.dirname(__file__), "service_account.json")
