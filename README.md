# Mariah Carey Music Videos Database

A searchable, filterable, and manageable database of Mariah Carey's music videos, powered by Google Sheets.

## Features

- **Search** across titles, albums, directors, and labels
- **Filter** by year, album, and director
- **Sort** by any column (title, year, album, director, release date, label)
- **Add** new music videos directly to the Google Sheet
- **Edit** existing entries
- **Delete** entries
- **Responsive** dark-themed UI with gold accents

## Tech Stack

- **Backend:** Python Flask REST API
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Database:** Google Sheets (via gspread API)
- **Authentication:** Google Service Account

## Setup

### 1. Google Sheets API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Google Sheets API**
4. Create a **Service Account** and download the JSON key file
5. Rename the key file to `service_account.json` and place it in the `backend/` folder
6. Share your Google Sheet with the service account email (found in the JSON file)

### 2. Configuration

Edit `backend/config.py` and set your `SPREADSHEET_ID`:

```python
SPREADSHEET_ID = "your-google-sheet-id-here"
```

The sheet ID is the long string in your sheet's URL:
`https://docs.google.com/spreadsheets/d/THIS_IS_THE_ID/edit`

### 3. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 4. Run the Backend

```bash
cd backend
python app.py
```

The API will start at `http://localhost:5000`.

### 5. Open the Frontend

Open `frontend/index.html` in your browser, or serve it with any static server.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/videos` | List all videos (with search/filter/sort params) |
| GET | `/api/videos/:id` | Get a single video by ID |
| POST | `/api/videos` | Add a new video |
| PUT | `/api/videos/:id` | Update a video |
| DELETE | `/api/videos/:id` | Delete a video |
| GET | `/api/filters` | Get distinct filter options |

### Query Parameters for GET /api/videos

- `search` - Text search across title, album, director, label
- `year` - Filter by year
- `album` - Filter by album
- `director` - Filter by director
- `label` - Filter by label
- `sort` - Sort field (title, year, album, director, release date, label)
- `order` - Sort order (asc or desc)

## Google Sheet Structure

The sheet should have these columns (first row as header):

ID | Title | Album | Year | Director | Release Date | Label | Certification | YouTube Link | YouTube Views | Notes
