# FastAPI Firebase & Supabase Template

## Setup

1. Create a Firebase project and download the service account key as `firebase_credentials.json` in the project root.
   - **Important:** Replace the placeholder values in `firebase_credentials.json` with your actual Firebase service account credentials.
2. Create a Supabase project and get your `SUPABASE_URL` and `SUPABASE_KEY`.
3. Set the following environment variables:
   - `FIREBASE_CRED_PATH` (default: `firebase_credentials.json`)
   - `SUPABASE_URL`
   - `SUPABASE_KEY`

## Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn firebase-admin supabase
```

## Database 
- See more details in [DATABASE.md](DATABASE.md)
- To generate ERD run : 
```bash 
python generate_erd.py 
```


## Run the server

```bash
python run.py
```

## Project Structure

- `app.py` - Contains all the FastAPI application logic, Firebase and Supabase setup
- `run.py` - Entry point for running the application
- `firebase_credentials.json` - Firebase service account credentials (not tracked in git)

## Endpoints

- `GET /users/me` - Returns current Firebase user info (requires Bearer token)
- `POST /data` - Insert data into Supabase (requires Bearer token)
- `GET /data` - Get all data from Supabase (requires Bearer token)
- `PUT /data/{item_id}` - Update data by id (requires Bearer token)
- `DELETE /data/{item_id}` - Delete data by id (requires Bearer token) 