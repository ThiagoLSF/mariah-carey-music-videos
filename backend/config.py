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
    "Aliases",                         # 8
    "Video Type",                      # 9
    "Video Category",                  # 10
    "Director",                        # 11
    "Director of Photography",         # 12
    "Producer",                        # 13
    "Editor",                          # 14
    "Post Production",                 # 15
    "Release Date (US)",               # 16
    "Release Date Accuracy",           # 17
    "Release Date Estimated",          # 18
    "Record Date",                     # 19
    "Record Date Accuracy",            # 20
    "Record Date Estimated",           # 21
    "Record Location",                 # 22
    "Duration (Seconds)",              # 23
    "ISRC",                            # 24
    "IMDB",                            # 25
    "Note",                            # 26
    "Album",                           # 27
    "Has Slate",                       # 28
    "Thumbnail",                       # 29
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
