# Journal Project

My journal project to log daily work, struggles, and intentions. 
Designed for developers and learners to reflect and track progress.

## Local Implentation
1.
   - python -m venv venv
   - source venv/bin/activate or venv\Scripts\activate on Windows
2.
   - pip install -r requirements.txt
3.
   - create a .env file with 
   - DATABASE_URL=postgresql://user:password@localhost:5432/devjournal
4.
   - Create your database table in postgres
   - CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
   );
5.
   - run application
   - fastapi dev main.py

### Example Entry
{
  "work": "Worked on FastAPI routes",
  "struggle": "Entries not created",
  "intention": "Fix configuration"
}

## Development Tasks

### API Implementation

1. Endpoint in `journal_router.py` have been updated:
   - GET /entries - List all journal entries
   - GET /entries/{entry_id} - Get single entry
   - DELETE /entries/{entry_id} - Delete specific entry

### Logging Setup

1. Basic console logging in `main.py`:
   - Configure basic logging
   - Set logging level to INFO
   - Add console handler

### Data Model Improvements

1. Entry model in `models/entry.py` has been added to `services/entry_service.py`:
   - Added basic field validation rules
   - Added input data sanitization
   - Added schema version tracking

### Development Environment

1. Configure cloud provider CLI in `.devcontainer/devcontainer.json`:
   - AWSCLI configured along with env variables

## Technical Implementation

### Data Schema

The journal entry data model is structured as follows:

| Field       | Type      | Description                                | Validation                   |
|-------------|-----------|--------------------------------------------|------------------------------|
| id          | string    | Unique identifier for the entry (UUID)     | Auto-generated UUID          |
| work        | string    | What did you work on today?                | Required, max 256 characters |
| struggle    | string    | What's one thing you struggled with today? | Required, max 256 characters |
| intention   | string    | What will you study/work on tomorrow?      | Required, max 256 characters |
| created_at  | datetime  | Timestamp when the entry was created       | Auto-generated UTC timestamp |
| updated_at  | datetime  | Timestamp when the entry was last updated  | Auto-updated UTC timestamp   |

All text fields sanitizatized to prevent injection attacks and ensure data quality. The schema includes version tracking to handle potential future changes to the data structure.

### API Endpoints

1. **GetEntries:** Returns a JSON list of all journal entries - IMPLEMENTED
2. **GetEntry:** Returns a specific journal entry by ID - IMPLEMENTED
3. **DeleteEntry:** Removes a specific journal entry - IMPLEMENTED
4. **CreateEntry:** Creates a new journal entry - IMPLEMENTED
5. **UpdateEntry:** Updates an existing journal entry - IMPLEMENTED
6. **DeleteAllEntries:** Removes all journal entries - IMPLEMENTED