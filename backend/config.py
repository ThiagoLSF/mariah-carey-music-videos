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
    "Final Review",                    # 0
    "Name",                            # 1
    "Key Artist",                      # 2
    "Main Video",                      # 3
    "Key Video",                       # 4
    "Unreleased",                      # 5
    "Version Name",                    # 6
    "Introduction Name",               # 7
    "Key Artist (dup)",                # 8 (duplicate column)
    "Aliases",                         # 9
    "Video Type",                      # 10
    "Video Category",                  # 11
    "Director",                        # 12
    "Director of Photography",         # 13
    "Producer",                        # 14
    "Editor",                          # 15
    "Post Production",                 # 16
    "Release Date (US)",               # 17
    "Release Date Accuracy",           # 18
    "Release Date Estimated",          # 19
    "Record Date",                     # 20
    "Record Date Accuracy",            # 21
    "Record Date Estimated",           # 22
    "Record Location",                 # 23
    "Duration (Seconds)",              # 24
    "ISRC",                            # 25
    "IMDB",                            # 26
    "Note",                            # 27
    "Album",                           # 28
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
]

# Service account file path
API_KEY_FILE = os.path.join(os.path.dirname(__file__), "service_account.json")
