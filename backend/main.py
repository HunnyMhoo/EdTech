from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

# Import routers from your application
from backend.routes import missions, questions
from backend.jobs.daily_reset import run_daily_reset_job
from backend.dependencies import get_mission_repository
from backend.database import db_manager
# If you have other routers, import them here as well
# from backend.routes import another_router 

# Configure logging for APScheduler and the job
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)
job_logger = logging.getLogger('backend.jobs.daily_reset') # Use the logger from the job module

# Initialize the FastAPI application
app = FastAPI(
    title="EdTech Backend API",
    description="API for the EdTech platform, including daily missions.",
    version="0.1.0"
)

# Initialize scheduler
scheduler = AsyncIOScheduler(timezone="UTC") # Explicitly set timezone to UTC for the scheduler

@app.on_event("startup")
async def startup_event():
    # Connect to the database
    db_manager.connect_to_database()

    # Get an instance of the repository to pass to the job
    mission_repo = get_mission_repository(db_manager.get_database())

    # Add the job to the scheduler
    # Run daily at 4:00 AM UTC
    scheduler.add_job(
        run_daily_reset_job, 
        'cron', 
        hour=4, 
        minute=0, 
        misfire_grace_time=3600,
        args=[mission_repo] # Pass the repository instance to the job
    )
    # Start the scheduler
    scheduler.start()
    job_logger.info("Scheduler started and daily_reset_job scheduled.")

@app.on_event("shutdown")
async def shutdown_event():
    # Shutdown the scheduler
    if scheduler.running:
        scheduler.shutdown()
        job_logger.info("Scheduler shut down.")
    # Close the database connection
    db_manager.close_database_connection()

# Include routers into the application
# The prefix will ensure all routes in missions.router start with /api
# Tags are useful for organizing endpoints in the OpenAPI documentation
app.include_router(missions.router, prefix="/api", tags=["Missions"])
app.include_router(questions.router, prefix="/api", tags=["Questions"])
# Include other routers here if you have them
# app.include_router(another_router.router, prefix="/api/v1/another", tags=["Another Feature"])

@app.get("/health", tags=["Health Check"])
async def health_check():
    """Simple health check endpoint to confirm the API is running."""
    return {"status": "ok", "message": "API is healthy"}

# To run this application (from the project root directory, e.g., EdTech/):
# Make sure your PYTHONPATH is set up if you have issues with module imports, e.g.:
# export PYTHONPATH=.
# Then run uvicorn:
# uvicorn backend.main:app --reload
# 
# Example: Accessing the missions endpoint after running:
# GET http://127.0.0.1:8000/api/missions/today
# Example: Accessing the health check endpoint:
# GET http://127.0.0.1:8000/health
# Example: Accessing a question:
# GET http://127.0.0.1:8000/api/questions/GATQ001 