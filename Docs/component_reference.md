# Component Reference

This document describes the key components of the EdTech Platform, grouped by their operational domain.

## Backend Components

### 1. FastAPI Application (`backend/main.py`)
*   **Description:** The main entry point for the backend server. Initializes the FastAPI application, includes all API routers, and may define global configurations or middleware.
*   **Location:** [`backend/main.py`](../backend/main.py)
*   **Dependencies:** FastAPI library, routers (e.g., `backend.routes.missions`).
*   **Key Functionality:** Serves the API, including a health check endpoint (`/health`).

### 2. Missions API Router (`backend/routes/missions.py`)
*   **Description:** Handles all API requests related to missions. Defines endpoints for mission retrieval and progress updates.
*   **Location:** [`backend/routes/missions.py`](../backend/routes/missions.py)
*   **Dependencies:** FastAPI, `backend.services.mission_service`, `backend.models.daily_mission`, `backend.models.api_responses`.
*   **Key Functionality:**
    *   Provides the `GET /api/missions/today` endpoint to fetch the current day's mission for a user, including progress.
    *   Provides the `PUT /api/missions/today/progress` endpoint to save mission progress.
    *   Uses a dependency (`get_current_user_id`) for (currently simulated) user identification.

### 3. Mission Service (`backend/services/mission_service.py`)
*   **Description:** Encapsulates the business logic for managing daily missions. This includes generating new missions, fetching existing ones, and updating mission progress.
*   **Location:** [`backend/services/mission_service.py`](../backend/services/mission_service.py)
*   **Dependencies:** Python standard libraries (datetime, random, pathlib, csv), `backend.models.daily_mission`.
*   **Key Functionality:**
    *   `get_todays_mission_for_user()`: Retrieves a user's mission for the current day (UTC+7), including progress, from the data store (currently a mock DB).
    *   `generate_daily_mission()`: Generates a new daily mission using `DailyMissionDocument`.
    *   `update_mission_progress()`: Updates the `current_question_index`, `answers`, and `status` of a user's daily mission.
    *   Internal functions simulating database interactions now use `DailyMissionDocument` and a list `_mock_db_missions`.
    *   `get_utc7_today_date()`: Utility for timezone-correct date calculations.

### 4. Data Models
*   **Description:** Defines the structure of data used within the application, primarily using Pydantic models for validation and serialization.
*   **Locations:**
    *   `backend/models/api_responses.py`: Contains generic `MissionResponse` and `ErrorResponse` models.
    *   `backend/models/daily_mission.py`: Contains `DailyMissionDocument` Pydantic model defining the structure of a mission, including progress fields, and `MissionStatus` enum.
*   **Dependencies:** Pydantic.
*   **Key Functionality:** Ensures data consistency and provides clear schemas for API contracts, database objects, and service layer interactions.

### 5. Question Data (`backend/data/gat_questions.csv`)
*   **Description:** A CSV file serving as the current source for questions used in daily missions.
*   **Location:** [`backend/data/gat_questions.csv`](../backend/data/gat_questions.csv)
*   **Dependencies:** None directly; accessed by `MissionService`.
*   **Key Functionality:** Provides a list of question IDs and other question-related data.

### 6. Integration Tests (`backend/tests/integration/test_missions_api.py`)
*   **Description:** Contains integration tests for the Missions API endpoints.
*   **Location:** [`backend/tests/integration/test_missions_api.py`](../backend/tests/integration/test_missions_api.py)
*   **Dependencies:** FastAPI TestClient, `unittest.mock`.
*   **Key Functionality:** Verifies the behavior of the `/api/missions/today` endpoint. (Note: Needs update for progress endpoint).

## Frontend Components

Modifications based on recent implementation of Task 5:

### 1. HomeScreen (`frontend/screens/HomeScreen.tsx`)
*   **Description:** Main screen of the app. May display an overview or entry point to the daily mission.
*   **Location:** `frontend/screens/HomeScreen.tsx` (Actual implementation details might vary based on how/if it links to `MissionScreen`).
*   **Dependencies:** React, React Native, API service module (`frontend/services/missionApi.ts`).

### 2. MissionScreen (`frontend/screens/MissionScreen.tsx`)
*   **Description:** Screen for interacting with an active mission. Fetches the mission (including progress), displays questions, handles user answers, and saves progress to the backend. Manages mission state like current question index and user's answers.
*   **Location:** `frontend/screens/MissionScreen.tsx` (Created)
*   **Dependencies:** React, React Native, `frontend/services/missionApi.ts`.

### 3. Mission API Service (`frontend/services/missionApi.ts`)
*   **Description:** A dedicated module to handle API calls to the backend for mission-related data. Includes functions to fetch the daily mission (with progress) and update mission progress.
*   **Location:** `frontend/services/missionApi.ts` (Updated)
*   **Dependencies:** Native `fetch` API. Defines `Mission`, `Answer`, `Question`, and `MissionProgressUpdatePayload` interfaces.

## Infrastructure Components (Conceptual / Planned)

*   **Database Server:** MongoDB instance (not yet provisioned; currently using mock DB in backend).
*   **Authentication Service:** LINE Login (external service).
*   **Hosting Environment:** Platform for deploying the FastAPI backend and serving the React Native app (e.g., cloud VMs, container services, app stores).
*   **Cron Job Runner:** System for executing the `daily_reset.py` job (e.g., Linux cron, cloud scheduler service).

Refer to the [Architecture Document](architecture.md) for a visual representation of how these components interact. 