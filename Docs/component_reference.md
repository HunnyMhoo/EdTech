# Component Reference

This document describes the key components of the EdTech Platform, grouped by their operational domain.

## Backend Components

### 1. FastAPI Application (`backend/main.py`)
*   **Description:** The main entry point for the backend server. Initializes the FastAPI application, includes all API routers, and may define global configurations or middleware.
*   **Location:** [`backend/main.py`](../backend/main.py)
*   **Dependencies:** FastAPI library, routers (e.g., `backend.routes.missions`).
*   **Key Functionality:** Serves the API, including a health check endpoint (`/health`).

### 2. Missions API Router (`backend/routes/missions.py`)
*   **Description:** Handles all API requests related to missions. Defines endpoints for mission retrieval and potentially other mission-related actions in the future.
*   **Location:** [`backend/routes/missions.py`](../backend/routes/missions.py)
*   **Dependencies:** FastAPI, `backend.services.mission_service`, `backend.models.api_responses`.
*   **Key Functionality:**
    *   Provides the `GET /api/missions/today` endpoint to fetch the current day's mission for a user.
    *   Uses a dependency (`get_current_user_id`) for (currently simulated) user identification.

### 3. Mission Service (`backend/services/mission_service.py`)
*   **Description:** Encapsulates the business logic for managing daily missions. This includes generating new missions and fetching existing ones.
*   **Location:** [`backend/services/mission_service.py`](../backend/services/mission_service.py)
*   **Dependencies:** Python standard libraries (datetime, random, pathlib, csv), Pydantic (for `DailyMission` model).
*   **Key Functionality:**
    *   `get_todays_mission_for_user()`: Retrieves a user's mission for the current day (UTC+7) from the data store (currently a mock DB).
    *   `generate_daily_mission()`: Generates a new daily mission by selecting random questions from a pool (CSV file) and stores it (mock DB).
    *   `_fetch_mission_from_db()`, `_find_mission_in_db()`, `_save_mission_to_db()`: Internal functions simulating database interactions with an in-memory dictionary (`_mock_db`).
    *   `get_utc7_today_midnight_utc0()`: Utility for timezone-correct date calculations.
    *   `_load_question_ids_from_csv()`: Loads question IDs from `backend/data/gat_questions.csv`.

### 4. Data Models
*   **Description:** Defines the structure of data used within the application, primarily using Pydantic models for validation and serialization.
*   **Locations:**
    *   `backend/models/api_responses.py`: Contains `MissionResponse` for standardizing API output.
    *   `backend/services/mission_service.py`: Contains the `DailyMission` Pydantic model (could be moved to `backend/models/daily_mission.py` as per original plan).
*   **Dependencies:** Pydantic.
*   **Key Functionality:** Ensures data consistency and provides clear schemas for API contracts and service layer interactions.

### 5. Question Data (`backend/data/gat_questions.csv`)
*   **Description:** A CSV file serving as the current source for questions used in daily missions.
*   **Location:** [`backend/data/gat_questions.csv`](../backend/data/gat_questions.csv)
*   **Dependencies:** None directly; accessed by `MissionService`.
*   **Key Functionality:** Provides a list of question IDs and other question-related data.

### 6. Integration Tests (`backend/tests/integration/test_missions_api.py`)
*   **Description:** Contains integration tests for the Missions API endpoints.
*   **Location:** [`backend/tests/integration/test_missions_api.py`](../backend/tests/integration/test_missions_api.py)
*   **Dependencies:** FastAPI TestClient, `unittest.mock`.
*   **Key Functionality:** Verifies the behavior of the `/api/missions/today` endpoint by mocking service layer dependencies and checking responses for success, not found, and error cases.

## Frontend Components (Planned)

As per the [Implementation Plan](Requirement/userstory/story1/implementation_plan.md), the frontend will be a React Native application. Key planned components include:

### 1. HomeScreen (`frontend/screens/HomeScreen.tsx`)
*   **Description:** Main screen of the app, responsible for fetching and displaying the daily mission on app load.
*   **Location:** `frontend/screens/HomeScreen.tsx` (to be created)
*   **Dependencies:** React, React Native, API service module.

### 2. MissionScreen (`frontend/screens/MissionScreen.tsx`)
*   **Description:** Screen for interacting with an active mission, displaying questions, and handling user answers. Will manage mission state like current question index.
*   **Location:** `frontend/screens/MissionScreen.tsx` (to be created)
*   **Dependencies:** React, React Native.

### 3. Mission API Service (`frontend/services/missionApi.ts`)
*   **Description:** A dedicated module to handle API calls to the backend for mission-related data.
*   **Location:** `frontend/services/missionApi.ts` (to be created)
*   **Dependencies:** A fetch library (e.g., native `fetch` or `axios`).

## Infrastructure Components (Conceptual / Planned)

*   **Database Server:** MongoDB instance (not yet provisioned; currently using mock DB in backend).
*   **Authentication Service:** LINE Login (external service).
*   **Hosting Environment:** Platform for deploying the FastAPI backend and serving the React Native app (e.g., cloud VMs, container services, app stores).
*   **Cron Job Runner:** System for executing the `daily_reset.py` job (e.g., Linux cron, cloud scheduler service).

Refer to the [Architecture Document](architecture.md) for a visual representation of how these components interact. 