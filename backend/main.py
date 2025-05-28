from fastapi import FastAPI

# Import routers from your application
from backend.routes import missions # Assuming missions.py is in backend/routes
# If you have other routers, import them here as well
# from backend.routes import another_router 

# Initialize the FastAPI application
app = FastAPI(
    title="EdTech Backend API",
    description="API for the EdTech platform, including daily missions.",
    version="0.1.0"
)

# Include routers into the application
# The prefix will ensure all routes in missions.router start with /api
# Tags are useful for organizing endpoints in the OpenAPI documentation
app.include_router(missions.router, prefix="/api", tags=["Missions"])
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