# API Contracts

This document provides details on the public and internal APIs available in the EdTech Platform backend. As the system evolves, this document will be updated to reflect new endpoints and changes.

## Conventions

-   **Base URL:** All API endpoints are prefixed with `/api` (e.g., `http://localhost:8000/api`).
-   **Authentication:** Currently simulated via a hardcoded user ID (`test_user_123`). Future implementation will use LINE Login (OAuth 2.0 bearer tokens).
-   **Response Format:** Standardized JSON responses using the `MissionResponse` model where applicable (`status`, `data`, `message`).
-   **Error Handling:** Uses standard HTTP status codes. Errors from FastAPI often return a JSON object with a `detail` field.

## Public APIs

These APIs are intended to be consumed by the frontend client (React Native app).

### Missions API

-   **Router Source:** [`backend/routes/missions.py`](../backend/routes/missions.py)
-   **Tag in OpenAPI:** `Missions`

#### 1. Get Today's Mission

*   **Description:** Retrieves the daily mission for the currently authenticated user for today (UTC+7).
*   **Method:** `GET`
*   **Path:** `/missions/today`
*   **Purpose:** Allows the frontend to fetch and display the user's current daily mission.
*   **Parameters:**
    *   None (User ID is derived from the authentication context - currently a hardcoded dependency `get_current_user_id`).
*   **Responses:**
    *   **`200 OK` (Success):**
        *   **Body:** `MissionResponse` model
            ```json
            {
                "status": "success",
                "data": {
                    "userId": "string",
                    "date": "datetime string (ISO 8601)", // UTC datetime representing start of UTC+7 day
                    "questionIds": ["string"],
                    "status": "string (e.g., not_started, in_progress, complete)",
                    "createdAt": "datetime string (ISO 8601)" // Optional
                },
                "message": "Today's mission retrieved successfully."
            }
            ```
        *   The `data` field contains a `DailyMission` schema object (defined in `backend.services.mission_service.DailyMission`).
    *   **`404 Not Found` (Error):**
        *   **Body:**
            ```json
            {
                "detail": "No mission found for user {user_id} for today (UTC+7)."
            }
            ```
    *   **`500 Internal Server Error` (Error):**
        *   **Body:**
            ```json
            {
                "detail": "An unexpected error occurred: {error_message}"
            }
            ```
*   **Code Reference:** `get_today_mission_for_current_user` function in [`backend/routes/missions.py`](../backend/routes/missions.py).

---

### Health Check API

-   **Router Source:** [`backend/main.py`](../backend/main.py)
-   **Tag in OpenAPI:** `Health Check`

#### 1. Health Check

*   **Description:** Simple endpoint to verify if the API server is running and healthy.
*   **Method:** `GET`
*   **Path:** `/health`
*   **Purpose:** Used for monitoring and operational checks.
*   **Parameters:** None.
*   **Responses:**
    *   **`200 OK` (Success):**
        *   **Body:**
            ```json
            {
                "status": "ok",
                "message": "API is healthy"
            }
            ```
*   **Code Reference:** `health_check` function in [`backend/main.py`](../backend/main.py).

---

## Internal APIs/Service Functions

While not strictly HTTP APIs, the backend services expose functions that act as internal contracts between components.

### Mission Service

-   **Source:** [`backend/services/mission_service.py`](../backend/services/mission_service.py)

#### 1. `get_todays_mission_for_user(user_id: str) -> Optional[DailyMission]`

*   **Description:** Retrieves today's (UTC+7) mission for a given user from the data store.
*   **Parameters:**
    *   `user_id (str)`: The ID of the user.
*   **Returns:** A `DailyMission` Pydantic model instance if a mission is found, otherwise `None`.
*   **Called by:** The `/missions/today` API endpoint.

#### 2. `generate_daily_mission(user_id: str, current_datetime_utc: Optional[datetime] = None) -> Dict[str, Any]`

*   **Description:** Generates and persists a new daily mission with 5 questions for the user. (Note: This is the existing function; a Pydantic-returning version `generate_daily_mission_for_user` was also added as a placeholder/refactor example).
*   **Parameters:**
    *   `user_id (str)`: The user's ID.
    *   `current_datetime_utc (Optional[datetime])`: For testing, to simulate a specific time.
*   **Returns:** A dictionary representing the mission.
*   **Raises:** `MissionAlreadyExistsError`, `NoQuestionsAvailableError`.

For a list of components, see the [Component Reference](component_reference.md). 