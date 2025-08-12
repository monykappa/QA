from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.qa import router as qa_router
from routes.categories import router as categories_router
from routes.exports import router as exports_router
from database import Base, engine
import models  # Import models to register with Base
import shutil
import os
from datetime import datetime
import schedule
import time
import threading

app = FastAPI(
    title="Q&A API",
    description="API for submitting, retrieving, updating, and exporting Q&A pairs with SQLite storage. Supports custom categories, explicit category addition, and real-time CSV and JSON exports saved to the server.",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema
Base.metadata.create_all(engine)

# Backup function
def backup_database():
    """Copy qa.db to backups directory with date-based filename."""
    db_file = "qa.db"
    backup_dir = "backups"
    current_date = datetime.now().strftime("%d_%m_%Y")
    backup_file = f"{backup_dir}/qa_{current_date}.db"

    # Check if database file exists
    if not os.path.exists(db_file):
        print(f"[{datetime.now()}] Database file {db_file} not found, skipping backup.")
        return

    # Create backups directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)

    # Check if backup for today already exists
    if os.path.exists(backup_file):
        print(f"[{datetime.now()}] Backup for {current_date} already exists: {backup_file}")
        return

    try:
        # Copy the database file
        shutil.copy2(db_file, backup_file)
        print(f"[{datetime.now()}] Successfully created backup: {backup_file}")
    except Exception as e:
        print(f"[{datetime.now()}] Failed to create backup: {str(e)}")

# Start backup scheduler in a background thread
@app.on_event("startup")
async def startup_event():
    def run_backups():
        # Schedule backup to run every 24 hours for production
        schedule.every(24).hours.do(backup_database)
        # For testing, comment the above line and uncomment the line below
        # schedule.every(1).minutes.do(backup_database)

        print(f"[{datetime.now()}] Starting database backup scheduler...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    # Run scheduler in a separate thread to avoid blocking FastAPI
    threading.Thread(target=run_backups, daemon=True).start()

# Include routers
app.include_router(qa_router, prefix="/qa", tags=["Q&A"])
app.include_router(categories_router, prefix="/categories", tags=["Categories"])
app.include_router(exports_router, prefix="/export", tags=["Exports"])
